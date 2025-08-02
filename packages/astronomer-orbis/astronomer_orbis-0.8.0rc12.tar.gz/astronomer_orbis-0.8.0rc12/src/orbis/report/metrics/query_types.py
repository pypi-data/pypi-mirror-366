"""Query type definitions for Orbis."""

from enum import Enum


class QueryType(Enum):
    """Types of queries supported in prometheus_queries.yaml"""

    SIMPLE = "simple"  # Only needs {namespace} formatting
    WORKER_QUEUE = "worker_queue"  # Needs {namespace} and worker queue pattern
    CONDITIONAL = "conditional"  # Needs {namespace}, {condition}
    OR_CONDITIONAL = "or_conditional"  # Needs {namespace}, {condition} with OR


def identify_query_type(metric_name: str) -> QueryType:
    """Identify the type of query based on metric name and data.

    Args:
        metric_name: Name of the metric (e.g. 'scheduler.cpu', 'ke.memory')

    Returns:
        QueryType: The type of query identified

    Examples:
        >>> identify_query_type('scheduler.cpu')
        QueryType.SIMPLE
        >>> identify_query_type('ke.cpu')
        QueryType.OR_CONDITIONAL
    """
    # KE queries are always OR_CONDITIONAL
    if metric_name.startswith("ke."):
        return QueryType.OR_CONDITIONAL

    # Celery worker queries
    if metric_name in ["celery.cpu", "celery.memory"]:
        return QueryType.WORKER_QUEUE

    # KPO queries are CONDITIONAL
    if metric_name.startswith("celery.kpo_"):
        return QueryType.CONDITIONAL

    # All other queries are SIMPLE
    return QueryType.SIMPLE
