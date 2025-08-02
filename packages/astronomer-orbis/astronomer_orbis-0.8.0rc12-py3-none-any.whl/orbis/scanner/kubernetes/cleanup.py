"""Cleanup helpers for deleting scanner resources (Jobs, Pods, RBAC)."""

from __future__ import annotations

import logging

from kubernetes.client import ApiException

from orbis.scanner.kubernetes.connection import K8sConnection
from orbis.scanner.models import ScannerConfig


class CleanupManager:
    """Delete all scanner-related objects in the target namespace."""

    def __init__(self, connection: K8sConnection) -> None:
        self.conn = connection
        self.logger: logging.Logger = connection.logger

    def cleanup_scanner_resources(self, namespace: str) -> None:
        self.logger.info("Cleaning up scanner resources in namespace: %s", namespace)

        try:
            # Delete Jobs
            jobs = self.conn.batch_v1.list_namespaced_job(namespace=namespace, label_selector="component=scanner")
            for job in jobs.items:
                self.conn.batch_v1.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
                self.logger.info("Deleted job: %s", job.metadata.name)

            # Delete Pods
            pods = self.conn.core_v1.list_namespaced_pod(namespace=namespace, label_selector="component=scanner")
            for pod in pods.items:
                self.conn.core_v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
                self.logger.info("Deleted pod: %s", pod.metadata.name)

            # RBAC resources
            cfg = ScannerConfig(namespace=namespace)
            try:
                self.conn.core_v1.delete_namespaced_service_account(name=cfg.service_account_name, namespace=namespace)
                self.logger.info("Deleted service account: %s", cfg.service_account_name)
            except ApiException as api_exc:
                if api_exc.status != 404:
                    self.logger.warning("Failed to delete service account: %s", api_exc)

            try:
                self.conn.rbac_v1.delete_cluster_role_binding(name=cfg.role_binding_name)
                self.logger.info("Deleted cluster role binding: %s", cfg.role_binding_name)
            except ApiException as api_exc:
                if api_exc.status != 404:
                    self.logger.warning("Failed to delete cluster role binding: %s", api_exc)

            try:
                self.conn.rbac_v1.delete_cluster_role(name="read-support-bundle")
                self.logger.info("Deleted cluster role: read-support-bundle")
            except ApiException as api_exc:
                if api_exc.status != 404:
                    self.logger.warning("Failed to delete cluster role: %s", api_exc)

        except ApiException as api_exc:
            self.logger.error("Error during cleanup: %s", api_exc)
            raise
