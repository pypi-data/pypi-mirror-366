# this_file: src/camtasio/__init__.py
"""Camtasio - Python toolkit for programmatically manipulating Camtasia project files."""

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

# Import main components
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
from .serialization import ProjectLoader, ProjectSaver, detect_version
from .transforms import PropertyTransformer, TransformConfig, TransformType

# Effects and annotations
from .effects import Effect, VisualEffect, ChromaKeyEffect
from .annotations import (
    Color,
    FillStyle,
    StrokeStyle,
    HorizontalAlignment,
    VerticalAlignment,
    text_callout,
    square_callout,
)

# Utilities
from .utils import RGBA, hex_to_rgb, FrameStamp

# Operations
from .operations import (
    add_media_to_track,
    remove_media,
    duplicate_media,
    find_media_references,
)

# CLI application
from .cli import app

__all__ = [
    # Models
    "AudioMedia",
    "Canvas",
    "ImageMedia",
    "Media",
    "Project",
    "ProjectMetadata",
    "SourceBin",
    "SourceItem",
    "Timeline",
    "Track",
    "VideoMedia",
    "create_media_from_dict",
    # Serialization
    "ProjectLoader",
    "ProjectSaver",
    "detect_version",
    # Transforms
    "PropertyTransformer",
    "TransformConfig",
    "TransformType",
    # Effects
    "Effect",
    "VisualEffect",
    "ChromaKeyEffect",
    # Annotations
    "Color",
    "FillStyle",
    "StrokeStyle",
    "HorizontalAlignment",
    "VerticalAlignment",
    "text_callout",
    "square_callout",
    # Utilities
    "RGBA",
    "hex_to_rgb",
    "FrameStamp",
    # Operations
    "add_media_to_track",
    "remove_media",
    "duplicate_media",
    "find_media_references",
    # CLI
    "app",
    # Version
    "__version__",
]
