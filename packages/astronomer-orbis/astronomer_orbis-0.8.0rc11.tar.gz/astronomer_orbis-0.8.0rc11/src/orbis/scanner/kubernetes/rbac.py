"""RBAC helpers for the Orbis Scanner.

`RBACManager` is responsible for rendering the unified ServiceAccount /
ClusterRole / ClusterRoleBinding template and applying it to the cluster.

The implementation is functionally identical to the original logic in
`K8sClient` – only repackaged for single-responsibility clarity.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.utils import create_from_yaml

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

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _apply_rbac_template(self, config: ScannerConfig) -> None:
        """Render the RBAC Jinja2 template and apply it with `create_from_yaml`.

        The template is designed to be idempotent: attempting to create
        already-existing resources results in a 409 and is simply logged.
        """
        context = {
            "sa_name": config.service_account_name,
            "role_binding_name": config.role_binding_name,
            "namespace": config.namespace,
        }

        rendered_yaml = render_template(SA_AND_ROLE_BINDING_YAML_PATH, context)

        tmp_file_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as tmp:
                tmp.write(rendered_yaml)
                tmp_file_path = tmp.name

            api_client = client.ApiClient()
            created_objects = create_from_yaml(api_client, tmp_file_path, namespace=config.namespace, verbose=False)

            kinds = ", ".join(obj.kind for obj in created_objects)
            self.logger.info(f"RBAC template applied; ensured objects: {kinds}")

        except ApiException as api_exc:
            if api_exc.status == 409:
                self.logger.info("RBAC resources already exist, skipping creation.")
            else:
                self.logger.error(f"Failed to apply RBAC template: {api_exc}")
                raise
        except Exception as exc:  # pragma: no cover
            self.logger.error(f"Unexpected error applying RBAC template: {exc}")
            raise
        finally:
            if tmp_file_path and Path(tmp_file_path).exists():
                try:
                    Path(tmp_file_path).unlink()
                except Exception:  # pragma: no cover
                    pass
