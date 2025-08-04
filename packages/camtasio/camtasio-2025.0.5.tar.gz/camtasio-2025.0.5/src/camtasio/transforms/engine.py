# this_file: src/camtasio/transforms/engine.py
"""Transform engine for applying transformations to Camtasia projects."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from loguru import logger

from ..models import Project


class TransformType(Enum):
    """Types of transformations that can be applied."""

    SPATIAL = auto()  # Scale positions, sizes, dimensions
    TEMPORAL = auto()  # Scale time, duration, speed


@dataclass
class TransformConfig:
    """Configuration for a transformation operation."""

    transform_type: TransformType
    factor: float
    preserve_audio_duration: bool = True  # For temporal transforms
    verbose: bool = False


class PropertyTransformer:
    """Engine for transforming project properties."""

    def __init__(self, config: TransformConfig):
        """Initialize transformer with configuration.

        Args:
            config: Transform configuration
        """
        self.config = config

    def transform_project(self, project: Project) -> Project:
        """Apply transformation to a project.

        Args:
            project: The project to transform

        Returns:
            New transformed project instance
        """
        if self.config.verbose:
            logger.info(
                f"Applying {self.config.transform_type.name} transform with factor {self.config.factor}"
            )

        if self.config.transform_type == TransformType.SPATIAL:
            return self._transform_spatial(project)
        elif self.config.transform_type == TransformType.TEMPORAL:
            return self._transform_temporal(project)
        else:
            raise ValueError(f"Unknown transform type: {self.config.transform_type}")

    def _transform_spatial(self, project: Project) -> Project:
        """Apply spatial transformation.

        Args:
            project: The project to transform

        Returns:
            New spatially scaled project
        """
        logger.info(f"Scaling project spatially by {self.config.factor}x")

        # Use the project's built-in spatial scaling
        return project.scale_spatial(self.config.factor)

    def _transform_temporal(self, project: Project) -> Project:
        """Apply temporal transformation.

        Args:
            project: The project to transform

        Returns:
            New temporally scaled project
        """
        logger.info(f"Scaling project temporally by {self.config.factor}x")

        if self.config.preserve_audio_duration:
            logger.info("Audio duration will be preserved")

        # Use the project's built-in temporal scaling
        # The Media models already handle audio preservation
        return project.scale_temporal(self.config.factor)

    def transform_dict(self, data: dict) -> dict:
        """Apply transformation to raw dictionary data.

        This is for direct JSON manipulation without domain models.

        Args:
            data: Project dictionary data

        Returns:
            Transformed dictionary
        """
        if self.config.transform_type == TransformType.SPATIAL:
            return self._transform_dict_spatial(data)
        elif self.config.transform_type == TransformType.TEMPORAL:
            return self._transform_dict_temporal(data)
        else:
            raise ValueError(f"Unknown transform type: {self.config.transform_type}")

    def _transform_dict_spatial(self, data: dict) -> dict:
        """Apply spatial transformation to dictionary.

        Args:
            data: Project dictionary

        Returns:
            Spatially transformed dictionary
        """
        # Define properties to scale
        scale_properties = {
            "width",
            "height",
            "translation0",
            "translation1",
            "translation2",
            "scale0",
            "scale1",
            "scale2",
            "geometryCrop0",
            "geometryCrop1",
            "geometryCrop2",
            "geometryCrop3",
            "corner-radius",
            "stroke-width",
            "widthAttr",
            "heightAttr",
        }

        def scale_value(key: str, value: Any) -> Any:
            """Scale a single value if it's a scalable property."""
            if key in scale_properties and isinstance(value, int | float):
                return value * self.config.factor
            return value

        def transform_dict_recursive(obj: Any, parent_key: str | None = None) -> Any:
            """Recursively transform dictionary values."""
            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    if key == "rect" and isinstance(value, list) and len(value) == 4:
                        # Scale rect arrays [x, y, width, height]
                        result[key] = [v * self.config.factor for v in value]
                    elif key == "trackRect" and isinstance(value, list) and len(value) == 4:
                        # Scale trackRect arrays
                        result[key] = [v * self.config.factor for v in value]
                    elif key == "keyframes" and isinstance(value, list):
                        # Handle keyframes specially
                        result[key] = []
                        for kf in value:
                            new_kf = kf.copy() if isinstance(kf, dict) else kf
                            if isinstance(new_kf, dict) and "value" in new_kf:
                                # Scale the value if parent is a spatial property
                                if parent_key in scale_properties:
                                    new_kf["value"] = new_kf["value"] * self.config.factor
                            result[key].append(new_kf)
                    elif isinstance(value, dict | list):
                        result[key] = transform_dict_recursive(value, key)
                    else:
                        result[key] = scale_value(key, value)
                return result
            elif isinstance(obj, list):
                return [transform_dict_recursive(item, parent_key) for item in obj]
            else:
                return obj

        return transform_dict_recursive(data)

    def _transform_dict_temporal(self, data: dict) -> dict:
        """Apply temporal transformation to dictionary.

        Args:
            data: Project dictionary

        Returns:
            Temporally transformed dictionary
        """
        # Define temporal properties to scale
        time_properties = {
            "start",
            "duration",
            "mediaStart",
            "mediaDuration",
            "trimStartSum",
            "time",
            "endTime",
        }

        def should_scale_temporal(parent_type: str, key: str) -> bool:
            """Determine if a temporal property should be scaled."""
            if key not in time_properties:
                return False

            # Don't scale audio duration if preserving
            if self.config.preserve_audio_duration and parent_type == "AMFile":
                if key in {"duration", "mediaStart", "mediaDuration"}:
                    return False

            return True

        def transform_dict_recursive(obj: Any, parent_type: str | None = None) -> Any:
            """Recursively transform dictionary values."""
            if isinstance(obj, dict):
                result = {}
                current_type = obj.get("_type", parent_type)

                for key, value in obj.items():
                    if key == "range" and isinstance(value, list) and len(value) == 2:
                        # Scale time ranges [start, end]
                        result[key] = [int(v * self.config.factor) for v in value]
                    elif should_scale_temporal(current_type, key) and isinstance(
                        value, int | float
                    ):
                        result[key] = int(value * self.config.factor)
                    elif isinstance(value, dict | list):
                        result[key] = transform_dict_recursive(value, current_type)
                    else:
                        result[key] = value
                return result
            elif isinstance(obj, list):
                return [transform_dict_recursive(item, parent_type) for item in obj]
            else:
                return obj

        return transform_dict_recursive(data)
