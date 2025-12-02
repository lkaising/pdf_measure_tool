"""
Export module for saving measurements to various formats.
"""

import csv
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from .measurement import MeasurementCollection, Measurement, ParticleDisplacement
from .calibration import Calibration
from .config import DEFAULT_CSV_OUTPUT, DEFAULT_JSON_OUTPUT


def export_measurements_csv(
    collection: MeasurementCollection,
    path: str,
    calibration: Optional[Calibration] = None
) -> str:
    """
    Export measurements to a CSV file.
    
    Args:
        collection: MeasurementCollection to export.
        path: Output file path.
        calibration: Optional calibration info to include in header.
        
    Returns:
        Path to the created file.
    """
    path = Path(path)
    
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        
        # Write header comment with metadata
        if calibration:
            f.write(f"# Calibration: {calibration.mm_per_pixel:.6f} mm/pixel ({calibration.source})\n")
        f.write(f"# Exported: {datetime.now().isoformat()}\n")
        
        # Write measurements
        if collection.measurements:
            f.write("# === MEASUREMENTS ===\n")
            headers = [
                "id", "label", "group", "page", 
                "x1_px", "y1_px", "x2_px", "y2_px",
                "dx_px", "dy_px", "pixel_distance", 
                "length_mm", "angle_deg", "notes"
            ]
            writer.writerow(headers)
            
            for m in collection.measurements:
                writer.writerow([
                    m.id, m.label, m.group, m.page_index,
                    f"{m.point1_px[0]:.2f}", f"{m.point1_px[1]:.2f}",
                    f"{m.point2_px[0]:.2f}", f"{m.point2_px[1]:.2f}",
                    f"{m.dx_px:.2f}", f"{m.dy_px:.2f}",
                    f"{m.pixel_distance:.2f}",
                    f"{m.length_mm:.4f}" if m.length_mm else "N/A",
                    f"{m.angle_degrees:.2f}",
                    m.notes
                ])
        
        # Write particle displacements
        if collection.particles:
            f.write("\n# === PARTICLE DISPLACEMENTS ===\n")
            headers = [
                "id", "label",
                "pre_x_px", "pre_y_px", "post_x_px", "post_y_px",
                "pre_page", "post_page",
                "dx_px", "dy_px", "magnitude_px",
                "dx_mm", "dy_mm", "magnitude_mm"
            ]
            writer.writerow(headers)
            
            for p in collection.particles:
                writer.writerow([
                    p.id, p.label,
                    f"{p.pre_position_px[0]:.2f}", f"{p.pre_position_px[1]:.2f}",
                    f"{p.post_position_px[0]:.2f}", f"{p.post_position_px[1]:.2f}",
                    p.pre_page_index, p.post_page_index,
                    f"{p.displacement_px[0]:.2f}", f"{p.displacement_px[1]:.2f}",
                    f"{p.displacement_magnitude_px:.2f}",
                    f"{p.displacement_mm[0]:.4f}" if p.displacement_mm else "N/A",
                    f"{p.displacement_mm[1]:.4f}" if p.displacement_mm else "N/A",
                    f"{p.displacement_magnitude_mm:.4f}" if p.displacement_magnitude_mm else "N/A",
                ])
    
    return str(path)


def export_measurements_json(
    collection: MeasurementCollection,
    path: str,
    calibration: Optional[Calibration] = None
) -> str:
    """
    Export measurements to a JSON file.
    
    Args:
        collection: MeasurementCollection to export.
        path: Output file path.
        calibration: Optional calibration info to include.
        
    Returns:
        Path to the created file.
    """
    path = Path(path)
    
    data = {
        "metadata": {
            "exported": datetime.now().isoformat(),
            "calibration": {
                "mm_per_pixel": calibration.mm_per_pixel if calibration else None,
                "source": calibration.source if calibration else None,
            }
        },
        "measurements": [m.to_dict() for m in collection.measurements],
        "particles": [p.to_dict() for p in collection.particles],
    }
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    
    return str(path)


def load_measurements_json(path: str) -> tuple[MeasurementCollection, Optional[Calibration]]:
    """
    Load measurements from a JSON file.
    
    Args:
        path: Path to JSON file.
        
    Returns:
        Tuple of (MeasurementCollection, Calibration or None).
    """
    from .calibration import Calibration
    
    with open(path, "r") as f:
        data = json.load(f)
    
    collection = MeasurementCollection()
    
    # Load measurements
    for m_data in data.get("measurements", []):
        measurement = Measurement(
            id=m_data["id"],
            label=m_data["label"],
            page_index=m_data["page"],
            point1_px=(m_data["x1_px"], m_data["y1_px"]),
            point2_px=(m_data["x2_px"], m_data["y2_px"]),
            pixel_distance=m_data["pixel_distance"],
            length_mm=m_data.get("length_mm"),
            group=m_data.get("group", "default"),
            notes=m_data.get("notes", ""),
        )
        collection.measurements.append(measurement)
        collection._next_measurement_id = max(collection._next_measurement_id, measurement.id + 1)
    
    # Load particles
    for p_data in data.get("particles", []):
        particle = ParticleDisplacement(
            id=p_data["id"],
            label=p_data["label"],
            pre_position_px=(p_data["pre_x_px"], p_data["pre_y_px"]),
            post_position_px=(p_data["post_x_px"], p_data["post_y_px"]),
            pre_page_index=p_data["pre_page"],
            post_page_index=p_data["post_page"],
            displacement_px=(p_data["dx_px"], p_data["dy_px"]),
            displacement_mm=(p_data.get("dx_mm"), p_data.get("dy_mm")) if p_data.get("dx_mm") else None,
        )
        collection.particles.append(particle)
        collection._next_particle_id = max(collection._next_particle_id, particle.id + 1)
    
    # Load calibration
    calibration = None
    cal_data = data.get("metadata", {}).get("calibration", {})
    if cal_data.get("mm_per_pixel"):
        calibration = Calibration(
            mm_per_pixel=cal_data["mm_per_pixel"],
            source=cal_data.get("source", "loaded"),
        )
    
    return collection, calibration
