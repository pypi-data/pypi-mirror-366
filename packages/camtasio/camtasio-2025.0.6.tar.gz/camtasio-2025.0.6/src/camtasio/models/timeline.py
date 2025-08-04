# this_file: src/camtasio/models/timeline.py
"""Timeline and track models for Camtasia projects."""

from dataclasses import dataclass, field
from typing import Any, Self

from .factory import create_media_from_dict
from .media import Media


@dataclass
class Transition:
    """Represents a transition between media items."""

    name: str
    duration: int
    left_media: int | None = None
    right_media: int | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def scale_temporal(self, factor: float) -> Self:
        """Scale transition duration."""
        return self.__class__(
            name=self.name,
            duration=int(self.duration * factor),
            left_media=self.left_media,
            right_media=self.right_media,
            attributes=self.attributes.copy(),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "name": self.name,
            "duration": self.duration,
            "attributes": self.attributes,
        }
        if self.left_media is not None:
            result["leftMedia"] = self.left_media
        if self.right_media is not None:
            result["rightMedia"] = self.right_media
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create Transition from dictionary."""
        return cls(
            name=data.get("name", ""),
            duration=data.get("duration", 0),
            left_media=data.get("leftMedia"),
            right_media=data.get("rightMedia"),
            attributes=data.get("attributes", {}),
        )


@dataclass
class Track:
    """Represents a track on the timeline."""

    track_index: int
    medias: list[Media] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    ident: str = ""
    audio_muted: bool = False
    video_hidden: bool = False
    magnetic: bool = False
    matte: int = 0
    solo: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_media(self, media: Media) -> None:
        """Add a media item to the track."""
        self.medias.append(media)

    def add_transition(self, transition: Transition) -> None:
        """Add a transition to the track."""
        self.transitions.append(transition)

    @property
    def duration(self) -> int:
        """Calculate track duration from media items."""
        if not self.medias:
            return 0
        return max(media.start + media.duration for media in self.medias)

    @property
    def media_count(self) -> int:
        """Count of media items on this track."""
        return len(self.medias)

    def scale_spatial(self, factor: float) -> Self:
        """Scale all spatial properties in the track."""
        return Track(
            track_index=self.track_index,
            medias=[media.scale_spatial(factor) for media in self.medias],
            transitions=self.transitions.copy(),  # Transitions don't have spatial properties
            parameters=self.parameters.copy(),
            ident=self.ident,
            audio_muted=self.audio_muted,
            video_hidden=self.video_hidden,
            magnetic=self.magnetic,
            matte=self.matte,
            solo=self.solo,
            metadata=self.metadata.copy(),
        )

    def scale_temporal(self, factor: float) -> Self:
        """Scale all temporal properties in the track."""
        return Track(
            track_index=self.track_index,
            medias=[media.scale_temporal(factor) for media in self.medias],
            transitions=[t.scale_temporal(factor) for t in self.transitions],
            parameters=self.parameters.copy(),
            ident=self.ident,
            audio_muted=self.audio_muted,
            video_hidden=self.video_hidden,
            magnetic=self.magnetic,
            matte=self.matte,
            solo=self.solo,
            metadata=self.metadata.copy(),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "trackIndex": self.track_index,
            "medias": [media.to_dict() for media in self.medias],
            "parameters": self.parameters,
        }

        if self.transitions:
            result["transitions"] = [t.to_dict() for t in self.transitions]
        if self.ident:
            result["ident"] = self.ident
        if self.audio_muted:
            result["audioMuted"] = self.audio_muted
        if self.video_hidden:
            result["videoHidden"] = self.video_hidden
        if self.magnetic:
            result["magnetic"] = self.magnetic
        if self.matte:
            result["matte"] = self.matte
        if self.solo:
            result["solo"] = self.solo
        if self.metadata:
            result["metadata"] = self.metadata

        return result


@dataclass
class Timeline:
    """Represents the project timeline."""

    id: int
    tracks: list[Track] = field(default_factory=list)

    @property
    def duration(self) -> int:
        """Calculate total timeline duration."""
        if not self.tracks:
            return 0
        return max(track.duration for track in self.tracks)

    @property
    def track_count(self) -> int:
        """Number of tracks in timeline."""
        return len(self.tracks)

    @property
    def media_count(self) -> int:
        """Total media items across all tracks."""
        return sum(track.media_count for track in self.tracks)

    def get_track(self, index: int) -> Track | None:
        """Get track by index."""
        for track in self.tracks:
            if track.track_index == index:
                return track
        return None

    def add_track(self, track: Track) -> None:
        """Add a track to the timeline."""
        self.tracks.append(track)

    def scale_spatial(self, factor: float) -> Self:
        """Scale all spatial properties in the timeline."""
        return Timeline(
            id=self.id,
            tracks=[track.scale_spatial(factor) for track in self.tracks],
        )

    def scale_temporal(self, factor: float) -> Self:
        """Scale all temporal properties in the timeline."""
        return Timeline(
            id=self.id,
            tracks=[track.scale_temporal(factor) for track in self.tracks],
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        # Camtasia uses a nested structure with sceneTrack
        return {
            "id": self.id,
            "sceneTrack": {
                "scenes": [{"csml": {"tracks": [track.to_dict() for track in self.tracks]}}]
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create Timeline from dictionary."""
        timeline_id = data.get("id", 0)
        tracks = []

        # Navigate the nested structure
        scene_track = data.get("sceneTrack", {})
        scenes = scene_track.get("scenes", [])
        if scenes:
            csml = scenes[0].get("csml", {})
            track_data = csml.get("tracks", [])

            for track_dict in track_data:
                # Parse media items
                medias = []
                for media_dict in track_dict.get("medias", []):
                    media = create_media_from_dict(media_dict)
                    medias.append(media)

                # Parse transitions
                transitions = []
                for trans_dict in track_dict.get("transitions", []):
                    transition = Transition.from_dict(trans_dict)
                    transitions.append(transition)

                track = Track(
                    track_index=track_dict.get("trackIndex", 0),
                    medias=medias,
                    transitions=transitions,
                    parameters=track_dict.get("parameters", {}),
                    ident=track_dict.get("ident", ""),
                    audio_muted=track_dict.get("audioMuted", False),
                    video_hidden=track_dict.get("videoHidden", False),
                    magnetic=track_dict.get("magnetic", False),
                    matte=track_dict.get("matte", 0),
                    solo=track_dict.get("solo", False),
                    metadata=track_dict.get("metadata", {}),
                )
                tracks.append(track)

        return cls(id=timeline_id, tracks=tracks)
