# src/orbis/api/houston.py
import json
from typing import Any

import requests
import yaml

from orbis.config import ASTRO_SOFTWARE_API_TOKEN, HOUSTON_QUERIES_FILE_PATH
from orbis.data.models import DeploymentConfig, WorkerQueueStats
from orbis.data.transform import calculate_scheduler_resources, calculate_worker_concurrency, calculate_worker_type
from orbis.utils.logger import get_early_logger

logger = get_early_logger()


class HoustonAPI:
    """Used to make requests to the Houston API."""

    def __init__(self, base_domain: str, token: str, verify_ssl: bool = True):
        self.base_url = f"https://houston.{base_domain}/v1"
        self.token = token
        self.verify_ssl = verify_ssl
        logger.info("Initializing Houston API with base URL: %s", self.base_url)
        self.queries = self._load_queries()

    def _load_queries(self):
        queries_path = HOUSTON_QUERIES_FILE_PATH
        logger.info("Loading queries from: %s", queries_path)
        with open(queries_path) as f:
            return yaml.safe_load(f)

    def _make_request(self, query: str) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        logger.info("Making request to Houston API")
        logger.debug("Request headers: %s", headers)
        logger.debug("Request query: %s", query)

        try:
            response = requests.post(self.base_url, json={"query": query}, headers=headers, verify=self.verify_ssl, timeout=30)
            logger.debug("Response status code: %s", response.status_code)
            logger.debug("Response text: %s", response.text)

            if not response.ok:
                logger.error("Houston API request failed with status %d: %s", response.status_code, response.text)
                raise ValueError(f"Houston API request failed: {response.text}")

            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Network error during Houston API request: %s", str(e))
            raise ValueError(f"Houston API request failed: {str(e)}")

    def get_all_deployments(self, workspaces: list[str]) -> list[dict[str, Any]]:
        logger.info("Getting all deployments for workspaces: %s", workspaces)
        deployments = []
        response = self._make_request(self.queries["get_all_deployments"])
        response_data = response.get("data") or {}
        all_workspaces = response_data.get("sysWorkspaces")
        if all_workspaces is None:
            all_workspaces = []
        for workspace in all_workspaces:
            if not workspaces or workspace["id"] in workspaces:
                deployments.extend(workspace.get("deployments", []))
        logger.info("Found %d deployments", len(deployments))
        return deployments

    def get_workspace_deployments(self, workspace_id: str) -> list[dict[str, Any]]:
        logger.info("Getting deployments for workspace: %s", workspace_id)
        deployments = []
        response = self._make_request(self.queries["get_workspace_deployments"].replace("<workspace_uuid>", workspace_id))
        response_data = response.get("data") or {}
        workspace = response_data.get("workspace")
        if workspace is None:
            logger.warning("Workspace not found: %s", workspace_id)
            return deployments
        deployments.extend(workspace.get("deployments", []))
        logger.info("Found %d deployments", len(deployments))
        return deployments


def get_organization_metadata(base_domain: str, workspaces: list[str], verify_ssl: bool = True) -> tuple[str, list[str], dict[str, DeploymentConfig]]:
    """Get organization namespaces."""
    logger.info("Getting organization metadata for domain: %s", base_domain)
    executors = {
        "CeleryExecutor": "CELERY",
        "KubernetesExecutor": "KUBERNETES",
    }
    namespaces: list[str] = []
    if not ASTRO_SOFTWARE_API_TOKEN:
        logger.error("ASTRO_SOFTWARE_API_TOKEN is not set")
        raise Exception("ASTRO_SOFTWARE_API_TOKEN is not set")

    logger.info("Creating Houston API client")
    houston_client = HoustonAPI(base_domain=base_domain, token=ASTRO_SOFTWARE_API_TOKEN, verify_ssl=verify_ssl)
    try:
        output_folder = base_domain.replace(".", "_")
        logger.info("Getting deployments from Houston API")
        deployments = houston_client.get_workspace_deployments(workspaces[0]) if len(workspaces) == 1 else houston_client.get_all_deployments(workspaces)
        if len(deployments) == 0:
            deployments = houston_client.get_all_deployments(workspaces)
        deployment_configs: dict[str, DeploymentConfig] = {}
        for deployment in deployments:
            namespace = deployment["namespace"]
            release_name = deployment["releaseName"]
            if deployment["config"]["executor"] not in executors:
                logger.warning("Executor not supported: %s. Skipping namespace %s", deployment["config"]["executor"], namespace)
                continue
            executor = executors[deployment["config"]["executor"]]
            scheduler_resources = deployment["config"]["scheduler"]["resources"]["limits"]
            scheduler_au = calculate_scheduler_resources(scheduler_resources)
            deployment_config = DeploymentConfig(
                namespace=namespace,
                release_name=release_name,
                name=deployment.get("label") or namespace,
                executor=executor,
                scheduler_replicas=deployment["config"]["scheduler"]["replicas"],
                scheduler_au=scheduler_au,
            )

            if executor.lower() == "celery":
                min_workers = 1
                max_workers = deployment["config"]["workers"]["replicas"]
                worker_type = calculate_worker_type(worker_resources=deployment["config"]["workers"]["resources"]["limits"])
                worker_concurrency = calculate_worker_concurrency(env_vars=deployment["environmentVariables"])
                worker_queue_stat = WorkerQueueStats(
                    queue_name="default",
                    mean_value=0,  # These will be populated later with actual metrics
                    median_value=0,
                    max_value=0,
                    min_value=0,
                    p90_value=0,
                    worker_type=worker_type,
                    worker_concurrency=worker_concurrency,
                    min_workers=min_workers,
                    max_workers=max_workers,
                )
                deployment_config.queues.append(worker_queue_stat)

            deployment_configs[namespace] = deployment_config
            namespaces.append(deployment["namespace"])

        logger.info("Deployment configs: %s", json.dumps({k: {**v.__dict__, "queues": [queue.__dict__ for queue in v.queues]} for k, v in deployment_configs.items()}, default=str))
        return output_folder, namespaces, deployment_configs

    except ValueError as e:
        logger.error("Error retrieving organization metadata: %s", str(e))
        raise
