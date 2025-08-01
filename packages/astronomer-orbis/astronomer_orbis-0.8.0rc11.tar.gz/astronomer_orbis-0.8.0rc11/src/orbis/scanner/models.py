from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ScannerConfig:
    """Configuration for scanner operations."""

    namespace: str
    image: str | None = None  # Docker image for the scanner pod (required for create operations)
    cpu: str = "1"
    memory: str = "1Gi"
    sleep_duration: str = "86400"
    cleanup: bool = True
    output_dir: str = "."

    # Optional diagnostic parameters
    customer_name: str | None = None
    cluster_name: str | None = None
    domain: str | None = None
    log_level: str = "info"
    additional_namespaces: list[str] = field(default_factory=list)
    all_namespaces: bool = False
    telescope_enabled: bool = False
    telescope_executor: str = "kubernetes"
    telescope_only: bool = False

    # Kubernetes connection
    kubeconfig_path: str | None = None

    # Polling configuration - sensible defaults, overridable via CLI
    poll_interval: int = 10
    error_retry_interval: int = 5
    poll_timeout: int = 3600

    @property
    def job_name(self) -> str:
        """Generate job name with timestamp."""
        return f"scanner-{datetime.now().strftime('%d-%m-%y')}"

    @property
    def service_account_name(self) -> str:
        """Service account name for scanner."""
        return "temp-scanner-support-bundle"

    @property
    def role_binding_name(self) -> str:
        """Role binding name for scanner."""
        return "scanner-admin-access-binding"

    @property
    def compressed_filename(self) -> str:
        """Generate compressed file name."""
        return f"scanner-{datetime.now().strftime('%d-%m-%y')}.tar.gz"

    @property
    def remote_tar_path(self) -> str:
        """Path to tar file in pod."""
        return f"/results/{self.compressed_filename}"

    @property
    def local_tar_path(self) -> str:
        """Local path for downloaded tar file."""
        return str(Path(self.output_dir) / self.compressed_filename)

    @property
    def validated_sleep_duration(self) -> str:
        """Get validated sleep duration with minimum 1 hour (3600 seconds) enforcement."""
        try:
            # Parse as integer (seconds)
            duration_seconds = int(self.sleep_duration)

            # Enforce minimum 1 hour (3600 seconds)
            if duration_seconds < 3600:
                return "3600"  # 1 hour in seconds

            return str(duration_seconds)
        except (ValueError, TypeError):
            # If not a valid integer, default to 1 day
            return "86400"

    def build_scanner_command_args(self) -> list[str]:
        """Build command arguments for scanner.py (in container)."""
        args = ["-a", self.namespace]

        if self.domain:
            args.extend(["-d", self.domain])

        if self.customer_name:
            args.extend(["-c", self.customer_name])

        if self.cluster_name:
            args.extend(["-n", self.cluster_name])

        if self.log_level:
            args.extend(["--log-level", self.log_level])

        if self.additional_namespaces:
            args.append("--airflow-namespaces")
            args.extend(self.additional_namespaces)

        if self.all_namespaces:
            args.append("--all-airflow-namespaces")

        if self.telescope_enabled:
            args.append("--telescope")

        if self.telescope_executor:
            args.extend(["--telescope_executor", self.telescope_executor])

        if self.telescope_only:
            args.append("--telescope-only")

        return args


@dataclass
class JobStatus:
    """Status information for a scanner Job."""

    name: str
    namespace: str
    creation_time: datetime | None = None
    start_time: datetime | None = None
    completion_time: datetime | None = None
    active: int = 0
    succeeded: int = 0
    failed: int = 0
    conditions: list[dict[str, Any]] = field(default_factory=list)
    ready: bool = False
    pod_name: str | None = None
    pod_status: str | None = None


@dataclass
class ScannerResult:
    """Result of scanner operation."""

    success: bool
    output_file: str | None = None
    error_message: str | None = None
    job_status: JobStatus | None = None
