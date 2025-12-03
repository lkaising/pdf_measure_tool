"""
Main entry point for PDF Measurement Tool.

Usage:
    python -m pdf_measure_tool path/to/file.pdf [--dpi DPI]
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive PDF measurement tool for biomechanics analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m pdf_measure_tool document.pdf
    python -m pdf_measure_tool document.pdf --dpi 200

Controls (in GUI):
    m       - Start measurement (click 2 points)
    c       - Calibrate (click 2 points, enter known distance)
    t       - Track particle displacement
    g       - Toggle measurement group
    s       - Save measurements to CSV/JSON
    ←/→     - Previous/next page
    h       - Show help
    q       - Quit
        """
    )

    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to the PDF file to measure."
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI for rendering PDF pages (default: 150). Higher = sharper but slower."
    )

    parser.add_argument(
        "--version",
        action="version",
        version="PDF Measurement Tool v0.2.0"
    )

    args = parser.parse_args()
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if pdf_path.suffix.lower() != ".pdf":
        print(f"Warning: File may not be a PDF: {pdf_path}", file=sys.stderr)

    from .pdf_loader import load_document
    from .gui import PdfMeasureViewer

    doc = load_document(str(pdf_path))
    viewer = PdfMeasureViewer(doc, dpi=args.dpi)
    viewer.run()
    doc.close()


if __name__ == "__main__":
    main()
