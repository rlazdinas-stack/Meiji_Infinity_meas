#!/usr/bin/env python3
"""
Demo script for Meiji Infinity Measurement Application
Demonstrates the measurement workflow without requiring a display.
"""

import cv2
import numpy as np
from camera_interface import LumeneraCamera
from image_processing import ImageProcessor


def create_demo_image():
    """Create a demo image with known line widths for testing."""
    height, width = 1024, 1280
    image = np.ones((height, width, 3), dtype=np.uint8) * 128
    
    # Add lines with known widths
    lines = [
        (200, 250, "50px"),   # 50 pixel wide line
        (400, 430, "30px"),   # 30 pixel wide line
        (600, 650, "50px"),   # 50 pixel wide line
        (850, 910, "60px"),   # 60 pixel wide line
        (1050, 1090, "40px"), # 40 pixel wide line
    ]
    
    for x_start, x_end, label in lines:
        image[:, x_start:x_end] = 255
    
    # Add some noise to make it realistic
    noise = np.random.randint(-15, 15, image.shape, dtype=np.int16)
    image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    return image, lines


def main():
    """Run the demo."""
    print("=" * 70)
    print("Meiji Infinity Measurement - Demo")
    print("=" * 70)
    print()
    
    # Create demo image
    print("Creating demo image with known line widths...")
    demo_image, known_lines = create_demo_image()
    print("Demo image created with lines:")
    for i, (x_start, x_end, label) in enumerate(known_lines, 1):
        print(f"  Line {i}: x={x_start}-{x_end}, width={label}")
    print()
    
    # Initialize processor
    print("Initializing image processor...")
    processor = ImageProcessor()
    print("✓ Processor ready\n")
    
    # Step 1: Edge Detection
    print("Step 1: Detecting edges...")
    edges = processor.detect_edges(demo_image, low_threshold=50, high_threshold=150)
    edge_count = np.sum(edges > 0)
    print(f"✓ {edge_count} edge pixels detected\n")
    
    # Step 2: Find Contours
    print("Step 2: Finding contours...")
    contours = processor.find_contours(edges)
    print(f"✓ {len(contours)} contours found\n")
    
    # Step 3: Approximate with Lines
    print("Step 3: Approximating contours with lines...")
    approximations = processor.approximate_contours_with_lines(contours)
    total_points = sum(len(approx) for approx in approximations)
    print(f"✓ {len(approximations)} line approximations created")
    print(f"  ({total_points} total points)\n")
    
    # Step 4: Subpixel Refinement
    print("Step 4: Refining edge positions to subpixel accuracy...")
    edge_positions = processor.refine_edges_subpixel(demo_image, edges, window_size=5)
    print(f"✓ {len(edge_positions)} rows processed")
    total_edges = sum(len(positions) for positions in edge_positions.values())
    print(f"  ({total_edges} total edge positions refined)\n")
    
    # Step 5: Calculate Line Widths
    print("Step 5: Calculating line widths...")
    measurements = processor.calculate_line_widths(edge_positions)
    print(f"✓ {len(measurements)} lines measured\n")
    
    # Display Results
    print("=" * 70)
    print("MEASUREMENT RESULTS")
    print("=" * 70)
    print()
    
    if len(measurements) == 0:
        print("No lines detected. Try adjusting edge detection parameters.")
    else:
        for i, meas in enumerate(measurements, 1):
            print(f"Line {i}:")
            print(f"  Mean Width:     {meas['mean_width']:.3f} pixels")
            print(f"  Std Deviation:  {meas['std_width']:.3f} pixels")
            print(f"  Min Width:      {meas['min_width']:.3f} pixels")
            print(f"  Max Width:      {meas['max_width']:.3f} pixels")
            print(f"  Samples:        {meas['num_samples']} rows")
            print(f"  Center:         ({meas['center_x']:.1f}, {meas['center_y']:.1f})")
            print()
    
    # Step 6: Draw Results
    print("Step 6: Drawing results on image...")
    result_image = processor.draw_results(
        demo_image,
        edges,
        approximations,
        measurements,
        show_edges=True,
        show_approx=True,
        show_measurements=True
    )
    
    # Save result
    output_file = "demo_result.png"
    cv2.imwrite(output_file, result_image)
    print(f"✓ Result saved to {output_file}\n")
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print()
    print("To run the full application with GUI:")
    print("  python main.py")
    print()


if __name__ == "__main__":
    main()
