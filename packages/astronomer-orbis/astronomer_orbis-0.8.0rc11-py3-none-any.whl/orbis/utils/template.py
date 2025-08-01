"""Utility helpers for working with Jinja2 templates stored on disk."""

from pathlib import Path
from typing import Any

from jinja2 import Template


def render_template(template_path: str | Path, context: dict[str, Any]) -> str:
    """Load a Jinja2 template from *template_path* and render it with *context*.

    Args:
        template_path: File system path to the Jinja2 template.
        context:       Dictionary with template variables.

    Returns:
        Rendered template as a string.
    """
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")

    template_text = path.read_text(encoding="utf-8")
    template = Template(template_text)
    return template.render(**context)
