# this_file: src/camtasio/serialization/__init__.py
"""Serialization and deserialization for Camtasia projects."""

from .json_encoder import CamtasiaJSONEncoder
from .json_handler import dumps_json, load_json_file, loads_json, save_json_file
from .loader import ProjectLoader
from .saver import ProjectSaver
from .version import ProjectVersion, detect_version, get_version_features, is_supported_version

__all__ = [
    "CamtasiaJSONEncoder",
    "ProjectLoader",
    "ProjectSaver",
    "ProjectVersion",
    "detect_version",
    "dumps_json",
    "get_version_features",
    "is_supported_version",
    "load_json_file",
    "loads_json",
    "save_json_file",
]
