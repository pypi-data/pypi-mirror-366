#!/usr/bin/env python3
"""Callout annotation creation functions."""
# this_file: src/camtasio/annotations/callouts.py

from typing import Dict, Any, Optional

from camtasio.annotations.types import (
    Color,
    FillStyle,
    StrokeStyle,
    HorizontalAlignment,
    VerticalAlignment,
)


def text_callout(
    text: str,
    font_name: str,
    font_weight: str,
    font_size: float = 96.0,
    font_color: Optional[Color] = None,
    height: float = 250.0,
    width: float = 400.0,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
    line_spacing: float = 0.0
) -> Dict[str, Any]:
    """Create a text callout annotation.
    
    Args:
        text: The text content
        font_name: Font family name
        font_weight: Font weight (e.g., "normal", "bold")
        font_size: Font size in points
        font_color: Text color (defaults to white)
        height: Callout height
        width: Callout width
        horizontal_alignment: Text horizontal alignment
        vertical_alignment: Text vertical alignment
        line_spacing: Line spacing
        
    Returns:
        Dictionary representing the text callout
    """
    if font_color is None:
        font_color = Color.white()
    
    return {
        "kind": "remix",
        "shape": "text",
        "style": "basic",
        "height": float(height),
        "line-spacing": float(line_spacing),
        "width": float(width),
        "word-wrap": 1.0,
        "horizontal-alignment": horizontal_alignment.value,
        "resize-behavior": "resizeText",
        "text": str(text),
        "vertical-alignment": vertical_alignment.value,
        "font": {
            "color-blue": font_color.blue,
            "color-green": font_color.green,
            "color-red": font_color.red,
            "size": float(font_size),
            "tracking": 0.0,
            "name": str(font_name),
            "weight": str(font_weight)
        },
        "textAttributes": {
            "type": "textAttributeList",
            "keyframes": [
                {
                    "endTime": 0,
                    "time": 0,
                    "value": None,
                    "duration": 0
                }
            ]
        }
    }


def square_callout(
    text: str,
    font_name: str,
    font_weight: str,
    font_size: float = 64.0,
    font_color: Optional[Color] = None,
    fill_color: Optional[Color] = None,
    fill_style: FillStyle = FillStyle.SOLID,
    stroke_color: Optional[Color] = None,
    stroke_width: float = 2.0,
    stroke_style: StrokeStyle = StrokeStyle.SOLID,
    height: float = 150.0,
    width: float = 350.0,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
    line_spacing: float = 0.0,
    tail_x: float = 0.0,
    tail_y: float = -20.0
) -> Dict[str, Any]:
    """Create a square callout annotation with optional tail.
    
    Args:
        text: The text content
        font_name: Font family name
        font_weight: Font weight (e.g., "normal", "bold")
        font_size: Font size in points
        font_color: Text color (defaults to black)
        fill_color: Background fill color (defaults to white)
        fill_style: Fill style (solid or gradient)
        stroke_color: Border stroke color (defaults to teal)
        stroke_width: Border stroke width
        stroke_style: Border stroke style
        height: Callout height
        width: Callout width
        horizontal_alignment: Text horizontal alignment
        vertical_alignment: Text vertical alignment
        line_spacing: Line spacing
        tail_x: Tail X position relative to center
        tail_y: Tail Y position relative to center
        
    Returns:
        Dictionary representing the square callout
    """
    if font_color is None:
        font_color = Color.black()
    if fill_color is None:
        fill_color = Color.white()
    if stroke_color is None:
        stroke_color = Color(0.0, 0.5, 0.5, 1.0)  # Teal
    
    return {
        "kind": "remix",
        "shape": "text-rectangle",
        "style": "basic",
        "fill-color-blue": fill_color.blue,
        "fill-color-green": fill_color.green,
        "fill-color-opacity": fill_color.opacity,
        "fill-color-red": fill_color.red,
        "height": float(height),
        "line-spacing": float(line_spacing),
        "stroke-color-blue": stroke_color.blue,
        "stroke-color-green": stroke_color.green,
        "stroke-color-opacity": stroke_color.opacity,
        "stroke-color-red": stroke_color.red,
        "stroke-width": float(stroke_width),
        "tail-x": float(tail_x),
        "tail-y": float(tail_y),
        "width": float(width),
        "word-wrap": 1.0,
        "fill-style": fill_style.value,
        "horizontal-alignment": horizontal_alignment.value,
        "resize-behavior": "resizeText",
        "stroke-style": stroke_style.value,
        "text": str(text),
        "vertical-alignment": vertical_alignment.value,
        "font": {
            "color-blue": font_color.blue,
            "color-green": font_color.green,
            "color-opacity": font_color.opacity,
            "color-red": font_color.red,
            "size": float(font_size),
            "tracking": 0.0,
            "name": str(font_name),
            "weight": str(font_weight)
        },
        "textAttributes": {
            "type": "textAttributeList",
            "keyframes": [
                {
                    "endTime": 0,
                    "time": 0,
                    "value": None,
                    "duration": 0
                }
            ]
        }
    }