"""Pod statistics processing for CSV generation."""

import logging
from math import ceil
from typing import Any

from orbis.data.models import MetricCalculation, NamespaceReport
from orbis.report.csv.templates import get_empty_row

logger = logging.getLogger("root")


def has_kpo_data(metrics: list[MetricCalculation]) -> bool:
    """Check if there is actual KPO data in the metrics."""
    try:
        kpo_metrics = [m for m in metrics if m.metric_name.startswith("KPO")]
        for metric in kpo_metrics:
            if metric.metric_name == "KPO Pod Count":
                if metric.mean_value > 0 or metric.max_value > 0 or metric.min_value > 0:
                    logger.info(f"Found non-zero KPO data in metric {metric.metric_name}")
                    return True
        logger.info("No non-zero KPO data found")
        return False
    except Exception as e:
        logger.error(f"Error checking KPO data: {e}")
        return False


def post_process_kpo_pod_stats(namespace_report: NamespaceReport) -> list[dict[str, Any]]:
    """Process KPO data and calculate A5 requirements.

    This function calculates A5 (1 vCPU, 2 GiB Mem) requirements for both small and large pods based on:
    - Small pods: Simple count-based calculation (count/4 rounded up)
    - Large pods: Maximum of count-based, CPU-based, and memory-based calculations

    Args:
        namespace_report: Report containing pod metrics

    Returns:
        List containing a single row with calculated worker count if KPO data exists,
        empty list otherwise
    """
    if not has_kpo_data(namespace_report.metrics):
        return []

    metrics_data = {
        "KPO CPU": None,
        "KPO Memory": None,
        "KPO Pod Count": (None, None),  # (small, large)
    }

    # Extract metrics in a structured way
    for metric in namespace_report.metrics:
        if not metric.metric_name.startswith("KPO") or not metric.pod_stats:
            continue

        if metric.metric_name == "KPO CPU":
            metrics_data["KPO CPU"] = metric.pod_stats[1] if len(metric.pod_stats) > 1 else None
        elif metric.metric_name == "KPO Memory":
            metrics_data["KPO Memory"] = metric.pod_stats[1] if len(metric.pod_stats) > 1 else None
        elif metric.metric_name == "KPO Pod Count":
            metrics_data["KPO Pod Count"] = metric.pod_stats[:2] if len(metric.pod_stats) >= 2 else (None, None)

    # Unpack count metrics
    kpo_count_small, _ = metrics_data["KPO Pod Count"]  # Large pod count is not used for Sizing Calculations

    # Calculate A5s for small pods
    small_a5s = ceil(kpo_count_small.mean_value / 4) if kpo_count_small else 0

    # Calculate A5s for large pods using different metrics
    large_pod_a5s = {
        "cpu": ceil(metrics_data["KPO CPU"].mean_value) if metrics_data["KPO CPU"] else 0,
        "memory": ceil(metrics_data["KPO Memory"].mean_value / 2) if metrics_data["KPO Memory"] else 0,
    }

    # Get maximum A5s from large pod calculations
    large_a5s = max(large_pod_a5s.values())

    # Calculate total A5s
    total_a5s = small_a5s + large_a5s

    if total_a5s == 0:
        return []

    # Create and populate KPO row
    kpo_row = get_empty_row()
    kpo_row.update({"Worker Type": "KPO", "Worker Queue Name": "^kpo", "Worker Size Hosted": "A5", "Worker Count": total_a5s})

    # Update other metrics
    for metric in namespace_report.metrics:
        if metric.metric_name.startswith("KPO"):
            update_kpo_metrics(kpo_row, metric)

    return [kpo_row]


def update_kpo_metrics(kpo_row: dict[str, Any], metric: MetricCalculation) -> None:
    """Update KPO CPU and Memory metrics."""
    if metric.metric_name == "KPO CPU":
        kpo_row.update({
            "worker_metrics.avg_worker_cpu (vCPU)": metric.mean_value,
            "worker_metrics.max_worker_cpu (vCPU)": metric.max_value,
            "worker_metrics.p90_worker_cpu (vCPU)": metric.p90_value,
        })
    elif metric.metric_name == "KPO Memory":
        kpo_row.update({
            "worker_metrics.avg_worker_mem (GB)": metric.mean_value,
            "worker_metrics.max_worker_mem (GB)": metric.max_value,
            "worker_metrics.p90_worker_mem (GB)": metric.p90_value,
        })


def post_process_ke_pod_stats(namespace_report: NamespaceReport, base_row: dict[str, Any]) -> dict[str, Any]:
    """Process Kubernetes Executor (KE) data and calculate A5 requirements.

    This function calculates A5 (1 vCPU, 2 GiB Mem) requirements for both small and large pods based on:
    - Small pods: Simple count-based calculation (count/4 rounded up)
    - Large pods: Maximum of count-based, CPU-based, and memory-based calculations

    Args:
        namespace_report: Report containing pod metrics and executor type
        base_row: Base dictionary to update with worker count

    Returns:
        Updated base_row with calculated worker count
    """
    if namespace_report.executor_type != "KUBERNETES":
        return base_row

    metrics_data = {
        "KE CPU": None,
        "KE Memory": None,
        "KE Pod Count": (None, None),  # (small, large)
    }

    # Extract metrics in a more structured way
    for metric in namespace_report.metrics:
        if metric.metric_name == "KE CPU":
            metrics_data["KE CPU"] = metric.pod_stats[1] if metric.pod_stats and len(metric.pod_stats) > 1 else None
        elif metric.metric_name == "KE Memory":
            metrics_data["KE Memory"] = metric.pod_stats[1] if metric.pod_stats and len(metric.pod_stats) > 1 else None
        elif metric.metric_name == "KE Pod Count":
            metrics_data["KE Pod Count"] = metric.pod_stats[:2] if metric.pod_stats and len(metric.pod_stats) >= 2 else (None, None)

    # Unpack count metrics
    ke_count_small, _ = metrics_data["KE Pod Count"]  # Large pod count is not used for Sizing Calculations

    logger.debug("Metrics Data: %s", metrics_data)

    # Calculate A5s for small pods
    small_a5s = ceil(ke_count_small.mean_value / 4) if ke_count_small else 0
    logger.debug("Small A5s: %s", small_a5s)

    # Calculate A5s for large pods using different metrics
    large_pod_a5s = {"cpu": ceil(metrics_data["KE CPU"].mean_value) if metrics_data["KE CPU"] else 0, "memory": ceil(metrics_data["KE Memory"].mean_value / 2) if metrics_data["KE Memory"] else 0}
    logger.debug("Large A5s Dict: %s", large_pod_a5s)

    # Get maximum A5s from large pod calculations
    large_a5s = max(large_pod_a5s.values()) if any(large_pod_a5s.values()) else 0

    # Calculate and set total A5s
    base_row["Worker Count"] = small_a5s + large_a5s
    return base_row
