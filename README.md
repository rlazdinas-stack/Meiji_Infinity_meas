# Meiji_Infinity_meas
Meiji microscope line width measuring app

## Features
- Live view from Lumenera Infinity 1 camera
- Real-time camera feed display
- Image capture for measurements
- GUI built with tkinter

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python meiji_app.py
```

## Usage

1. Click "Start Live View" to open the camera feed
2. The live view will display the camera stream in real-time
3. Click "Measure" to capture an image for measurement
4. Click "Stop Live View" to close the camera feed

## Requirements
- Python 3.7+
- OpenCV
- Pillow
- NumPy
- Lumenera Infinity SDK (optional - falls back to OpenCV camera)
