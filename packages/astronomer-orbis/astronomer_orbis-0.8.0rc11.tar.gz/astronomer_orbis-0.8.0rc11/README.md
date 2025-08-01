# Orbis
<div style="text-align:center">
   <img src="docs/assets/orbis_logo.svg" width="50%" alt="Orbis Logo">
</div>

Orbis is a deployment compute report generator tool developed by RDC Team. It analyzes data from Prometheus to provide insights into deployment metrics and resource utilization for Astronomer Software platforms.

## Docs

- Internal Docs : https://potential-waffle-pl91nlj.pages.github.io/
- External Docs : https://astronomer.github.io/orbis-docs/

## Features

- Generates comprehensive deployment compute reports
- Analyzes CPU, memory, and pod count metrics
- Supports both Kubernetes and Celery executors
- Creates visualizations for easy data interpretation
- Exports reports in DOCX, JSON, and CSV formats
- Supports resume functionality for interrupted report generation
- Diagnostic scanner for collecting cluster information

## Flow Diagram
![Alt text](docs/assets/flow_diagram.png)

## Installation

To install Orbis, follow these steps:

1. Download the distributions from [Releases](https://github.com/astronomer/orbis/releases)

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the package:
   ```
   pip install orbis-0.4.0-py3-none-any.whl
   ```

## Docker Build

You can also run Orbis using Docker. Here's how:

1. Build the Docker image:
   ```bash
   docker build -t orbis-tool .
   ```

2. Run Orbis using Docker:
   ```bash
   # Run interactive shell
   docker run -it orbis-tool bash

   # Run Orbis command directly (example)
   docker run --rm -it \
     --env-file .env \
     -v $(pwd)/output:/app/output \
     orbis-tool orbis compute-software \
     -s <start-date> \
     -e <end-date> \
     -o <organization>
   ```

   Replace `<start-date>`, `<end-date>`, and `<organization>` with your desired values.

   Note: Make sure to:
   - Create a `.env` file with required environment variables
   - Mount the output directory to persist the generated reports

## Configuration

Before running Orbis, Generate a System Admin Level API Token and add it to the `.env` file as `ASTRO_SOFTWARE_API_TOKEN=<GENERATED_TOKEN>`.

## Usage

**NOTE**: The `sizing` subcommand is now deprecated and will be removed in future versions.


To generate a deployment compute report for Astronomer Software, use the following command:

```
orbis compute-software -s START_DATE -e END_DATE -o ORGANIZATION_ID [-v] [-w Workspaces] [-z] [-r] [-p] [-u]
```

Arguments:
- `-s, --start_date`: Start date for the report (format: YYYY-MM-DD)
- `-e, --end_date`: End date for the report (format: YYYY-MM-DD)
- `-o, --organization_id`: BASEDOMAIN
- `-v, --verbose`: Enable verbose logging (optional)
- `-c, --clusters`: Comma-separated list of cluster IDs (for Astro, optional)
- `-w, --workspaces`: Comma-separated list of Workspace IDs (for Software, optional)
- `-z, --compress`: Compress the output reports (optional)
- `-r, --resume`: Resume report generation from the last saved state (optional)
- `-p, --persist`: Persist temporary files in output folder (optional)
- `-u, --url`: Pre-signed (in quotes) URL to upload report (for Software, optional)

Example:
```
orbis compute-software -s 2023-01-01 -e 2023-01-31 -o your-organization-domain.com
```

### Scanner

The scanner functionality allows you to collect diagnostic information from Kubernetes clusters:

```
orbis scanner create -a NAMESPACE --image quay.io/astronomer/orbis-scanner:latest [OPTIONS]
```

Key commands:
- `orbis scanner create`: Create and run diagnostic scanner
- `orbis scanner retrieve`: Retrieve data from existing scanner pod
- `orbis scanner status`: Check scanner job status
- `orbis scanner clean`: Clean up scanner resources

See `scanner-image/` directory for container image definition.

## Output

Orbis generates:

1. A comprehensive deployment compute report in DOCX format
2. A JSON report for automation purposes
3. A CSV report for automation purposes

## Development

To set up the development environment:

1. Clone the repository

2. Install development dependencies:
   ```
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```
   pre-commit install
   ```

4. Run tests:
   ```
   pytest tests/
   ```

### Debugging

Create a `.vscode` folder and add `launch.json` file with the following contents:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Orbis",
            "type": "debugpy",
            "request": "launch",
            "module": "orbis.cli",
            "console": "integratedTerminal",
            "args": [
                "sizing",
                "-o",
                "<org_id>",
                "-s",
                "2024-07-03",
                "-e",
                "2024-07-04"
            ]
        }
    ]
}
```

### Using pre-commit

Pre-commit is used to maintain code quality. Here's how to use it:

1. Run pre-commit on all files:
   ```
   pre-commit run --all-files
   ```

2. Run pre-commit on staged files:
   ```
   pre-commit run
   ```

3. Run a specific hook:
   ```
   pre-commit run <hook_id>
   ```
   Replace `<hook_id>` with the ID of the specific hook you want to run (e.g., `ruff`).

4. To bypass pre-commit hooks when committing:
   ```
   git commit -m "Your commit message" --no-verify
   ```

Pre-commit will run automatically before each commit once the hooks are installed.
