#!/usr/bin/env python3
"""Type definitions for annotations."""
# this_file: src/camtasio/annotations/types.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


@dataclass(frozen=True)
class Color:
    """Normalized color representation for annotations (0.0-1.0)."""
    
    red: float
    green: float
    blue: float
    opacity: float = 1.0
    
    def __post_init__(self):
        """Validate color components are in valid range."""
        for comp_name in ('red', 'green', 'blue', 'opacity'):
            value = getattr(self, comp_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f'Color {comp_name} component out of range [0.0, 1.0], got {value}'
                )
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, a: int = 255) -> Color:
        """Create Color from RGB values (0-255)."""
        return cls(
            red=r / 255.0,
            green=g / 255.0,
            blue=b / 255.0,
            opacity=a / 255.0
        )
    
    @classmethod
    def from_hex(cls, hex_color: str) -> Color:
        """Create Color from hex string."""
        from camtasio.utils.color import hex_to_rgb
        channels = hex_to_rgb(hex_color)
        if len(channels) == 3:
            return cls.from_rgb(*channels, 255)
        return cls.from_rgb(*channels)
    
    def to_rgb(self) -> Tuple[int, int, int, int]:
        """Convert to RGB tuple (0-255)."""
        return (
            int(self.red * 255),
            int(self.green * 255),
            int(self.blue * 255),
            int(self.opacity * 255)
        )
    
    @classmethod
    def white(cls) -> Color:
        """Pure white color."""
        return cls(1.0, 1.0, 1.0, 1.0)
    
    @classmethod
    def black(cls) -> Color:
        """Pure black color."""
        return cls(0.0, 0.0, 0.0, 1.0)
    
    @classmethod
    def transparent(cls) -> Color:
        """Fully transparent color."""
        return cls(0.0, 0.0, 0.0, 0.0)


class HorizontalAlignment(str, Enum):
    """Horizontal text alignment options."""
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'


class VerticalAlignment(str, Enum):
    """Vertical text alignment options."""
    TOP = 'top'
    CENTER = 'center'
    BOTTOM = 'bottom'


class FillStyle(str, Enum):
    """Fill style options for shapes."""
    SOLID = 'solid'
    GRADIENT = 'gradient'


class StrokeStyle(str, Enum):
    """Stroke style options for shapes."""
    SOLID = 'solid'
    DASH = 'dash'
    DOT = 'dot'
    DASH_DOT = 'dashdot'
    DASH_DOT_DOT = 'dashdotdot'