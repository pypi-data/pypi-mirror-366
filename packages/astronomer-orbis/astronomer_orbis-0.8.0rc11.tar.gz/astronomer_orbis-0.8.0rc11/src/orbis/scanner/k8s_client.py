import logging

from orbis.scanner.models import JobStatus, ScannerConfig
from orbis.utils.logger import get_early_logger


class K8sClient:
    """Kubernetes operations for scanner using Python client.

    This façade keeps the public surface identical to the original
    monolithic implementation but forwards each call to specialised helper
    classes that now live under `orbis.scanner.kubernetes`.
    """

    def __init__(self, kubeconfig_path: str | None = None, logger: logging.Logger | None = None):
        self.logger = logger or get_early_logger()

        from orbis.scanner.kubernetes import (
            CleanupManager,
            FileTransfer,
            JobManager,
            K8sConnection,
            PodManager,
            RBACManager,
        )

        self.conn = K8sConnection(kubeconfig_path, self.logger)

        self.core_v1 = self.conn.core_v1
        self.apps_v1 = self.conn.apps_v1
        self.batch_v1 = self.conn.batch_v1
        self.rbac_v1 = self.conn.rbac_v1

        self.rbac_mgr = RBACManager(self.conn)
        self.pod_mgr = PodManager(self.conn)
        self.job_mgr = JobManager(self.conn, self.pod_mgr)
        self.file_mgr = FileTransfer(self.conn, self.pod_mgr)
        self.cleanup_mgr = CleanupManager(self.conn)

    def create_service_account(self, config: ScannerConfig) -> bool:
        """Ensure ServiceAccount (and related RBAC objects) exist."""
        return self.rbac_mgr.create_service_account(config)

    def create_cluster_role_binding(self, config: ScannerConfig) -> bool:
        """Ensure ClusterRoleBinding (and related RBAC objects) exist."""
        return self.rbac_mgr.create_cluster_role_binding(config)

    def create_job(self, config: ScannerConfig) -> str:
        """Render and apply the scanner Job; returns Job name."""
        return self.job_mgr.create_job(config)

    def get_job_status(self, job_name: str, namespace: str) -> JobStatus:
        """Retrieve up-to-date status for the given Job."""
        return self.job_mgr.get_job_status(job_name, namespace)

    def wait_for_job_completion(
        self,
        job_name: str,
        namespace: str,
        config: ScannerConfig,
        timeout: int | None = None,
    ) -> tuple[bool, bool]:
        """Block until the Job is done OR early readiness OR timeout."""
        return self.job_mgr.wait_for_job_completion(job_name, namespace, config, timeout)

    def find_scanner_pod(self, namespace: str) -> str | None:
        """Locate the scanner pod for a given namespace."""
        return self.pod_mgr.find_scanner_pod(namespace)

    def copy_file_from_pod(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        """Copy a file from pod ➜ local disk (base64 streaming)."""
        return self.file_mgr.copy_file_from_pod(pod_name, namespace, remote_path, local_path)

    def verify_file_checksum(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        """Validate checksum of copied file matches remote."""
        return self.file_mgr.verify_file_checksum(pod_name, namespace, remote_path, local_path)

    def cleanup_scanner_resources(self, namespace: str) -> None:
        """Delete all scanner-related resources (Jobs, Pods, RBAC)."""
        self.cleanup_mgr.cleanup_scanner_resources(namespace)
