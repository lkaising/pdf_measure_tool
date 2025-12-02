"""
Measurement data models and calculations.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Point:
    """A 2D point with pixel coordinates."""
    x: float
    y: float
    
    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)
    
    @classmethod
    def from_tuple(cls, t: tuple[float, float]) -> "Point":
        return cls(x=t[0], y=t[1])


@dataclass
class Measurement:
    """Represents a distance measurement between two points."""
    id: int
    label: str
    page_index: int
    point1_px: tuple[float, float]
    point2_px: tuple[float, float]
    pixel_distance: float
    length_mm: Optional[float]
    group: str = "default"  # e.g., "pre", "post", "fiber", "edge"
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""
    
    @property
    def dx_px(self) -> float:
        """Horizontal displacement in pixels."""
        return self.point2_px[0] - self.point1_px[0]
    
    @property
    def dy_px(self) -> float:
        """Vertical displacement in pixels."""
        return self.point2_px[1] - self.point1_px[1]
    
    @property
    def angle_degrees(self) -> float:
        """Angle of measurement line in degrees (from horizontal)."""
        return np.degrees(np.arctan2(self.dy_px, self.dx_px))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            "id": self.id,
            "label": self.label,
            "group": self.group,
            "page": self.page_index,
            "x1_px": self.point1_px[0],
            "y1_px": self.point1_px[1],
            "x2_px": self.point2_px[0],
            "y2_px": self.point2_px[1],
            "dx_px": self.dx_px,
            "dy_px": self.dy_px,
            "pixel_distance": self.pixel_distance,
            "length_mm": self.length_mm,
            "angle_deg": self.angle_degrees,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes,
        }


@dataclass
class ParticleDisplacement:
    """Represents a particle tracked between pre and post images."""
    id: int
    label: str
    pre_position_px: tuple[float, float]
    post_position_px: tuple[float, float]
    pre_page_index: int
    post_page_index: int
    displacement_px: tuple[float, float]
    displacement_mm: Optional[tuple[float, float]]
    
    @property
    def displacement_magnitude_px(self) -> float:
        """Magnitude of displacement in pixels."""
        return np.sqrt(self.displacement_px[0]**2 + self.displacement_px[1]**2)
    
    @property
    def displacement_magnitude_mm(self) -> Optional[float]:
        """Magnitude of displacement in mm."""
        if self.displacement_mm is None:
            return None
        return np.sqrt(self.displacement_mm[0]**2 + self.displacement_mm[1]**2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            "id": self.id,
            "label": self.label,
            "pre_x_px": self.pre_position_px[0],
            "pre_y_px": self.pre_position_px[1],
            "post_x_px": self.post_position_px[0],
            "post_y_px": self.post_position_px[1],
            "pre_page": self.pre_page_index,
            "post_page": self.post_page_index,
            "dx_px": self.displacement_px[0],
            "dy_px": self.displacement_px[1],
            "displacement_magnitude_px": self.displacement_magnitude_px,
            "dx_mm": self.displacement_mm[0] if self.displacement_mm else None,
            "dy_mm": self.displacement_mm[1] if self.displacement_mm else None,
            "displacement_magnitude_mm": self.displacement_magnitude_mm,
        }


class MeasurementCollection:
    """Collection of measurements with utility methods."""
    
    def __init__(self):
        self.measurements: List[Measurement] = []
        self.particles: List[ParticleDisplacement] = []
        self._next_measurement_id = 1
        self._next_particle_id = 1
    
    def add_measurement(
        self,
        label: str,
        page_index: int,
        point1_px: tuple[float, float],
        point2_px: tuple[float, float],
        mm_per_pixel: Optional[float] = None,
        group: str = "default",
        notes: str = ""
    ) -> Measurement:
        """
        Add a new measurement.
        
        Args:
            label: Label for the measurement.
            page_index: Page where measurement was made.
            point1_px: First point in pixels.
            point2_px: Second point in pixels.
            mm_per_pixel: Scale factor for conversion (None if uncalibrated).
            group: Group/category for the measurement.
            notes: Optional notes.
            
        Returns:
            The created Measurement object.
        """
        pixel_distance = distance_px(point1_px, point2_px)
        length_mm = pixel_distance * mm_per_pixel if mm_per_pixel else None
        
        measurement = Measurement(
            id=self._next_measurement_id,
            label=label,
            page_index=page_index,
            point1_px=point1_px,
            point2_px=point2_px,
            pixel_distance=pixel_distance,
            length_mm=length_mm,
            group=group,
            notes=notes,
        )
        
        self.measurements.append(measurement)
        self._next_measurement_id += 1
        
        return measurement
    
    def add_particle(
        self,
        label: str,
        pre_position_px: tuple[float, float],
        post_position_px: tuple[float, float],
        pre_page_index: int,
        post_page_index: int,
        mm_per_pixel: Optional[float] = None
    ) -> ParticleDisplacement:
        """
        Add a particle displacement tracking.
        
        Args:
            label: Label for the particle.
            pre_position_px: Position in pre-test image (pixels).
            post_position_px: Position in post-test image (pixels).
            pre_page_index: Page index of pre-test image.
            post_page_index: Page index of post-test image.
            mm_per_pixel: Scale factor for conversion.
            
        Returns:
            The created ParticleDisplacement object.
        """
        dx = post_position_px[0] - pre_position_px[0]
        dy = post_position_px[1] - pre_position_px[1]
        displacement_px = (dx, dy)
        
        displacement_mm = None
        if mm_per_pixel:
            displacement_mm = (dx * mm_per_pixel, dy * mm_per_pixel)
        
        particle = ParticleDisplacement(
            id=self._next_particle_id,
            label=label,
            pre_position_px=pre_position_px,
            post_position_px=post_position_px,
            pre_page_index=pre_page_index,
            post_page_index=post_page_index,
            displacement_px=displacement_px,
            displacement_mm=displacement_mm,
        )
        
        self.particles.append(particle)
        self._next_particle_id += 1
        
        return particle
    
    def delete_last_measurement(self) -> Optional[Measurement]:
        """Remove and return the last measurement."""
        if self.measurements:
            return self.measurements.pop()
        return None
    
    def delete_last_particle(self) -> Optional[ParticleDisplacement]:
        """Remove and return the last particle."""
        if self.particles:
            return self.particles.pop()
        return None
    
    def clear_all(self):
        """Clear all measurements and particles."""
        self.measurements.clear()
        self.particles.clear()
        self._next_measurement_id = 1
        self._next_particle_id = 1
    
    def get_measurements_by_group(self, group: str) -> List[Measurement]:
        """Get all measurements in a specific group."""
        return [m for m in self.measurements if m.group == group]
    
    def get_measurements_by_page(self, page_index: int) -> List[Measurement]:
        """Get all measurements on a specific page."""
        return [m for m in self.measurements if m.page_index == page_index]
    
    def update_calibration(self, mm_per_pixel: float):
        """Update all measurements with new calibration."""
        for m in self.measurements:
            m.length_mm = m.pixel_distance * mm_per_pixel
        
        for p in self.particles:
            dx = p.displacement_px[0] * mm_per_pixel
            dy = p.displacement_px[1] * mm_per_pixel
            p.displacement_mm = (dx, dy)


def distance_px(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points in pixels."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.sqrt(dx**2 + dy**2)


def length_mm(
    p1: tuple[float, float],
    p2: tuple[float, float],
    mm_per_pixel: float
) -> float:
    """Calculate distance between two points in millimeters."""
    return distance_px(p1, p2) * mm_per_pixel
