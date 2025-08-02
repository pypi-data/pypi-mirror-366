"""Job-level helpers for the Orbis Scanner."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import cast

import yaml
from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.utils import create_from_dict

from orbis.config.settings import SCANNER_JOB_YAML_PATH
from orbis.scanner.kubernetes.connection import K8sConnection
from orbis.scanner.kubernetes.pod import PodManager
from orbis.scanner.models import JobStatus, ScannerConfig
from orbis.utils.template import render_template


class JobManager:
    """Create Jobs, poll status, and wait for completion / early readiness."""

    def __init__(self, connection: K8sConnection, pod_mgr: PodManager) -> None:
        self.conn = connection
        self.pod_mgr = pod_mgr
        self.logger: logging.Logger = connection.logger

    def create_job(self, config: ScannerConfig) -> str:
        """Render the unified Jinja2 template and apply it to the cluster."""
        scanner_args = config.build_scanner_command_args()
        scanner_cmd = f"scanner.py {' '.join(scanner_args)} && cp /data/*.tar.gz /results/"

        ctx = {
            "job_name": config.job_name,
            "namespace": config.namespace,
            "sa_name": config.service_account_name,
            "image": config.image,
            "scanner_command": scanner_cmd,
            "memory": config.memory,
            "cpu": config.cpu,
            "sleep_duration": config.validated_sleep_duration,
            "tool_name": "orbis",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        rendered_yaml = render_template(SCANNER_JOB_YAML_PATH, ctx)
        self.logger.debug("Rendered YAML:\n%s", rendered_yaml)
        api_client = client.ApiClient()

        try:
            job_name_found = None
            manifests_found = []

            for manifest in yaml.safe_load_all(rendered_yaml):
                if not isinstance(manifest, dict):
                    continue

                kind = manifest.get("kind")
                manifests_found.append(kind)
                self.logger.debug("Processing manifest with kind: %s", kind)

                if kind == "Job":
                    job_name_from_manifest = manifest.get("metadata", {}).get("name")
                    self.logger.debug("Found Job manifest with name: %s", job_name_from_manifest)

                    job_obj = create_from_dict(
                        api_client,
                        data=manifest,
                        namespace=config.namespace,
                        verbose=False,
                    )

                    if hasattr(job_obj, "metadata") and job_obj.metadata and job_obj.metadata.name:
                        job_name_found = job_obj.metadata.name
                    elif job_name_from_manifest:
                        job_name_found = job_name_from_manifest

                    if job_name_found:
                        self.logger.info("Created job: %s", job_name_found)
                        return job_name_found

            if not job_name_found:
                self.logger.error("No Job object found. Manifests found: %s", manifests_found)
                raise RuntimeError("Job creation failed: Job object not found in rendered YAML")

        except ApiException as api_exc:
            self.logger.error("Failed to create job: %s", api_exc)
            raise

    def get_job_status(self, job_name: str, namespace: str) -> JobStatus:
        """Return a rich `JobStatus` dataclass with pod info & readiness flag."""
        try:
            job = cast(
                client.V1Job,
                self.conn.batch_v1.read_namespaced_job_status(name=job_name, namespace=namespace),
            )

            if not job.metadata or not job.status:
                raise RuntimeError("Job metadata or status is missing")

            status = JobStatus(
                name=job.metadata.name or "",
                namespace=job.metadata.namespace or "",
                creation_time=job.metadata.creation_timestamp,
                start_time=job.status.start_time,
                completion_time=job.status.completion_time,
                active=job.status.active or 0,
                succeeded=job.status.succeeded or 0,
                failed=job.status.failed or 0,
            )

            if job.status.conditions:
                for condition in job.status.conditions:
                    status.conditions.append({
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message,
                        "last_transition_time": condition.last_transition_time,
                    })

                    if condition.type == "Complete" and condition.status == "True":
                        status.ready = True

            pod_name = self.pod_mgr.find_scanner_pod(namespace)
            if pod_name:
                status.pod_name = pod_name
                pod = cast(
                    client.V1Pod,
                    self.conn.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace),
                )
                if pod.status:
                    status.pod_status = pod.status.phase

                    init_statuses = getattr(pod.status, "init_container_statuses", []) or []
                    for init_cs in init_statuses:
                        if init_cs.name == "scanner-init" and init_cs.state and init_cs.state.terminated and init_cs.state.terminated.exit_code == 0:
                            if not status.ready:
                                self.logger.info("Init container 'scanner-init' terminated – marking ready.")
                            status.ready = True

            return status

        except ApiException as api_exc:
            self.logger.error("Failed to get job status: %s", api_exc)
            raise

    def wait_for_job_completion(
        self,
        job_name: str,
        namespace: str,
        config: ScannerConfig,
        timeout: int | None = None,
    ) -> tuple[bool, bool]:
        """Block until job succeeds OR early readiness OR timeout.

        Returns (job_completed, init_container_running).
        """
        start_time = time.time()
        last_status_log = None
        discovered_pod = None

        self.logger.info("Entering custom job wait: will detect init container completion for early exit.")

        timeout = timeout or config.poll_timeout
        poll_interval = config.poll_interval
        error_retry = config.error_retry_interval
        remote_bundle_path = config.remote_tar_path

        while time.time() - start_time < timeout:
            try:
                status = self.get_job_status(job_name, namespace)
                current = f"Active={status.active}, Succeeded={status.succeeded}, Failed={status.failed}"

                if current != last_status_log:
                    self.logger.info("Job %s: %s", job_name, current)
                    last_status_log = current

                if status.succeeded and status.succeeded > 0:
                    self.logger.info("Job completed successfully (status.succeeded > 0).")
                    return True, False
                if status.failed and status.failed > 0:
                    self.logger.error("Job failed.")
                    self._log_failed_job_details(job_name, namespace)
                    return False, False

                if not discovered_pod:
                    discovered_pod = self.pod_mgr._discover_and_log_pod(job_name, namespace, status)

                current_pod = status.pod_name or discovered_pod
                if current_pod:
                    if self.pod_mgr._check_init_container_completion(current_pod, namespace, remote_bundle_path):
                        return True, False

                time.sleep(poll_interval)

            except ApiException as api_exc:
                self.logger.warning("Error checking job status: %s", api_exc)
                time.sleep(error_retry)
            except Exception as exc:  # pragma: no cover
                self.logger.error("Unexpected error in wait_for_job_completion: %s", exc)
                time.sleep(error_retry)

        current_pod = discovered_pod or self.pod_mgr.find_scanner_pod(namespace)
        init_running = False
        if current_pod:
            init_running = self.pod_mgr._is_init_container_running(current_pod, namespace)

        self._log_job_timeout(
            job_name,
            namespace,
            timeout,
            discovered_pod,
            remote_bundle_path,
            init_running,
        )
        return False, init_running

    def _log_job_timeout(
        self,
        job_name: str,
        namespace: str,
        timeout: int,
        discovered_pod: str | None,
        remote_bundle_path: str,
        init_container_running: bool = False,
    ) -> None:
        """Provide context-rich logging for timeout scenarios."""
        if not discovered_pod:
            self.logger.error("Job %s timed out after %s s. Could not find associated pod.", job_name, timeout)
            return

        if init_container_running:
            self.logger.warning(
                "Job %s monitoring timed out after %s s, but init container is still running.",
                job_name,
                timeout,
            )
            self.logger.warning("Init container may still be making progress. Resources left intact for manual retrieval.")
            self.logger.warning(
                "To check progress: kubectl logs %s -n %s -c scanner-init",
                discovered_pod,
                namespace,
            )
            self.logger.warning("To retrieve when ready: orbis scanner retrieve -n %s", namespace)
        elif not self.pod_mgr._check_init_container_completion(discovered_pod, namespace, remote_bundle_path):
            self.logger.error(
                "Job %s timed out after %s s. Init container did not complete successfully.",
                job_name,
                timeout,
            )
        else:
            self.logger.error(
                "Job %s timed out after %s s. Bundle file not found at %s.",
                job_name,
                timeout,
                remote_bundle_path,
            )

    def _log_failed_job_details(self, job_name: str, namespace: str) -> None:
        """Output quick hints to diagnose failed Jobs."""
        try:
            pod_name = self.pod_mgr.find_scanner_pod(namespace)
            if pod_name:
                self.logger.error(
                    "Job '%s' failed. Check pod logs: kubectl logs %s -n %s -c scanner-init",
                    job_name,
                    pod_name,
                    namespace,
                )
            else:
                self.logger.error("Job '%s' failed but could not find associated pod", job_name)
        except Exception as exc:  # pragma: no cover
            self.logger.error("Could not get failed job details for '%s': %s", job_name, exc)
