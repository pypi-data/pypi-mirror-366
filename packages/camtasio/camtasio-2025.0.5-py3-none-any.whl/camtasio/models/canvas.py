# this_file: src/camtasio/models/canvas.py
"""Canvas model representing project dimensions and settings."""

from dataclasses import dataclass
from typing import Self, Any


@dataclass(frozen=True)
class Canvas:
    """Represents the canvas (project dimensions) of a Camtasia project.

    This is an immutable class - all operations return new instances.
    """

    width: float
    height: float
    frame_rate: int = 30

    def scale(self, factor: float) -> Self:
        """Return a new Canvas scaled by the given factor.

        Args:
            factor: Scale factor (e.g., 1.5 for 150%)

        Returns:
            New Canvas instance with scaled dimensions
        """
        return Canvas(
            width=self.width * factor,
            height=self.height * factor,
            frame_rate=self.frame_rate,  # Frame rate doesn't scale
        )

    def resize(self, width: float | None = None, height: float | None = None) -> Self:
        """Return a new Canvas with specified dimensions.

        Args:
            width: New width (uses current if None)
            height: New height (uses current if None)

        Returns:
            New Canvas instance with updated dimensions
        """
        return cls(
            width=width if width is not None else self.width,
            height=height if height is not None else self.height,
            frame_rate=self.frame_rate,
        )

    @property
    def aspect_ratio(self) -> float:
        """Calculate the aspect ratio (width/height)."""
        return self.width / self.height if self.height > 0 else 0

    @property
    def is_landscape(self) -> bool:
        """Check if canvas is landscape orientation."""
        return self.width > self.height

    @property
    def is_portrait(self) -> bool:
        """Check if canvas is portrait orientation."""
        return self.height > self.width

    @property
    def is_square(self) -> bool:
        """Check if canvas is square."""
        return self.width == self.height

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {"width": self.width, "height": self.height, "videoFormatFrameRate": self.frame_rate}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create Canvas from dictionary.

        Args:
            data: Dictionary with canvas data

        Returns:
            New Canvas instance
        """
        return cls(
            width=float(data.get("width", 1920)),
            height=float(data.get("height", 1080)),
            frame_rate=int(data.get("videoFormatFrameRate", 30)),
        )

    @classmethod
    def standard_sizes(cls) -> dict[str, Self]:
        """Get common standard canvas sizes."""
        return {
            "720p": cls(1280, 720, 30),
            "1080p": cls(1920, 1080, 30),
            "1080p60": cls(1920, 1080, 60),
            "4K": cls(3840, 2160, 30),
            "4K60": cls(3840, 2160, 60),
            "square": cls(1080, 1080, 30),
            "vertical": cls(1080, 1920, 30),
        }
