"""
PDF Measurement Tool

Interactive Python tool for measuring distances on PDF pages,
designed for biomechanics and materials analysis.
"""

__version__ = "0.2.0"
__author__ = "PDF Measure Tool"

from .pdf_loader import PdfDocument, PageImage, load_document
from .calibration import Calibration, page_scale_from_pdf, scale_from_known_length
from .measurement import Measurement, MeasurementCollection, ParticleDisplacement, Rectangle
from .export import export_measurements_csv, export_measurements_json
from .visualization import plot_rectangle_with_particles, create_visualization_from_json
from .gui import PdfMeasureViewer, run_viewer

__all__ = [
    "PdfDocument",
    "PageImage",
    "load_document",
    "Calibration",
    "page_scale_from_pdf",
    "scale_from_known_length",
    "Measurement",
    "MeasurementCollection",
    "ParticleDisplacement",
    "Rectangle",
    "export_measurements_csv",
    "export_measurements_json",
    "plot_rectangle_with_particles",
    "create_visualization_from_json",
    "PdfMeasureViewer",
    "run_viewer",
]
