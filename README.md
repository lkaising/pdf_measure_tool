# PDF Measurement Tool

Interactive Python tool for measuring distances on PDF pages, designed for biomechanics and materials analysis (e.g., pre/post-test particle tracking, strain calculations).

## Features

- **Load any PDF file** and navigate between pages
- **Render pages as images** with zoom and pan controls
- **Click to measure distances** between any two points
- **Particle tracking mode** to track displacement between pre and post images
- **Calibration options**:
  - Automatic calibration from PDF page dimensions
  - Manual calibration by clicking two points of known distance
- **Measurement groups** to organize pre/post/fiber/edge measurements
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
| `m` | Enter **measure mode** (click 2 points to measure distance) |
| `c` | Enter **calibration mode** (click 2 points, enter known distance) |
| `t` | **Track particle** (click pre position, then post position) |
| `g` | Toggle measurement **group** (pre/post/fiber/edge/other) |
| `s` | **Save** measurements to CSV and JSON |
| `d` | **Delete** last measurement |
| `x` | Clear **all** measurements (with confirmation) |
| `←` / `→` | Previous / Next page |
| `[` / `]` | Previous / Next page (alternative) |
| `Home` / `End` | First / Last page |
| `h` or `?` | Show help |
| `Escape` | Cancel current mode |
| `q` | Quit |

### Mouse Controls

- **Click** in measure/calibrate/track mode to place points
- Use the **matplotlib toolbar** at the bottom for:
  - Pan (hand icon)
  - Zoom to rectangle (magnifier icon)
  - Home (reset view)

## Workflow Example (Biomechanics Project)

1. **Load your PDF** with pre and post-test images:
   ```bash
   python -m pdf_measure_tool Biomechanics_Project.pdf
   ```

2. **Calibrate** (if needed):
   - Press `c` to enter calibration mode
   - Click two points on a known reference (e.g., scale bar)
   - Enter the known distance when prompted

3. **Measure sample dimensions**:
   - Press `g` until group shows "pre"
   - Press `m` and click to measure initial sample width/height
   - Navigate to post-test page with `→`
   - Press `g` until group shows "post"
   - Press `m` and measure final dimensions

4. **Track particle displacements**:
   - Go to pre-test page
   - Press `t` to enter tracking mode
   - Click on a particle in the pre-test image
   - Navigate to post-test page
   - Click on the same particle in the post-test image
   - Displacement is automatically calculated

5. **Save results**:
   - Press `s` to export measurements
   - Files saved as `YourPDF_measurements.csv` and `.json`

## Output Format

### CSV Output

```csv
# Calibration: 0.084667 mm/pixel (manual)
# Exported: 2024-01-15T10:30:00
# === MEASUREMENTS ===
id,label,group,page,x1_px,y1_px,x2_px,y2_px,dx_px,dy_px,pixel_distance,length_mm,angle_deg,notes
1,M1,pre,0,100.5,200.3,300.2,200.1,199.7,-0.2,199.7,16.9123,0.06,
2,M2,post,0,100.5,200.3,310.8,200.1,210.3,-0.2,210.3,17.8087,0.05,

# === PARTICLE DISPLACEMENTS ===
id,label,pre_x_px,pre_y_px,post_x_px,post_y_px,pre_page,post_page,dx_px,dy_px,magnitude_px,dx_mm,dy_mm,magnitude_mm
1,P1,150.0,180.0,155.2,178.5,0,0,5.2,-1.5,5.41,0.4403,-0.1270,0.4582
```

## Limitations

- Assumes PDF drawings are to scale (or requires manual calibration)
- No automatic detection of features (all manual clicking)
- Requires matplotlib GUI backend (may need configuration on some systems)

## For Your Biomechanics Project

This tool is perfect for:
- Measuring pre/post sample dimensions to calculate strain
- Tracking highlighted particle positions to compute displacement fields
- Calculating thickness changes (you mentioned 3mm → 2mm)
- Exporting data for strain tensor calculations

After exporting measurements, you can calculate:
- **Normal strains**: ε = (L_final - L_initial) / L_initial
- **Engineering strain**: from particle displacements
- **Principal strains**: using strain transformation equations
- **Material properties**: E, G, ν from stress-strain relationships

## Dependencies

- PyMuPDF (fitz) >= 1.24.0
- matplotlib >= 3.8.0
- numpy >= 1.26.0
- pandas >= 2.2.0 (optional, for CSV handling)

## License

MIT License - Use freely for your projects!
