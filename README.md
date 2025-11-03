# Meiji Infinity Measurement Application

A Python application for measuring line widths using the Lumenera Infinity 1 camera with the Meiji microscope. The application provides live camera view, edge detection, contour approximation, and subpixel-accurate line width measurements.

## Features

- **Live Camera View**: Real-time video streaming from Lumenera Infinity 1 camera
- **Image Capture**: Capture frames for measurement with the "Meas" button
- **Edge Detection**: Advanced Canny edge detection with adjustable thresholds
- **Contour Approximation**: Approximate detected edges with straight lines using Douglas-Peucker algorithm
- **Subpixel Refinement**: Refine edge positions to subpixel accuracy for each image row
- **Line Width Measurement**: Calculate precise line width measurements with statistics
- **Visual Results**: Display measurements overlaid on captured images

## Requirements

- Python 3.7 or higher
- OpenCV
- NumPy
- Pillow
- SciPy
- Lumenera Infinity SDK (optional - runs in simulation mode without SDK)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rlazdinas-stack/Meiji_Infinity_meas.git
cd Meiji_Infinity_meas
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install Lumenera Infinity SDK:
   - Download and install the Lumenera Infinity SDK from the manufacturer
   - Ensure the SDK libraries are in your system path
   - Without the SDK, the application runs in simulation mode with test patterns

## Usage

1. Run the application:
```bash
python main.py
```

2. **Start Live View**: Click "Start Live View" to begin streaming from the camera

3. **Adjust Parameters**: Use the Canny Low/High spinboxes to adjust edge detection sensitivity
   - Lower values detect more edges (but may include noise)
   - Higher values detect only strong edges

4. **Capture and Measure**: Click "Meas" to capture the current frame and perform measurements
   - Edges are detected and highlighted in green
   - Contours are approximated with blue lines
   - Line widths are measured and displayed in cyan with statistics

5. **View Results**: The right panel shows the processed image with measurements
   - Yellow measurement lines indicate detected line widths
   - Text labels show mean width ± standard deviation
   - Detailed statistics appear in the text area below

6. **Clear Results**: Click "Clear" to remove measurement results

## How It Works

### Edge Detection
The application uses the Canny edge detection algorithm to identify edges in the captured image:
1. Convert image to grayscale
2. Apply Gaussian blur to reduce noise
3. Detect edges using Canny algorithm with configurable thresholds

### Contour Approximation
Detected edges are approximated as straight lines:
1. Find contours from the edge image
2. Apply Douglas-Peucker algorithm to approximate contours with line segments
3. Simplifies complex edge patterns into measurable lines

### Subpixel Refinement
For maximum accuracy, edge positions are refined to subpixel precision:
1. Process each row of the image independently
2. Calculate intensity gradient at edge pixels
3. Fit parabola around maximum gradient for subpixel interpolation
4. Achieve measurement accuracy better than 1 pixel

### Line Width Calculation
Line widths are calculated from refined edge positions:
1. Group edge positions into left/right edge pairs
2. Calculate width for each row that contains both edges
3. Compute statistics: mean, standard deviation, min, max
4. Display measurements on the image

## File Structure

```
Meiji_Infinity_meas/
├── main.py                 # Main application with GUI
├── camera_interface.py     # Lumenera camera SDK wrapper
├── image_processing.py     # Image processing and measurement algorithms
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Troubleshooting

### Camera Not Detected
- Verify Lumenera SDK is installed correctly
- Check camera USB connection
- The application will run in simulation mode if camera is not available

### No Lines Detected
- Adjust Canny threshold values
- Ensure there are clear vertical lines in the image
- Check that the image has sufficient contrast

### Inaccurate Measurements
- Increase edge detection quality by adjusting thresholds
- Ensure proper lighting and focus
- Verify calibration of microscope optics

## License

This project is provided as-is for microscopy measurement applications.

## Author

Development for Meiji microscope line width measurement
