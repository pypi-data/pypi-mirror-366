# this_file: src/camtasio/serialization/json_encoder.py
"""Custom JSON encoder for Camtasia projects."""

import json
import math
from typing import Any

from loguru import logger


class CamtasiaJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles special float values for Camtasia."""

    # Maximum negative value that Camtasia seems to accept
    # Use slightly smaller than the max to avoid infinity
    MIN_SAFE_FLOAT = -1.7976931348623157e308

    def encode(self, o: Any) -> str:
        """Encode object to JSON string."""
        # First, preprocess the object to handle special values
        processed = self._preprocess(o)
        return super().encode(processed)

    def _preprocess(self, obj: Any) -> Any:
        """Preprocess object to handle special float values."""
        if isinstance(obj, float):
            if math.isinf(obj):
                if obj < 0:
                    logger.warning("Converting -Infinity to safe minimum value")
                    return self.MIN_SAFE_FLOAT
                else:
                    logger.warning("Converting Infinity to safe maximum value")
                    return -self.MIN_SAFE_FLOAT  # Positive max
            elif math.isnan(obj):
                logger.warning("Converting NaN to 0.0")
                return 0.0
            return obj
        elif isinstance(obj, dict):
            return {k: self._preprocess(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._preprocess(item) for item in obj]
        return obj

    def iterencode(self, o: Any, _one_shot: bool = False):
        """Encode object to JSON string iteratively."""
        # Preprocess before encoding
        processed = self._preprocess(o)
        return super().iterencode(processed, _one_shot)
