"""Annotations system for Camtasia projects."""
# this_file: src/camtasio/annotations/__init__.py

from camtasio.annotations.callouts import square_callout, text_callout
from camtasio.annotations.types import (
    Color,
    FillStyle,
    HorizontalAlignment,
    StrokeStyle,
    VerticalAlignment,
)

__all__ = [
    "Color",
    "FillStyle",
    "HorizontalAlignment",
    "StrokeStyle",
    "VerticalAlignment",
    "square_callout",
    "text_callout",
]
