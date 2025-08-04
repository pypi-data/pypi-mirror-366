# this_file: src/camtasio/serialization/json_handler.py
"""Centralized JSON handling with orjson support."""

from pathlib import Path
from typing import Any

try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False

from loguru import logger


def load_json_file(file_path: str | Path) -> dict[str, Any]:
    """Load JSON from file using orjson if available.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    path = Path(file_path)

    if HAS_ORJSON:
        logger.debug("Using orjson for faster JSON parsing")
        with open(path, "rb") as f:
            return orjson.loads(f.read())
    else:
        logger.debug("Using standard json library")
        with open(path, encoding="utf-8") as f:
            return json.load(f)


def save_json_file(
    data: dict[str, Any], file_path: str | Path, indent: int = 2, ensure_ascii: bool = False
) -> None:
    """Save JSON to file using orjson if available.

    Args:
        data: Data to save
        file_path: Path to save to
        indent: Indentation level (only 2 supported with orjson)
        ensure_ascii: Whether to escape non-ASCII characters
    """
    path = Path(file_path)

    if HAS_ORJSON:
        logger.debug("Using orjson for faster JSON serialization")
        # orjson handles formatting differently
        options = orjson.OPT_INDENT_2 if indent == 2 else 0
        if not ensure_ascii:
            options |= orjson.OPT_NON_STR_KEYS

        # orjson returns bytes, so we write in binary mode
        with open(path, "wb") as f:
            f.write(orjson.dumps(data, option=options))
    else:
        logger.debug("Using standard json library")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                separators=(",", ": "),
            )


def dumps_json(data: dict[str, Any], indent: int = 2, ensure_ascii: bool = False) -> str:
    """Convert data to JSON string using orjson if available.

    Args:
        data: Data to serialize
        indent: Indentation level (only 2 supported with orjson)
        ensure_ascii: Whether to escape non-ASCII characters

    Returns:
        JSON string
    """
    if HAS_ORJSON:
        # orjson handles formatting differently
        options = orjson.OPT_INDENT_2 if indent == 2 else 0
        if not ensure_ascii:
            options |= orjson.OPT_NON_STR_KEYS
        return orjson.dumps(data, option=options).decode("utf-8")
    else:
        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            separators=(",", ": "),
        )


def loads_json(json_str: str) -> dict[str, Any]:
    """Parse JSON string using orjson if available.

    Args:
        json_str: JSON string to parse

    Returns:
        Parsed data
    """
    if HAS_ORJSON:
        return orjson.loads(json_str)
    else:
        return json.loads(json_str)
