"""RBAC helpers for the Orbis Scanner.

`RBACManager` is responsible for rendering the unified ServiceAccount /
ClusterRole / ClusterRoleBinding template and applying it to the cluster.

The implementation is functionally identical to the original logic in
`K8sClient` – only repackaged for single-responsibility clarity.
"""

from __future__ import annotations

import logging
from datetime import datetime

import yaml
from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.utils import create_from_dict

from orbis.config.settings import SA_AND_ROLE_BINDING_YAML_PATH
from orbis.scanner.kubernetes.connection import K8sConnection
from orbis.scanner.models import ScannerConfig
from orbis.utils.template import render_template


class RBACManager:
    """Handle ServiceAccount, ClusterRole, and ClusterRoleBinding resources."""

    def __init__(self, connection: K8sConnection) -> None:
        self.conn = connection
        self.logger: logging.Logger = connection.logger

    def create_service_account(self, config: ScannerConfig) -> bool:  # pragma: no cover
        """Ensure ServiceAccount and related RBAC objects exist (idempotent)."""
        self._apply_rbac_template(config)
        self.logger.info(f"ServiceAccount ensured: {config.service_account_name}")
        return True

    def create_cluster_role_binding(self, config: ScannerConfig) -> bool:  # pragma: no cover
        """Ensure ClusterRoleBinding (plus Role / SA) exist (idempotent)."""
        self._apply_rbac_template(config)
        self.logger.info(f"ClusterRoleBinding ensured: {config.role_binding_name}")
        return True

    def _apply_rbac_template(self, config: ScannerConfig) -> None:
        """Render RBAC template and create each object with create_from_dict."""

        context = {
            "sa_name": config.service_account_name,
            "role_binding_name": config.role_binding_name,
            "namespace": config.namespace,
            "tool_name": "orbis",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        rendered_yaml: str = render_template(SA_AND_ROLE_BINDING_YAML_PATH, context)
        api_client = client.ApiClient()

        created_kinds: list[str] = []

        try:
            for manifest in yaml.safe_load_all(rendered_yaml):
                if not isinstance(manifest, dict):
                    continue

                kind = manifest.get("kind")
                if kind:
                    created_kinds.append(kind)

                try:
                    # One object per call; namespace is applied to namespaced kinds,
                    # silently ignored by cluster-scoped kinds (Role, ClusterRoleBinding)
                    create_from_dict(
                        api_client,
                        data=manifest,
                        namespace=config.namespace,
                        verbose=False,
                    )
                except ApiException as exc:
                    if exc.status == 409:
                        continue
                    raise

            kinds_str = ", ".join(created_kinds) if created_kinds else "N/A"
            self.logger.info(f"RBAC template applied; ensured objects: {kinds_str}")

        except ApiException as exc:
            self.logger.error(f"Failed to apply RBAC template: {exc}")
            raise
