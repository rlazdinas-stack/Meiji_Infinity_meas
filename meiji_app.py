#!/usr/bin/env python3
"""
Meiji Microscope Line Width Measuring Application
Main application with live view functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import threading
import time


class CameraInterface:
    """
    Camera interface wrapper for Lumenera Infinity SDK
    Falls back to OpenCV for testing when SDK is not available
    """
    
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.use_opencv_fallback = True
        
    def initialize(self):
        """Initialize camera connection"""
        try:
            # Try to initialize Lumenera SDK (placeholder for actual SDK)
            # In production, this would use: from lucamapi import LucamCamera
            # self.camera = LucamCamera()
            
            # For now, fallback to OpenCV for testing
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
            self.use_opencv_fallback = True
            return True
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def start_capture(self):
        """Start camera capture"""
        self.is_running = True
        
    def stop_capture(self):
        """Stop camera capture"""
        self.is_running = False
        
    def get_frame(self):
        """Get a single frame from the camera"""
        if self.camera is None or not self.is_running:
            return None
            
        if self.use_opencv_fallback:
            ret, frame = self.camera.read()
            if ret:
                # Convert BGR to RGB for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame
        return None
    
    def release(self):
        """Release camera resources"""
        self.is_running = False
        if self.camera is not None:
            if self.use_opencv_fallback:
                self.camera.release()
            self.camera = None


class MeijiApp:
    """Main application class for Meiji microscope measurement"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Meiji Microscope - Line Width Measurement")
        self.root.geometry("1024x768")
        
        # Initialize camera interface
        self.camera = CameraInterface()
        
        # Live view state
        self.live_view_active = False
        self.update_thread = None
        
        # Setup UI
        self.setup_ui()
        
        # Initialize camera
        if self.camera.initialize():
            print("Camera initialized successfully")
        else:
            messagebox.showwarning("Camera Warning", 
                "Could not initialize camera. Live view may not work.")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel at top
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Live View button
        self.live_view_btn = ttk.Button(
            control_frame, 
            text="Start Live View",
            command=self.toggle_live_view
        )
        self.live_view_btn.grid(row=0, column=0, padx=5)
        
        # Measure button
        self.measure_btn = ttk.Button(
            control_frame,
            text="Measure",
            command=self.capture_and_measure,
            state=tk.DISABLED
        )
        self.measure_btn.grid(row=0, column=1, padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="Status: Ready"
        )
        self.status_label.grid(row=0, column=2, padx=20)
        
        # Live view display area
        display_frame = ttk.LabelFrame(main_frame, text="Live View", padding="10")
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas for displaying camera feed
        self.canvas = tk.Canvas(
            display_frame, 
            bg='black',
            width=800,
            height=600
        )
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Placeholder text
        self.canvas.create_text(
            400, 300,
            text="Live view not active\nClick 'Start Live View' to begin",
            fill="white",
            font=("Arial", 16),
            tags="placeholder"
        )
    
    def toggle_live_view(self):
        """Toggle live view on/off"""
        if not self.live_view_active:
            self.start_live_view()
        else:
            self.stop_live_view()
    
    def start_live_view(self):
        """Start the live view"""
        if self.camera.start_capture():
            self.live_view_active = True
            self.live_view_btn.config(text="Stop Live View")
            self.measure_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Live View Active")
            
            # Remove placeholder
            self.canvas.delete("placeholder")
            
            # Start update thread
            self.update_thread = threading.Thread(target=self.update_live_view, daemon=True)
            self.update_thread.start()
        else:
            self.camera.start_capture()
            self.live_view_active = True
            self.live_view_btn.config(text="Stop Live View")
            self.measure_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Live View Active")
            
            # Remove placeholder
            self.canvas.delete("placeholder")
            
            # Start update thread
            self.update_thread = threading.Thread(target=self.update_live_view, daemon=True)
            self.update_thread.start()
    
    def stop_live_view(self):
        """Stop the live view"""
        self.live_view_active = False
        self.camera.stop_capture()
        self.live_view_btn.config(text="Start Live View")
        self.measure_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Live View Stopped")
        
        # Clear canvas and show placeholder
        self.canvas.delete("all")
        self.canvas.create_text(
            400, 300,
            text="Live view not active\nClick 'Start Live View' to begin",
            fill="white",
            font=("Arial", 16),
            tags="placeholder"
        )
    
    def update_live_view(self):
        """Update the live view display - runs in separate thread"""
        while self.live_view_active:
            frame = self.camera.get_frame()
            if frame is not None:
                # Resize frame to fit canvas
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # Use default size if canvas not yet rendered
                if canvas_width <= 1:
                    canvas_width = 800
                if canvas_height <= 1:
                    canvas_height = 600
                
                # Calculate aspect ratio preserving resize
                h, w = frame.shape[:2]
                aspect = w / h
                
                if canvas_width / canvas_height > aspect:
                    new_h = canvas_height
                    new_w = int(canvas_height * aspect)
                else:
                    new_w = canvas_width
                    new_h = int(canvas_width / aspect)
                
                # Resize frame
                frame_resized = cv2.resize(frame, (new_w, new_h))
                
                # Convert to PhotoImage
                image = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(image=image)
                
                # Update canvas on main thread
                self.root.after(0, self._update_canvas, photo)
            
            # Control frame rate
            time.sleep(1/30)  # ~30 fps
    
    def _update_canvas(self, photo):
        """Update canvas with new image - must run on main thread"""
        self.canvas.delete("all")
        self.canvas.create_image(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            image=photo
        )
        # Keep a reference to prevent garbage collection
        self.canvas.image = photo
    
    def capture_and_measure(self):
        """Capture current frame and perform measurements"""
        frame = self.camera.get_frame()
        if frame is not None:
            self.status_label.config(text="Status: Image captured - Ready for measurement")
            messagebox.showinfo("Capture", "Image captured successfully!\nMeasurement features to be implemented.")
        else:
            messagebox.showerror("Error", "Failed to capture image")
    
    def cleanup(self):
        """Cleanup resources before closing"""
        self.stop_live_view()
        self.camera.release()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MeijiApp(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.cleanup)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
