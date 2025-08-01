"""CSV generation for Orbis reports.

This module serves as the main entry point for CSV generation functionality.
It delegates the actual processing to specialized modules in the csv package.
"""

import logging

from orbis.data.models import OverallReport
from orbis.report.csv.processing import generate_csv_from_report

logger = logging.getLogger("root")


def generate_csv(overall_report: OverallReport, csv_file_path: str) -> None:
    """Generate a CSV file from the overall report.

    Args:
        overall_report: The OverallReport containing all namespace reports
        csv_file_path: Path where the CSV file should be written

    Raises:
        Exception: If CSV generation fails
    """
    try:
        generate_csv_from_report(overall_report, csv_file_path)
    except Exception as e:
        logger.error(f"Failed to generate CSV at {csv_file_path}: {e}")
        raise
