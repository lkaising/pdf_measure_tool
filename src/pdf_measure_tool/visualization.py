"""
Visualization module for rectangles and particles.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Optional

from .measurement import MeasurementCollection, Rectangle, ParticleDisplacement


def plot_rectangle_with_particles(
    collection: MeasurementCollection,
    output_path: str
) -> Optional[str]:
    """
    Create side-by-side visualization of pre and post rectangles with particles.

    Args:
        collection: MeasurementCollection with rectangles and particles
        output_path: Base path for output file (will add _visualization.png)

    Returns:
        Path to created image file, or None if no data to plot
    """
    # Check if we have rectangles to plot
    has_pre = collection.pre_rectangle is not None
    has_post = collection.post_rectangle is not None

    if not has_pre and not has_post:
        return None

    # Create figure with side-by-side subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # Plot pre rectangle
    if has_pre:
        _plot_single_rectangle(
            axes[0],
            collection.pre_rectangle,
            collection.particles,
            "pre",
            "Pre-Test Specimen"
        )
    else:
        axes[0].text(0.5, 0.5, "No Pre Rectangle",
                     ha='center', va='center', fontsize=14, color='gray')
        axes[0].set_title("Pre-Test Specimen")

    # Plot post rectangle
    if has_post:
        _plot_single_rectangle(
            axes[1],
            collection.post_rectangle,
            collection.particles,
            "post",
            "Post-Test Specimen"
        )
    else:
        axes[1].text(0.5, 0.5, "No Post Rectangle",
                     ha='center', va='center', fontsize=14, color='gray')
        axes[1].set_title("Post-Test Specimen")

    # Add overall title
    particle_count = len(collection.particles)
    fig.suptitle(f"Specimen Measurement Visualization ({particle_count} particles)",
                 fontsize=16, fontweight='bold')

    # Adjust layout
    plt.tight_layout()

    # Save figure
    output_path = Path(output_path)
    viz_path = output_path.parent / f"{output_path.stem}_visualization.png"
    plt.savefig(viz_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    return str(viz_path)


def _plot_single_rectangle(
    ax: plt.Axes,
    rectangle: Rectangle,
    particles: list[ParticleDisplacement],
    group: str,
    title: str
):
    """
    Plot a single rectangle with its particles.

    Args:
        ax: Matplotlib axes to plot on
        rectangle: Rectangle to plot
        particles: List of all particles
        group: "pre" or "post" to determine which coordinates to use
        title: Title for the subplot
    """
    # Draw rectangle outline
    width_mm = rectangle.width_mm
    height_mm = rectangle.height_mm

    # Rectangle corners
    rect_x = [0, width_mm, width_mm, 0, 0]
    rect_y = [0, 0, height_mm, height_mm, 0]

    ax.plot(rect_x, rect_y, 'k-', linewidth=2)

    # Plot particles
    particle_xs = []
    particle_ys = []
    particle_labels = []

    for particle in particles:
        if group == "pre":
            x_mm, y_mm = particle.pre_position_mm
        else:  # post
            x_mm, y_mm = particle.post_position_mm

        particle_xs.append(x_mm)
        particle_ys.append(y_mm)
        particle_labels.append(particle.label)

    # Plot particle points
    if particle_xs:
        ax.scatter(particle_xs, particle_ys,
                  c='red', s=100, marker='o',
                  edgecolors='black', linewidths=1.5,
                  zorder=5, label='Particles')

        # Add labels for each particle
        for i, (x, y, label) in enumerate(zip(particle_xs, particle_ys, particle_labels)):
            # Offset label slightly above and to the right of point
            offset_x = width_mm * 0.02
            offset_y = height_mm * 0.02

            ax.annotate(f'{label}\n({x:.2f}, {y:.2f})',
                       xy=(x, y),
                       xytext=(x + offset_x, y + offset_y),
                       fontsize=9,
                       ha='left',
                       va='bottom',
                       bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='yellow',
                                alpha=0.7,
                                edgecolor='black',
                                linewidth=0.5),
                       arrowprops=dict(arrowstyle='->',
                                     connectionstyle='arc3,rad=0',
                                     color='black',
                                     linewidth=1))

    # Set axis properties
    ax.set_xlabel('X (mm)', fontsize=12)
    ax.set_ylabel('Y (mm)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Set axis limits with padding
    padding = 0.1
    ax.set_xlim(-width_mm * padding, width_mm * (1 + padding))
    ax.set_ylim(-height_mm * padding, height_mm * (1 + padding))

    # Equal aspect ratio
    ax.set_aspect('equal', adjustable='box')

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Legend
    ax.legend(loc='upper right', fontsize=10)

    # Add dimensions annotation
    ax.text(0.02, 0.98,
           f'Dimensions:\n{width_mm:.2f} × {height_mm:.2f} mm',
           transform=ax.transAxes,
           fontsize=10,
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))


def create_visualization_from_json(json_path: str) -> Optional[str]:
    """
    Create visualization from a saved JSON file.

    Args:
        json_path: Path to JSON measurements file

    Returns:
        Path to created visualization, or None if failed
    """
    from .export import load_measurements_json

    try:
        collection, _ = load_measurements_json(json_path)
        output_path = Path(json_path).with_suffix('.png')
        return plot_rectangle_with_particles(collection, str(output_path))
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return None
