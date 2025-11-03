"""
Image Processing and Measurement Module
Implements edge detection, contour approximation, and line width measurement.
"""

import cv2
import numpy as np
from scipy import ndimage
from scipy.interpolate import UnivariateSpline


class ImageProcessor:
    """
    Handles image processing tasks including edge detection,
    contour approximation, and subpixel measurement.
    """
    
    def __init__(self):
        self.edges = None
        self.contours = None
        self.line_approximations = None
        self.edge_positions = None
        self.measurements = []
    
    def detect_edges(self, image, low_threshold=50, high_threshold=150):
        """
        Detect edges in the image using Canny edge detector.
        
        Args:
            image: Input image (BGR or grayscale)
            low_threshold: Lower threshold for Canny detector
            high_threshold: Upper threshold for Canny detector
            
        Returns:
            numpy.ndarray: Binary edge map
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
        
        # Detect edges
        self.edges = cv2.Canny(blurred, low_threshold, high_threshold)
        
        return self.edges
    
    def find_contours(self, edge_image=None):
        """
        Find contours from edge image.
        
        Args:
            edge_image: Binary edge image (uses self.edges if None)
            
        Returns:
            list: List of contours
        """
        if edge_image is None:
            edge_image = self.edges
        
        if edge_image is None:
            return []
        
        # Find contours
        contours, hierarchy = cv2.findContours(
            edge_image, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_NONE
        )
        
        self.contours = contours
        return contours
    
    def approximate_contours_with_lines(self, contours=None, epsilon_factor=0.01):
        """
        Approximate contours with straight lines using Douglas-Peucker algorithm.
        
        Args:
            contours: List of contours (uses self.contours if None)
            epsilon_factor: Approximation accuracy factor
            
        Returns:
            list: List of approximated contours
        """
        if contours is None:
            contours = self.contours
        
        if contours is None:
            return []
        
        approximations = []
        for contour in contours:
            # Calculate epsilon based on contour perimeter
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            
            # Approximate contour
            approx = cv2.approxPolyDP(contour, epsilon, True)
            approximations.append(approx)
        
        self.line_approximations = approximations
        return approximations
    
    def refine_edges_subpixel(self, image, edge_image=None, window_size=5):
        """
        Refine edge positions to subpixel accuracy for each row.
        
        Args:
            image: Original grayscale image
            edge_image: Binary edge image (uses self.edges if None)
            window_size: Size of window for subpixel refinement
            
        Returns:
            dict: Dictionary with row indices as keys and list of edge positions as values
        """
        if edge_image is None:
            edge_image = self.edges
        
        if edge_image is None:
            return {}
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        edge_positions = {}
        height, width = edge_image.shape
        
        # Process each row
        for row in range(height):
            # Find edge pixels in this row
            edge_cols = np.where(edge_image[row, :] > 0)[0]
            
            if len(edge_cols) == 0:
                continue
            
            subpixel_positions = []
            
            for col in edge_cols:
                # Extract intensity profile around the edge
                start_col = max(0, col - window_size)
                end_col = min(width, col + window_size + 1)
                
                profile = gray[row, start_col:end_col].astype(np.float64)
                
                if len(profile) < 3:
                    continue
                
                # Calculate gradient
                gradient = np.gradient(profile)
                
                # Find the maximum gradient position (steepest edge)
                max_grad_idx = np.argmax(np.abs(gradient))
                
                # Fit a parabola around the maximum for subpixel accuracy
                if max_grad_idx > 0 and max_grad_idx < len(gradient) - 1:
                    # Use three points for parabolic interpolation
                    y1, y2, y3 = gradient[max_grad_idx-1:max_grad_idx+2]
                    
                    # Parabolic interpolation formula
                    if abs(2*y2 - y1 - y3) > 1e-6:
                        offset = 0.5 * (y1 - y3) / (2*y2 - y1 - y3)
                    else:
                        offset = 0.0
                    
                    subpixel_col = start_col + max_grad_idx + offset
                    subpixel_positions.append(subpixel_col)
            
            if subpixel_positions:
                edge_positions[row] = sorted(subpixel_positions)
        
        self.edge_positions = edge_positions
        return edge_positions
    
    def calculate_line_widths(self, edge_positions=None):
        """
        Calculate line widths from edge positions.
        Assumes edges come in pairs (left and right edges of lines).
        
        Args:
            edge_positions: Dictionary of edge positions per row
            
        Returns:
            list: List of measurement dictionaries containing line width info
        """
        if edge_positions is None:
            edge_positions = self.edge_positions
        
        if edge_positions is None or len(edge_positions) == 0:
            return []
        
        measurements = []
        
        # For each row, pair up edges that are close together
        # Collect all edge pairs across all rows
        all_pairs = []
        
        for row, positions in edge_positions.items():
            if len(positions) < 2:
                continue
            
            # Pair consecutive edges (assuming they form line boundaries)
            for i in range(0, len(positions) - 1, 2):
                if i + 1 < len(positions):
                    left_pos = positions[i]
                    right_pos = positions[i + 1]
                    width = right_pos - left_pos
                    
                    # Only consider reasonable widths (filter out noise)
                    if width > 5 and width < 500:
                        center = (left_pos + right_pos) / 2
                        all_pairs.append({
                            'row': row,
                            'left': left_pos,
                            'right': right_pos,
                            'width': width,
                            'center': center
                        })
        
        if len(all_pairs) == 0:
            self.measurements = []
            return []
        
        # Group pairs that belong to the same line (similar center position)
        # Sort by center position
        all_pairs.sort(key=lambda x: x['center'])
        
        line_groups = []
        current_group = [all_pairs[0]]
        
        for i in range(1, len(all_pairs)):
            pair = all_pairs[i]
            prev_pair = all_pairs[i - 1]
            
            # If centers are close (within 50 pixels), they're likely the same line
            if abs(pair['center'] - prev_pair['center']) < 50:
                current_group.append(pair)
            else:
                if len(current_group) > 0:
                    line_groups.append(current_group)
                current_group = [pair]
        
        if len(current_group) > 0:
            line_groups.append(current_group)
        
        # Calculate statistics for each line group
        for group in line_groups:
            if len(group) < 3:  # Require at least 3 samples for a valid measurement
                continue
            
            widths = [p['width'] for p in group]
            rows = [p['row'] for p in group]
            centers = [p['center'] for p in group]
            left_edges = [p['left'] for p in group]
            right_edges = [p['right'] for p in group]
            
            measurement = {
                'mean_width': np.mean(widths),
                'std_width': np.std(widths),
                'min_width': np.min(widths),
                'max_width': np.max(widths),
                'num_samples': len(widths),
                'center_x': np.mean(centers),
                'center_y': np.mean(rows),
                'rows': rows,
                'left_edge': left_edges,
                'right_edge': right_edges
            }
            measurements.append(measurement)
        
        self.measurements = measurements
        return measurements
    
    def draw_results(self, image, edge_image=None, approximations=None, 
                    measurements=None, show_edges=True, show_approx=True, 
                    show_measurements=True):
        """
        Draw processing results on the image.
        
        Args:
            image: Original image to draw on
            edge_image: Edge detection result
            approximations: Line approximations
            measurements: Width measurements
            show_edges: Whether to show edge overlay
            show_approx: Whether to show line approximations
            show_measurements: Whether to show measurements
            
        Returns:
            numpy.ndarray: Image with results drawn
        """
        result = image.copy()
        
        # Draw edges in green
        if show_edges and edge_image is not None:
            edge_overlay = cv2.cvtColor(edge_image, cv2.COLOR_GRAY2BGR)
            edge_overlay[:, :, 1] = edge_image  # Green channel
            result = cv2.addWeighted(result, 0.7, edge_overlay, 0.3, 0)
        
        # Draw line approximations in blue
        if show_approx and approximations is not None:
            for approx in approximations:
                cv2.drawContours(result, [approx], -1, (255, 0, 0), 2)
        
        # Draw measurements
        if show_measurements and measurements is not None:
            for i, meas in enumerate(measurements):
                center_x = int(meas['center_x'])
                center_y = int(meas['center_y'])
                mean_width = meas['mean_width']
                std_width = meas['std_width']
                
                # Draw measurement line
                half_width = int(mean_width / 2)
                cv2.line(result, 
                        (center_x - half_width, center_y),
                        (center_x + half_width, center_y),
                        (0, 255, 255), 2)
                
                # Draw arrows at ends
                cv2.arrowedLine(result,
                              (center_x - half_width, center_y),
                              (center_x - half_width - 20, center_y),
                              (0, 255, 255), 2)
                cv2.arrowedLine(result,
                              (center_x + half_width, center_y),
                              (center_x + half_width + 20, center_y),
                              (0, 255, 255), 2)
                
                # Add text with measurement
                text = f"Width: {mean_width:.2f} +/- {std_width:.2f} px"
                text_y = center_y - 20
                
                # Add background for text
                (text_width, text_height), _ = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                cv2.rectangle(result,
                            (center_x - text_width // 2 - 5, text_y - text_height - 5),
                            (center_x + text_width // 2 + 5, text_y + 5),
                            (0, 0, 0), -1)
                
                # Draw text
                cv2.putText(result, text,
                           (center_x - text_width // 2, text_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return result
