"""Worker queue processing for CSV generation."""

import logging
from typing import Any

from orbis.data.models import MetricCalculation, NamespaceReport, WorkerQueueStats
from orbis.report.csv.metrics import update_metrics
from orbis.report.csv.templates import get_empty_row

logger = logging.getLogger("root")


def process_worker_queues_stats(namespace_report: NamespaceReport, base_row: dict[str, Any]) -> list[dict[str, Any]]:
    celery_metrics = [m for m in namespace_report.metrics if m.worker_queue_stats]
    logger.info(f"Found {len(celery_metrics)} celery metrics with worker queue stats")

    pod_count_metric = next((m for m in namespace_report.metrics if m.metric_name == "Celery Pod Count"), None)
    logger.info(f"Pod count metric found: {pod_count_metric is not None}")

    if not celery_metrics or not celery_metrics[0].worker_queue_stats:
        return []

    logger.info(f"Number of worker queue stats: {len(celery_metrics[0].worker_queue_stats)}")

    rows = []
    for queue_stat in sorted(celery_metrics[0].worker_queue_stats, key=lambda x: x.queue_name != "default"):
        if queue_stat:  # Remove worker_type check since it's now properly populated
            logger.info(f"Processing queue: {queue_stat.queue_name}")
            rows.append(create_worker_row(namespace_report, base_row, queue_stat, pod_count_metric, queue_stat.queue_name == "default"))
        else:
            logger.warning(f"Skipping queue stat: {queue_stat}")

    return rows


def create_worker_row(namespace_report: NamespaceReport, base_row: dict[str, Any], queue_stat: Any, pod_count_metric: Any, is_default: bool) -> dict[str, Any]:
    """Create a row for a worker queue."""
    worker_row = base_row.copy() if is_default else get_empty_row()
    worker_type = get_worker_type(queue_stat)

    worker_row.update({
        "Worker Type": worker_type,
        "Worker Queue Name": queue_stat.queue_name,
        "Worker Concurrency": getattr(queue_stat, "worker_concurrency", ""),
        "Min Worker": getattr(queue_stat, "min_workers", ""),
        "Max Workers": getattr(queue_stat, "max_workers", ""),
        "Worker Size Hosted": "",
        "Worker Count": get_worker_count(pod_count_metric, queue_stat.queue_name),
    })

    update_worker_metrics(worker_row, queue_stat, namespace_report.metrics)

    if is_default:
        for metric in namespace_report.metrics:
            if metric.metric_name.startswith("Scheduler") or metric.metric_name.startswith("Total"):
                update_metrics(worker_row, metric)

    return worker_row


def update_worker_metrics(worker_row: dict[str, Any], queue_stat: Any, metrics: list[MetricCalculation]) -> None:
    """Update worker CPU and Memory metrics for a queue."""
    metric_mappings = {
        "Celery CPU": {
            "worker_metrics.avg_worker_cpu (vCPU)": "mean_value",
            "worker_metrics.max_worker_cpu (vCPU)": "max_value",
            "worker_metrics.p90_worker_cpu (vCPU)": "p90_value",
        },
        "Celery Memory": {
            "worker_metrics.avg_worker_mem (GB)": "mean_value",
            "worker_metrics.max_worker_mem (GB)": "max_value",
            "worker_metrics.p90_worker_mem (GB)": "p90_value",
        },
    }

    try:
        for metric_name in metric_mappings:
            metric = next((m for m in metrics if m.metric_name == metric_name), None)
            if metric and metric.worker_queue_stats:
                queue_stat_metric = next((qs for qs in metric.worker_queue_stats if qs.queue_name == queue_stat.queue_name), None)
                if queue_stat_metric:
                    for csv_key, metric_attr in metric_mappings[metric_name].items():
                        worker_row[csv_key] = getattr(queue_stat_metric, metric_attr)

        if queue_stat.queue_name == "default":
            for metric in metrics:
                if metric.metric_name.startswith("Total"):
                    value = next((v for v in [metric.last_value, metric.mean_value] if v is not None), 0)
                    worker_row[metric.metric_name] = round(float(value))
    except Exception as e:
        logger.error(f"Error updating worker metrics for queue {queue_stat.queue_name}: {e}")


def get_worker_type(queue_stat: WorkerQueueStats) -> str:
    """Format worker type string based on machine type or memory/CPU specs."""
    logger.debug("=== Worker Type Debug Info ===")
    logger.debug(f"Queue name: {queue_stat.queue_name}")
    logger.debug(f"Queue stat full object: {queue_stat}")
    logger.debug(f"Worker type attribute: {getattr(queue_stat, 'worker_type', None)}")
    logger.debug(f"Worker type type: {type(getattr(queue_stat, 'worker_type', None))}")
    logger.debug("===========================")

    if not queue_stat.worker_type:
        logger.warning(f"Could not determine worker type for queue {queue_stat.queue_name}")
        return "N/A"

    try:
        if isinstance(queue_stat.worker_type, dict):
            logger.debug(f"Worker type dict keys: {queue_stat.worker_type.keys()}")
            if "astroMachine" in queue_stat.worker_type:
                return queue_stat.worker_type["astroMachine"]
            elif "machinetype" in queue_stat.worker_type:
                return queue_stat.worker_type["machinetype"]
            elif "Memory" in queue_stat.worker_type and "CPU" in queue_stat.worker_type:
                return f"Memory {queue_stat.worker_type['Memory']}, CPU {queue_stat.worker_type['CPU']}"
        return str(queue_stat.worker_type)  # If it's a direct value
    except (AttributeError, KeyError) as e:
        logger.warning(f"Could not determine worker type for queue {queue_stat.queue_name}: {e}")
        return "N/A"


def get_worker_count(pod_count_metric: MetricCalculation, queue_name: str) -> str | float:
    """Get the worker count for a specific queue."""
    try:
        if pod_count_metric and pod_count_metric.worker_queue_stats:
            queue_stat = next((qs for qs in pod_count_metric.worker_queue_stats if qs.queue_name == queue_name), None)
            return queue_stat.mean_value if queue_stat else ""
    except Exception as e:
        logger.error(f"Error getting worker count for queue {queue_name}: {e}")
    return ""
