"""Centralised Kubernetes connection handling.

`K8sConnection` is responsible for:
1. Loading the appropriate Kubernetes configuration (kube-config or in-cluster).
2. Exposing fully-initialised API client instances for other helpers to reuse.
3. Holding a reference to the shared logger so that all helpers log
   consistently.

The logic is extracted verbatim (with minor stylistic tweaks) from the original
`K8sClient` implementation to keep behaviour identical.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from kubernetes import client, config

from orbis.utils.logger import get_early_logger


class K8sConnection:
    """Establishes API clients and shares them across helper modules."""

    def __init__(self, kubeconfig_path: str | None = None, logger: logging.Logger | None = None) -> None:
        self.logger = logger or get_early_logger()
        self._load_config(kubeconfig_path)

        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
        self.rbac_v1 = client.RbacAuthorizationV1Api()

    def _load_config(self, kubeconfig_path: str | None) -> None:
        """Load Kubernetes configuration following a priority order.

        1. Explicit `kubeconfig_path` provided by the caller
        2. `KUBECONFIG` environment variable
        3. Default location `~/.kube/config`
        4. In-cluster configuration (when running inside a pod)
        """
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
                self.logger.info(f"Loaded kube-config from explicit path: {kubeconfig_path}")
            elif os.getenv("KUBECONFIG"):
                env_path = os.getenv("KUBECONFIG")
                config.load_kube_config(config_file=env_path)
                self.logger.info(f"Loaded kube-config from $KUBECONFIG: {env_path}")
            elif Path.home().joinpath(".kube", "config").exists():
                config.load_kube_config()
                self.logger.info("Loaded kube-config from default path ~/.kube/config")
            else:
                config.load_incluster_config()
                self.logger.info("Loaded in-cluster Kubernetes configuration")
        except Exception as exc:
            raise RuntimeError(f"Failed to load Kubernetes configuration: {exc}") from exc
