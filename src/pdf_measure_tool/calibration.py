"""
Calibration module for converting pixel distances to physical units.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class Calibration:
    """Represents a calibration for converting pixels to mm."""
    mm_per_pixel: float
    source: str  # "page" or "manual"
    page_index: Optional[int] = None
    point1_px: Optional[tuple[float, float]] = None
    point2_px: Optional[tuple[float, float]] = None
    known_length_mm: Optional[float] = None

    def pixels_to_mm(self, pixel_distance: float) -> float:
        """Convert a pixel distance to millimeters."""
        return pixel_distance * self.mm_per_pixel

    def mm_to_pixels(self, mm_distance: float) -> float:
        """Convert a millimeter distance to pixels."""
        return mm_distance / self.mm_per_pixel


def page_scale_from_pdf(page_width_mm: float, page_width_px: int) -> Calibration:
    """
    Create a calibration based on PDF page dimensions.

    This assumes the PDF page is rendered at true scale.

    Args:
        page_width_mm: Width of the page in millimeters.
        page_width_px: Width of the rendered page in pixels.

    Returns:
        Calibration object.
    """
    mm_per_pixel = page_width_mm / page_width_px
    return Calibration(
        mm_per_pixel=mm_per_pixel,
        source="page"
    )


def scale_from_known_length(
    p1_px: tuple[float, float],
    p2_px: tuple[float, float],
    known_length_mm: float,
    page_index: Optional[int] = None
) -> Calibration:
    """
    Create a calibration from two points with a known distance.

    Args:
        p1_px: First point in pixels (x, y).
        p2_px: Second point in pixels (x, y).
        known_length_mm: Known distance between points in millimeters.
        page_index: Optional page index where calibration was performed.

    Returns:
        Calibration object.
    """
    dx = p2_px[0] - p1_px[0]
    dy = p2_px[1] - p1_px[1]
    pixel_distance = np.sqrt(dx**2 + dy**2)

    mm_per_pixel = known_length_mm / pixel_distance

    return Calibration(
        mm_per_pixel=mm_per_pixel,
        source="manual",
        page_index=page_index,
        point1_px=p1_px,
        point2_px=p2_px,
        known_length_mm=known_length_mm
    )


def calculate_pixel_distance(
    p1: tuple[float, float],
    p2: tuple[float, float]
) -> float:
    """
    Calculate Euclidean distance between two points in pixels.

    Args:
        p1: First point (x, y).
        p2: Second point (x, y).

    Returns:
        Distance in pixels.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.sqrt(dx**2 + dy**2)
