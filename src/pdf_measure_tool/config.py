"""
Configuration constants for PDF Measurement Tool.
"""

# Default rendering DPI for PDF pages
DEFAULT_DPI = 150

# Points per inch (PDF standard)
POINTS_PER_INCH = 72

# Millimeters per inch
MM_PER_INCH = 25.4

# Default output file names
DEFAULT_CSV_OUTPUT = "measurements.csv"
DEFAULT_JSON_OUTPUT = "measurements.json"

# GUI Colors
MEASUREMENT_LINE_COLOR = "red"
MEASUREMENT_POINT_COLOR = "yellow"
CALIBRATION_LINE_COLOR = "blue"
CALIBRATION_POINT_COLOR = "cyan"

# Marker sizes
POINT_MARKER_SIZE = 8
LINE_WIDTH = 1.5

# Font sizes
LABEL_FONT_SIZE = 9

# Keyboard shortcuts
SHORTCUTS = {
    "measure": "m",
    "calibrate": "c", 
    "save": "s",
    "toggle_group": "g",
    "delete_last": "d",
    "clear_all": "x",
    "help": "h",
    "quit": "q",
}
