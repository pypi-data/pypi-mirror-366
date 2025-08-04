# this_file: src/camtasio/serialization/version.py
"""Version detection and compatibility for Camtasia projects."""

from enum import Enum
from typing import Any

from loguru import logger


class ProjectVersion(Enum):
    """Known Camtasia project versions."""

    V4_0 = "4.0"  # Camtasia 2020
    V9_0 = "9.0"  # Camtasia 2021+
    V3_0 = "3.0"  # Camtasia 2019
    V2_0 = "2.0"  # Camtasia 2018
    V1_0 = "1.0"  # Camtasia 9 and earlier
    UNKNOWN = "unknown"

    @property
    def edit_rate(self) -> int:
        """Get the default edit rate for this version."""
        if self == ProjectVersion.V4_0:
            return 60  # 60 ticks/second
        elif self == ProjectVersion.V9_0:
            return 705600000  # High precision timing
        else:
            return 60  # Default to old rate

    @property
    def is_supported(self) -> bool:
        """Check if this version is supported."""
        return self in {ProjectVersion.V4_0, ProjectVersion.V9_0}

    @property
    def is_legacy(self) -> bool:
        """Check if this is a legacy version (pre-2020)."""
        return self in {ProjectVersion.V3_0, ProjectVersion.V2_0, ProjectVersion.V1_0}


def detect_version(data: dict[str, Any]) -> ProjectVersion:
    """Detect project version from data.

    Args:
        data: Project dictionary data

    Returns:
        Detected project version
    """
    version_str = data.get("version", "")

    # Try to match known versions
    for version in ProjectVersion:
        if version.value == version_str:
            logger.info(f"Detected project version: {version.value}")
            return version

    # Log warning for unknown version
    logger.warning(f"Unknown project version: {version_str}")
    return ProjectVersion.UNKNOWN


def is_supported_version(data: dict[str, Any]) -> bool:
    """Check if project version is supported.

    Args:
        data: Project dictionary data

    Returns:
        True if version is supported
    """
    version = detect_version(data)

    if not version.is_supported:
        if version.is_legacy:
            logger.error(
                f"Legacy project version detected: {version.value}. "
                f"This file format is from an older version of Camtasia and is not fully supported. "
                f"Some features may not work correctly. "
                f"This tool supports versions {ProjectVersion.V4_0.value} (Camtasia 2020) and {ProjectVersion.V9_0.value} (Camtasia 2021+)"
            )
        else:
            logger.error(
                f"Unknown project version: {version.value}. "
                f"This tool supports versions {ProjectVersion.V4_0.value} and {ProjectVersion.V9_0.value}"
            )
        return False

    return True


def get_version_features(version: ProjectVersion) -> dict:
    """Get feature set for a specific version.

    Args:
        version: Project version

    Returns:
        Dictionary of feature flags
    """
    features = {
        "has_high_precision_timing": False,
        "has_sub_frame_editing": False,
        "has_loudness_normalization": False,
        "has_authoring_client": False,
    }

    if version == ProjectVersion.V9_0:
        features.update(
            {
                "has_high_precision_timing": True,
                "has_sub_frame_editing": True,
                "has_loudness_normalization": True,
                "has_authoring_client": True,
            }
        )

    return features
