"""Effects system for Camtasia projects."""
# this_file: src/camtasio/effects/__init__.py

from camtasio.effects.base import Effect, VisualEffect
from camtasio.effects.chroma_key import ChromaKeyEffect

__all__ = ["ChromaKeyEffect", "Effect", "VisualEffect"]
