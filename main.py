"""
Meiji Infinity Measurement Application
Main application for live camera view and line width measurement.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
from camera_interface import LumeneraCamera
from image_processing import ImageProcessor


class MeijiMeasurementApp:
    """
    Main application window for Meiji microscope line width measurement.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Meiji Infinity Measurement")
        self.root.geometry("1400x900")
        
        # Initialize camera and processor
        self.camera = LumeneraCamera()
        self.processor = ImageProcessor()
        
        # State variables
        self.is_running = False
        self.current_frame = None
        self.captured_frame = None
        self.processed_frame = None
        self.update_thread = None
        
        # Thread lock for frame access
        self.frame_lock = threading.Lock()
        
        # Create GUI
        self._create_widgets()
        
        # Start camera
        self._initialize_camera()
    
    def _create_widgets(self):
        """Create and layout GUI widgets."""
        
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Control panel
        control_panel = ttk.Frame(main_container)
        control_panel.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Title
        title_label = ttk.Label(control_panel, text="Meiji Infinity Measurement", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=6, pady=(0, 10))
        
        # Control buttons
        self.start_btn = ttk.Button(control_panel, text="Start Live View", 
                                    command=self._start_live_view)
        self.start_btn.grid(row=1, column=0, padx=5)
        
        self.stop_btn = ttk.Button(control_panel, text="Stop", 
                                   command=self._stop_live_view, state='disabled')
        self.stop_btn.grid(row=1, column=1, padx=5)
        
        self.meas_btn = ttk.Button(control_panel, text="Meas", 
                                   command=self._measure, state='disabled',
                                   style='Accent.TButton')
        self.meas_btn.grid(row=1, column=2, padx=5)
        
        self.clear_btn = ttk.Button(control_panel, text="Clear", 
                                    command=self._clear_measurement)
        self.clear_btn.grid(row=1, column=3, padx=5)
        
        # Edge detection parameters
        ttk.Label(control_panel, text="Canny Low:").grid(row=1, column=4, padx=(20, 5))
        self.canny_low = tk.IntVar(value=50)
        canny_low_spin = ttk.Spinbox(control_panel, from_=0, to=255, 
                                     textvariable=self.canny_low, width=8)
        canny_low_spin.grid(row=1, column=5, padx=5)
        
        ttk.Label(control_panel, text="Canny High:").grid(row=2, column=4, padx=(20, 5))
        self.canny_high = tk.IntVar(value=150)
        canny_high_spin = ttk.Spinbox(control_panel, from_=0, to=255, 
                                      textvariable=self.canny_high, width=8)
        canny_high_spin.grid(row=2, column=5, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Status: Ready")
        status_label = ttk.Label(control_panel, textvariable=self.status_var, 
                                font=('Arial', 10))
        status_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Display area
        display_container = ttk.Frame(main_container)
        display_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_container.columnconfigure(0, weight=1)
        display_container.columnconfigure(1, weight=1)
        display_container.rowconfigure(0, weight=1)
        
        # Live view panel
        live_panel = ttk.LabelFrame(display_container, text="Live View", padding="5")
        live_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        live_panel.columnconfigure(0, weight=1)
        live_panel.rowconfigure(0, weight=1)
        
        self.live_canvas = tk.Canvas(live_panel, bg='black', width=640, height=512)
        self.live_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Measurement panel
        meas_panel = ttk.LabelFrame(display_container, text="Measurement Result", padding="5")
        meas_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        meas_panel.columnconfigure(0, weight=1)
        meas_panel.rowconfigure(0, weight=1)
        
        self.meas_canvas = tk.Canvas(meas_panel, bg='black', width=640, height=512)
        self.meas_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results text area
        results_frame = ttk.LabelFrame(main_container, text="Measurement Results", padding="5")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        
        # Create scrolled text widget
        text_scroll = ttk.Scrollbar(results_frame)
        text_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.results_text = tk.Text(results_frame, height=8, width=80, 
                                   yscrollcommand=text_scroll.set)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        text_scroll.config(command=self.results_text.yview)
        
    def _initialize_camera(self):
        """Initialize the camera."""
        if self.camera.open():
            self.status_var.set("Status: Camera connected")
        else:
            self.status_var.set("Status: Camera connection failed")
            messagebox.showwarning("Camera", "Could not connect to camera. Running in simulation mode.")
    
    def _start_live_view(self):
        """Start live view from camera."""
        if not self.is_running:
            if self.camera.start_streaming():
                self.is_running = True
                self.start_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                self.meas_btn.config(state='normal')
                self.status_var.set("Status: Live view active")
                
                # Start update thread
                self.update_thread = threading.Thread(target=self._update_live_view, daemon=True)
                self.update_thread.start()
            else:
                messagebox.showerror("Error", "Failed to start camera streaming")
    
    def _stop_live_view(self):
        """Stop live view."""
        if self.is_running:
            self.is_running = False
            self.camera.stop_streaming()
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.meas_btn.config(state='disabled')
            self.status_var.set("Status: Live view stopped")
    
    def _update_live_view(self):
        """Update live view in separate thread."""
        while self.is_running:
            frame = self.camera.grab_frame()
            if frame is not None:
                with self.frame_lock:
                    self.current_frame = frame
                # Update display in main thread
                self.root.after(0, self._display_live_frame, frame)
            time.sleep(0.033)  # ~30 fps
    
    def _display_live_frame(self, frame):
        """Display frame in live view canvas."""
        if frame is None:
            return
        
        # Resize frame to fit canvas
        canvas_width = self.live_canvas.winfo_width()
        canvas_height = self.live_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate scaling to fit canvas while maintaining aspect ratio
            h, w = frame.shape[:2]
            scale = min(canvas_width / w, canvas_height / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            resized = cv2.resize(frame, (new_w, new_h))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=img)
            
            # Update canvas
            self.live_canvas.delete("all")
            x = (canvas_width - new_w) // 2
            y = (canvas_height - new_h) // 2
            self.live_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.live_canvas.image = photo  # Keep a reference
    
    def _measure(self):
        """Capture image and perform measurement."""
        # Safely copy current frame
        with self.frame_lock:
            if self.current_frame is None:
                messagebox.showwarning("Warning", "No frame available for measurement")
                return
            self.captured_frame = self.current_frame.copy()
        
        self.status_var.set("Status: Processing measurement...")
        self.results_text.delete(1.0, tk.END)
        
        # Process in separate thread to avoid blocking GUI
        threading.Thread(target=self._process_measurement, daemon=True).start()
    
    def _process_measurement(self):
        """Process the captured frame for measurement."""
        try:
            # Get parameters
            low_thresh = self.canny_low.get()
            high_thresh = self.canny_high.get()
            
            # Detect edges
            edges = self.processor.detect_edges(self.captured_frame, low_thresh, high_thresh)
            
            # Find contours
            contours = self.processor.find_contours(edges)
            
            # Approximate with lines
            approximations = self.processor.approximate_contours_with_lines(contours)
            
            # Refine edges to subpixel
            edge_positions = self.processor.refine_edges_subpixel(self.captured_frame, edges)
            
            # Calculate measurements
            measurements = self.processor.calculate_line_widths(edge_positions)
            
            # Draw results
            result_image = self.processor.draw_results(
                self.captured_frame,
                edges,
                approximations,
                measurements,
                show_edges=True,
                show_approx=True,
                show_measurements=True
            )
            
            self.processed_frame = result_image
            
            # Update display in main thread
            self.root.after(0, self._display_measurement_result, result_image, measurements)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Measurement failed: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Status: Measurement failed"))
    
    def _display_measurement_result(self, result_image, measurements):
        """Display measurement result."""
        # Display image
        canvas_width = self.meas_canvas.winfo_width()
        canvas_height = self.meas_canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate scaling
            h, w = result_image.shape[:2]
            scale = min(canvas_width / w, canvas_height / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            resized = cv2.resize(result_image, (new_w, new_h))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=img)
            
            # Update canvas
            self.meas_canvas.delete("all")
            x = (canvas_width - new_w) // 2
            y = (canvas_height - new_h) // 2
            self.meas_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.meas_canvas.image = photo  # Keep a reference
        
        # Display measurement text
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "=== Line Width Measurements ===\n\n")
        
        if len(measurements) == 0:
            self.results_text.insert(tk.END, "No lines detected.\n")
            self.results_text.insert(tk.END, "Try adjusting Canny thresholds.\n")
        else:
            for i, meas in enumerate(measurements):
                self.results_text.insert(tk.END, f"Line {i+1}:\n")
                self.results_text.insert(tk.END, f"  Mean Width: {meas['mean_width']:.3f} pixels\n")
                self.results_text.insert(tk.END, f"  Std Dev: {meas['std_width']:.3f} pixels\n")
                self.results_text.insert(tk.END, f"  Min Width: {meas['min_width']:.3f} pixels\n")
                self.results_text.insert(tk.END, f"  Max Width: {meas['max_width']:.3f} pixels\n")
                self.results_text.insert(tk.END, f"  Samples: {meas['num_samples']} rows\n")
                self.results_text.insert(tk.END, f"  Position: ({meas['center_x']:.1f}, {meas['center_y']:.1f})\n")
                self.results_text.insert(tk.END, "\n")
        
        self.status_var.set(f"Status: Measurement complete - {len(measurements)} line(s) detected")
    
    def _clear_measurement(self):
        """Clear measurement results."""
        self.meas_canvas.delete("all")
        self.results_text.delete(1.0, tk.END)
        self.processed_frame = None
        self.status_var.set("Status: Results cleared")
    
    def cleanup(self):
        """Cleanup resources."""
        self.is_running = False
        if self.camera:
            self.camera.close()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = MeijiMeasurementApp(root)
    
    # Handle window close
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
