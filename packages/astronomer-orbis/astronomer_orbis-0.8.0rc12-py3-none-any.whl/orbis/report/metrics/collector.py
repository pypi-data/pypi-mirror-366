import logging
from datetime import datetime

import polars as pl

from orbis.api.prometheus import PrometheusData
from orbis.config import (
    ASTRO_SOFTWARE_API_TOKEN,
    SCHEDULER_QUERIES,
    SOFTWARE_QUERIES_FILE_PATH,
    parse_yaml,
)
from orbis.data.models import DeploymentConfig, Figure, Metric, PodStats, ReportMetadata, WorkerQueueStats
from orbis.data.transform import process_metric_data
from orbis.report.metrics.k8s_queries import update_k8s_metrics
from orbis.report.metrics.query_types import identify_query_type
from orbis.report.metrics.query_validation import validate_query_formatting
from orbis.report.visualizer import Visualizer

logger = logging.getLogger("root")


def create_metric(metric_identifier: str, metric_data: dict, namespace: str, worker_queues: list[WorkerQueueStats] | None = None, executor_type: str | None = None) -> Metric:
    """Create a Metric object from raw data."""
    can_have_worker_queues = ["Celery CPU", "Celery Memory", "Celery Pod Count"]
    metric = Metric(
        metric_identifier=metric_identifier,
        metric_name=metric_data["metric"],
        queries=metric_data["queries"],
        file_name=metric_data["file_name"].format(namespace=namespace),
        aggregators=metric_data["aggregators"],
        table_headers=metric_data["table_headers"],
        include_in=metric_data.get("include_in", {"docx": True, "csv": True, "json": True}),
        worker_queues=worker_queues if (worker_queues is not None and metric_data["metric"] in can_have_worker_queues) else [],
        executor_type=executor_type if executor_type is not None else "",
        pod_stats=[],  # Initialize empty pod_stats list if this is a pod metric
        query_types=metric_data.get("query_types"),  # Get query_types if present
    )
    return metric


async def get_data_object(organization_name: str, namespace: str, start_date, end_date, verify_ssl: bool = True) -> PrometheusData:
    """Get the appropriate data object based on whether it's Astro or Software."""
    if not ASTRO_SOFTWARE_API_TOKEN:
        raise ValueError("ASTRO_SOFTWARE_API_TOKEN environment variable is required")

    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    return PrometheusData(
        token=ASTRO_SOFTWARE_API_TOKEN,
        organization_name=organization_name,
        namespace=namespace,
        start_date=start_date,
        end_date=end_date,
        verify_ssl=verify_ssl,
    )


class QueryTransformer:
    """Transforms query patterns based on platform."""

    @staticmethod
    def transform_pod_pattern(query: str) -> str:
        """Transform pod query patterns based on platform."""
        if "worker-default-.*" in query:
            return query.replace("worker-default-.*", "worker-.*")
        return query


async def get_metric_data(data_obj: PrometheusData, metric: Metric, namespace: str, release_name: str | None) -> list[pl.DataFrame]:
    """Get metric data from the data object.

    Args:
        data_obj: Data object (PrometheusData)
        metric: Metric object containing queries
        namespace: Namespace to query
        release_name: Release name to query

    Returns:
        list: List of dataframes with query results, each dataframe has columns:
            - Time Stamp: The timestamp of the data point
            - Value: The metric value
            - PodType: (optional) The pod type if this is a pod metric
    """
    query_type = identify_query_type(metric.metric_identifier)
    queries = []
    query_types = []  # Track pod types for each query if this is a pod metric

    # Handle each query in the metric
    for idx, query in enumerate(metric.queries):
        # Validate query formatting
        is_valid, error = validate_query_formatting(query, query_type)
        if not is_valid:
            logger.error(f"Invalid query formatting: {error}")
            logger.error(f"Query: {query}")
            continue

        # Format the query
        try:
            formatted_query = query.format(namespace=namespace, release_name=release_name)
            transformed_query = QueryTransformer.transform_pod_pattern(formatted_query)
            queries.append(transformed_query)
            # Check if this is a pod-based metric or has pod types specified
            if hasattr(metric, "pod_small_large") or _is_pod_based_metric(metric):
                query_types.append(metric.query_types[idx] if metric.query_types else "small" if idx == 0 else "large")
        except KeyError as e:
            logger.error(f"Failed to format query: {e}")
            logger.error(f"Query: {query}")
            continue

    if not queries:
        logger.error("No valid queries found")
        return []

    # Execute each query and process results
    dfs = []
    for idx, query in enumerate(queries):
        df = await data_obj.query_over_range(
            query=query,
            step=5,
        )
        df = process_metric_data(df, start_date=data_obj.start_date, end_date=data_obj.end_date)

        # Always add pod type if query_types exist
        if query_types and idx < len(query_types):
            df = df.with_columns(pl.lit(query_types[idx]).alias("PodType"))

        dfs.append(df)
    return dfs


def get_type_selector(executor_type: DeploymentConfig) -> str | None:
    """Get the appropriate type selector based on executor type."""
    if executor_type.executor.lower() == "kubernetes":
        logger.info("Namespace has Kubernetes Executor. Plotting KE+KPO.")
        return "ke"
    elif executor_type.executor.lower() == "celery":
        logger.info("Namespace has Celery Executor. Plotting Celery metrics.")
        return "celery"
    else:
        logger.warning(f"Unknown executor type: {executor_type}")
        return None


def update_queries_for_type(parsed_yaml_queries: dict, type_selector: str, worker_queues: list[WorkerQueueStats] | None):
    """Update queries based on type selector."""
    logger.info(f"Updating queries for type: {type_selector}")
    if type_selector == "ke":
        logger.info("Processing KE queries")
        update_k8s_queries(parsed_yaml_queries, type_selector)
    elif type_selector == "celery":
        if worker_queues:
            logger.info("Updating Celery queries with worker queues.")
            update_celery_queries(parsed_yaml_queries, type_selector, worker_queues)
        # Also update KPO metrics for Celery executor
        update_k8s_queries(parsed_yaml_queries, type_selector)


def update_celery_queries(parsed_yaml_queries: dict, type_selector: str, worker_queues: list[WorkerQueueStats] | None):
    """Update Celery queries with worker queue information."""
    for metric in ["cpu", "memory", "pod_count"]:
        base_query = parsed_yaml_queries[type_selector][metric]["queries"][0]
        if worker_queues:
            # Update queries with worker queue names
            parsed_yaml_queries[type_selector][metric]["queries"] = [base_query.replace("worker-.*", f"worker-{queue.queue_name}-.*") for queue in worker_queues]
        else:
            parsed_yaml_queries[type_selector][metric]["queries"] = [base_query]


def update_k8s_queries(parsed_yaml_queries: dict, type_selector: str):
    """Update Kubernetes-related queries (KE/KPO) with pod type information."""
    logger.info(f"Updating K8s queries for {type_selector}")
    if type_selector in parsed_yaml_queries:
        logger.info(f"Found metrics: {list(parsed_yaml_queries[type_selector].keys())}")
    metrics_to_remove, metrics_to_add = update_k8s_metrics(parsed_yaml_queries, type_selector)
    logger.info(f"Metrics to remove: {metrics_to_remove}")
    logger.info(f"Metrics to add: {list(metrics_to_add.keys())}")

    # Remove old metrics and add new ones
    for metric in metrics_to_remove:
        del parsed_yaml_queries[type_selector][metric]

    parsed_yaml_queries[type_selector].update(metrics_to_add)


def _collect_metrics(parsed_yaml_queries: dict, namespace: str, worker_queues: list[WorkerQueueStats] | None, executor_type: str, type_selector: str) -> list[Metric]:
    """Collect all metrics for a namespace."""
    metrics = []

    # Process non-reporting metrics
    # Non reporting metrics are top level and not parents.
    non_reporting_queries = ["total_task_success", "total_task_failure"]
    for metric_identifier in non_reporting_queries:
        if metric_identifier in parsed_yaml_queries:
            metric_data = parsed_yaml_queries[metric_identifier]
            metrics.append(create_metric(metric_identifier, metric_data, namespace, worker_queues, executor_type))

    # Process executor-specific metrics
    for query_type in [SCHEDULER_QUERIES, type_selector]:
        for metric_identifier, metric_data in parsed_yaml_queries[query_type].items():
            metrics.append(create_metric(metric_identifier, metric_data, namespace, worker_queues, executor_type))

    return metrics


def _calculate_stats(df: pl.DataFrame) -> dict:
    """Calculate statistics for a dataframe."""
    logger.debug("=== Stats Calculation Debug ===")
    logger.debug(f"Input DataFrame shape: {df.shape}")
    logger.debug(f"Columns: {df.columns}")

    if "PodType" in df.columns:
        unique_pod_types = df.select(pl.col("PodType").unique()).to_series().to_list()
        logger.debug(f"Pod Types present: {unique_pod_types}")
        logger.debug("Raw values per pod type:")
        # for pod_type in ["small", "large"]:
        #     pod_values = df.filter(pl.col("PodType") == pod_type).select(pl.col("Value")).to_series().to_list()
        #     logger.debug(f"{pod_type}: {pod_values}")

        # Preprocess first
        preprocessed_df = _preprocess_dataframe(df)
        if preprocessed_df is None or preprocessed_df.is_empty():
            preprocessed_df = df  # Use original if preprocessing failed

        # Then do time-based aggregation
        aggregated_df = preprocessed_df.group_by("Time Stamp").agg([
            pl.col("Value").mean().alias("Value"),
            *(pl.col(col).first() for col in preprocessed_df.columns if col not in ["Time Stamp", "Value"]),
        ])

        # aggregated_values = aggregated_df.select(pl.col("Value")).to_series().to_list()
        # logger.debug(f"Aggregated values: {aggregated_values}")

        stats = _compute_basic_stats(aggregated_df)
        logger.debug(f"Main stats from aggregated values: {stats}")

        stats["pod_stats"] = _compute_pod_stats(preprocessed_df)
        logger.debug(f"Individual pod stats: {stats['pod_stats']}")
    else:
        # For non-pod metrics, just preprocess and compute stats
        preprocessed_df = _preprocess_dataframe(df)
        if preprocessed_df is None or preprocessed_df.is_empty():
            stats = _get_default_stats()
        else:
            stats = _compute_basic_stats(preprocessed_df)
        logger.debug(f"Non-pod stats: {stats}")

    logger.debug("===========================")
    return stats


def _get_default_stats() -> dict[str, float | list]:
    stats: dict[str, float | list] = {"mean_value": 0, "median_value": 0, "max_value": 0, "min_value": 0, "p90_value": 0}
    stats["pod_stats"] = []
    stats["worker_queue_stats"] = []
    return stats


def _preprocess_dataframe(df: pl.DataFrame) -> pl.DataFrame | None:
    """Preprocess dataframe values with proper type casting."""
    try:
        # Only handle type casting and null filtering, no aggregation
        df = df.with_columns(pl.col("Value").cast(pl.Float64, strict=False))
        df = df.filter(pl.col("Value").is_not_null() & pl.col("Value").is_finite())
        return df if len(df) > 0 else None
    except pl.exceptions.ComputeError:
        return None


def _compute_basic_stats(df: pl.DataFrame) -> dict:
    """Compute basic statistics with proper null/invalid value handling."""
    default_stats = _get_default_stats()

    if df.is_empty():
        return default_stats

    preprocessed_df = _preprocess_dataframe(df)
    if preprocessed_df is None or preprocessed_df.is_empty():
        return default_stats

    return {
        "mean_value": preprocessed_df.select(pl.col("Value").mean())[0, 0] or 0,
        "median_value": preprocessed_df.select(pl.col("Value").median())[0, 0] or 0,
        "max_value": preprocessed_df.select(pl.col("Value").max())[0, 0] or 0,
        "min_value": preprocessed_df.select(pl.col("Value").min())[0, 0] or 0,
        "p90_value": preprocessed_df.select(pl.col("Value").quantile(0.9))[0, 0] or 0,
        "last_value": preprocessed_df.select(pl.col("Value").last())[0, 0] or 0,
    }


def _compute_pod_stats(df: pl.DataFrame) -> list[dict]:
    """Compute statistics for each pod type."""
    pod_stats = []
    for pod_type in ["small", "large"]:
        pod_df = df.filter(pl.col("PodType") == pod_type)
        if not pod_df.is_empty():
            pod_stats.append({"pod_type": pod_type, **_compute_basic_stats(pod_df)})
    return pod_stats


async def _process_pod_stats(metric: Metric, dfs: list[pl.DataFrame]) -> None:
    """Process pod stats for each DataFrame."""
    logger.info(f"Processing pod stats for metric: {metric.metric_name}")
    metric.pod_stats = []
    for df in dfs:
        if "PodType" in df.columns:
            pod_type = df.select(pl.col("PodType")).row(0)[0]
            metric.pod_stats.append(_create_pod_stats(pod_type, df))


def _create_pod_stats(pod_type: str, df: pl.DataFrame) -> PodStats:
    stats = _calculate_stats(df)
    logger.info(f"Added stats for pod type: {pod_type}")
    return PodStats(
        pod_type=pod_type,
        mean_value=stats["mean_value"],
        median_value=stats["median_value"],
        max_value=stats["max_value"],
        min_value=stats["min_value"],
        p90_value=stats["p90_value"],
    )


async def _process_worker_queue_stats(metric: Metric, dfs: list[pl.DataFrame]) -> None:
    logger.info(f"Processing worker queues for metric: {metric.metric_name}")
    metric.worker_queues = [_create_worker_queue_stats(queue, df) for queue, df in zip(metric.worker_queues, dfs) if not df.is_empty()]


def _create_worker_queue_stats(queue: WorkerQueueStats, df: pl.DataFrame) -> WorkerQueueStats:
    """Create a worker queue stats object preserving original metadata."""
    stats = _calculate_stats(df)
    logger.info(f"Added stats for queue: {queue.queue_name}")
    return WorkerQueueStats(
        queue_name=queue.queue_name,
        mean_value=stats["mean_value"],
        median_value=stats["median_value"],
        max_value=stats["max_value"],
        min_value=stats["min_value"],
        p90_value=stats["p90_value"],
        worker_type=queue.worker_type,
        worker_concurrency=queue.worker_concurrency,
        min_workers=queue.min_workers,
        max_workers=queue.max_workers,
    )


def _is_pod_based_metric(metric: Metric) -> bool:
    return len(metric.queries) > 1 and ("ke" in metric.metric_name.lower() or "kpo" in metric.metric_name.lower())


async def _process_single_metric(metric: Metric, data_obj: PrometheusData, namespace: str, release_name: str | None, visualizer: Visualizer) -> Figure | None:
    """Process a single metric and return its figure."""
    logger.info(f"Processing metric: {metric.metric_name} for namespace {namespace}")
    figure = visualizer.get_figure_if_resume(metric) if visualizer.resume else None
    if not figure:
        # Get data once
        metric_data = await get_metric_data(data_obj, metric, namespace, release_name)
        if metric_data:
            stats = None

            # Process stats
            if _is_pod_based_metric(metric):
                await _process_pod_stats(metric, metric_data)
                # Calculate combined stats for visualization
                combined_df = pl.concat(metric_data)
                agg_expr = pl.col("Value").sum() if "Pod Count" in metric.metric_name else pl.col("Value").mean()
                combined_stats = combined_df.group_by("Time Stamp").agg([agg_expr.alias("Value")])
                stats = _calculate_stats(combined_stats)

            if metric.worker_queues:
                await _process_worker_queue_stats(metric, metric_data)

            # Generate visualization
            figure = visualizer.generate_graph(dataframes=metric_data, metric=metric)
            if _is_pod_based_metric(metric) and stats:
                figure.statistics = stats
                figure.pod_stats = metric.pod_stats

    return figure


async def get_metrics_data_and_plot(
    metadata: ReportMetadata,
    executor_types: dict[str, DeploymentConfig],
    progress_callback=None,
    is_resume: bool = False,
    verify_ssl: bool = True,
) -> list[Figure]:
    """Fetch data from Prometheus and create visualizations."""
    figures = []
    queries_file_path = SOFTWARE_QUERIES_FILE_PATH

    for namespace in metadata.namespaces:
        logger.info(f"Processing namespace: {namespace}")
        parsed_yaml_queries = parse_yaml(file_name=queries_file_path)

        executor_type = executor_types[namespace]
        release_name = executor_type.release_name

        worker_queues = executor_type.queues if executor_type.queues else None

        # First get the type selector
        type_selector = get_type_selector(executor_type)
        if type_selector is None:
            continue

        # Then update queries based on the type
        update_queries_for_type(parsed_yaml_queries, type_selector, worker_queues)

        # Now collect metrics using the updated queries
        metrics = _collect_metrics(parsed_yaml_queries, namespace, worker_queues, executor_type.executor, type_selector)

        data_obj = await get_data_object(metadata.organization_name, namespace, metadata.start_date, metadata.end_date, verify_ssl=verify_ssl)

        visualizer = Visualizer(
            namespace=namespace,
            organization_name=metadata.organization_name,
            release_name=release_name,
            resume=is_resume,
            metadata=metadata,
        )

        for metric in metrics:
            figure = await _process_single_metric(metric, data_obj, namespace, release_name, visualizer)
            if figure:
                figures.append(figure)

            if progress_callback:
                progress_callback()

    return figures
