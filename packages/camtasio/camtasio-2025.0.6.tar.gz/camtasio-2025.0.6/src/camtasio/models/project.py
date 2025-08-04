# this_file: src/camtasio/models/project.py
"""Project model representing a complete Camtasia project."""

from dataclasses import dataclass, field
from typing import Self

from loguru import logger

from .canvas import Canvas
from .source import SourceBin
from .timeline import Timeline


@dataclass
class ProjectMetadata:
    """Project metadata and settings."""

    title: str = ""
    description: str = ""
    author: str = ""
    version: str = "9.0"
    edit_rate: int = 705600000
    target_loudness: float = -18.0
    should_apply_loudness_normalization: bool = True
    audio_format_sample_rate: int = 44100
    allow_sub_frame_editing: bool = False
    authoring_client_name: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "editRate": self.edit_rate,
            "targetLoudness": self.target_loudness,
            "shouldApplyLoudnessNormalization": self.should_apply_loudness_normalization,
            "audioFormatSampleRate": self.audio_format_sample_rate,
        }

        if self.allow_sub_frame_editing:
            result["allowSubFrameEditing"] = self.allow_sub_frame_editing
        if self.authoring_client_name:
            result["authoringClientName"] = self.authoring_client_name

        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create ProjectMetadata from dictionary."""
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "9.0"),
            edit_rate=data.get("editRate", 705600000),
            target_loudness=data.get("targetLoudness", -18.0),
            should_apply_loudness_normalization=data.get("shouldApplyLoudnessNormalization", True),
            audio_format_sample_rate=data.get("audioFormatSampleRate", 44100),
            allow_sub_frame_editing=data.get("allowSubFrameEditing", False),
            authoring_client_name=data.get("authoringClientName", {}),
        )


@dataclass
class Project:
    """Represents a complete Camtasia project."""

    canvas: Canvas
    source_bin: SourceBin
    timeline: Timeline
    metadata: ProjectMetadata

    @property
    def version(self) -> str:
        """Get project version."""
        return self.metadata.version

    @property
    def edit_rate(self) -> int:
        """Get project edit rate."""
        return self.metadata.edit_rate

    @property
    def duration(self) -> float:
        """Get project duration in seconds."""
        if self.edit_rate > 0:
            return self.timeline.duration / self.edit_rate
        return 0.0

    def scale_spatial(self, factor: float) -> Self:
        """Scale all spatial properties in the project."""
        logger.info(f"Scaling project spatially by {factor}x")

        return Project(
            canvas=self.canvas.scale(factor),
            source_bin=self.source_bin.scale_spatial(factor),
            timeline=self.timeline.scale_spatial(factor),
            metadata=self.metadata,  # Metadata doesn't scale
        )

    def scale_temporal(self, factor: float) -> Self:
        """Scale all temporal properties in the project."""
        logger.info(f"Scaling project temporally by {factor}x")

        return Project(
            canvas=self.canvas,  # Canvas doesn't scale temporally
            source_bin=self.source_bin,  # Source bin doesn't scale temporally
            timeline=self.timeline.scale_temporal(factor),
            metadata=self.metadata,  # Metadata doesn't scale
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        # Merge canvas and metadata properties at root level
        result = self.metadata.to_dict()

        # Add canvas properties
        canvas_dict = self.canvas.to_dict()
        result["width"] = canvas_dict["width"]
        result["height"] = canvas_dict["height"]
        result["videoFormatFrameRate"] = canvas_dict["videoFormatFrameRate"]

        # Add source bin and timeline
        result["sourceBin"] = self.source_bin.to_list()
        result["timeline"] = self.timeline.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create Project from dictionary.

        Args:
            data: Dictionary containing project data

        Returns:
            New Project instance
        """
        # Handle missing required fields gracefully
        if "width" not in data or "height" not in data:
            logger.warning("Missing width/height in project data, using defaults (1920x1080)")

        # Extract canvas from root properties
        canvas = Canvas.from_dict(data)

        # Extract metadata from root properties
        metadata = ProjectMetadata.from_dict(data)

        # Extract source bin
        source_bin_data = data.get("sourceBin", [])
        if not isinstance(source_bin_data, list):
            logger.warning(f"Invalid sourceBin type: {type(source_bin_data)}, using empty list")
            source_bin_data = []
        source_bin = SourceBin.from_list(source_bin_data)

        # Extract timeline
        timeline_data = data.get("timeline", {})
        if not isinstance(timeline_data, dict):
            logger.warning(f"Invalid timeline type: {type(timeline_data)}, using empty dict")
            timeline_data = {}
        timeline = Timeline.from_dict(timeline_data)

        # Log version info
        logger.info(
            f"Loaded project version {metadata.version} with edit rate {metadata.edit_rate}"
        )

        return cls(
            canvas=canvas,
            source_bin=source_bin,
            timeline=timeline,
            metadata=metadata,
        )

    @classmethod
    def empty(cls, width: int = 1920, height: int = 1080, fps: int = 30) -> Self:
        """Create an empty project with default settings."""
        return cls(
            canvas=Canvas(width=width, height=height, frame_rate=fps),
            source_bin=SourceBin(),
            timeline=Timeline(id=1),
            metadata=ProjectMetadata(),
        )
