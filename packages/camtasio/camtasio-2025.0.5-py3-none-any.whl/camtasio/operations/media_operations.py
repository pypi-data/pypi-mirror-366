#!/usr/bin/env python3
"""High-level media operations for Camtasia projects."""
# this_file: src/camtasio/operations/media_operations.py

from typing import Optional, Sequence, Any
from loguru import logger


def add_media_to_track(
    project: Any,
    track_index: int,
    media_id: str,
    start_frame: int,
    duration: Optional[int] = None,
    effects: Optional[Sequence[Any]] = None
) -> None:
    """Add media from media bin to a timeline track.
    
    This coordinates between the media bin and timeline to properly
    add media references to tracks.
    
    Args:
        project: The Camtasia project instance
        track_index: Index of the track to add media to
        media_id: ID of the media in the media bin
        start_frame: Frame number where media starts on timeline
        duration: Duration in frames (None uses full media duration)
        effects: Optional sequence of Effect objects to apply
        
    Raises:
        KeyError: If track index or media ID not found
        ValueError: If media would overlap existing track media
    """
    logger.debug(f"Adding media {media_id} to track {track_index} at frame {start_frame}")
    
    # Validate track exists
    if track_index >= len(project.timeline.tracks):
        raise KeyError(f"Track index {track_index} not found in timeline")
    
    track = project.timeline.tracks[track_index]
    
    # Validate media exists
    if media_id not in project.media_bin:
        raise KeyError(f"Media ID {media_id} not found in media bin")
    
    media = project.media_bin[media_id]
    
    # Add media to track (let track handle overlap validation)
    track.add_media(media, start_frame, duration, effects)
    
    logger.info(f"Successfully added media {media_id} to track {track_index}")


def remove_media(
    project: Any,
    media_id: str,
    clear_tracks: bool = True
) -> None:
    """Remove media from the media bin and optionally from all tracks.
    
    By default, this removes all references to the media from tracks.
    Set clear_tracks=False to prevent removal if track references exist.
    
    Args:
        project: The Camtasia project instance
        media_id: ID of the media to remove
        clear_tracks: Whether to remove track references (default: True)
        
    Raises:
        KeyError: If media ID not found
        ValueError: If clear_tracks=False and track references exist
    """
    logger.debug(f"Removing media {media_id} from project (clear_tracks={clear_tracks})")
    
    # Validate media exists
    if media_id not in project.media_bin:
        raise KeyError(f"Media ID {media_id} not found in media bin")
    
    # Find and handle track references
    track_references = []
    for track_idx, track in enumerate(project.timeline.tracks):
        for track_media in track.medias:
            if hasattr(track_media, 'source') and track_media.source == media_id:
                track_references.append((track_idx, track_media.id))
    
    if track_references and not clear_tracks:
        raise ValueError(
            f"Cannot remove media {media_id}: found {len(track_references)} "
            f"track references and clear_tracks=False"
        )
    
    # Remove track references if requested
    if clear_tracks:
        for track_idx, track_media_id in track_references:
            track = project.timeline.tracks[track_idx]
            del track.medias[track_media_id]
            logger.debug(f"Removed track media {track_media_id} from track {track_idx}")
    
    # Remove from media bin
    del project.media_bin[media_id]
    logger.info(f"Successfully removed media {media_id} from project")


def duplicate_media(
    project: Any,
    source_media_id: str,
    new_media_id: Optional[str] = None
) -> str:
    """Duplicate media in the media bin.
    
    Creates a copy of existing media with a new ID.
    
    Args:
        project: The Camtasia project instance
        source_media_id: ID of media to duplicate
        new_media_id: Optional ID for new media (auto-generated if None)
        
    Returns:
        The ID of the newly created media
        
    Raises:
        KeyError: If source media not found
        ValueError: If new_media_id already exists
    """
    if source_media_id not in project.media_bin:
        raise KeyError(f"Source media ID {source_media_id} not found")
    
    if new_media_id and new_media_id in project.media_bin:
        raise ValueError(f"Media ID {new_media_id} already exists")
    
    # Generate new ID if not provided
    if not new_media_id:
        base_id = f"{source_media_id}_copy"
        counter = 1
        while f"{base_id}_{counter}" in project.media_bin:
            counter += 1
        new_media_id = f"{base_id}_{counter}"
    
    # Copy media
    source_media = project.media_bin[source_media_id]
    project.media_bin[new_media_id] = source_media.copy()
    
    logger.info(f"Duplicated media {source_media_id} as {new_media_id}")
    return new_media_id


def find_media_references(project: Any, media_id: str) -> list[tuple[int, str]]:
    """Find all track references to a media bin item.
    
    Args:
        project: The Camtasia project instance
        media_id: ID of the media to search for
        
    Returns:
        List of (track_index, track_media_id) tuples
        
    Raises:
        KeyError: If media ID not found
    """
    if media_id not in project.media_bin:
        raise KeyError(f"Media ID {media_id} not found in media bin")
    
    references = []
    for track_idx, track in enumerate(project.timeline.tracks):
        for track_media in track.medias:
            if hasattr(track_media, 'source') and track_media.source == media_id:
                references.append((track_idx, track_media.id))
    
    logger.debug(f"Found {len(references)} references to media {media_id}")
    return references