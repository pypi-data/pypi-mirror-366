# this_file: src/camtasio/__init__.py
"""Camtasio - Python toolkit for programmatically manipulating Camtasia project files."""

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

# Import main components
from .annotations import (
    Color,
    FillStyle,
    HorizontalAlignment,
    StrokeStyle,
    VerticalAlignment,
    square_callout,
    text_callout,
)

# CLI application
from .cli import app

# Effects and annotations
from .effects import ChromaKeyEffect, Effect, VisualEffect
from .models import (
    AudioMedia,
    Canvas,
    ImageMedia,
    Media,
    Project,
    ProjectMetadata,
    SourceBin,
    SourceItem,
    Timeline,
    Track,
    VideoMedia,
    create_media_from_dict,
)

# Operations
from .operations import (
    add_media_to_track,
    duplicate_media,
    find_media_references,
    remove_media,
)
from .serialization import ProjectLoader, ProjectSaver, detect_version
from .transforms import PropertyTransformer, TransformConfig, TransformType

# Utilities
from .utils import RGBA, FrameStamp, hex_to_rgb

__all__ = [
    # Utilities
    "RGBA",
    # Models
    "AudioMedia",
    "Canvas",
    "ChromaKeyEffect",
    # Annotations
    "Color",
    # Effects
    "Effect",
    "FillStyle",
    "FrameStamp",
    "HorizontalAlignment",
    "ImageMedia",
    "Media",
    "Project",
    # Serialization
    "ProjectLoader",
    "ProjectMetadata",
    "ProjectSaver",
    # Transforms
    "PropertyTransformer",
    "SourceBin",
    "SourceItem",
    "StrokeStyle",
    "Timeline",
    "Track",
    "TransformConfig",
    "TransformType",
    "VerticalAlignment",
    "VideoMedia",
    "VisualEffect",
    # Version
    "__version__",
    # Operations
    "add_media_to_track",
    # CLI
    "app",
    "create_media_from_dict",
    "detect_version",
    "duplicate_media",
    "find_media_references",
    "hex_to_rgb",
    "remove_media",
    "square_callout",
    "text_callout",
]
