from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkerQueueStats:
    queue_name: str
    mean_value: float
    median_value: float
    max_value: float
    min_value: float
    p90_value: float
    worker_type: dict[str, str] | None = None  # Format: {"machinetype": str, "Memory": str, "CPU": str}
    worker_concurrency: int | None = None
    min_workers: int | None = None
    max_workers: int | None = None

    def to_dict(self):
        return {
            "queue_name": self.queue_name,
            "mean_value": self.mean_value,
            "median_value": self.median_value,
            "max_value": self.max_value,
            "min_value": self.min_value,
            "p90_value": self.p90_value,
            "worker_type": self.worker_type,
            "worker_concurrency": self.worker_concurrency,
            "min_workers": self.min_workers,
            "max_workers": self.max_workers,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            queue_name=data["queue_name"],
            mean_value=data["mean_value"],
            median_value=data["median_value"],
            max_value=data["max_value"],
            min_value=data["min_value"],
            p90_value=data["p90_value"],
            worker_type=data.get("worker_type"),
            worker_concurrency=data.get("worker_concurrency"),
            min_workers=data.get("min_workers"),
            max_workers=data.get("max_workers"),
        )


@dataclass
class PodStats:
    """Represents statistics for a pod type (small or large)."""

    pod_type: str  # "small" or "large"
    mean_value: float
    median_value: float
    max_value: float
    min_value: float
    p90_value: float

    def __repr__(self):
        return (
            f"PodStats("
            f"type={self.pod_type}, "
            f"mean_value={self.mean_value:.2f}, "
            f"median_value={self.median_value:.2f}, "
            f"max_value={self.max_value:.2f}, "
            f"min_value={self.min_value:.2f}, "
            f"p90_value={self.p90_value:.2f}"
            f")"
        )

    def to_dict(self):
        return {
            "pod_type": self.pod_type,
            "mean_value": self.mean_value,
            "median_value": self.median_value,
            "max_value": self.max_value,
            "min_value": self.min_value,
            "p90_value": self.p90_value,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            pod_type=data["pod_type"],
            mean_value=data["mean_value"],
            median_value=data["median_value"],
            max_value=data["max_value"],
            min_value=data["min_value"],
            p90_value=data["p90_value"],
        )


@dataclass
class Metric:
    """
    Represents a specific metric.
    Any recommendations/suggestions/features needs to be added in this class.
    """

    metric_identifier: str
    metric_name: str
    file_name: str
    queries: list[str]
    aggregators: dict[str, bool]
    table_headers: dict[str, bool]
    worker_queues: list[WorkerQueueStats]
    executor_type: str
    include_in: dict[str, bool] | None = None
    pod_stats: list[PodStats] | None = None
    query_types: list[str] | None = None

    def __repr__(self):
        return f"Metric(identifier={self.metric_identifier}, name={self.metric_name})"

    def to_dict(self):
        return {
            "metric_identifier": self.metric_identifier,
            "metric_name": self.metric_name,
            "file_name": self.file_name,
            "queries": self.queries,
            "aggregators": self.aggregators,
            "table_headers": self.table_headers,
            "worker_queues": [queue.to_dict() for queue in self.worker_queues],
            "executor_type": self.executor_type,
            "include_in": self.include_in,
            "pod_stats": [stat.to_dict() for stat in self.pod_stats] if self.pod_stats else None,
            "query_types": self.query_types,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            metric_identifier=data["metric_identifier"],
            metric_name=data["metric_name"],
            file_name=data["file_name"],
            queries=data["queries"],
            aggregators=data["aggregators"],
            table_headers=data["table_headers"],
            worker_queues=[WorkerQueueStats.from_dict(queue) for queue in data["worker_queues"]],
            executor_type=data["executor_type"],
            include_in=data.get("include_in"),
            pod_stats=[PodStats.from_dict(stat) for stat in data.get("pod_stats")] if data.get("pod_stats") else None,
            query_types=data.get("query_types"),
        )


@dataclass
class MetricCalculation:
    """Represents calculations for a single metric."""

    metric_name: str
    mean_value: float
    median_value: float
    max_value: float
    min_value: float
    p90_value: float
    last_value: float
    worker_queue_stats: list[WorkerQueueStats] | None = None
    pod_stats: list[PodStats] | None = None

    def __repr__(self):
        return (
            f"MetricCalculation("
            f"name={self.metric_name}, "
            f"mean_value={self.mean_value}, "
            f"median_value={self.median_value}, "
            f"max_value={self.max_value}, "
            f"min_value={self.min_value}, "
            f"p90_value={self.p90_value}, "
            f"last_value={self.last_value}"
            f")"
        )

    def to_dict(self):
        result = {
            "metric_name": self.metric_name,
            "mean_value": self.mean_value,
            "median_value": self.median_value,
            "max_value": self.max_value,
            "min_value": self.min_value,
            "p90_value": self.p90_value,
            "last_value": self.last_value,
        }
        if self.worker_queue_stats:
            result["worker_queue_stats"] = [stat.to_dict() for stat in self.worker_queue_stats]
        if self.pod_stats:
            result["pod_stats"] = [stat.to_dict() for stat in self.pod_stats]
        return result


@dataclass
class ReportMetadata:
    """
    Represents metadata for a generated report.
    """

    organization_name: str
    start_date: str
    end_date: str
    namespaces: list[str]

    def __repr__(self):
        return f"ReportMetadata(org={self.organization_name}, start={self.start_date}, end={self.end_date})"


@dataclass
class DeploymentConfig:
    namespace: str
    name: str
    executor: str
    queues: list[WorkerQueueStats] = field(default_factory=list)
    release_name: str | None = None
    scheduler_replicas: int | None = None
    scheduler_au: str | None = None

    def __repr__(self):
        return f"DeploymentConfig(namespace={self.namespace}, executor={self.executor})"

    def to_dict(self):
        return {
            "namespace": self.namespace,
            "name": self.name,
            "executor": self.executor,
            "queues": [queue for queue in self.queues],
            "release_name": self.release_name,
            "scheduler_replicas": self.scheduler_replicas,
            "scheduler_au": self.scheduler_au,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            namespace=data["namespace"],
            name=data["name"],
            executor=data["executor"],
            queues=[queue for queue in data["queues"]],
            release_name=data.get("release_name"),
            scheduler_replicas=data.get("scheduler_replicas"),
            scheduler_au=data.get("scheduler_au"),
        )


@dataclass
class Figure:
    """
    Represents a generated figure with its metadata.

    This model can help customize the figure for different executors or scenarios.
    """

    image_path: str
    metric: Metric
    statistics: dict[str, float]
    namespace: str
    release_name: str | None = None
    worker_queue_stats: list[WorkerQueueStats] | None = None
    pod_stats: list[PodStats] | None = None
    url: str | None = None

    def __repr__(self):
        return f"Figure(metric={self.metric.metric_name}, namespace={self.namespace})"

    def to_dict(self):
        result = {
            "image_path": self.image_path,
            "metric": self.metric.to_dict(),
            "statistics": self.statistics,
            "namespace": self.namespace,
            "release_name": self.release_name,
            "worker_queue_stats": [stat.to_dict() for stat in self.worker_queue_stats] if self.worker_queue_stats else None,
            "pod_stats": [stat.to_dict() for stat in self.pod_stats] if self.pod_stats else None,
            "url": self.url,
        }
        return result

    @classmethod
    def from_dict(cls, data):
        return cls(
            image_path=data["image_path"],
            metric=Metric.from_dict(data["metric"]),
            statistics=data["statistics"],
            namespace=data["namespace"],
            release_name=data.get("release_name"),
            worker_queue_stats=[WorkerQueueStats.from_dict(stat) for stat in data.get("worker_queue_stats", [])] if data.get("worker_queue_stats") else None,
            pod_stats=[PodStats.from_dict(stat) for stat in data.get("pod_stats", [])] if data.get("pod_stats") else None,
            url=data.get("url"),
        )


@dataclass
class NamespaceReport:
    """Represents the report for a single namespace."""

    namespace: str
    name: str
    executor_type: str
    metrics: list[MetricCalculation]
    scheduler_replicas: int | None = None
    scheduler_au: str | None = None
    worker_au: float | None = None
    worker_resources: dict[str, float] | None = None

    def __repr__(self):
        return f"NamespaceReport(namespace={self.namespace}, executor={self.executor_type})"

    def to_dict(self):
        return {
            "namespace": self.namespace,
            "name": self.name,
            "executor_type": self.executor_type,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "scheduler_replicas": self.scheduler_replicas,
            "scheduler_au": self.scheduler_au,
            "worker_au": self.worker_au,
            "worker_resources": self.worker_resources,
        }


@dataclass
class OverallReport:
    """Represents the overall report with all calculations."""

    organization_name: str
    start_date: datetime
    end_date: datetime
    generated_at: datetime
    namespace_reports: list[NamespaceReport]

    def __repr__(self):
        return f"OverallReport(org={self.organization_name}, reports={len(self.namespace_reports)})"

    def to_dict(self):
        return {
            "organization_name": self.organization_name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "generated_at": self.generated_at.isoformat(),
            "namespace_reports": [report.to_dict() for report in self.namespace_reports],
        }
