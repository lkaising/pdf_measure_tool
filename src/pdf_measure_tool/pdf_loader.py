"""
PDF loading and rendering module.

Handles loading PDF documents and rendering pages as numpy arrays.
"""

import fitz  # PyMuPDF
import numpy as np
from dataclasses import dataclass
from typing import Optional

from .config import DEFAULT_DPI, POINTS_PER_INCH, MM_PER_INCH


@dataclass
class PageImage:
    """Represents a rendered PDF page as an image with metadata."""
    image: np.ndarray
    width_px: int
    height_px: int
    width_mm: float
    height_mm: float
    page_index: int
    dpi: int
    
    @property
    def mm_per_pixel(self) -> float:
        """Calculate mm per pixel based on page dimensions."""
        return self.width_mm / self.width_px


class PdfDocument:
    """Wrapper for a PDF document with rendering capabilities."""
    
    def __init__(self, path: str):
        """
        Load a PDF document.
        
        Args:
            path: Path to the PDF file.
        """
        self.path = path
        self._doc = fitz.open(path)
        self._cached_pages: dict[tuple[int, int], PageImage] = {}
    
    @property
    def num_pages(self) -> int:
        """Get the number of pages in the document."""
        return len(self._doc)
    
    def get_page_size_mm(self, page_index: int) -> tuple[float, float]:
        """
        Get the page size in millimeters.
        
        Args:
            page_index: Zero-based page index.
            
        Returns:
            Tuple of (width_mm, height_mm).
        """
        page = self._doc[page_index]
        rect = page.rect
        # rect is in points, convert to mm
        width_mm = rect.width / POINTS_PER_INCH * MM_PER_INCH
        height_mm = rect.height / POINTS_PER_INCH * MM_PER_INCH
        return width_mm, height_mm
    
    def render_page(self, page_index: int, dpi: int = DEFAULT_DPI, 
                    use_cache: bool = True) -> PageImage:
        """
        Render a PDF page to an image.
        
        Args:
            page_index: Zero-based page index.
            dpi: Resolution to render at.
            use_cache: Whether to use cached renders.
            
        Returns:
            PageImage with the rendered page and metadata.
        """
        cache_key = (page_index, dpi)
        
        if use_cache and cache_key in self._cached_pages:
            return self._cached_pages[cache_key]
        
        page = self._doc[page_index]
        
        # Calculate zoom factor for desired DPI
        zoom = dpi / POINTS_PER_INCH
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to numpy array
        if pix.alpha:
            image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, 4
            )
        else:
            image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, 3
            )
        
        # Get page size in mm
        width_mm, height_mm = self.get_page_size_mm(page_index)
        
        page_image = PageImage(
            image=image.copy(),  # Copy to avoid memory issues
            width_px=pix.width,
            height_px=pix.height,
            width_mm=width_mm,
            height_mm=height_mm,
            page_index=page_index,
            dpi=dpi
        )
        
        if use_cache:
            self._cached_pages[cache_key] = page_image
        
        return page_image
    
    def close(self):
        """Close the document."""
        self._doc.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def load_document(path: str) -> PdfDocument:
    """
    Load a PDF document.
    
    Args:
        path: Path to the PDF file.
        
    Returns:
        PdfDocument object.
    """
    return PdfDocument(path)
