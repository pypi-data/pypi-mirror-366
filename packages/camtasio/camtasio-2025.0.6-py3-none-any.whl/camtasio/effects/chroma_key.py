#!/usr/bin/env python3
"""ChromaKey effect implementation."""
# this_file: src/camtasio/effects/chroma_key.py

from __future__ import annotations

from typing import Any

from camtasio.utils.color import RGBA


class ChromaKeyEffect:
    """ChromaKey (green screen) effect for Camtasia."""

    # Constants
    MINIMUM_TOLERANCE: float = 0.0
    MAXIMUM_TOLERANCE: float = 1.0
    MINIMUM_SOFTNESS: float = 0.0
    MAXIMUM_SOFTNESS: float = 1.0
    MINIMUM_DEFRINGE: float = -1.0
    MAXIMUM_DEFRINGE: float = 1.0
    MINIMUM_COMPENSATION: float = 0.0
    MAXIMUM_COMPENSATION: float = 1.0

    def __init__(
        self,
        tolerance: float | None = None,
        softness: float | None = None,
        defringe: float | None = None,
        compensation: float | None = None,
        inverted: bool | None = None,
        hue: str | RGBA | None = None,
    ):
        """Initialize ChromaKey effect with validation."""
        self.name = "ChromaKey"
        self.category = "categoryVisualEffects"

        # Set and validate tolerance
        self.tolerance = tolerance if tolerance is not None else 0.1
        if not (self.MINIMUM_TOLERANCE <= self.tolerance <= self.MAXIMUM_TOLERANCE):
            raise ValueError(
                f"ChromaKey tolerance {self.tolerance} out of range "
                f"{self.MINIMUM_TOLERANCE}-{self.MAXIMUM_TOLERANCE}"
            )

        # Set and validate softness
        self.softness = softness if softness is not None else 0.1
        if not (self.MINIMUM_SOFTNESS <= self.softness <= self.MAXIMUM_SOFTNESS):
            raise ValueError(
                f"ChromaKey softness {self.softness} out of range "
                f"{self.MINIMUM_SOFTNESS}-{self.MAXIMUM_SOFTNESS}"
            )

        # Set and validate defringe
        self.defringe = defringe if defringe is not None else 0.0
        if not (self.MINIMUM_DEFRINGE <= self.defringe <= self.MAXIMUM_DEFRINGE):
            raise ValueError(
                f"ChromaKey defringe {self.defringe} out of range "
                f"{self.MINIMUM_DEFRINGE}-{self.MAXIMUM_DEFRINGE}"
            )

        # Set and validate compensation
        self.compensation = compensation if compensation is not None else 0.0
        if not (self.MINIMUM_COMPENSATION <= self.compensation <= self.MAXIMUM_COMPENSATION):
            raise ValueError(
                f"ChromaKey compensation {self.compensation} out of range "
                f"{self.MINIMUM_COMPENSATION}-{self.MAXIMUM_COMPENSATION}"
            )

        # Set inverted
        self.inverted = inverted if inverted is not None else False

        # Set hue color
        if hue is None:
            self.hue = RGBA(0, 255, 0, 255)  # Default green
        elif isinstance(hue, str):
            self.hue = RGBA.from_hex(hue)
        else:
            self.hue = hue

    @property
    def alpha(self) -> float:
        """Get normalized alpha channel (0.0-1.0)."""
        return self.hue.alpha / RGBA.MAXIMUM_CHANNEL

    @property
    def red(self) -> float:
        """Get normalized red channel (0.0-1.0)."""
        return self.hue.red / RGBA.MAXIMUM_CHANNEL

    @property
    def green(self) -> float:
        """Get normalized green channel (0.0-1.0)."""
        return self.hue.green / RGBA.MAXIMUM_CHANNEL

    @property
    def blue(self) -> float:
        """Get normalized blue channel (0.0-1.0)."""
        return self.hue.blue / RGBA.MAXIMUM_CHANNEL

    @property
    def parameters(self) -> dict[str, Any]:
        """Get effect parameters for serialization."""
        return {
            "clrCompensation": self.compensation,
            "color-alpha": self.alpha,
            "color-red": self.red,
            "color-green": self.green,
            "color-blue": self.blue,
            "defringe": self.defringe,
            "enabled": 1,
            "invertEffect": float(self.inverted),
            "softness": self.softness,
            "tolerance": self.tolerance,
        }

    @property
    def metadata(self) -> dict[str, Any]:
        """Get effect metadata for Camtasia project."""
        return {
            f"default-{self.name}-{key}": self._format_metadata_value(value)
            for key, value in self._metadata().items()
        }

    def _metadata(self) -> dict[str, Any]:
        """Get default metadata values."""
        return {
            "color": RGBA(0, 255, 0, 255).as_tuple(),  # Default green
            "defringe": 0.0,
            "invertEffect": 0,
            "softness": 0.1,
            "tolerance": 0.1,
            "clrCompensation": 0.0,
        }

    @staticmethod
    def _format_metadata_value(value: Any) -> str:
        """Format metadata value for Camtasia."""
        if isinstance(value, int | float) and value == 0:
            value = 0
        return str(value).replace(" ", "")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChromaKeyEffect:
        """Create ChromaKeyEffect from dictionary data."""
        params = data.get("parameters", {})

        # Extract color from float values
        hue = RGBA.from_floats(
            red=params.get("color-red", 0.0),
            green=params.get("color-green", 1.0),
            blue=params.get("color-blue", 0.0),
            alpha=params.get("color-alpha", 1.0),
        )

        return cls(
            tolerance=params.get("tolerance", 0.1),
            softness=params.get("softness", 0.1),
            defringe=params.get("defringe", 0.0),
            compensation=params.get("clrCompensation", 0.0),
            inverted=bool(params.get("invertEffect", 0)),
            hue=hue,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "effectName": self.name,
            "category": self.category,
            "parameters": self.parameters,
        }

    def __eq__(self, other: object) -> bool:
        """Check equality with another ChromaKey effect."""
        if not isinstance(other, ChromaKeyEffect):
            return False

        return (
            self.tolerance == other.tolerance
            and self.softness == other.softness
            and self.defringe == other.defringe
            and self.compensation == other.compensation
            and self.inverted == other.inverted
            and self.hue == other.hue
        )

    def __repr__(self) -> str:
        """String representation of ChromaKey effect."""
        return (
            f"ChromaKeyEffect(tolerance={self.tolerance}, softness={self.softness}, "
            f"defringe={self.defringe}, compensation={self.compensation}, "
            f"inverted={self.inverted}, hue={self.hue})"
        )
