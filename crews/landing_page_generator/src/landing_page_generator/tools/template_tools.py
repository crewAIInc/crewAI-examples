import json
import shutil
import re
from pathlib import Path

from langchain.tools import tool


class TemplateTools():

  @tool("Learn landing page options")
  def learn_landing_page_options(input):
    """Learn the templates at your disposal"""
    try:
      # Safely read the templates configuration file
      config_path = Path("config/templates.json").resolve()
      
      # Validate the config file exists and is readable
      if not config_path.exists():
        return "Error: Templates configuration file not found."
      
      # Check if the path is within expected boundaries
      if not str(config_path).endswith("config/templates.json"):
        return "Error: Invalid configuration file path."
      
      with open(config_path, "r", encoding="utf-8") as f:
        templates = json.load(f)
      
      return json.dumps(templates, indent=2)
    except Exception as e:
      return f"Error reading templates configuration: {str(e)}"

  @tool("Copy landing page template to project folder")
  def copy_landing_page_template_to_project_folder(landing_page_template):
    """Copy a landing page template to your project 
    folder so you can start modifying it, it expects 
    a landing page template folder as input"""
    try:
      # Validate input
      if not isinstance(landing_page_template, str):
        return "Error: Template name must be a string."
      
      # Clean and validate template name
      template_name = landing_page_template.strip()
      
      # Validate template name contains only safe characters
      if not re.match(r'^[a-zA-Z0-9_\-]+$', template_name):
        return "Error: Template name contains invalid characters. Only alphanumeric, underscore, and hyphen are allowed."
      
      # Prevent path traversal
      if ".." in template_name or "/" in template_name or "\\" in template_name:
        return "Error: Template name cannot contain path traversal characters."
      
      # Establish safe base directories
      templates_base = Path("templates").resolve()
      workdir_base = Path("workdir").resolve()
      
      # Create source and destination paths
      source_path = templates_base / template_name
      destination_path = workdir_base / template_name
      
      # Resolve paths and validate they're within expected directories
      source_resolved = source_path.resolve()
      destination_resolved = destination_path.resolve()
      
      # Ensure source is within templates directory
      if not str(source_resolved).startswith(str(templates_base)):
        return "Error: Source template path is outside allowed templates directory."
      
      # Ensure destination is within workdir
      if not str(destination_resolved).startswith(str(workdir_base)):
        return "Error: Destination path is outside allowed working directory."
      
      # Check if source template exists
      if not source_resolved.exists():
        return f"Error: Template '{template_name}' does not exist in templates directory."
      
      # Check if source is a directory
      if not source_resolved.is_dir():
        return f"Error: Template '{template_name}' is not a directory."
      
      # Check if destination already exists
      if destination_resolved.exists():
        return f"Error: Destination '{template_name}' already exists in workdir. Please choose a different name or remove the existing directory."
      
      # Create parent directories if needed
      destination_resolved.parent.mkdir(parents=True, exist_ok=True)
      
      # Copy the template
      shutil.copytree(source_resolved, destination_resolved)
      
      return f"Template '{template_name}' copied successfully to workdir and ready to be modified. Main files should be under ./{template_name}/src/components, you should focus on those."
      
    except PermissionError:
      return "Error: Permission denied. Cannot copy template to destination."
    except Exception as e:
      return f"Error copying template: {str(e)}"
