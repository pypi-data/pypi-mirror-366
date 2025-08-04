# this_file: src/camtasio/serialization/loader.py
"""Project loader for deserializing Camtasia projects."""

from pathlib import Path
from typing import Any

from loguru import logger

from ..models import Project
from .json_handler import load_json_file
from .version import is_supported_version


class ProjectLoader:
    """Loads and deserializes Camtasia project files."""

    def __init__(self, strict_version_check: bool = False):
        """Initialize loader.

        Args:
            strict_version_check: If True, fail on unsupported versions
        """
        self.strict_version_check = strict_version_check

    def load_file(self, file_path: str | Path) -> Project:
        """Load project from file.

        Args:
            file_path: Path to .tscproj file

        Returns:
            Loaded Project instance

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
            ValueError: If version is unsupported and strict checking is enabled
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Project file not found: {path}")

        logger.info(f"Loading project from: {path}")

        # Load JSON data using centralized handler
        data = load_json_file(path)

        return self.load_dict(data)

    def load_dict(self, data: dict[str, Any]) -> Project:
        """Load project from dictionary.

        Args:
            data: Project dictionary data

        Returns:
            Loaded Project instance

        Raises:
            ValueError: If version is unsupported and strict checking is enabled
        """
        # Validate structure first
        validation_errors = self.validate_structure(data)
        if validation_errors:
            logger.warning(f"Project structure validation issues: {validation_errors}")
            if self.strict_version_check:
                raise ValueError(f"Invalid project structure: {'; '.join(validation_errors)}")

        # Check version compatibility
        if not is_supported_version(data):
            if self.strict_version_check:
                raise ValueError(f"Unsupported project version: {data.get('version', 'unknown')}")
            else:
                logger.warning("Loading unsupported version - some features may not work correctly")

        # Create project from dictionary
        try:
            project = Project.from_dict(data)
            logger.info(f"Successfully loaded project (version {project.version})")
            return project
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            raise

    def validate_structure(self, data: dict) -> list[str]:
        """Validate project structure and return any issues.

        Args:
            data: Project dictionary data

        Returns:
            List of validation error messages
        """
        errors = []

        # Check if data is a dict
        if not isinstance(data, dict):
            errors.append(f"Project data must be a dictionary, got {type(data).__name__}")
            return errors

        # Check critical fields for newer versions
        version = data.get("version", "unknown")
        if version in ["9.0", "4.0"]:
            # These versions require specific fields
            required_fields = ["version", "editRate", "width", "height"]
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field for version {version}: {field}")

        # Check sourceBin structure if present
        if "sourceBin" in data:
            if not isinstance(data["sourceBin"], list):
                errors.append("sourceBin must be a list")
            else:
                for i, item in enumerate(data["sourceBin"]):
                    if not isinstance(item, dict):
                        errors.append(f"sourceBin[{i}] must be a dictionary")
                    elif "id" not in item:
                        errors.append(f"sourceBin[{i}] missing 'id' field")

        # Check timeline structure if present
        if "timeline" in data:
            timeline = data["timeline"]
            if not isinstance(timeline, dict):
                errors.append("timeline must be a dictionary")

        return errors
