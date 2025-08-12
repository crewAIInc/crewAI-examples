import os
from langchain.tools import tool
from pymarkdown.api import PyMarkdownApi, PyMarkdownApiException


@tool("markdown_validation_tool")
def markdown_validation_tool(file_path: str) -> str:
    """
    A tool to review files for markdown syntax errors.

    Parameters:
    - file_path: The path to the markdown file to be reviewed.

    Returns:
    - validation_results: A formatted string of validation results or summary.
    """

    try:
        if not os.path.exists(file_path):
            return "Error: The provided file path does not exist."

        # Perform the markdown scan

        scan_result = PyMarkdownApi().scan_path(file_path.strip())

        # Always return formatted scan results
        return format_scan_result(scan_result)

    except PyMarkdownApiException as this_exception:
        return f"API Exception: {str(this_exception)}"


def format_scan_result(scan_result) -> str:
    """
    Format the PyMarkdownApi scan result.

    Parameters:
    - scan_result: The result from the PyMarkdownApi scan.

    Returns:
    - A formatted string summarizing the issues found or a simple success message.
    """
    if not scan_result.scan_failures:
        return "No markdown validation issues found."

    # Format only essential information
    output = []
    for failure in scan_result.scan_failures:
        output.append(
            f"File: {failure.scan_file}, Line: {failure.line_number}, "
            f"Rule: {failure.rule_id} ({failure.rule_name}) - {failure.rule_description}"
        )

    return "\n".join(output)
