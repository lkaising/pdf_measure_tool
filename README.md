# PDF Measurement Tool

Interactive Python tool for measuring rectangles on PDF pages, designed for biomechanics and materials analysis (e.g., pre/post-test specimen dimension tracking, strain calculations).

## Features

- **Load any PDF file** and navigate between pages
- **Render pages as images** with zoom and pan controls
- **Rectangle measurement** - click 2 diagonal corners to measure specimen dimensions
- **Pre/Post comparison** - store one pre-test and one post-test rectangle
- **Particle tracking mode** to track displacement between pre and post images
- **Automatic calibration** from PDF page dimensions
- **Coordinate transformation** - bottom-left corner as origin (0,0) in mm space
- **Export to CSV and JSON** for further analysis

## Installation

```bash
# Clone or download the repository
cd pdf_measure_tool

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# From the src directory
cd src
python -m pdf_measure_tool path/to/your/file.pdf

# With custom DPI (higher = sharper but slower)
python -m pdf_measure_tool path/to/your/file.pdf --dpi 200
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| `m` | Enter **measure mode** (click 2 diagonal corners of rectangle) |
| `g` | Toggle measurement **group** (pre/post) |
| `t` | **Track particle** (click pre position, then post position) |
| `s` | **Save** measurements to CSV and JSON |
| `d` | **Delete** rectangle for current group |
| `x` | Clear **all** measurements (with confirmation) |
| `←` / `→` | Previous / Next page |
| `[` / `]` | Previous / Next page (alternative) |
| `Home` / `End` | First / Last page |
| `h` or `?` | Show help |
| `Escape` | Cancel current mode |
| `q` | Quit |

### Mouse Controls

- **Click** in measure/track mode to place points
- Use the **matplotlib toolbar** at the bottom for:
  - Pan (hand icon)
  - Zoom to rectangle (magnifier icon)
  - Home (reset view)

## Rectangle Measurement

The tool is designed to measure **axis-aligned rectangles** (edges parallel to PDF x/y axes) that represent specimen states.

### How it Works

1. **Press `m`** to enter measure mode
2. **Click two diagonal corners** of the rectangle (any diagonal: top-left to bottom-right, or top-right to bottom-left)
3. The program automatically:
   - Derives all 4 corners
   - Calculates width and height in pixels and mm
   - Transforms coordinates so bottom-left corner = (0, 0) in mm space
   - Stores the rectangle (overwrites previous measurement for that group)

### Group System

- **Pre group**: Stores the pre-test specimen rectangle
- **Post group**: Stores the post-test specimen rectangle
- **Toggle with `g`** to switch between groups
- **Only 1 rectangle per group** - new measurements overwrite old ones

### Coordinate Systems

**Pixel Coordinates** (as measured):
- Origin: Top-left of PDF page
- X increases left to right
- Y increases top to bottom

**MM Coordinates** (for analysis):
- Origin: Bottom-left corner of the rectangle (0, 0)
- X increases left to right
- Y increases bottom to top
- Simplifies strain and deformation calculations

## Calibration

The tool **automatically calibrates** using the PDF page dimensions. This assumes your PDF drawings are to scale. The calibration converts pixel measurements to millimeters based on the page size.

## Workflow Example (Biomechanics Project)

1. **Load your PDF** with pre and post-test images:
   ```bash
   python -m pdf_measure_tool Biomechanics_Project.pdf
   ```

2. **Measure pre-test specimen**:
   - Ensure you're on the pre-test page
   - Press `g` until group shows "pre"
   - Press `m` to enter measure mode
   - Click two diagonal corners of the specimen rectangle
   - Rectangle is stored with dimensions

3. **Measure post-test specimen**:
   - Navigate to post-test page with `→`
   - Press `g` to switch to "post" group
   - Press `m` and click two diagonal corners
   - Post rectangle is stored

4. **Track particle displacements** (optional):
   - Go to pre-test page
   - Press `t` to enter tracking mode
   - Click on a particle in the pre-test image
   - Navigate to post-test page
   - Click on the same particle in the post-test image
   - Displacement is automatically calculated

5. **Save results**:
   - Press `s` to export measurements
   - Files saved as `YourPDF_measurements.csv` and `.json` in `results/` folder

## Output Format

### CSV Output

```csv
# Calibration: 0.084667 mm/pixel (page)
# Exported: 2024-01-15T10:30:00

# === PRE RECTANGLE ===
group,page,bottom_left_x_px,bottom_left_y_px,bottom_right_x_px,bottom_right_y_px,top_left_x_px,top_left_y_px,top_right_x_px,top_right_y_px,bottom_left_x_mm,bottom_left_y_mm,bottom_right_x_mm,bottom_right_y_mm,top_left_x_mm,top_left_y_mm,top_right_x_mm,top_right_y_mm,width_px,height_px,width_mm,height_mm
pre,0,100.50,400.20,350.80,400.20,100.50,150.30,350.80,150.30,0.0000,0.0000,21.2000,0.0000,0.0000,21.1500,21.2000,21.1500,250.30,249.90,21.2000,21.1500

# === POST RECTANGLE ===
post,0,105.20,405.80,345.60,405.80,105.20,160.40,345.60,160.40,0.0000,0.0000,20.3500,0.0000,0.0000,20.8000,20.3500,20.8000,240.40,245.40,20.3500,20.8000
```

### JSON Output

```json
{
  "metadata": {
    "exported": "2024-01-15T10:30:00",
    "calibration": {
      "mm_per_pixel": 0.084667,
      "source": "page"
    }
  },
  "rectangles": {
    "pre": {
      "group": "pre",
      "page": 0,
      "bottom_left_px": [100.5, 400.2],
      "width_px": 250.3,
      "height_px": 249.9,
      "width_mm": 21.2,
      "height_mm": 21.15,
      ...
    },
    "post": {
      "group": "post",
      ...
    }
  }
}
```

## Validation

- If you accidentally click two points that form an invalid rectangle (zero width or height), the tool will show an error message and allow you to remeasure
- Invalid measurements are not stored

## Limitations

- Rectangles must be **axis-aligned** (not rotated)
- Calibration assumes PDF drawings are to scale (based on page dimensions)
- Only **one pre and one post rectangle** can be stored at a time
- Requires matplotlib GUI backend (may need configuration on some systems)

## For Your Biomechanics Project

This tool is perfect for:
- Measuring pre/post specimen dimensions to calculate strain
- Getting precise rectangle measurements with automatic corner detection
- Tracking specimen deformation with mm-accurate measurements
- Exporting data in a format optimized for strain calculations (bottom-left origin)

After exporting measurements, you can calculate:
- **Normal strains**:
  - ε_x = (width_post - width_pre) / width_pre
  - ε_y = (height_post - height_pre) / height_pre
- **Engineering strain**: from specimen dimensional changes
- **Principal strains**: using strain transformation equations
- **Material properties**: E, G, ν from stress-strain relationships

## Dependencies

- PyMuPDF (fitz) >= 1.24.0
- matplotlib >= 3.8.0
- numpy >= 1.26.0
- pandas >= 2.2.0 (optional, for CSV handling)

## License

MIT License - Use freely for your projects!
