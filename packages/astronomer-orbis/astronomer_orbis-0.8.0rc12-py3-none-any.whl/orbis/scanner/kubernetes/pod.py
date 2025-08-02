"""Pod-level helpers for the Orbis Scanner."""

from __future__ import annotations

import logging
import shlex
from typing import cast

from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.stream import stream

from orbis.scanner.kubernetes.connection import K8sConnection
from orbis.scanner.models import JobStatus


class PodManager:
    """Handle pod discovery and container-state checks."""

    def __init__(self, connection: K8sConnection) -> None:
        self.conn = connection
        self.logger: logging.Logger = connection.logger

    def find_scanner_pod(self, namespace: str) -> str | None:
        """Locate the scanner pod via `component=scanner` label selector."""
        try:
            pods = cast(
                client.V1PodList,
                self.conn.core_v1.list_namespaced_pod(namespace=namespace, label_selector="component=scanner"),
            )

            if not pods.items:
                self.logger.error(
                    "No scanner pods found in namespace %s with label component=scanner",
                    namespace,
                )
                return None

            if len(pods.items) > 1:
                self.logger.warning(
                    "Found %s scanner pods, using the first one: %s",
                    len(pods.items),
                    pods.items[0].metadata.name,
                )

            selected = pods.items[0]
            pod_name = selected.metadata.name
            pod_status = selected.status.phase if selected.status else "Unknown"

            self.logger.info("Selected scanner pod: %s (status: %s)", pod_name, pod_status)

            if pod_status not in ["Running", "Succeeded"]:
                self.logger.warning("Pod %s is in %s state – file copy may fail", pod_name, pod_status)

            return pod_name

        except ApiException as api_exc:
            self.logger.error("Failed to find scanner pod: %s", api_exc)
            return None

    def _check_init_container_completion(self, pod_name: str, namespace: str, remote_bundle_path: str) -> bool:
        """Return True when 'scanner-init' container is done *and* bundle exists."""
        try:
            pod = self.conn.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            init_statuses = pod.status.init_container_statuses or []

            for ics in init_statuses:
                if ics.name == "scanner-init":
                    state = ics.state
                    if state and state.terminated and state.terminated.exit_code == 0:
                        terminated_at = state.terminated.finished_at
                        self.logger.info(
                            "Init container 'scanner-init' completed successfully at %s.",
                            terminated_at,
                        )
                        return self._verify_bundle_file_exists(pod_name, namespace, remote_bundle_path)
            return False
        except Exception as exc:  # pragma: no cover
            self.logger.error("Error checking init container completion: %s", exc)
            return False

    def _is_init_container_running(self, pod_name: str, namespace: str) -> bool:
        """Check whether 'scanner-init' container is currently running."""
        try:
            pod = self.conn.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            init_statuses = pod.status.init_container_statuses or []

            for ics in init_statuses:
                if ics.name == "scanner-init":
                    state = ics.state
                    if state and state.running:
                        self.logger.info("Init container 'scanner-init' is currently running.")
                        return True
            return False
        except Exception as exc:  # pragma: no cover
            self.logger.error("Error checking init container running state: %s", exc)
            return False

    def _verify_bundle_file_exists(self, pod_name: str, namespace: str, remote_bundle_path: str) -> bool:
        """Return True when the support-bundle file exists in the pod."""
        try:
            sanitized_path = shlex.quote(remote_bundle_path)
            exec_cmd = ["sh", "-c", f"test -f {sanitized_path} && ls -l {sanitized_path}"]
            resp = stream(
                self.conn.core_v1.connect_get_namespaced_pod_exec,
                pod_name,
                namespace,
                command=exec_cmd,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )

            if resp.strip():
                file_info = resp.strip().splitlines()
                self.logger.info("Support bundle file confirmed: %s", file_info[-1])
                self.logger.info("EARLY JOB EXIT: Detected support bundle present and init container done.")
                return True
            else:
                self.logger.warning(
                    "Init container done, but support bundle does not exist at '%s' yet.",
                    remote_bundle_path,
                )
                return False

        except Exception as exc:  # pragma: no cover
            self.logger.error("Error checking for support bundle after init container: %s", exc)
            return False

    def _discover_and_log_pod(self, job_name: str, namespace: str, status: JobStatus) -> str | None:
        """Find the pod once and emit a single log line for monitoring."""
        pod_name = status.pod_name or self.find_scanner_pod(namespace)
        if pod_name:
            self.logger.info("Monitoring pod for init container completion: %s", pod_name)
        return pod_name
