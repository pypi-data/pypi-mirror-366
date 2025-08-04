"""Annotations system for Camtasia projects."""
# this_file: src/camtasio/annotations/__init__.py

from camtasio.annotations.types import (
    Color,
    FillStyle,
    StrokeStyle,
    HorizontalAlignment,
    VerticalAlignment,
)
from camtasio.annotations.callouts import text_callout, square_callout

__all__ = [
    "Color",
    "FillStyle", 
    "StrokeStyle",
    "HorizontalAlignment",
    "VerticalAlignment",
    "text_callout",
    "square_callout",
]