"""
Matplotlib-based GUI for PDF measurement tool.
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
import numpy as np
from enum import Enum, auto
from typing import Optional, List, Callable
from pathlib import Path

from .pdf_loader import PdfDocument, PageImage
from .calibration import Calibration, page_scale_from_pdf
from .measurement import MeasurementCollection, Measurement, Rectangle
from .export import export_measurements_csv, export_measurements_json
from .config import (
    MEASUREMENT_LINE_COLOR, MEASUREMENT_POINT_COLOR,
    POINT_MARKER_SIZE, LINE_WIDTH, LABEL_FONT_SIZE,
    SHORTCUTS, DEFAULT_DPI
)


class Mode(Enum):
    """Interaction modes for the viewer."""
    VIEW = auto()
    MEASURE = auto()
    PARTICLE_PRE = auto()
    PARTICLE_POST = auto()


class PdfMeasureViewer:
    """Interactive PDF viewer with measurement capabilities."""

    def __init__(self, document: PdfDocument, dpi: int = DEFAULT_DPI):
        """
        Initialize the viewer.

        Args:
            document: PdfDocument to view.
            dpi: DPI for rendering pages.
        """
        self.doc = document
        self.dpi = dpi
        self.current_page = 0

        # State
        self.mode = Mode.VIEW
        self.current_group = "pre"
        self.measurements = MeasurementCollection()
        self.calibration: Optional[Calibration] = None

        # Temporary click storage
        self._click_points: List[tuple[float, float]] = []
        self._temp_particle_pre: Optional[tuple[float, float]] = None
        self._temp_particle_pre_page: Optional[int] = None
        self._measurement_label_counter = 1
        self._particle_label_counter = 1

        # Plot elements to track for removal
        self._temp_artists = []
        self._rectangle_artists = []

        # Set up the figure
        self._setup_figure()

        # Load first page
        self._load_page(0)

        # Initialize with page-based calibration
        self._auto_calibrate()

    def _setup_figure(self):
        """Set up the matplotlib figure and axes."""
        self.fig, self.ax = plt.subplots(figsize=(12, 9))
        plt.subplots_adjust(bottom=0.15, top=0.92)

        # Status text at top
        self.status_text = self.fig.text(
            0.5, 0.96, "", ha="center", va="top", fontsize=10,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8)
        )

        # Info text at bottom
        self.info_text = self.fig.text(
            0.02, 0.02, "", ha="left", va="bottom", fontsize=8,
            family="monospace"
        )

        # Connect events
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.fig.canvas.mpl_connect("button_press_event", self._on_click)

        # Set window title
        self.fig.canvas.manager.set_window_title(f"PDF Measure Tool - {Path(self.doc.path).name}")

        self._update_status()
        self._update_info()

    def _load_page(self, page_index: int):
        """Load and display a page."""
        if page_index < 0 or page_index >= self.doc.num_pages:
            return

        self.current_page = page_index
        self.page_image = self.doc.render_page(page_index, self.dpi)

        # Clear and redraw
        self.ax.clear()
        self.ax.imshow(self.page_image.image)
        self.ax.set_title(f"Page {page_index + 1} / {self.doc.num_pages}")
        self.ax.set_xlabel("x (pixels)")
        self.ax.set_ylabel("y (pixels)")

        # Clear temporary artists
        self._temp_artists.clear()
        self._rectangle_artists.clear()

        # Redraw rectangles for this page
        self._draw_rectangles()

        self._update_status()
        self._update_info()
        self.fig.canvas.draw_idle()

    def _auto_calibrate(self):
        """Set up automatic page-based calibration."""
        if self.page_image:
            self.calibration = page_scale_from_pdf(
                self.page_image.width_mm,
                self.page_image.width_px
            )
            self.measurements.update_calibration(self.calibration.mm_per_pixel)

    def _update_status(self):
        """Update the status text."""
        mode_text = {
            Mode.VIEW: "VIEW MODE - Press 'h' for help",
            Mode.MEASURE: f"MEASURE MODE - Click 2 diagonal corners of {self.current_group.upper()} rectangle",
            Mode.PARTICLE_PRE: "PARTICLE TRACK - Click PRE-test position",
            Mode.PARTICLE_POST: "PARTICLE TRACK - Click POST-test position",
        }

        status = mode_text.get(self.mode, "")

        if self._click_points:
            status += f" [{len(self._click_points)}/2 clicks]"

        self.status_text.set_text(status)

    def _update_info(self):
        """Update the info text."""
        cal_str = "Not calibrated"
        if self.calibration:
            cal_str = f"{self.calibration.mm_per_pixel:.4f} mm/px ({self.calibration.source})"

        # Count rectangles
        rect_count = 0
        if self.measurements.pre_rectangle:
            rect_count += 1
        if self.measurements.post_rectangle:
            rect_count += 1

        info = (
            f"Rectangles: {rect_count} (Pre: {'✓' if self.measurements.pre_rectangle else '✗'}, "
            f"Post: {'✓' if self.measurements.post_rectangle else '✗'}) | "
            f"Particles: {len(self.measurements.particles)} | "
            f"Calibration: {cal_str} | "
            f"Group: {self.current_group}"
        )
        self.info_text.set_text(info)

    def _on_key(self, event):
        """Handle keyboard events."""
        if event.key == SHORTCUTS["help"] or event.key == "?":
            self._show_help()

        elif event.key == SHORTCUTS["measure"]:
            self._start_measure_mode()

        elif event.key == SHORTCUTS["save"]:
            self._save_measurements()

        elif event.key == SHORTCUTS["toggle_group"]:
            self._toggle_group()

        elif event.key == SHORTCUTS["delete_last"]:
            self._delete_current_group()

        elif event.key == SHORTCUTS["clear_all"]:
            self._clear_all()

        elif event.key == "t":  # Track particle
            self._start_particle_tracking()

        elif event.key == "escape":
            self._cancel_mode()

        elif event.key in ["left", "["]:
            self._load_page(self.current_page - 1)

        elif event.key in ["right", "]"]:
            self._load_page(self.current_page + 1)

        elif event.key == "home":
            self._load_page(0)

        elif event.key == "end":
            self._load_page(self.doc.num_pages - 1)

        elif event.key == SHORTCUTS["quit"]:
            plt.close(self.fig)

        self._update_status()
        self._update_info()
        self.fig.canvas.draw_idle()

    def _on_click(self, event):
        """Handle mouse click events."""
        # Ignore clicks outside the axes or toolbar interactions
        if event.inaxes != self.ax:
            return
        if self.fig.canvas.toolbar.mode != "":
            return  # Zoom/pan mode active

        x, y = event.xdata, event.ydata

        if self.mode == Mode.MEASURE:
            self._handle_measure_click(x, y)

        elif self.mode == Mode.PARTICLE_PRE:
            self._handle_particle_pre_click(x, y)

        elif self.mode == Mode.PARTICLE_POST:
            self._handle_particle_post_click(x, y)

    def _start_measure_mode(self):
        """Enter measurement mode."""
        self.mode = Mode.MEASURE
        self._click_points.clear()
        self._clear_temp_artists()

    def _start_particle_tracking(self):
        """Enter particle tracking mode."""
        self.mode = Mode.PARTICLE_PRE
        self._click_points.clear()
        self._temp_particle_pre = None
        self._temp_particle_pre_page = None
        self._clear_temp_artists()
        print("\n[Particle Tracking] Click particle position in PRE-test image.")

    def _cancel_mode(self):
        """Cancel current mode and return to view mode."""
        self.mode = Mode.VIEW
        self._click_points.clear()
        self._temp_particle_pre = None
        self._clear_temp_artists()

    def _toggle_group(self):
        """Toggle between measurement groups."""
        groups = ["pre", "post"]
        current_idx = groups.index(self.current_group) if self.current_group in groups else -1
        self.current_group = groups[(current_idx + 1) % len(groups)]
        print(f"Group set to: {self.current_group}")

    def _handle_measure_click(self, x: float, y: float):
        """Handle a click in measure mode."""
        self._click_points.append((x, y))

        # Draw the point
        point = self.ax.plot(
            x, y, "o",
            color=MEASUREMENT_POINT_COLOR,
            markersize=POINT_MARKER_SIZE,
            markeredgecolor="black",
            markeredgewidth=1
        )[0]
        self._temp_artists.append(point)

        if len(self._click_points) == 2:
            p1, p2 = self._click_points

            # Create rectangle
            rectangle = self.measurements.add_rectangle(
                group=self.current_group,
                page_index=self.current_page,
                point1_px=p1,
                point2_px=p2,
                mm_per_pixel=self.calibration.mm_per_pixel if self.calibration else None,
            )

            if rectangle is None:
                # Invalid rectangle
                print("Error: Invalid rectangle (zero width or height). Please remeasure.")
                self._clear_temp_artists()
                self._click_points.clear()
                self._update_status()
                self.fig.canvas.draw_idle()
                return

            # Draw permanent rectangle
            self._draw_rectangle(rectangle)

            # Clear temp artists
            self._clear_temp_artists()

            # Report
            mm_str = f"{rectangle.width_mm:.3f} mm × {rectangle.height_mm:.3f} mm"
            px_str = f"{rectangle.width_px:.1f} px × {rectangle.height_px:.1f} px"
            print(f"[{rectangle.group.capitalize()} Rectangle] Measured: {px_str} = {mm_str}")

            # Reset for next measurement
            self._click_points.clear()

        self._update_status()
        self._update_info()
        self.fig.canvas.draw_idle()

    def _handle_particle_pre_click(self, x: float, y: float):
        """Handle click for particle pre-position."""
        self._temp_particle_pre = (x, y)
        self._temp_particle_pre_page = self.current_page

        # Draw marker
        point = self.ax.plot(
            x, y, "^",
            color="lime",
            markersize=POINT_MARKER_SIZE + 2,
            markeredgecolor="black",
            markeredgewidth=1
        )[0]
        self._temp_artists.append(point)

        self.mode = Mode.PARTICLE_POST
        print(f"[Particle] PRE position recorded at ({x:.1f}, {y:.1f}). Now click POST position (can be on different page).")

        self._update_status()
        self.fig.canvas.draw_idle()

    def _handle_particle_post_click(self, x: float, y: float):
        """Handle click for particle post-position."""
        if self._temp_particle_pre is None:
            self.mode = Mode.VIEW
            return

        post_pos = (x, y)

        # Create particle displacement
        label = f"P{self._particle_label_counter}"
        particle = self.measurements.add_particle(
            label=label,
            pre_position_px=self._temp_particle_pre,
            post_position_px=post_pos,
            pre_page_index=self._temp_particle_pre_page,
            post_page_index=self.current_page,
            mm_per_pixel=self.calibration.mm_per_pixel if self.calibration else None,
        )
        self._particle_label_counter += 1

        # Report
        dx, dy = particle.displacement_px
        mag_px = particle.displacement_magnitude_px

        if particle.displacement_mm:
            dx_mm, dy_mm = particle.displacement_mm
            mag_mm = particle.displacement_magnitude_mm
            print(f"[{label}] Displacement: ({dx:.1f}, {dy:.1f}) px = ({dx_mm:.3f}, {dy_mm:.3f}) mm, magnitude: {mag_mm:.3f} mm")
        else:
            print(f"[{label}] Displacement: ({dx:.1f}, {dy:.1f}) px, magnitude: {mag_px:.1f} px")

        # Clear and reset
        self._clear_temp_artists()
        self._temp_particle_pre = None
        self._temp_particle_pre_page = None
        self.mode = Mode.VIEW

        self._update_status()
        self._update_info()
        self.fig.canvas.draw_idle()

    def _draw_rectangle(self, rect: Rectangle):
        """Draw a rectangle on the plot."""
        if rect.page_index != self.current_page:
            return

        # Choose color based on group
        if rect.group == "pre":
            color = "cyan"
            label = "Pre"
        elif rect.group == "post":
            color = "orange"
            label = "Post"
        else:
            color = "yellow"
            label = rect.group

        # Draw rectangle outline (4 sides)
        corners = [
            rect.bottom_left_px,
            rect.bottom_right_px,
            rect.top_right_px,
            rect.top_left_px,
            rect.bottom_left_px  # Close the rectangle
        ]

        xs = [c[0] for c in corners]
        ys = [c[1] for c in corners]

        line = self.ax.plot(
            xs, ys,
            color=color,
            linewidth=1.5,
            alpha=0.7,
            linestyle='-'
        )[0]

        # Draw corner dots
        corner_dots = self.ax.plot(
            xs[:-1], ys[:-1],  # Exclude the duplicate closing point
            "o",
            color=color,
            markersize=POINT_MARKER_SIZE - 2,
            markeredgecolor="black",
            markeredgewidth=0.5,
        )[0]

        self._rectangle_artists.extend([line, corner_dots])

    def _draw_rectangles(self):
        """Draw all rectangles for the current page."""
        if self.measurements.pre_rectangle:
            self._draw_rectangle(self.measurements.pre_rectangle)
        if self.measurements.post_rectangle:
            self._draw_rectangle(self.measurements.post_rectangle)

    def _clear_temp_artists(self):
        """Remove temporary drawing elements."""
        for artist in self._temp_artists:
            artist.remove()
        self._temp_artists.clear()

    def _redraw_all(self):
        """Redraw the current page with all rectangles."""
        self._load_page(self.current_page)

    def _delete_current_group(self):
        """Delete the rectangle for the current group."""
        deleted = self.measurements.delete_rectangle(self.current_group)
        if deleted:
            print(f"Deleted {deleted.group} rectangle.")
            self._redraw_all()
        else:
            print(f"No {self.current_group} rectangle to delete.")

    def _clear_all(self):
        """Clear all measurements after confirmation."""
        confirm = input("Clear ALL measurements? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.measurements.clear_all()
            self._measurement_label_counter = 1
            self._particle_label_counter = 1
            print("All measurements cleared.")
            self._redraw_all()

    def _save_measurements(self):
        """Save measurements to file."""
        has_data = (
            self.measurements.pre_rectangle is not None or
            self.measurements.post_rectangle is not None or
            len(self.measurements.measurements) > 0 or
            len(self.measurements.particles) > 0
        )

        if not has_data:
            print("No measurements to save.")
            return

        base_name = Path(self.doc.path).stem
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        csv_path = results_dir / f"{base_name}_measurements.csv"
        export_measurements_csv(self.measurements, str(csv_path), self.calibration)
        print(f"Saved: {csv_path}")

        json_path = results_dir / f"{base_name}_measurements.json"
        export_measurements_json(self.measurements, str(json_path), self.calibration)
        print(f"Saved: {json_path}")

    def _show_help(self):
        """Display help information."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                  PDF MEASUREMENT TOOL - HELP                 ║
╠══════════════════════════════════════════════════════════════╣
║  NAVIGATION                                                  ║
║    ← / →  or  [ / ]    Previous / Next page                  ║
║    Home / End          First / Last page                     ║
║    Mouse drag          Pan (when pan tool selected)          ║
║    Scroll              Zoom (when zoom tool selected)        ║
║                                                              ║
║  RECTANGLE MEASUREMENT                                       ║
║    m          Enter measure mode (click 2 diagonal corners)  ║
║    g          Toggle group (pre/post)                        ║
║    Escape     Cancel current mode                            ║
║                                                              ║
║  PARTICLE TRACKING                                           ║
║    t          Track particle (pre → post position)           ║
║                                                              ║
║  DATA MANAGEMENT                                             ║
║    s          Save measurements to CSV and JSON              ║
║    d          Delete rectangle for current group             ║
║    x          Clear all measurements                         ║
║                                                              ║
║  OTHER                                                       ║
║    h or ?     Show this help                                 ║
║    q          Quit                                           ║
║                                                              ║
║  Use the matplotlib toolbar for zoom/pan controls.           ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(help_text)

    def run(self):
        """Run the viewer (blocking)."""
        print("\n" + "="*60)
        print("PDF MEASUREMENT TOOL")
        print("="*60)
        print(f"Loaded: {self.doc.path}")
        print(f"Pages: {self.doc.num_pages}")
        print(f"Rendering at {self.dpi} DPI")
        if self.calibration:
            print(f"Calibration: {self.calibration.mm_per_pixel:.4f} mm/pixel (auto from page size)")
        print("\nPress 'h' or '?' for help")
        print("="*60 + "\n")

        plt.show()


def run_viewer(pdf_path: str, dpi: int = DEFAULT_DPI):
    """
    Convenience function to run the viewer.

    Args:
        pdf_path: Path to PDF file.
        dpi: Rendering DPI.
    """
    from .pdf_loader import load_document

    doc = load_document(pdf_path)
    viewer = PdfMeasureViewer(doc, dpi=dpi)
    viewer.run()
    doc.close()
