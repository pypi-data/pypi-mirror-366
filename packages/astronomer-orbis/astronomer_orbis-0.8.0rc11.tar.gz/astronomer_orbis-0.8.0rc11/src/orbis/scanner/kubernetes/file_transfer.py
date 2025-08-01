"""File-transfer utilities for moving support bundles from pod → local disk."""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import shlex
from typing import cast

from kubernetes import client
from kubernetes.stream import stream

from orbis.scanner.kubernetes.connection import K8sConnection
from orbis.scanner.kubernetes.pod import PodManager


class FileTransfer:
    """High-level helper to copy files out of the scanner pod."""

    def __init__(self, connection: K8sConnection, pod_mgr: PodManager) -> None:
        self.conn = connection
        self.pod_mgr = pod_mgr
        self.logger: logging.Logger = connection.logger

    def copy_file_from_pod(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        """Copy a (potentially large) binary file using base64 streaming."""
        try:
            self.logger.info("Starting file copy from pod %s:%s to %s", pod_name, remote_path, local_path)

            if not self._validate_remote_file_exists(pod_name, namespace, remote_path):
                return False

            if not self._validate_pod_readiness(pod_name, namespace):
                return False

            exec_command = ["base64", remote_path]
            self.logger.info("Executing copy command on pod %s: %s", pod_name, " ".join(exec_command))

            resp = stream(
                self.conn.core_v1.connect_get_namespaced_pod_exec,
                pod_name,
                namespace,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            base64_data = self._collect_base64_data_from_stream(resp)
            if not base64_data:
                return False

            if not self._decode_and_write_file(base64_data, local_path):
                return False

            return self._verify_copied_file(local_path)

        except Exception as exc:  # pragma: no cover
            self.logger.error(
                "Failed to copy file from pod %s:%s to %s: %s",
                pod_name,
                remote_path,
                local_path,
                exc,
            )
            self.logger.debug(
                "Pod=%s, Namespace=%s, Remote=%s, Local=%s",
                pod_name,
                namespace,
                remote_path,
                local_path,
            )
            self._log_detailed_error_context(pod_name, namespace, remote_path, str(exc))
            return False

    def _collect_base64_data_from_stream(self, resp) -> str:
        base64_chunks: list[str] = []
        stderr_output: list[str] = []

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                stdout_data = resp.read_stdout()
                if isinstance(stdout_data, bytes):
                    stdout_data = stdout_data.decode("utf-8", errors="replace")
                base64_chunks.append(stdout_data)

            if resp.peek_stderr():
                stderr_data = resp.read_stderr()
                if isinstance(stderr_data, bytes):
                    stderr_data = stderr_data.decode("utf-8", errors="replace")
                stderr_output.append(stderr_data)
                self.logger.warning("stderr: %s", stderr_data)

        resp.close()

        if stderr_output:
            self.logger.error("Command stderr output: %s", "".join(stderr_output))

        clean_base64 = "".join("".join(base64_chunks).split())
        if not clean_base64:
            self.logger.error("No base64 data received from pod")
            return ""

        return clean_base64

    def _decode_and_write_file(self, base64_data: str, local_path: str) -> bool:
        try:
            binary = base64.b64decode(base64_data)
            with open(local_path, "wb") as fh:
                fh.write(binary)
            return True
        except Exception as exc:  # pragma: no cover
            self.logger.error("Failed to decode base64 data: %s", exc)
            return False

    def _verify_copied_file(self, local_path: str) -> bool:
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            size = os.path.getsize(local_path)
            self.logger.info("File copied successfully: %s (%s bytes)", local_path, size)
            return True
        if not os.path.exists(local_path):
            self.logger.error("File copy verification failed: %s does not exist", local_path)
        else:
            self.logger.error("File copy verification failed: %s has zero size", local_path)
        return False

    def verify_file_checksum(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        try:
            exec_cmd = ["sha256sum", remote_path]
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
            remote_checksum = resp.split()[0]

            with open(local_path, "rb") as fh:
                local_checksum = hashlib.sha256(fh.read()).hexdigest()

            if remote_checksum == local_checksum:
                self.logger.info("File checksum verification passed")
                return True
            self.logger.error("File checksum verification failed")
            return False

        except Exception as exc:  # pragma: no cover
            self.logger.error("Checksum verification failed: %s", exc)
            return False

    def _validate_remote_file_exists(self, pod_name: str, namespace: str, remote_path: str) -> bool:
        try:
            self.logger.debug("Checking if remote file exists: %s", remote_path)
            sanitized = shlex.quote(remote_path)
            exec_cmd = ["sh", "-c", f"test -f {sanitized} && ls -la {sanitized}"]
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
                self.logger.info("Remote file exists: %s", remote_path)
                self.logger.debug("File details: %s", resp.strip())
                return True
            self.logger.error("Remote file does not exist: %s", remote_path)
            return False
        except Exception as exc:  # pragma: no cover
            self.logger.error("Failed to validate remote file existence: %s", exc)
            return False

    def _validate_pod_readiness(self, pod_name: str, namespace: str) -> bool:
        try:
            pod = cast(
                client.V1Pod,
                self.conn.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace),
            )

            if not pod.status:
                self.logger.error("Pod %s has no status information", pod_name)
                return False

            phase = pod.status.phase
            self.logger.debug("Pod %s phase: %s", pod_name, phase)

            if phase == "Succeeded":
                self.logger.warning("Pod %s is in 'Succeeded' state – cannot exec into containers.", pod_name)
                self.logger.warning("The scanner has completed but the main container has exited.")
                self.logger.warning(
                    "To retrieve the support bundle manually, run:\\nkubectl cp %s:/results/scanner-*.tar.gz ./scanner-bundle.tar.gz -n %s",
                    pod_name,
                    namespace,
                )
                return False

            if phase != "Running":
                self.logger.error("Pod %s is not in a ready state. Current phase: %s", pod_name, phase)
                return False

            if pod.status.container_statuses:
                for cs in pod.status.container_statuses:
                    if not cs.ready:
                        self.logger.warning("Container %s in pod %s is not ready", cs.name, pod_name)

            return True

        except Exception as exc:  # pragma: no cover
            self.logger.error("Failed to validate pod readiness: %s", exc)
            return False

    def _log_detailed_error_context(self, pod_name: str, namespace: str, remote_path: str, error_message: str) -> None:
        try:
            self.logger.error("=== Detailed Error Context for Pod %s ===", pod_name)

            try:
                pod = cast(
                    client.V1Pod,
                    self.conn.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace),
                )
                if pod.status:
                    self.logger.error("Pod phase: %s", pod.status.phase)
                    if pod.status.container_statuses:
                        for cs in pod.status.container_statuses:
                            self.logger.error(
                                "Container %s: ready=%s restart=%s",
                                cs.name,
                                cs.ready,
                                cs.restart_count,
                            )
                            if cs.state and cs.state.waiting:
                                self.logger.error(
                                    "Container %s waiting: %s – %s",
                                    cs.name,
                                    cs.state.waiting.reason,
                                    cs.state.waiting.message,
                                )
                            if cs.state and cs.state.terminated:
                                self.logger.error(
                                    "Container %s terminated: %s – %s",
                                    cs.name,
                                    cs.state.terminated.reason,
                                    cs.state.terminated.message,
                                )
            except Exception as exc:
                self.logger.error("Could not get pod status: %s", exc)

            # List /results
            try:
                exec_cmd = ["ls", "-la", "/results"]
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
                self.logger.error("Contents of /results directory: %s", resp)
            except Exception as exc:
                self.logger.error("Could not list /results directory: %s", exc)

            try:
                exec_cmd = [
                    "find",
                    "/results",
                    "/data",
                    "/tmp",
                    "-name",
                    "*.tar.gz",
                    "-type",
                    "f",
                ]
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
                self.logger.error("All .tar.gz files in pod: %s", resp)
            except Exception as exc:
                self.logger.error("Could not search for .tar.gz files: %s", exc)

            self.logger.error("Original error: %s", error_message)
            self.logger.error("=== End Error Context ===")

        except Exception as exc:  # pragma: no cover
            self.logger.error("Failed to gather error context: %s", exc)
