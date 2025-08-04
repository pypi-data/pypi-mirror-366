#!/usr/bin/env python3
"""Timing utilities for frame-based time calculations."""
# this_file: src/camtasio/utils/timing.py

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class FrameStamp:
    """Timestamp representation using frame number and frame rate.

    Times in Camtasia projects are frame-based. This class provides
    conversion between frame numbers and clock time.
    """

    frame_number: int
    frame_rate: int

    def __post_init__(self) -> None:
        """Validate frame stamp values."""
        if self.frame_rate <= 0:
            raise ValueError(f"Frame rate must be positive, got {self.frame_rate}")
        if self.frame_number < 0:
            raise ValueError(f"Frame number must be non-negative, got {self.frame_number}")

    @property
    def frame_time(self) -> tuple[timedelta, int]:
        """Get time as (seconds_timedelta, subsecond_frames).

        This matches Camtasia's UI time display format where time is shown
        at second resolution with sub-second timing in frames.

        Returns:
            Tuple of (timedelta for whole seconds, remaining frames)
        """
        seconds, sub_frames = divmod(self.frame_number, self.frame_rate)
        return (timedelta(seconds=seconds), sub_frames)

    @property
    def time(self) -> timedelta:
        """Get high-resolution time as timedelta.

        Returns:
            timedelta with subsecond precision
        """
        seconds = self.frame_number / self.frame_rate
        return timedelta(seconds=seconds)

    @property
    def total_seconds(self) -> float:
        """Get total time in seconds as float."""
        return self.frame_number / self.frame_rate

    @classmethod
    def from_seconds(cls, seconds: float, frame_rate: int) -> FrameStamp:
        """Create FrameStamp from seconds.

        Args:
            seconds: Time in seconds
            frame_rate: Frame rate to use

        Returns:
            New FrameStamp instance
        """
        frame_number = round(seconds * frame_rate)
        return cls(frame_number=frame_number, frame_rate=frame_rate)

    @classmethod
    def from_timedelta(cls, td: timedelta, frame_rate: int) -> FrameStamp:
        """Create FrameStamp from timedelta.

        Args:
            td: timedelta instance
            frame_rate: Frame rate to use

        Returns:
            New FrameStamp instance
        """
        return cls.from_seconds(td.total_seconds(), frame_rate)

    def __str__(self) -> str:
        """Format as 'seconds;frames' (Camtasia style)."""
        secs, frames = self.frame_time
        return f'{int(secs.total_seconds())};{frames}'

    def __repr__(self) -> str:
        """Detailed representation."""
        return f'FrameStamp(frame_number={self.frame_number}, frame_rate={self.frame_rate})'

    def __lt__(self, other: FrameStamp) -> bool:
        """Compare by time value."""
        if not isinstance(other, FrameStamp):
            return NotImplemented
        return self.time < other.time

    def __le__(self, other: FrameStamp) -> bool:
        """Compare by time value."""
        if not isinstance(other, FrameStamp):
            return NotImplemented
        return self.time <= other.time

    def __gt__(self, other: FrameStamp) -> bool:
        """Compare by time value."""
        if not isinstance(other, FrameStamp):
            return NotImplemented
        return self.time > other.time

    def __ge__(self, other: FrameStamp) -> bool:
        """Compare by time value."""
        if not isinstance(other, FrameStamp):
            return NotImplemented
        return self.time >= other.time

    def __add__(self, other: FrameStamp) -> FrameStamp:
        """Add two FrameStamps together."""
        if not isinstance(other, FrameStamp):
            return NotImplemented
        return self._add_frame_stamps(
            self.frame_rate, self.frame_number,
            other.frame_rate, other.frame_number
        )

    def __sub__(self, other: FrameStamp) -> FrameStamp:
        """Subtract one FrameStamp from another."""
        if not isinstance(other, FrameStamp):
            return NotImplemented
        return self._add_frame_stamps(
            self.frame_rate, self.frame_number,
            other.frame_rate, -other.frame_number
        )

    @staticmethod
    def _add_frame_stamps(
        frame_rate_1: int, frame_number_1: int,
        frame_rate_2: int, frame_number_2: int
    ) -> FrameStamp:
        """Add two frame stamps with different frame rates.

        The result uses the least common multiple of the frame rates
        to maintain precision.
        """
        # Find least common multiple of frame rates
        common_frame_rate = _lcm(frame_rate_1, frame_rate_2)

        # Convert frame numbers to common frame rate
        frame_1_scaled = (common_frame_rate // frame_rate_1) * frame_number_1
        frame_2_scaled = (common_frame_rate // frame_rate_2) * frame_number_2

        return FrameStamp(
            frame_number=frame_1_scaled + frame_2_scaled,
            frame_rate=common_frame_rate
        )

    def to_frame_rate(self, new_frame_rate: int) -> FrameStamp:
        """Convert to a different frame rate.

        Args:
            new_frame_rate: Target frame rate

        Returns:
            New FrameStamp with converted frame rate
        """
        seconds = self.total_seconds
        new_frame_number = round(seconds * new_frame_rate)
        return FrameStamp(
            frame_number=new_frame_number,
            frame_rate=new_frame_rate
        )


def _lcm(a: int, b: int) -> int:
    """Calculate least common multiple of two integers."""
    return abs(a * b) // math.gcd(a, b)
