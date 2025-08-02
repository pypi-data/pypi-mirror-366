"""Kubernetes query handling utilities for Orbis.

This module handles pod-type metrics for Kubernetes resources. Pod types have fixed
conditions (small/large) based on resource usage:
- Small pods: <=0.25 vCPU or <=500MiB memory
- Large pods: >0.25 vCPU or >500MiB memory
"""

import logging

logger = logging.getLogger(__name__)


def process_pod_type_query(base_query: str, pod_type_config: dict) -> str:
    """Process a query for a specific pod type.

    Args:
        base_query: Base query with condition placeholder
        pod_type_config: Configuration for the pod type (small/large) containing the conditions

    Returns:
        str: Processed query with all conditions replaced
    """
    processed_query = base_query

    # Process each condition in the config
    for condition_key, condition_value in pod_type_config.items():
        logger.info(f"Processing query with {condition_key}: {condition_value}")
        processed_query = processed_query.replace(f"{{{condition_key}}}", condition_value)

    logger.info("Query processed successfully")
    return processed_query


def create_pod_type_metric(metric_data: dict) -> dict:
    """Create a new metric that handles multiple pod types.

    Creates a single metric with multiple queries, one for each pod type.
    The query_types list maintains the order: [small, large]

    Args:
        metric_data: Original metric data containing base query

    Returns:
        dict: New metric data with queries for all pod types
    """
    logger.info(f"Creating pod type metric: {metric_data['metric']}")

    queries = []
    query_types = []  # Maintains order of pod types [small, large]

    pod_types = metric_data["pod_types"]
    for pod_type, config in pod_types.items():
        logger.info(f"Processing query for pod type: {pod_type}")
        query = process_pod_type_query(metric_data["queries"][0], config)
        logger.info(f"Processed query: {query}")
        queries.append(query)
        query_types.append(pod_type)

    return {
        "file_name": metric_data["file_name"],
        "metric": metric_data["metric"],
        "queries": queries,
        "aggregators": metric_data["aggregators"].copy(),
        "table_headers": metric_data["table_headers"].copy(),
        "pod_small_large": pod_types,
        "query_types": query_types,
    }


def update_k8s_metrics(parsed_yaml_queries: dict, type_selector: str) -> tuple[list[str], dict[str, dict]]:
    """Update Kubernetes metrics with pod type information.

    For metrics that need pod type handling, creates a single metric with
    multiple queries (one per pod type).

    Args:
        parsed_yaml_queries: Parsed YAML queries dictionary
        type_selector: Type selector (e.g. 'ke', 'kpo')

    Returns:
        tuple[list[str], dict[str, dict]]: List of metrics to remove and dictionary of metrics to add
    """
    logger.info(f"Updating K8s metrics for {type_selector}")
    metrics_to_remove = []
    metrics_to_add = {}

    # Get all metrics for this type
    type_metrics = parsed_yaml_queries.get(type_selector, {})
    logger.info(f"Found metrics: {list(type_metrics.keys())}")

    # Process each metric
    for metric_name, metric_data in type_metrics.items():
        # Skip metrics that don't need pod type handling
        should_handle = _should_handle_pod_types(metric_data)
        if not should_handle:
            logger.info(f"Skipping {metric_name} - not a pod type metric")
            continue

        logger.info(f"Processing metric: {metric_name}")
        metrics_to_remove.append(metric_name)

        # Create a single metric with queries for all pod types
        metrics_to_add[metric_name] = create_pod_type_metric(metric_data)
        logger.info(f"Created pod type metric: {metric_name}")

    return metrics_to_remove, metrics_to_add


def _should_handle_pod_types(metric_data: dict) -> bool:
    """Check if a metric should be handled as a pod type metric.

    Args:
        metric_data: Metric data from YAML

    Returns:
        bool: True if metric should be handled as pod type metric
    """
    # Only handle metrics that explicitly have pod_types configuration
    if "pod_types" not in metric_data:
        return False

    # Verify pod_types has valid configuration
    pod_types = metric_data["pod_types"]
    return any("cpu_condition" in config or "memory_condition" in config for config in pod_types.values())
