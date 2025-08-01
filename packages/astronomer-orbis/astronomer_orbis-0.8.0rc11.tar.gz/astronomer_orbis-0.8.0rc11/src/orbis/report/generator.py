import json
import logging
import os
from datetime import datetime

from orbis.config import DECIMAL_PRECISION
from orbis.data.models import DeploymentConfig, Figure, MetricCalculation, NamespaceReport, OverallReport, PodStats, ReportMetadata, WorkerQueueStats
from orbis.report.csv_generator import generate_csv_from_report
from orbis.report.document.docx import DocxReportGenerator
from orbis.report.metrics.collector import get_metrics_data_and_plot

logger = logging.getLogger("root")


def apply_precision(figures: list[Figure]) -> list[Figure]:
    if not figures:
        logger.warning("Empty figures list provided to apply_precision")
        return []

    for figure in figures:
        if not figure:
            logger.warning("Null figure encountered")
            continue

        try:
            _apply_precision_to_figure(figure)
        except Exception as e:
            logger.error(f"Error applying precision to figure {figure.metric.metric_name}: {str(e)}")

    return figures


def _apply_precision_to_figure(figure: Figure) -> None:
    if not figure.statistics:
        logger.warning(f"Missing statistics for figure {figure.metric.metric_name}")
        return

    figure.statistics = _round_statistics(figure.statistics, figure.metric.metric_name)

    if figure.worker_queue_stats:
        for stat in figure.worker_queue_stats:
            if stat:
                _round_worker_queue_stats(stat, figure.metric.metric_name)

    if figure.pod_stats:
        for stat in figure.pod_stats:
            if stat:
                _round_pod_stats(stat, figure.metric.metric_name)


def _round_statistics(statistics: dict, metric_name: str) -> dict:
    new_stats = {}
    for key, value in statistics.items():
        if value is not None:
            try:
                new_stats[key] = round(float(value), DECIMAL_PRECISION)
            except (TypeError, ValueError) as e:
                logger.error(f"Error applying precision to {key} in figure {metric_name}: {str(e)}")
                return {}
    return new_stats


def _round_worker_queue_stats(stat: WorkerQueueStats, metric_name: str) -> None:
    try:
        for attr in ["mean_value", "median_value", "max_value", "min_value", "p90_value"]:
            setattr(stat, attr, round(float(getattr(stat, attr)), DECIMAL_PRECISION))
    except (TypeError, ValueError) as e:
        logger.error(f"Error applying precision to worker queue stats in figure {metric_name}: {str(e)}")


def _round_pod_stats(stat: PodStats, metric_name: str) -> None:
    try:
        for attr in ["mean_value", "median_value", "max_value", "min_value", "p90_value"]:
            setattr(stat, attr, round(float(getattr(stat, attr)), DECIMAL_PRECISION))
    except (TypeError, ValueError) as e:
        logger.error(f"Error applying precision to pod stats in figure {metric_name}: {str(e)}")


async def generate_report(metadata: ReportMetadata, executor_types: dict[str, DeploymentConfig], progress_callback=None, is_resume=False, verify_ssl: bool = True) -> list[Figure]:
    figures = []
    try:
        figures = await get_metrics_data_and_plot(
            metadata=metadata,
            executor_types=executor_types,
            progress_callback=progress_callback,
            is_resume=is_resume,
            verify_ssl=verify_ssl,
        )
        apply_precision(figures)

        docx_generator = DocxReportGenerator(metadata, progress_callback)
        docx_generator.setup_document()
        included_figures = [f for f in figures if f.metric.include_in and f.metric.include_in.get("docx", True)]
        for i, figure in enumerate(included_figures):
            docx_generator.add_figure(figure)
            docx_generator.add_visualization_url(figure)
            docx_generator.add_statistics_table(figure)
            if i < len(included_figures) - 1:  # Don't add page break after last figure
                docx_generator.doc.add_page_break()
        docx_generator.save_document()

        if progress_callback:
            progress_callback()

        overall_report = OverallReport(
            organization_name=metadata.organization_name,
            start_date=datetime.fromisoformat(metadata.start_date),
            end_date=datetime.fromisoformat(metadata.end_date),
            generated_at=datetime.now(),
            namespace_reports=[],
        )

        for namespace in metadata.namespaces:
            namespace_report = NamespaceReport(
                namespace=namespace,
                name=executor_types[namespace].name,
                executor_type=executor_types[namespace].executor,
                metrics=[],
                scheduler_replicas=executor_types[namespace].scheduler_replicas,
                scheduler_au=executor_types[namespace].scheduler_au,
            )

            for figure in figures:
                if figure.namespace == namespace:
                    worker_queue_stats = []
                    pod_stats = []
                    if figure.worker_queue_stats and figure.metric.metric_name in ["Celery CPU", "Celery Memory", "Celery Pod Count"]:
                        worker_queue_stats = figure.worker_queue_stats
                    if figure.metric.pod_stats and ("ke" in figure.metric.metric_name.lower() or "kpo" in figure.metric.metric_name.lower()):
                        pod_stats = figure.metric.pod_stats
                    metric_calc = MetricCalculation(
                        metric_name=figure.metric.metric_name,
                        mean_value=figure.statistics["mean_value"],
                        median_value=figure.statistics["median_value"],
                        max_value=figure.statistics["max_value"],
                        min_value=figure.statistics["min_value"],
                        p90_value=figure.statistics["p90_value"],
                        last_value=figure.statistics["last_value"],
                        worker_queue_stats=worker_queue_stats if worker_queue_stats else None,
                        pod_stats=pod_stats if pod_stats else None,
                    )
                    namespace_report.metrics.append(metric_calc)

            overall_report.namespace_reports.append(namespace_report)

        output_folder = f"output/{metadata.organization_name}"
        json_output_path = os.path.join(output_folder, f"{metadata.organization_name}_report.json")
        logger.info(f"Exporting JSON report: {json_output_path}")
        with open(json_output_path, "w") as json_file:
            json.dump(overall_report.to_dict(), json_file, default=str, indent=2)

        csv_output_path = os.path.join(output_folder, f"{metadata.organization_name}_report.csv")
        logger.info(f"Generating CSV report: {csv_output_path}")
        generate_csv_from_report(overall_report, csv_output_path)

        if progress_callback:
            progress_callback()
        return figures
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise e
