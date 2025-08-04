# this_file: src/camtasio/models/factory.py
"""Factory functions for creating model instances from JSON data."""

from typing import Any

from loguru import logger

from .media import AudioMedia, Callout, ImageMedia, Media, VideoMedia


def create_media_from_dict(data: dict[str, Any]) -> Media:
    """Create appropriate Media subclass instance from dictionary data.

    Args:
        data: Dictionary containing media data with '_type' field

    Returns:
        Appropriate Media subclass instance

    Raises:
        ValueError: If media type is unknown or data is invalid
    """
    media_type = data.get("_type", "")

    # Map of type strings to classes
    type_map = {
        "VMFile": VideoMedia,
        "ScreenVMFile": VideoMedia,
        "AMFile": AudioMedia,
        "IMFile": ImageMedia,
        "Callout": Callout,
        "UnifiedMedia": VideoMedia,  # Treat as video for now
        "Group": VideoMedia,  # Groups can contain multiple media, treat as video
        "StitchedMedia": VideoMedia,  # Stitched media is like concatenated video
    }

    media_class = type_map.get(media_type)
    if not media_class:
        logger.warning(f"Unknown media type: {media_type}, defaulting to VideoMedia")
        # Default to VideoMedia for unknown types
        media_class = VideoMedia

    # Extract common fields
    common_fields = {
        "id": data.get("id", 0),
        "src": data.get("src", 0),
        "track_number": data.get("trackNumber", 0),
        "start": data.get("start", 0),
        "duration": data.get("duration", 0),
        "media_start": data.get("mediaStart", 0),
        "media_duration": data.get("mediaDuration", 0),
        "scalar": data.get("scalar", 1.0),
        "attributes": data.get("attributes", {}),
        "parameters": data.get("parameters", {}),
        "effects": data.get("effects", []),
        "metadata": data.get("metadata", {}),
        "animation_tracks": data.get("animationTracks", {}),
    }

    # Handle type-specific fields
    if media_class == AudioMedia:
        return AudioMedia(**common_fields, channel_number=data.get("channelNumber", "0,1"))
    elif media_class == ImageMedia:
        return ImageMedia(**common_fields, trim_start_sum=data.get("trimStartSum", 0))
    elif media_class == Callout:
        return Callout(**common_fields, definition=data.get("def", {}))
    else:
        # VideoMedia or default
        return media_class(**common_fields)


def detect_media_type(source_item: dict) -> str:
    """Detect media type from source item data.

    Args:
        source_item: Source item dictionary from sourceBin

    Returns:
        Media type string (VMFile, AMFile, IMFile, etc.)
    """
    # Check source tracks
    source_tracks = source_item.get("sourceTracks", [])

    has_video = False
    has_audio = False
    has_image = False

    for track in source_tracks:
        track_type = track.get("type", -1)
        if track_type == 0:
            has_video = True
        elif track_type == 1:
            has_image = True
        elif track_type == 2:
            has_audio = True

    # Determine media type based on tracks
    if has_video:
        # Check if it's a screen recording
        metadata = source_item.get("metadata", {})
        if metadata.get("IsScreenRecording"):
            return "ScreenVMFile"
        return "VMFile"
    elif has_image:
        return "IMFile"
    elif has_audio:
        return "AMFile"
    else:
        # Default to video if unclear
        return "VMFile"
