"""Query validation utilities for Orbis."""

from orbis.report.metrics.query_types import QueryType


def validate_query_formatting(query: str, query_type: QueryType) -> tuple[bool, str]:  # noqa: C901
    """Validate that all required placeholders in a query are properly formatted.

    Args:
        query: The query string to validate
        query_type: Type of the query from QueryType enum

    Returns:
        tuple[bool, str]: (is_valid, error_message)

    Examples:
        >>> validate_query_formatting('rate(container_cpu{{namespace="{namespace}"}}[5m])', QueryType.SIMPLE)
        (True, '')
        >>> validate_query_formatting('sum(...{condition})', QueryType.CONDITIONAL)
        (True, '')
    """
    # All queries must have {namespace} placeholder
    if not ("{namespace}" in query or "{release_name}" in query):
        return False, "Missing {namespace} or {release_name} placeholder"

    # Validate based on query type
    if query_type in [QueryType.CONDITIONAL, QueryType.OR_CONDITIONAL]:
        if not any(cond in query for cond in ["{cpu_condition}", "{memory_condition}"]):
            return False, "Missing condition placeholder for conditional query"

    # Valid placeholders that can use single braces
    valid_placeholders = ["{namespace}", "{release_name}", "{cpu_condition}", "{memory_condition}", "{bitwise_condition}"]

    # Track parentheses and braces
    open_parens = 0
    open_braces = 0

    i = 0
    while i < len(query):
        # Track parentheses for complete query structure
        if query[i] == "(":
            open_parens += 1
        elif query[i] == ")":
            open_parens -= 1
            if open_parens < 0:
                return False, "Found unmatched closing parenthesis"

        # Check for opening double braces
        if i + 1 < len(query) and query[i : i + 2] == "{{":
            open_braces += 1
            # Find matching closing braces
            closing = query.find("}}", i)
            if closing == -1:
                return False, "Found unmatched opening braces"

            # Only validate label format inside double braces
            label_content = query[i + 2 : closing]
            for label in label_content.split(","):
                label = label.strip()
                if not label:
                    continue
                if not any(op in label for op in ["=", "!=", "=~", "!~"]):
                    return False, "Found unescaped curly braces"

            i = closing + 2
            open_braces -= 1
            continue

        # Check for single braces
        if query[i] == "{":
            # Must be a valid placeholder
            is_valid = False
            for placeholder in valid_placeholders:
                if query[i:].startswith(placeholder):
                    is_valid = True
                    i += len(placeholder)
                    break
            if not is_valid:
                return False, "Found unescaped curly braces"
            continue

        # Check for unmatched closing braces
        if query[i] == "}":
            return False, "Found unmatched closing brace"

        i += 1

    # Check for incomplete structure
    if open_braces > 0 or open_parens > 0:
        return False, "Found unmatched opening braces"

    return True, ""
