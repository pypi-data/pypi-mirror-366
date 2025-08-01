from datetime import datetime
from pathlib import Path

from orbis.config.settings import SA_AND_ROLE_BINDING_YAML_PATH, SCANNER_JOB_YAML_PATH
from orbis.scanner.models import ScannerConfig
from orbis.utils.logger import get_early_logger
from orbis.utils.template import render_template


class YamlGenerator:
    """Generate YAML manifests for scanner operations."""

    def __init__(self):
        self.logger = get_early_logger()

    def generate_service_account_yaml(self, config: ScannerConfig) -> str:
        """Render ServiceAccount + RBAC YAML from single template file."""
        context = {
            "sa_name": config.service_account_name,
            "role_binding_name": config.role_binding_name,
            "namespace": config.namespace,
        }
        return render_template(SA_AND_ROLE_BINDING_YAML_PATH, context).strip()

    def generate_job_yaml(self, config: ScannerConfig) -> str:
        """Render scanner job YAML using the unified template."""
        scanner_args = config.build_scanner_command_args()
        scanner_command = f"scanner.py {' '.join(scanner_args)} && cp /data/*.tar.gz /results/"

        context = {
            "job_name": config.job_name,
            "namespace": config.namespace,
            "sa_name": config.service_account_name,
            "image": config.image,
            "scanner_command": scanner_command,
            "memory": config.memory,
            "cpu": config.cpu,
            "sleep_duration": config.validated_sleep_duration,
        }

        return render_template(SCANNER_JOB_YAML_PATH, context).strip()

    def generate_support_bundle(self, config: ScannerConfig) -> str:
        """Generate complete support bundle YAML with instructions."""
        sa_yaml = self.generate_service_account_yaml(config)
        job_yaml = self.generate_job_yaml(config)

        instructions = f"""# =============================================================================
# ASTRONOMER Scanner - Support Bundle Generation
# =============================================================================
#
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Namespace: {config.namespace}
# Customer: {config.customer_name or "N/A"}
# Cluster: {config.cluster_name or "N/A"}
#
# Instructions for the infrastructure team:
# 1. Save this YAML to a file (e.g., scanner-bundle.yaml)
# 2. Apply using: kubectl apply -f scanner-bundle.yaml
# 3. Monitor the job: kubectl logs -f job/{config.job_name} -n {config.namespace}
# 4. Copy the support bundle when job completes (see instructions below)
# 5. Clean up resources using kubectl commands (see cleanup section below)
#
# ⚠️  SECURITY NOTE:
# This creates a ServiceAccount with a custom ClusterRole (read-support-bundle) for diagnostic collection.
# The ClusterRole has read-only access to cluster resources. All resources should be cleaned up after use.
#
# =============================================================================

{sa_yaml}
---
{job_yaml}

# =============================================================================
# Post-deployment Instructions:
#
# To check job status:
#   kubectl get job {config.job_name} -n {config.namespace}
#   kubectl get pods -l component=scanner -n {config.namespace}
#
# To view logs:
#   kubectl logs -f job/{config.job_name} -n {config.namespace} -c scanner-init
#
# To retrieve data (once job completes):
#   # Find the scanner pod
#   POD_NAME=$(kubectl get pods -l component=scanner -n {config.namespace} -o jsonpath='{{.items[0].metadata.name}}')
#
#   # Copy the support bundle from the pod to your local machine
#   kubectl cp $POD_NAME:/results/scanner-*.tar.gz ./scanner-bundle.tar.gz -n {config.namespace}
#
# To clean up (choose one option):
#   Option 1 - Manual kubectl commands (recommended for infrastructure teams):
#     kubectl delete job {config.job_name} -n {config.namespace}
#     kubectl delete serviceaccount temp-scanner-support-bundle -n {config.namespace}
#     kubectl delete clusterrole read-support-bundle
#     kubectl delete clusterrolebinding scanner-admin-access-binding
#     kubectl delete pods -l component=scanner -n {config.namespace}
#
#   Option 2 - Delete using original YAML file:
#     kubectl delete -f scanner-bundle.yaml
# ============================================================================="""

        return instructions

    def write_to_file(self, content: str, output_file: str) -> bool:
        """Write YAML content to file."""
        try:
            output_path = Path(output_file)
            output_path.write_text(content)
            self.logger.info(f"YAML saved to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write YAML to {output_file}: {e}")
            return False
