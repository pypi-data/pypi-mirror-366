"""Metric processing and updates for CSV generation."""

import logging
from typing import Any

from orbis.data.models import MetricCalculation

logger = logging.getLogger("root")


def update_metrics(row: dict[str, Any], metric: MetricCalculation | None) -> None:
    """Update metrics in the row based on metric type."""
    if not metric:
        logger.warning("Received empty metric, skipping update")
        return

    logger.info(f"Updating metrics for {metric.metric_name}")

    # Mapping of metric names to their CSV column names and corresponding attributes
    metric_mappings = {
        "Scheduler CPU": {
            "scheduler_metrics.avg_scheduler_cpu (vCPU)": "mean_value",
            "scheduler_metrics.max_scheduler_cpu (vCPU)": "max_value",
            "scheduler_metrics.p90_scheduler_cpu (vCPU)": "p90_value",
        },
        "Scheduler Memory": {
            "scheduler_metrics.avg_scheduler_mem (GB)": "mean_value",
            "scheduler_metrics.max_scheduler_mem (GB)": "max_value",
            "scheduler_metrics.p90_scheduler_mem (GB)": "p90_value",
        },
        "KE CPU": {
            "worker_metrics.avg_worker_cpu (vCPU)": "mean_value",
            "worker_metrics.max_worker_cpu (vCPU)": "max_value",
            "worker_metrics.p90_worker_cpu (vCPU)": "p90_value",
        },
        "KE Memory": {
            "worker_metrics.avg_worker_mem (GB)": "mean_value",
            "worker_metrics.max_worker_mem (GB)": "max_value",
            "worker_metrics.p90_worker_mem (GB)": "p90_value",
        },
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
        "Total Task Success": {
            "Total Task Success": "last_value",
        },
        "Total Task Failure": {
            "Total Task Failure": "last_value",
        },
        "Celery Pod Count": {
            "Worker Count": "mean_value",  # Map pod count to Worker Count column
        },
    }

    try:
        if metric.metric_name in metric_mappings:
            for csv_key, metric_attr in metric_mappings[metric.metric_name].items():
                value = getattr(metric, metric_attr, None)
                # Special handling for task metrics
                if metric.metric_name in ["Total Task Success", "Total Task Failure"]:
                    # Use last_value if available, otherwise fall back to mean
                    if value is None:
                        logger.warning(f"{metric.metric_name}: last_value is None, falling back to mean")
                        value = getattr(metric, "mean_value", 0)
                    value = round(float(value) if value is not None else 0)
                    logger.info(f"Setting {metric.metric_name} to {value}")
                row[csv_key] = value
    except Exception as e:
        logger.error(f"Error updating metric {metric.metric_name}: {e}")
        # Set default values for task metrics on error
        if metric.metric_name == "Total Task Success":
            row["Total Task Success"] = 0
        elif metric.metric_name == "Total Task Failure":
            row["Total Task Failure"] = 0


def update_base_row_metrics(base_row: dict[str, Any], metrics: list[MetricCalculation]) -> None:
    """Update base row with metrics that are not specific to workers or pods."""
    for metric in metrics:
        update_metrics(base_row, metric)


def update_kubernetes_metrics(base_row: dict[str, Any], metrics: list[MetricCalculation]) -> None:
    """Update Kubernetes-specific metrics in the base row."""
    ke_metrics = [m for m in metrics if m.metric_name.startswith("KE")]
    for metric in ke_metrics:
        update_metrics(base_row, metric)
