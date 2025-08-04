from langchain.tools import tool
import os
from pathlib import Path
import re


class FileTools():

  @tool("Write File with content")
  def write_file(data):
    """Useful to write a file to a given path with a given content. 
       The input to this tool should be a pipe (|) separated text 
       of length two, representing the full path of the file, 
       including the /workdir/template, and the React 
       Component code content you want to write to it.
       For example, `./Keynote/src/components/Hero.jsx|REACT_COMPONENT_CODE_PLACEHOLDER`.
       Replace REACT_COMPONENT_CODE_PLACEHOLDER with the actual 
       code you want to write to the file."""
    try:
      # Split the input data
      if "|" not in data:
        return "Error: Input must contain a pipe (|) separator between path and content."
      
      path, content = data.split("|", 1)  # Split only on first pipe
      
      # Clean and validate the path
      path = path.strip().replace("\n", "").replace(" ", "").replace("`", "")
      
      # Validate path contains only safe characters
      if not re.match(r'^[a-zA-Z0-9._/\-]+$', path):
        return "Error: Path contains invalid characters. Only alphanumeric, dots, slashes, and hyphens are allowed."
      
      # Establish the safe working directory
      workdir = Path("./workdir").resolve()
      
      # Handle path normalization
      if path.startswith("./workdir/"):
        # Remove the ./workdir/ prefix to get relative path
        relative_path = path[10:]
      elif path.startswith("./"):
        # Remove ./ prefix
        relative_path = path[2:]
      elif path.startswith("/"):
        return "Error: Absolute paths are not allowed."
      else:
        relative_path = path
      
      # Validate the relative path doesn't contain traversal attempts
      if ".." in relative_path or relative_path.startswith("/"):
        return "Error: Path traversal detected. Relative paths with '..' are not allowed."
      
      # Create the full safe path
      target_path = workdir / relative_path
      
      # Resolve the path and ensure it's still within workdir
      try:
        resolved_path = target_path.resolve()
        if not str(resolved_path).startswith(str(workdir)):
          return "Error: Path resolves outside of allowed working directory."
      except Exception:
        return "Error: Invalid path resolution."
      
      # Validate file extension (security: prevent writing to system files)
      allowed_extensions = {'.jsx', '.js', '.tsx', '.ts', '.css', '.scss', '.html', '.json', '.md', '.txt', '.yaml', '.yml'}
      if resolved_path.suffix.lower() not in allowed_extensions:
        return f"Error: File extension '{resolved_path.suffix}' not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
      
      # Create parent directories if they don't exist
      resolved_path.parent.mkdir(parents=True, exist_ok=True)
      
      # Write the file
      with open(resolved_path, "w", encoding="utf-8") as f:
        f.write(content)
      
      return f"File written to {resolved_path}."
      
    except ValueError as e:
      return f"Error: {str(e)}"
    except PermissionError:
      return "Error: Permission denied. Cannot write to the specified path."
    except Exception as e:
      return f"Error: {str(e)}"
