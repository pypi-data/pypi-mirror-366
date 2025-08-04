# this_file: src/camtasio/models/source.py
"""Source media models for Camtasia projects."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceTrack:
    """Represents a track within a source media item."""

    range: list[int]  # [start, end]
    type: int  # 0=video, 1=image, 2=audio
    edit_rate: int
    track_rect: list[int]  # [x, y, width, height]
    sample_rate: float | str = 0
    bit_depth: int = 0
    num_channels: int = 0
    integrated_lufs: float = 100.0
    peak_level: float = -1.0
    meta_data: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    tag: int = 0

    @property
    def is_video(self) -> bool:
        """Check if this is a video track."""
        return self.type == 0

    @property
    def is_image(self) -> bool:
        """Check if this is an image track."""
        return self.type == 1

    @property
    def is_audio(self) -> bool:
        """Check if this is an audio track."""
        return self.type == 2

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "range": self.range,
            "type": self.type,
            "editRate": self.edit_rate,
            "trackRect": self.track_rect,
            "sampleRate": self.sample_rate,
            "bitDepth": self.bit_depth,
            "numChannels": self.num_channels,
            "integratedLUFS": self.integrated_lufs,
            "peakLevel": self.peak_level,
            "metaData": self.meta_data,
        }
        if self.tag:
            result["tag"] = self.tag
        if self.parameters:
            result["parameters"] = self.parameters
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceTrack":
        """Create SourceTrack from dictionary."""
        # Handle sample rate which can be string fraction or number
        sample_rate = data.get("sampleRate", 0)
        if isinstance(sample_rate, str) and "/" in sample_rate:
            # Convert fraction string to float
            try:
                num, den = sample_rate.split("/")
                sample_rate = float(num) / float(den)
            except (ValueError, ZeroDivisionError):
                sample_rate = 0

        return cls(
            range=data.get("range", [0, 0]),
            type=data.get("type", 0),
            edit_rate=data.get("editRate", 0),
            track_rect=data.get("trackRect", [0, 0, 0, 0]),
            sample_rate=sample_rate,
            bit_depth=data.get("bitDepth", 0),
            num_channels=data.get("numChannels", 0),
            integrated_lufs=data.get("integratedLUFS", 100.0),
            peak_level=data.get("peakLevel", -1.0),
            meta_data=data.get("metaData", ""),
            parameters=data.get("parameters", {}),
            tag=data.get("tag", 0),
        )


@dataclass
class SourceItem:
    """Represents a source media item in the source bin."""

    id: int
    src: str  # File path
    rect: list[int]  # [x, y, width, height]
    last_mod: str  # ISO timestamp
    source_tracks: list[SourceTrack] = field(default_factory=list)
    loudness_normalization: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def width(self) -> int:
        """Get media width from rect."""
        return self.rect[2] if len(self.rect) >= 4 else 0

    @property
    def height(self) -> int:
        """Get media height from rect."""
        return self.rect[3] if len(self.rect) >= 4 else 0

    @property
    def has_video(self) -> bool:
        """Check if source has video tracks."""
        return any(track.is_video for track in self.source_tracks)

    @property
    def has_audio(self) -> bool:
        """Check if source has audio tracks."""
        return any(track.is_audio for track in self.source_tracks)

    @property
    def is_image(self) -> bool:
        """Check if source is an image."""
        return any(track.is_image for track in self.source_tracks)

    def scale_spatial(self, factor: float) -> "SourceItem":
        """Return new SourceItem with scaled spatial properties."""
        new_rect = [
            int(self.rect[0] * factor),
            int(self.rect[1] * factor),
            int(self.rect[2] * factor),
            int(self.rect[3] * factor),
        ]

        new_tracks = []
        for track in self.source_tracks:
            new_track_rect = [
                int(track.track_rect[0] * factor),
                int(track.track_rect[1] * factor),
                int(track.track_rect[2] * factor),
                int(track.track_rect[3] * factor),
            ]
            new_track = SourceTrack(
                range=track.range,
                type=track.type,
                edit_rate=track.edit_rate,
                track_rect=new_track_rect,
                sample_rate=track.sample_rate,
                bit_depth=track.bit_depth,
                num_channels=track.num_channels,
                integrated_lufs=track.integrated_lufs,
                peak_level=track.peak_level,
                meta_data=track.meta_data,
                parameters=track.parameters,
                tag=track.tag,
            )
            new_tracks.append(new_track)

        return SourceItem(
            id=self.id,
            src=self.src,
            rect=new_rect,
            last_mod=self.last_mod,
            source_tracks=new_tracks,
            loudness_normalization=self.loudness_normalization,
            metadata=self.metadata.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "id": self.id,
            "src": self.src,
            "rect": self.rect,
            "lastMod": self.last_mod,
            "loudnessNormalization": self.loudness_normalization,
            "sourceTracks": [track.to_dict() for track in self.source_tracks],
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceItem":
        """Create SourceItem from dictionary."""
        return cls(
            id=data.get("id", 0),
            src=data.get("src", ""),
            rect=data.get("rect", [0, 0, 0, 0]),
            last_mod=data.get("lastMod", ""),
            source_tracks=[SourceTrack.from_dict(track) for track in data.get("sourceTracks", [])],
            loudness_normalization=data.get("loudnessNormalization", True),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SourceBin:
    """Container for all source media items."""

    items: list[SourceItem] = field(default_factory=list)

    def get_by_id(self, item_id: int) -> SourceItem | None:
        """Get source item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def add_item(self, item: SourceItem) -> None:
        """Add a source item to the bin."""
        self.items.append(item)

    def scale_spatial(self, factor: float) -> "SourceBin":
        """Return new SourceBin with all items scaled."""
        return SourceBin(items=[item.scale_spatial(factor) for item in self.items])

    def to_list(self) -> list[dict[str, Any]]:
        """Convert to list of dictionaries for serialization."""
        return [item.to_dict() for item in self.items]

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> "SourceBin":
        """Create SourceBin from list of dictionaries."""
        return cls(items=[SourceItem.from_dict(item) for item in data])
