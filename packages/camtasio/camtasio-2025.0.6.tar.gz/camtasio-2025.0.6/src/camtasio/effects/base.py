#!/usr/bin/env python3
"""Base classes for Camtasia effects."""
# this_file: src/camtasio/effects/base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Effect(ABC):
    """Base class for all Camtasia effects."""

    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """Get effect parameters as dictionary."""
        pass

    @property
    def metadata(self) -> dict[str, Any]:
        """Get effect metadata for Camtasia project."""
        return {
            f"default-{self.name}-{key}": self._format_metadata_value(value)
            for key, value in self._metadata().items()
        }

    @abstractmethod
    def _metadata(self) -> dict[str, Any]:
        """Get raw metadata dictionary."""
        pass

    @staticmethod
    def _format_metadata_value(value: Any) -> str:
        """Format metadata value for Camtasia."""
        if isinstance(value, int | float) and value == 0:
            value = 0
        return str(value).replace(" ", "")


class VisualEffect(Effect):
    """Base class for visual effects."""

    def __init__(self, name: str):
        super().__init__(name, "categoryVisualEffects")
