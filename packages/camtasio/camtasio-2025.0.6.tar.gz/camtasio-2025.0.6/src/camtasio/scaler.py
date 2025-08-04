# this_file: src/camtasio/scaler.py
"""Core scaling functionality for Camtasia .tscproj files."""

from pathlib import Path
from typing import Any, ClassVar

from loguru import logger

from .serialization import load_json_file, save_json_file


class TscprojScaler:
    """Handles scaling of Camtasia project files."""

    # Properties that should be scaled
    SCALE_PROPERTIES: ClassVar[set[str]] = {
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

    # Properties containing 'scale' that should be multiplied by the factor
    MULTIPLY_SCALE_PROPERTIES: ClassVar[set[str]] = {"scale0", "scale1", "scale2"}

    # Special array properties that contain dimensions
    DIMENSION_ARRAYS: ClassVar[set[str]] = {"rect", "trackRect"}

    def __init__(self, scale_factor: float, verbose: bool = False):
        """Initialize the scaler with a scale factor.

        Args:
            scale_factor: The scaling factor (e.g., 1.5 for 150%)
            verbose: Enable verbose logging
        """
        self.scale_factor = scale_factor
        self.verbose = verbose
        if verbose:
            logger.enable("tscprojpy")
        else:
            logger.disable("tscprojpy")

    def scale_file(self, input_path: str | Path, output_path: str | Path) -> None:
        """Scale a .tscproj file and save the result.

        Args:
            input_path: Path to the input .tscproj file
            output_path: Path to save the scaled .tscproj file
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        logger.info(f"Loading project from {input_path}")

        # Load the JSON data
        data = load_json_file(input_path)

        logger.info(f"Scaling by factor {self.scale_factor}")

        # Scale the data
        scaled_data = self._scale_object(data)

        # Save the scaled data
        logger.info(f"Saving scaled project to {output_path}")
        save_json_file(scaled_data, output_path, indent=2, ensure_ascii=False)

        logger.success(f"Successfully scaled project by {self.scale_factor}x")

    def _scale_object(self, obj: Any, path: str = "") -> Any:
        """Recursively scale an object.

        Args:
            obj: The object to scale (dict, list, or primitive)
            path: Current path in the object hierarchy (for logging)

        Returns:
            The scaled object
        """
        if isinstance(obj, dict):
            return self._scale_dict(obj, path)
        elif isinstance(obj, list):
            return self._scale_list(obj, path)
        else:
            return obj

    def _scale_dict(self, d: dict, path: str) -> dict:
        """Scale a dictionary object.

        Args:
            d: Dictionary to scale
            path: Current path for logging

        Returns:
            Scaled dictionary
        """
        result = {}

        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key

            # Check if this is a special def object with dimensions
            if key == "def" and isinstance(value, dict):
                result[key] = self._scale_def_object(value, current_path)
            # Check if this is a dimension array
            elif key in self.DIMENSION_ARRAYS and isinstance(value, list):
                result[key] = self._scale_dimension_array(value, current_path)
            # Check if this is a scalable property
            elif key in self.SCALE_PROPERTIES and isinstance(value, int | float):
                result[key] = self._scale_value(key, value, current_path)
            # Check for keyframes that might contain scalable values
            elif key == "keyframes" and isinstance(value, list):
                result[key] = self._scale_keyframes(value, current_path)
            # Check for default dimension properties in metadata
            elif key.startswith("default-") and any(
                prop in key for prop in ["width", "height", "scale", "translation"]
            ):
                if isinstance(value, dict) and "value" in value:
                    scaled_dict = value.copy()
                    prop_name = key.replace("default-", "")
                    if prop_name in self.SCALE_PROPERTIES:
                        scaled_dict["value"] = self._scale_value(
                            prop_name, value["value"], current_path
                        )
                        result[key] = scaled_dict
                    else:
                        result[key] = value
                else:
                    result[key] = value
            else:
                # Recursively process nested objects
                result[key] = self._scale_object(value, current_path)

        return result

    def _scale_list(self, lst: list, path: str) -> list:
        """Scale a list object.

        Args:
            lst: List to scale
            path: Current path for logging

        Returns:
            Scaled list
        """
        return [self._scale_object(item, f"{path}[{i}]") for i, item in enumerate(lst)]

    def _scale_value(self, property_name: str, value: int | float, path: str) -> int | float:
        """Scale a single numeric value based on property type.

        Args:
            property_name: Name of the property being scaled
            value: The numeric value to scale
            path: Current path for logging

        Returns:
            Scaled value
        """
        if property_name in self.MULTIPLY_SCALE_PROPERTIES:
            # For scale properties, multiply the existing scale
            scaled = value * self.scale_factor
            logger.debug(f"Scaling {path}: {value} * {self.scale_factor} = {scaled}")
        else:
            # For dimension properties, apply the scale factor directly
            scaled = value * self.scale_factor
            logger.debug(f"Scaling {path}: {value} -> {scaled}")

        return scaled

    def _scale_dimension_array(self, arr: list, path: str) -> list:
        """Scale a dimension array like rect or trackRect.

        Args:
            arr: Array to scale [x, y, width, height]
            path: Current path for logging

        Returns:
            Scaled array
        """
        if len(arr) == 4:
            # Scale all four values (x, y, width, height)
            scaled = [v * self.scale_factor if isinstance(v, int | float) else v for v in arr]
            logger.debug(f"Scaling array {path}: {arr} -> {scaled}")
            return scaled
        else:
            logger.warning(f"Unexpected array length at {path}: {len(arr)}")
            return arr

    def _scale_def_object(self, def_obj: dict, path: str) -> dict:
        """Scale a definition object (like callout definitions).

        Args:
            def_obj: Definition object to scale
            path: Current path for logging

        Returns:
            Scaled definition object
        """
        result = def_obj.copy()

        # Scale specific properties in def objects
        for prop in ["width", "height", "corner-radius", "stroke-width"]:
            if prop in result and isinstance(result[prop], int | float):
                result[prop] = result[prop] * self.scale_factor
                logger.debug(f"Scaling {path}.{prop}: {def_obj[prop]} -> {result[prop]}")

        return result

    def _scale_keyframes(self, keyframes: list, path: str) -> list:
        """Scale keyframe values if they contain scalable properties.

        Args:
            keyframes: List of keyframe objects
            path: Current path for logging

        Returns:
            List of scaled keyframe objects
        """
        result = []

        for i, keyframe in enumerate(keyframes):
            if isinstance(keyframe, dict):
                scaled_keyframe = keyframe.copy()

                # Check if the keyframe has a value that should be scaled
                if "value" in scaled_keyframe and isinstance(scaled_keyframe["value"], int | float):
                    # Determine if this keyframe is for a scalable property
                    # by checking the parent path
                    parent_prop = path.split(".")[-2] if "." in path else ""

                    if parent_prop in self.SCALE_PROPERTIES:
                        scaled_keyframe["value"] = self._scale_value(
                            parent_prop, keyframe["value"], f"{path}[{i}].value"
                        )

                result.append(scaled_keyframe)
            else:
                result.append(keyframe)

        return result
