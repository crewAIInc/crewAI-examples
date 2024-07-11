import os
import sys
from langchain.tools import tool
from pymarkdown.api import PyMarkdownApi, PyMarkdownApiException

@tool("markdown_validation_tool")
def markdown_validation_tool(file_path: str) -> str:
    """
    A tool to review files for markdown syntax errors.

    Parameters:
    - file_path: The path to the markdown file to be reviewed.

    Returns:
    - validation_results: A list of validation results 
    and suggestions on how to fix them.
    """
    
    print("\n\nValidating Markdown syntax...\n\n" + file_path)

    scan_result = None
    try:
        if not (os.path.exists(file_path)):
           return "Could not validate file. The provided file path does not exist."

        scan_result = PyMarkdownApi().scan_path(file_path.rstrip().lstrip())
        results = str(scan_result)    
        return results  # Return the reviewed document
    except PyMarkdownApiException as this_exception:
        print(f"API Exception: {this_exception}", file=sys.stderr)
        return f"API Exception: {str(this_exception)}"
  