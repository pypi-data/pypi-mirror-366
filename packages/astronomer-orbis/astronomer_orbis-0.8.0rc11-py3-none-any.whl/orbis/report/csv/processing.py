"""Core CSV processing logic."""

import csv
import logging
from typing import Any

from orbis.data.models import NamespaceReport, OverallReport
from orbis.report.csv.metrics import update_base_row_metrics, update_kubernetes_metrics
from orbis.report.csv.pods import post_process_ke_pod_stats, post_process_kpo_pod_stats
from orbis.report.csv.queues import process_worker_queues_stats
from orbis.report.csv.templates import get_csv_template_headers, get_empty_row

logger = logging.getLogger("root")


def create_row(namespace_report: NamespaceReport) -> dict[str, Any]:
    """Create a base row with deployment information."""
    logger.info(f"Creating base row for deployment {namespace_report.name} in namespace {namespace_report.namespace}")
    try:
        row = get_empty_row()
        row.update({
            "Deployment Name": namespace_report.name,
            "Deployment Name Space": namespace_report.namespace,
            "executor": namespace_report.executor_type,
            "scheduler_replicas": namespace_report.scheduler_replicas,
            "Scheduler AU": namespace_report.scheduler_au,
            "Scheduler HA/Non HA Hosted": "",
            "Scheduler Size Hosted": "",
        })
        return row
    except Exception as e:
        logger.error(f"Error creating base row: {e}")
        raise


def process_namespace_report(namespace_report: NamespaceReport) -> list[dict[str, Any]]:
    """Process a single namespace report and return list of rows for CSV."""
    try:
        base_row = create_row(namespace_report)
        update_base_row_metrics(base_row, namespace_report.metrics)

        if namespace_report.executor_type == "CELERY":
            return process_celery_report(namespace_report, base_row)
        else:
            base_row.update({"Worker Count": "", "Worker Size Hosted": "A5"})
            return [process_kubernetes_report(namespace_report, base_row)]
    except Exception as e:
        logger.error(f"Error processing namespace report: {e}")
        return create_fallback_row(namespace_report)


def process_celery_report(namespace_report: NamespaceReport, base_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Process Celery executor report."""
    rows = []

    # Get regular worker queue rows first
    worker_rows = get_worker_rows(namespace_report, base_row)
    if worker_rows:
        rows.extend(worker_rows)
    else:
        # Only add fallback row if no worker rows
        rows.append(create_fallback_worker_row(base_row))

    # Add KPO row if exists
    kpo_rows = post_process_kpo_pod_stats(namespace_report)
    if kpo_rows:
        rows.extend(kpo_rows)

    return rows


def process_kubernetes_report(namespace_report: NamespaceReport, base_row: dict[str, Any]) -> dict[str, Any]:
    """Process Kubernetes executor report."""
    update_kubernetes_metrics(base_row, namespace_report.metrics)

    return post_process_ke_pod_stats(namespace_report, base_row)


def get_worker_rows(namespace_report: NamespaceReport, base_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Get worker rows for Celery executor."""
    try:
        return process_worker_queues_stats(namespace_report, base_row)
    except Exception as e:
        logger.error(f"Error processing worker queues: {e}")
        return []


def get_pod_rows(namespace_report: NamespaceReport) -> list[dict[str, Any]]:
    """Get pod rows for Kubernetes executor."""
    try:
        return post_process_kpo_pod_stats(namespace_report)
    except Exception as e:
        logger.error(f"Error processing pod stats: {e}")
        return []


def create_fallback_worker_row(base_row: dict[str, Any]) -> dict[str, Any]:
    """Create a fallback worker row when processing fails."""
    worker_row = base_row.copy()
    worker_row.update({"Worker Type": "default"})
    return worker_row


def create_fallback_row(namespace_report: NamespaceReport) -> list[dict[str, Any]]:
    """Create a fallback row when processing fails."""
    try:
        return [create_row(namespace_report)]
    except Exception:
        row = get_empty_row()
        row["Deployment Name"] = namespace_report.name
        return [row]


def generate_csv_from_report(overall_report: OverallReport, csv_file_path: str) -> None:
    """Generate CSV file from the overall report."""
    try:
        headers = get_csv_template_headers()
        rows = []

        for namespace_report in overall_report.namespace_reports:
            try:
                namespace_rows = process_namespace_report(namespace_report)
                rows.extend(namespace_rows)
            except Exception as e:
                logger.error(f"Error processing namespace {namespace_report.namespace}: {e}")
                rows.extend(create_fallback_row(namespace_report))

        with open(csv_file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            logger.info(rows)
            writer.writerows(rows)

        logger.info(f"Successfully wrote CSV to {csv_file_path}")
    except Exception as e:
        logger.error(f"Failed to generate CSV: {e}")
        raise
