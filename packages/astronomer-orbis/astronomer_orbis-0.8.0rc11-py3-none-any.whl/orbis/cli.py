import asyncio
import logging
from importlib.metadata import version

import click
import requests
import urllib3
from pendulum import from_format

from orbis.api import houston
from orbis.config import (
    CPU,
    MEMORY,
    SLEEP_DURATION,
    SOFTWARE_QUERIES_FILE_PATH,
    parse_yaml,
    validate_input_args,
)
from orbis.data.models import ReportMetadata
from orbis.report.generator import generate_report
from orbis.scanner.models import ScannerConfig
from orbis.scanner.service import ScannerService
from orbis.utils.fileio import compress_output_files, create_output_folder, perform_cleanup
from orbis.utils.logger import get_logger, update_early_logger_level

# Suppress InsecureRequestWarning when SSL verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _compute_verbose_level(verbose: int, log_level: str = "info") -> int:
    """Compute verbose level from CLI flags."""
    if verbose > 0:
        return verbose
    # Map log_level to verbose level if no --verbose flag used
    log_level_mapping = {"warn": 1, "info": 2, "debug": 3}
    return log_level_mapping.get(log_level.lower(), 2)


def _init_scanner_logger(namespace: str, verbose_level: int) -> logging.Logger:
    """Initialize scanner logger with persistent file in output directory."""
    output_folder = create_output_folder(f"scanner_{namespace}")
    log_file = f"{output_folder}/scanner_{namespace}.log"
    return get_logger(f"scanner_{namespace}", log_file, verbose_level)


def display_input_arguments(start_date, end_date, base_domain, clusters=None, workspaces=None) -> None:
    """Display input arguments."""
    click.echo(f"Input Arguments:\nStart Date: {start_date}\nEnd Date: {end_date}\nBase Domain: {base_domain}")
    if clusters:
        click.echo(f"Clusters: {clusters}")
    if workspaces:
        click.echo(f"Workspaces: {workspaces}")


def get_version() -> str:
    """Get orbis version."""
    try:
        return version("astronomer-orbis")
    except Exception:
        return "unknown"


@click.group()
@click.version_option(version=get_version(), prog_name="orbis")
@click.pass_context
def cli(ctx):
    ctx.max_content_width = 200
    if ctx.invoked_subcommand is None:
        click.echo("Orbis CLI")
        click.echo("\nAvailable commands:")
        click.echo("  compute-software  Generate deployment compute reports for Astronomer Software")
        click.echo("  scanner           Diagnostic information scanner for Astronomer Software")
        ctx.exit(0)


@cli.command(name="version")
def version_cmd():
    """Show orbis version."""
    click.echo(f"orbis, version {get_version()}")


@cli.group(name="scanner")
def scanner_group():
    """Diagnostic information scanner for Astronomer Software."""
    pass


@scanner_group.command(name="create")
@click.option("-a", "--namespace", required=True, help="Namespace where Astronomer is installed")
@click.option("--interactive", is_flag=True, help="Generate YAML only for manual application")
@click.option("--output-file", help="Save YAML to specified file")
@click.option("--cpu", default=CPU, help=f"CPU cores (default: {CPU})")
@click.option("--memory", default=MEMORY, help=f"Memory in GiB (default: {MEMORY})")
@click.option("--sleep", default=SLEEP_DURATION, help=f"Sleep time in seconds (default: {SLEEP_DURATION}, minimum: 3600)")
@click.option("--image", required=True, help="Docker image for the scanner pod (must be accessible by the cluster)")
@click.option("--cleanup/--no-cleanup", default=True, help="Clean up resources after completion")
@click.option("-d", "--domain", help="Specify the optional base domain for the cluster")
@click.option("-c", "--customer", help="Specify the customer name")
@click.option("-n", "--cluster", help="Specify the cluster name")
@click.option("--log-level", type=click.Choice(["warn", "info", "debug"], case_sensitive=False), default="info", help="Set the logging level (default: info)")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (use -v, -vv, or -vvv for more detailed logging)")
@click.option("--airflow-namespaces", multiple=True, help="Specify additional namespaces to include")
@click.option("--all-airflow-namespaces", is_flag=True, help="Collect data from all namespaces in the cluster")
@click.option("--telescope", is_flag=True, help="Enable telescope data collection")
@click.option("--telescope-executor", default="kubernetes", help="Specify the executor for telescope")
@click.option("--telescope-only", is_flag=True, help="Collect only telescope data and related helm info")
@click.option("--kubeconfig", help="Path to kubeconfig file")
@click.option("--poll-interval", default=10, help="Polling interval in seconds (default: 10)")
@click.option("--error-retry-interval", default=5, help="Error retry interval in seconds (default: 5)")
@click.option("--poll-timeout", default=3600, help="Overall polling timeout in seconds (default: 3600)")
def scanner_create(
    namespace,
    interactive,
    output_file,
    cpu,
    memory,
    sleep,
    image,
    cleanup,
    domain,
    customer,
    cluster,
    log_level,
    verbose,
    airflow_namespaces,
    all_airflow_namespaces,
    telescope,
    telescope_executor,
    telescope_only,
    kubeconfig,
    poll_interval,
    error_retry_interval,
    poll_timeout,
):
    """Create support bundle (directly or via YAML)."""
    # Compute verbose level and setup logging
    verbose_level = _compute_verbose_level(verbose, log_level)
    update_early_logger_level(verbose_level)
    scanner_logger = _init_scanner_logger(namespace, verbose_level)

    config = ScannerConfig(
        namespace=namespace,
        cpu=cpu,
        memory=memory,
        sleep_duration=sleep,
        image=image,
        cleanup=cleanup,
        domain=domain,
        customer_name=customer,
        cluster_name=cluster,
        log_level=log_level,
        additional_namespaces=list(airflow_namespaces),
        all_namespaces=all_airflow_namespaces,
        telescope_enabled=telescope,
        telescope_executor=telescope_executor,
        telescope_only=telescope_only,
        kubeconfig_path=kubeconfig,
        poll_interval=poll_interval,
        error_retry_interval=error_retry_interval,
        poll_timeout=poll_timeout,
    )

    service = ScannerService(config, scanner_logger)

    if interactive:
        # Generate YAML only
        result = service.generate_yaml(output_file)
        if result.success:
            click.echo("YAML generated successfully.")
            if output_file:
                click.echo(f"File saved to: {output_file}")
                click.echo("Share with your infrastructure team.")
                click.echo(f"After they apply it, retrieve data with: orbis scanner retrieve -a {namespace}")
        else:
            click.echo(f"Error: {result.error_message}")
            exit(1)
    else:
        # Execute directly and retrieve
        click.echo("Starting scanner in direct execution mode...")
        result = service.create_and_execute()
        if result.success:
            click.echo(f"Support bundle created successfully: {result.output_file}")
        else:
            click.echo(f"Error: {result.error_message}")
            exit(1)


@scanner_group.command(name="retrieve")
@click.option("-a", "--namespace", required=True, help="Namespace where Astronomer is installed")
@click.option("--pod-name", help="Specific pod name to retrieve from")
@click.option("--output-dir", default=".", help="Directory to save the retrieved data")
@click.option("--cleanup/--no-cleanup", default=True, help="Clean up resources after retrieving")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (use -v, -vv, or -vvv for more detailed logging)")
@click.option("--kubeconfig", help="Path to kubeconfig file")
def scanner_retrieve(namespace, pod_name, output_dir, cleanup, verbose, kubeconfig):
    """Retrieve data from a running scanner pod."""
    # Compute verbose level and setup logging
    verbose_level = _compute_verbose_level(verbose)
    update_early_logger_level(verbose_level)
    scanner_logger = _init_scanner_logger(namespace, verbose_level)

    config = ScannerConfig(namespace=namespace, image="", cleanup=cleanup, output_dir=output_dir, kubeconfig_path=kubeconfig)

    service = ScannerService(config, scanner_logger)
    result = service.retrieve_data(namespace, pod_name)

    if result.success:
        click.echo(f"Support bundle retrieved: {result.output_file}")
        if cleanup:
            cleanup_result = service.cleanup_resources(namespace)
            if cleanup_result.success:
                click.echo("Resources cleaned up successfully")
            else:
                click.echo(f"Cleanup warning: {cleanup_result.error_message}")
    else:
        click.echo(f"Error: {result.error_message}")
        exit(1)


@scanner_group.command(name="status")
@click.option("-a", "--namespace", required=True, help="Namespace where Astronomer is installed")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (use -v, -vv, or -vvv for more detailed logging)")
@click.option("--kubeconfig", help="Path to kubeconfig file")
def scanner_status(namespace, verbose, kubeconfig):
    """Check status of scanner job."""
    # Compute verbose level and setup logging
    verbose_level = _compute_verbose_level(verbose)
    update_early_logger_level(verbose_level)
    scanner_logger = _init_scanner_logger(namespace, verbose_level)

    config = ScannerConfig(namespace=namespace, image="", kubeconfig_path=kubeconfig)
    service = ScannerService(config, scanner_logger)
    status = service.check_status(namespace)

    click.echo("Scanner Status Report")
    click.echo("────────────────────────")
    click.echo(f"Job Name: {status.name}")
    click.echo(f"Namespace: {status.namespace}")
    click.echo(f"Pod Name: {status.pod_name or 'N/A'}")
    click.echo(f"Pod Status: {status.pod_status or 'N/A'}")
    click.echo(f"Active Jobs: {status.active}")
    click.echo(f"Succeeded: {status.succeeded}")
    click.echo(f"Failed: {status.failed}")
    click.echo(f"Data Ready: {'Yes' if status.ready else 'No'}")

    if status.start_time:
        click.echo(f"Started: {status.start_time}")
    if status.completion_time:
        click.echo(f"Completed: {status.completion_time}")


@scanner_group.command(name="clean")
@click.option("-a", "--namespace", required=True, help="Namespace where Astronomer is installed")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (use -v, -vv, or -vvv for more detailed logging)")
@click.option("--kubeconfig", help="Path to kubeconfig file")
@click.option("--dry-run", is_flag=True, help="Show kubectl commands that would be executed without running them")
def scanner_clean(namespace, verbose, kubeconfig, dry_run):
    """Clean up scanner resources."""
    # Compute verbose level and setup logging
    verbose_level = _compute_verbose_level(verbose)
    update_early_logger_level(verbose_level)
    scanner_logger = _init_scanner_logger(namespace, verbose_level)

    config = ScannerConfig(namespace=namespace, image="", kubeconfig_path=kubeconfig)
    service = ScannerService(config, scanner_logger)

    if dry_run:
        click.echo("The following kubectl commands would be executed:")
        click.echo(f"kubectl delete jobs -l component=scanner -n {namespace}")
        click.echo(f"kubectl delete pods -l component=scanner -n {namespace}")
        click.echo(f"kubectl delete serviceaccount temp-scanner-support-bundle -n {namespace}")
        click.echo("kubectl delete clusterrole read-support-bundle")
        click.echo("kubectl delete clusterrolebinding scanner-admin-access-binding")
        click.echo("\nTo execute these commands, run without --dry-run flag:")
        click.echo(f"orbis scanner clean -a {namespace}")
        return

    result = service.cleanup_resources(namespace)

    if result.success:
        click.echo("Resources cleaned up successfully")
    else:
        click.echo(f"Cleanup failed: {result.error_message}")
        exit(1)


@cli.command(name="compute-software")
@click.option("-s", "--start_date", required=True, help="Start Date. Format: YYYY-MM-DD")
@click.option("-e", "--end_date", required=True, help="End Date. Format: YYYY-MM-DD")
@click.option("-o", "--organization_id", required=False, help="Organization ID [Deprecated, Use base_domain or -b instead]")
@click.option("-b", "--base_domain", required=False, help="Base Domain")
@click.option("-v", "--verbose", count=True, help="Increase verbosity (use -v, -vv, or -vvv for more detailed logging)")
@click.option("-w", "--workspaces", default="", help="Comma-separated list of workspace IDs")
@click.option("-r", "--resume", is_flag=True, help="Resume from previous run")
@click.option("-z", "--compress", is_flag=True, help="Create compressed output of HTML, CSV, and JSON files")
@click.option("-p", "--persist", is_flag=True, help="Persist temporary generated images/files in the output folder")
@click.option("-u", "--url", default="", help="Pre-signed URL (in quotes) to upload report")
@click.option("--verify-ssl", default=True, type=bool, help="Disable SSL verification for requests")
@click.pass_context
def compute_software(ctx, start_date, end_date, organization_id, base_domain, verbose, workspaces, resume, compress, persist, url, clusters=False, verify_ssl=True):
    """Generate deployment compute reports for Astronomer Software."""
    generate_report_common(ctx, start_date, end_date, organization_id, base_domain, verbose, clusters, workspaces, resume, compress, persist, url, verify_ssl=verify_ssl)


def generate_report_common(ctx, start_date, end_date, organization_id, base_domain, verbose, clusters, workspaces, resume, compress, persist, url, verify_ssl=True) -> None:
    if not (start_date and end_date and (base_domain or organization_id)):
        click.echo("Error: start_date, end_date, and base_domain/organization_id(deprecated) are required.")
        ctx.exit(1)

    # Update early logger level based on verbosity
    update_early_logger_level(verbose)

    if organization_id and not base_domain:
        click.echo("Warning: organization_id/-o is deprecated. Use base_domain/-b instead.")
        base_domain = organization_id

    start_date = from_format(start_date, "YYYY-MM-DD")
    end_date = from_format(end_date, "YYYY-MM-DD")

    workspaces = [workspace for workspace in workspaces.strip().split(",") if workspace]
    display_input_arguments(start_date, end_date, base_domain, workspaces=workspaces)

    click.echo("Validating input arguments...")
    validate_input_args(base_domain, start_date, end_date)
    click.clear()

    generate_software_report(start_date, end_date, base_domain, verbose, workspaces, resume, compress, persist, url, verify_ssl=verify_ssl)


def generate_software_report(start_date, end_date, base_domain, verbose, workspaces, resume, compress, persist, url, verify_ssl=True) -> None:
    display_input_arguments(start_date, end_date, base_domain, workspaces=workspaces)
    try:
        organization_domain, namespaces, executor_types = houston.get_organization_metadata(base_domain=base_domain, workspaces=workspaces, verify_ssl=verify_ssl)
    except Exception as e:
        click.echo(e)
        click.echo("Error occurred while fetching organization metadata. Please verify Token and Base Domain.")
        return

    if not namespaces:
        click.echo("No deployments found for the given organization. Please verify Base Domain and Workspace IDs.")
        return

    click.echo(f"Output folder: {organization_domain}")
    output_folder = create_output_folder(organization_domain)

    logger = get_logger("root", f"{output_folder}/{organization_domain}.log", verbose)
    logger.info("Generating report for Organization Domain: %s", organization_domain)
    logger.info("Start Date: %s", start_date)
    logger.info("End Date: %s", end_date)
    logger.info("Workspaces: %s", workspaces)

    click.echo(f"Generating report for {len(namespaces)} deployments under Organization Domain: {organization_domain}")

    generate_report_with_progress(organization_domain, start_date, end_date, namespaces, executor_types, resume, compress, persist, url, verify_ssl=verify_ssl)


def generate_report_with_progress(organization_name, start_date, end_date, namespaces, executor_types, resume, compress, persist, url, verify_ssl=True) -> None:
    total_steps = calculate_total_steps(namespaces, executor_types)
    with click.progressbar(length=total_steps, label="Processing") as bar:

        def update_progress():
            bar.update(1)

        metadata = ReportMetadata(organization_name=organization_name, start_date=start_date.isoformat(), end_date=end_date.isoformat(), namespaces=namespaces)

        asyncio.run(generate_report(metadata, executor_types, progress_callback=update_progress, is_resume=resume, verify_ssl=verify_ssl))

    click.clear()
    display_input_arguments(start_date, end_date, organization_name)
    click.echo(f"Generating report for {len(namespaces)} deployments under Organization: {organization_name}")
    bar.update(total_steps)
    click.echo("\nReport generated successfully. Find report under the output folder.")

    if compress or url:
        compressed_zip_file = compress_output_files(organization_name)
        click.echo("Report compressed successfully.")
        if url:
            click.echo("Uploading report...")
            payload = {"package": ("orbis_reports.zip", open(compressed_zip_file, "rb"), "application/zip")}
            requests.put(url=url, files=payload, timeout=300)
            click.echo("Report uploaded successfully.")

    if not persist:
        perform_cleanup(create_output_folder(organization_name), namespaces)


def calculate_total_steps(namespaces, executor_types) -> int:
    total_steps = 0

    # Parse the YAML queries file
    queries_file_path = SOFTWARE_QUERIES_FILE_PATH
    parsed_yaml_queries = parse_yaml(file_name=queries_file_path)

    # Count scheduler metrics (common for all)
    scheduler_metrics = len(parsed_yaml_queries.get("scheduler", {}))

    # Count non-reporting metrics
    non_reporting_metrics = sum(1 for key in ["total_task_success", "total_task_failure"] if key in parsed_yaml_queries)

    # Count executor-specific metrics
    ke_metrics = len(parsed_yaml_queries.get("ke", {}))
    celery_metrics = len(parsed_yaml_queries.get("celery", {}))

    for namespace in namespaces:
        executor = executor_types[namespace].executor
        if executor.lower() == "kubernetes":
            # Add KE metrics and scheduler metrics
            total_steps += ke_metrics + scheduler_metrics + non_reporting_metrics
        elif executor.lower() == "celery":
            # Add Celery metrics and scheduler metrics
            total_steps += celery_metrics + scheduler_metrics + non_reporting_metrics

    return total_steps


if __name__ == "__main__":
    cli()
