import tkinter as tk
from tkinter import ttk, filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np

from ultralytics import YOLO
from picamera2 import Picamera2

class SolderingApp(tk.Tk):
    def __init__(self, model_path="best.pt", confidence_threshold=0.5):
        """
        model_path: Path to the YOLO model (e.g. 'best.pt' if in the same directory).
        confidence_threshold: Minimum confidence to draw bounding boxes.
        """
        super().__init__()

        self.title("PCB Soldering QA/QC App (YOLO Inference)")
        self.geometry("1000x600")

        # --- Load YOLO model ---
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

        # --- Set up Pi Camera 2 ---
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"format": "RGB888", "size": (640, 480)}
        )
        self.picam2.configure(config)
        self.picam2.start()

        self.last_frame = None      # Stores the most recent camera frame (NumPy array, RGB)
        self.captured_image = None  # Stores the captured image (PIL format)

        # --- Define UI Layout ---
        # Left frame holds live camera feed and buttons.
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Subdivide left frame into feed display and button area.
        self.feed_frame = ttk.Frame(self.left_frame)
        self.feed_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Right frame for the captured or classified image.
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Label for camera feed.
        self.camera_label = ttk.Label(self.feed_frame, text="Camera Feed")
        self.camera_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons for capture, classification, saving, and exit.
        self.capture_button = ttk.Button(
            self.button_frame, text="Capture Image", command=self.capture_image
        )
        self.capture_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.classify_button = ttk.Button(
            self.button_frame, text="Classify (ML)", command=self.run_classification
        )
        self.classify_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.save_button = ttk.Button(
            self.button_frame, text="Save Image", command=self.save_classified_image
        )
        self.save_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.exit_button = ttk.Button(
            self.button_frame, text="Exit", command=self.on_closing
        )
        self.exit_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Label for captured/classified image.
        self.image_label = ttk.Label(self.right_frame, text="Captured / Classified Image")
        self.image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Start updating the camera feed.
        self.update_camera_feed()

    def update_camera_feed(self):
        """
        Continuously capture frames from the Pi Camera 2 and display them in the GUI.
        """
        frame = self.picam2.capture_array()  # returns an RGB NumPy array
        if frame is not None:
            self.last_frame = frame  # Update last_frame for capture
            pil_image = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=pil_image)
            self.camera_label.imgtk = imgtk  # Prevent garbage collection.
            self.camera_label.configure(image=imgtk)
        # Update again after 30 ms.
        self.after(30, self.update_camera_feed)

    def capture_image(self):
        """
        Captures the current frame (self.last_frame) and displays it on the right.
        """
        if self.last_frame is not None:
            self.captured_image = Image.fromarray(self.last_frame)
            imgtk = ImageTk.PhotoImage(image=self.captured_image)
            self.image_label.imgtk = imgtk
            self.image_label.configure(image=imgtk)

    def run_classification(self):
        """
        Runs YOLO inference on the captured image, draws colored bounding boxes
        based on class name, and updates the display.
        """
        if self.captured_image is not None:
            # Convert from PIL (RGB) to OpenCV format (BGR).
            open_cv_image = cv2.cvtColor(np.array(self.captured_image), cv2.COLOR_RGB2BGR)

            # YOLO Inference.
            results = self.model(open_cv_image, verbose=False)
            detections = results[0].boxes  # Get detections from the first result.

            for box in detections:
                conf = float(box.conf[0].item())
                if conf < self.confidence_threshold:
                    continue

                cls_id = int(box.cls[0].item())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                xmin, ymin, xmax, ymax = xyxy

                # Get class name.
                class_name = self.model.names.get(cls_id, f"CLS_{cls_id}")

                # Determine bounding box color based on class name.
                if class_name.lower() == "good":
                    color = (0, 255, 0)        # Green.
                elif class_name.lower() == "missing":
                    color = (0, 0, 255)        # red.
                elif class_name.lower() == "red":
                    color = (0, 165, 255)      # Orange.
                else:
                    color = (255, 255, 255)    # White as default.

                # Draw bounding box.
                cv2.rectangle(open_cv_image, (xmin, ymin), (xmax, ymax), color, 2)
                label = f"{class_name}: {conf:.2f}"
                cv2.putText(
                    open_cv_image, label, (xmin, max(ymin - 5, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
                )

            # Convert back to PIL for display.
            classified_pil = Image.fromarray(cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB))
            self.captured_image = classified_pil
            imgtk = ImageTk.PhotoImage(image=classified_pil)
            self.image_label.imgtk = imgtk
            self.image_label.configure(image=imgtk)

    def save_classified_image(self):
        """
        Saves the current classified (annotated) image to a user-chosen file.
        """
        if self.captured_image is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All Files", "*.*")]
            )
            if file_path:
                self.captured_image.save(file_path)

    def on_closing(self):
        """Stop the camera and close the application."""
        self.picam2.stop()
        self.destroy()

def main():
    app = SolderingApp(model_path="best.pt", confidence_threshold=0.5)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()