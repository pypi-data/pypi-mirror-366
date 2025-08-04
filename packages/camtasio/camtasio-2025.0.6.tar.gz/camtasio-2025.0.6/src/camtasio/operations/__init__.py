"""
Operations modules for Camtasia projects.

This package provides high-level operations for manipulating Camtasia projects,
including scaling, transforming, and other complex modifications.
"""
# this_file: src/camtasio/operations/__init__.py

from camtasio.operations.media_operations import (
    add_media_to_track,
    duplicate_media,
    find_media_references,
    remove_media,
)

__all__ = [
    "add_media_to_track",
    "duplicate_media",
    "find_media_references",
    "remove_media",
]
