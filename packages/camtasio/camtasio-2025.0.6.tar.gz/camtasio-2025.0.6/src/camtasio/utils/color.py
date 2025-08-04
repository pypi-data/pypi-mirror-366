#!/usr/bin/env python3
"""Color utilities for Camtasia projects."""
# this_file: src/camtasio/utils/color.py

from __future__ import annotations

from dataclasses import dataclass


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    """Convert hex color string to RGB(A) tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF0000", "FF0000", "#FF0000FF")

    Returns:
        Tuple of RGB(A) values (0-255)

    Raises:
        ValueError: If hex color format is invalid
    """
    h = hex_color.lstrip("#")
    num_digits = len(h)

    if num_digits == 3:
        return (
            int(h[0], 16) * 17,  # Expand 0xF to 0xFF
            int(h[1], 16) * 17,
            int(h[2], 16) * 17,
        )
    elif num_digits == 4:
        return (
            int(h[0], 16) * 17,
            int(h[1], 16) * 17,
            int(h[2], 16) * 17,
            int(h[3], 16) * 17,
        )
    elif num_digits == 6:
        return (
            int(h[0:2], 16),
            int(h[2:4], 16),
            int(h[4:6], 16),
        )
    elif num_digits == 8:
        return (
            int(h[0:2], 16),
            int(h[2:4], 16),
            int(h[4:6], 16),
            int(h[6:8], 16),
        )
    else:
        raise ValueError(f"Invalid hex color format: {hex_color!r}")


@dataclass(frozen=True)
class RGBA:
    """RGBA color representation with validation."""

    red: int
    green: int
    blue: int
    alpha: int = 255

    MINIMUM_CHANNEL: int = 0
    MAXIMUM_CHANNEL: int = 255

    def __post_init__(self) -> None:
        """Validate channel values."""
        for name, value in [
            ("red", self.red),
            ("green", self.green),
            ("blue", self.blue),
            ("alpha", self.alpha)
        ]:
            if not (self.MINIMUM_CHANNEL <= value <= self.MAXIMUM_CHANNEL):
                raise ValueError(
                    f"RGBA {name} channel {value} out of range "
                    f"{self.MINIMUM_CHANNEL}-{self.MAXIMUM_CHANNEL}"
                )

    @classmethod
    def from_hex(cls, hex_color: str) -> RGBA:
        """Create RGBA from hex color string."""
        channels = hex_to_rgb(hex_color)
        if len(channels) == 3:
            return cls(*channels, alpha=cls.MAXIMUM_CHANNEL)
        return cls(*channels)

    @classmethod
    def from_floats(cls, red: float, green: float, blue: float, alpha: float = 1.0) -> RGBA:
        """Create RGBA from float values (0.0-1.0)."""
        return cls(
            int(red * cls.MAXIMUM_CHANNEL),
            int(green * cls.MAXIMUM_CHANNEL),
            int(blue * cls.MAXIMUM_CHANNEL),
            int(alpha * cls.MAXIMUM_CHANNEL),
        )

    def as_tuple(self) -> tuple[int, int, int, int]:
        """Return as (r, g, b, a) tuple."""
        return (self.red, self.green, self.blue, self.alpha)

    def as_floats(self) -> tuple[float, float, float, float]:
        """Return as normalized float tuple (0.0-1.0)."""
        return (
            self.red / self.MAXIMUM_CHANNEL,
            self.green / self.MAXIMUM_CHANNEL,
            self.blue / self.MAXIMUM_CHANNEL,
            self.alpha / self.MAXIMUM_CHANNEL,
        )

    def to_hex(self, include_alpha: bool = True) -> str:
        """Convert to hex color string."""
        if include_alpha and self.alpha != self.MAXIMUM_CHANNEL:
            return f"#{self.red:02X}{self.green:02X}{self.blue:02X}{self.alpha:02X}"
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"
