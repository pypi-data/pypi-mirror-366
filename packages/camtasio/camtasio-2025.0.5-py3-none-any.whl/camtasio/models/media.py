# this_file: src/camtasio/models/media.py
"""Media models representing timeline media items."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Media(ABC):
    """Base class for all media types on the timeline."""

    id: int
    src: int  # References SourceBin item ID
    track_number: int = 0
    start: int = 0
    duration: int = 0
    media_start: int = 0
    media_duration: int = 0
    scalar: float | str = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    effects: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    animation_tracks: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def scale_spatial(self, factor: float) -> "Media":
        """Scale spatial properties."""
        pass

    @abstractmethod
    def scale_temporal(self, factor: float) -> "Media":
        """Scale temporal properties."""
        pass

    @abstractmethod
    def get_type(self) -> str:
        """Get the _type value for serialization."""
        pass

    def _scale_parameters(self, factor: float) -> dict[str, Any]:
        """Scale spatial parameters."""
        scaled = self.parameters.copy()

        # Scale position parameters
        for key in ["translation0", "translation1", "translation2"]:
            if key in scaled and isinstance(scaled[key], int | float):
                scaled[key] = scaled[key] * factor

        # Scale size parameters
        for key in ["scale0", "scale1", "scale2"]:
            if key in scaled and isinstance(scaled[key], int | float):
                scaled[key] = scaled[key] * factor

        # Scale crop parameters
        for key in ["geometryCrop0", "geometryCrop1", "geometryCrop2", "geometryCrop3"]:
            if key in scaled and isinstance(scaled[key], int | float):
                scaled[key] = scaled[key] * factor

        # Handle keyframe animations
        for key, value in scaled.items():
            if isinstance(value, dict) and "keyframes" in value:
                # Scale keyframe values for spatial properties
                if any(prop in key for prop in ["translation", "scale", "geometryCrop"]):
                    value["keyframes"] = self._scale_keyframes_spatial(value["keyframes"], factor)

        return scaled

    def _scale_keyframes_spatial(self, keyframes: list[dict[str, Any]], factor: float) -> list[dict[str, Any]]:
        """Scale spatial values in keyframes."""
        scaled_keyframes = []
        for kf in keyframes:
            new_kf = kf.copy()
            if "value" in new_kf:
                new_kf["value"] = new_kf["value"] * factor
            scaled_keyframes.append(new_kf)
        return scaled_keyframes

    def _scale_keyframes_temporal(self, keyframes: list[dict[str, Any]], factor: float) -> list[dict[str, Any]]:
        """Scale temporal values in keyframes."""
        scaled_keyframes = []
        for kf in keyframes:
            new_kf = kf.copy()
            if "time" in new_kf and isinstance(new_kf["time"], int | float):
                new_kf["time"] = int(new_kf["time"] * factor)
            if "endTime" in new_kf and isinstance(new_kf["endTime"], int | float):
                new_kf["endTime"] = int(new_kf["endTime"] * factor)
            if "duration" in new_kf and isinstance(new_kf["duration"], int | float):
                new_kf["duration"] = int(new_kf["duration"] * factor)
            scaled_keyframes.append(new_kf)
        return scaled_keyframes

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "id": self.id,
            "_type": self.get_type(),
            "src": self.src,
            "trackNumber": self.track_number,
            "start": self.start,
            "duration": self.duration,
            "mediaStart": self.media_start,
            "mediaDuration": self.media_duration,
            "scalar": self.scalar,
        }

        if self.attributes:
            result["attributes"] = self.attributes
        if self.parameters:
            result["parameters"] = self.parameters
        if self.effects:
            result["effects"] = self.effects
        if self.metadata:
            result["metadata"] = self.metadata
        if self.animation_tracks:
            result["animationTracks"] = self.animation_tracks

        return result


@dataclass
class VideoMedia(Media):
    """Video media file (VMFile, ScreenVMFile)."""

    def get_type(self) -> str:
        """Get the _type value."""
        # Could be VMFile or ScreenVMFile based on attributes
        return str(self.attributes.get("_type", "VMFile"))

    def scale_spatial(self, factor: float) -> "VideoMedia":
        """Scale spatial properties."""
        return VideoMedia(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=self.start,
            duration=self.duration,
            media_start=self.media_start,
            media_duration=self.media_duration,
            scalar=self.scalar,
            attributes=self.attributes.copy(),
            parameters=self._scale_parameters(factor),
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )

    def scale_temporal(self, factor: float) -> "VideoMedia":
        """Scale temporal properties."""
        # Scale time properties
        new_start = int(self.start * factor)
        new_duration = int(self.duration * factor)
        new_media_start = (
            int(self.media_start * factor)
            if isinstance(self.media_start, int | float)
            else self.media_start
        )
        new_media_duration = (
            int(self.media_duration * factor)
            if isinstance(self.media_duration, int | float)
            else self.media_duration
        )

        # Scale keyframe times
        new_params = self.parameters.copy()
        for _key, value in new_params.items():
            if isinstance(value, dict) and "keyframes" in value:
                value["keyframes"] = self._scale_keyframes_temporal(value["keyframes"], factor)

        return VideoMedia(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=new_start,
            duration=new_duration,
            media_start=new_media_start,
            media_duration=new_media_duration,
            scalar=self.scalar,
            attributes=self.attributes.copy(),
            parameters=new_params,
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )


@dataclass
class AudioMedia(Media):
    """Audio media file (AMFile)."""

    channel_number: str = "0,1"

    def get_type(self) -> str:
        """Get the _type value."""
        return "AMFile"

    def scale_spatial(self, factor: float) -> "AudioMedia":
        """Audio has no spatial properties to scale."""
        return AudioMedia(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=self.start,
            duration=self.duration,
            media_start=self.media_start,
            media_duration=self.media_duration,
            scalar=self.scalar,
            channel_number=self.channel_number,
            attributes=self.attributes.copy(),
            parameters=self.parameters.copy(),  # No spatial scaling for audio
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )

    def scale_temporal(self, factor: float) -> "AudioMedia":
        """Scale temporal properties - but preserve audio duration!"""
        # Only scale start position, not duration
        new_start = int(self.start * factor)

        # Scale keyframe times (for volume fades, etc.)
        new_params = self.parameters.copy()
        for _key, value in new_params.items():
            if isinstance(value, dict) and "keyframes" in value:
                value["keyframes"] = self._scale_keyframes_temporal(value["keyframes"], factor)

        return AudioMedia(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=new_start,
            duration=self.duration,  # Preserved!
            media_start=self.media_start,  # Preserved!
            media_duration=self.media_duration,  # Preserved!
            scalar=self.scalar,
            channel_number=self.channel_number,
            attributes=self.attributes.copy(),
            parameters=new_params,
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = super().to_dict()
        result["channelNumber"] = self.channel_number
        return result


@dataclass
class ImageMedia(Media):
    """Image media file (IMFile)."""

    trim_start_sum: int = 0

    def get_type(self) -> str:
        """Get the _type value."""
        return "IMFile"

    def scale_spatial(self, factor: float) -> "ImageMedia":
        """Scale spatial properties."""
        return ImageMedia(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=self.start,
            duration=self.duration,
            media_start=self.media_start,
            media_duration=self.media_duration,
            scalar=self.scalar,
            trim_start_sum=self.trim_start_sum,
            attributes=self.attributes.copy(),
            parameters=self._scale_parameters(factor),
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )

    def scale_temporal(self, factor: float) -> "ImageMedia":
        """Scale temporal properties."""
        new_start = int(self.start * factor)
        new_duration = int(self.duration * factor)
        new_trim = int(self.trim_start_sum * factor)

        # Scale keyframe times
        new_params = self.parameters.copy()
        for _key, value in new_params.items():
            if isinstance(value, dict) and "keyframes" in value:
                value["keyframes"] = self._scale_keyframes_temporal(value["keyframes"], factor)

        return ImageMedia(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=new_start,
            duration=new_duration,
            media_start=self.media_start,
            media_duration=self.media_duration,
            scalar=self.scalar,
            trim_start_sum=new_trim,
            attributes=self.attributes.copy(),
            parameters=new_params,
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = super().to_dict()
        if self.trim_start_sum:
            result["trimStartSum"] = self.trim_start_sum
        return result


@dataclass
class Callout(Media):
    """Callout/annotation object."""

    definition: dict[str, Any] = field(default_factory=dict)

    def get_type(self) -> str:
        """Get the _type value."""
        return "Callout"

    def scale_spatial(self, factor: float) -> "Callout":
        """Scale spatial properties including definition."""
        # Scale definition properties
        new_def = self.definition.copy()
        for key in ["width", "height", "corner-radius", "stroke-width"]:
            if key in new_def:
                new_def[key] = new_def[key] * factor

        return Callout(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=self.start,
            duration=self.duration,
            media_start=self.media_start,
            media_duration=self.media_duration,
            scalar=self.scalar,
            definition=new_def,
            attributes=self.attributes.copy(),
            parameters=self._scale_parameters(factor),
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )

    def scale_temporal(self, factor: float) -> "Callout":
        """Scale temporal properties."""
        new_start = int(self.start * factor)
        new_duration = int(self.duration * factor)

        # Scale keyframe times
        new_params = self.parameters.copy()
        for _key, value in new_params.items():
            if isinstance(value, dict) and "keyframes" in value:
                value["keyframes"] = self._scale_keyframes_temporal(value["keyframes"], factor)

        return Callout(
            id=self.id,
            src=self.src,
            track_number=self.track_number,
            start=new_start,
            duration=new_duration,
            media_start=self.media_start,
            media_duration=self.media_duration,
            scalar=self.scalar,
            definition=self.definition.copy(),
            attributes=self.attributes.copy(),
            parameters=new_params,
            effects=self.effects.copy(),
            metadata=self.metadata.copy(),
            animation_tracks=self.animation_tracks.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = super().to_dict()
        if self.definition:
            result["def"] = self.definition
        return result

    @classmethod
    def text(cls, text: str, font_size: float = 24, **style: Any) -> "Callout":
        """Create a text callout."""
        definition = {"kind": "text", "text": text, "font-size": font_size, **style}
        return cls(
            id=0,  # Will be assigned later
            src=0,  # No source reference
            definition=definition,
        )


# Convenience type aliases for specific media types
VMFile = VideoMedia
AMFile = AudioMedia
IMFile = ImageMedia
