"""Orbis Scanner - Diagnostic information scanner for Astronomer Software.

This module provides comprehensive diagnostic information collection capabilities
for Astronomer Software deployments in Kubernetes clusters.

Main Components:
- ScannerService: Main service class for scanner operations
- ScannerConfig: Configuration management for scanner operations
- K8sClient: Kubernetes client wrapper for secure operations
- YamlGenerator: YAML template generation for interactive mode

CLI Commands:
- orbis scanner create: Create support bundle (directly or via YAML)
- orbis scanner retrieve: Retrieve data from running scanner pod
- orbis scanner status: Check status of scanner job
- orbis scanner clean: Clean up scanner resources

Usage Examples:
    # Interactive mode - Generate YAML for infrastructure team
    orbis scanner create -a astronomer --interactive --output-file scanner-bundle.yaml

    # Direct execution mode
    orbis scanner create -a astronomer

    # Check scanner status
    orbis scanner status -a astronomer

    # Retrieve data from completed scanner
    orbis scanner retrieve -a astronomer

    # Clean up resources
    orbis scanner clean -a astronomer
"""

from .k8s_client import K8sClient
from .models import JobStatus, ScannerConfig, ScannerResult
from .service import ScannerService
from .yaml_generator import YamlGenerator

__all__ = [
    "ScannerConfig",
    "ScannerResult",
    "JobStatus",
    "ScannerService",
    "K8sClient",
    "YamlGenerator",
]
