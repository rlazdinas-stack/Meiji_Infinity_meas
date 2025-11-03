# Meiji Infinity Measurement Application

A Python application for measuring line widths using the Lumenera INFINITY1-3C camera with the Meiji microscope. The application provides live camera view, edge detection, contour approximation, and subpixel-accurate line width measurements.

## Camera Specifications

- **Model**: INFINITY1-3C (color)
- **Model ID**: 0xA3
- **Serial Number**: 202711
- **Interface**: USB 2.0
- **Resolution**: 2048x1536
- **API Version**: 2.1.1.126
- **Driver Version**: 5.2.4.251
- **Firmware Version**: 28.68
- **FPGA Version**: 14.62

## Features

- **Live Camera View**: Real-time video streaming from INFINITY1-3C camera via USB 2.0
- **Image Capture**: Capture frames for measurement with the "Meas" button
- **Edge Detection**: Advanced Canny edge detection with adjustable thresholds
- **Contour Approximation**: Approximate detected edges with straight lines using Douglas-Peucker algorithm
- **Subpixel Refinement**: Refine edge positions to subpixel accuracy for each image row
- **Line Width Measurement**: Calculate precise line width measurements with statistics
- **Visual Results**: Display measurements overlaid on captured images
- **Camera Information**: Display complete camera specifications and firmware versions

## Requirements

- Python 3.7 or higher
- OpenCV
- NumPy
- Pillow
- Lumenera Lucam API/SDK (optional - runs in simulation mode without SDK)
- USB 2.0 port for camera connection

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

3. (Optional) Install Lumenera Lucam API/SDK:
   - Download and install the Lumenera Lucam API from the manufacturer
   - Ensure the SDK libraries (LucamAPI.dll on Windows or liblucamapi.so on Linux) are in your system path
   - Connect the INFINITY1-3C camera to a USB 2.0 port
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
├── camera_interface.py     # INFINITY1-3C camera Lucam API wrapper
├── image_processing.py     # Image processing and measurement algorithms
├── demo.py                 # Command-line demo for testing
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Troubleshooting

### Camera Not Detected
- Verify Lumenera Lucam API is installed correctly
- Check that INFINITY1-3C camera is connected to a USB 2.0 port
- Verify camera power LED is on
- Check USB cable connection
- Try a different USB 2.0 port
- The application will run in simulation mode if camera is not available

### USB Connection Issues
- Ensure the camera is connected to a USB 2.0 port (not USB 3.0 only)
- Check Device Manager (Windows) or lsusb (Linux) for camera recognition
- Reinstall Lumenera drivers if necessary
- Verify the camera serial number matches: 202711

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
