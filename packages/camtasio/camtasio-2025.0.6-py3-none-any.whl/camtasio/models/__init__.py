# this_file: src/camtasio/models/__init__.py
"""Domain models for Camtasia project structure."""

from .canvas import Canvas
from .factory import create_media_from_dict, detect_media_type
from .media import AMFile, AudioMedia, Callout, ImageMedia, IMFile, Media, VideoMedia, VMFile
from .project import Project, ProjectMetadata
from .source import SourceBin, SourceItem, SourceTrack
from .timeline import Timeline, Track, Transition

__all__ = [
    "AMFile",
    "AudioMedia",
    "Callout",
    "Canvas",
    "IMFile",
    "ImageMedia",
    # Media types
    "Media",
    # Core project structure
    "Project",
    "ProjectMetadata",
    # Source media
    "SourceBin",
    "SourceItem",
    "SourceTrack",
    # Timeline structure
    "Timeline",
    "Track",
    "Transition",
    # Specific media file types
    "VMFile",
    "VideoMedia",
    # Factory functions
    "create_media_from_dict",
    "detect_media_type",
]
