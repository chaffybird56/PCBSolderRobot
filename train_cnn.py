#!/usr/bin/env python3
import tensorflow as tf
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

def train_two_phase_finetuning(data_dir, batch_size=8, img_size=(224,224), epochs1=5, epochs2=5):
    """
    Example code for a two-phase fine-tuning approach.
    1) Phase 1: Freeze partial network from layer 0..fine_tune_at, train at LR=1e-4
    2) Phase 2: Unfreeze more layers (or all), reduce LR to e.g. 1e-5, train more.
    """

    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        validation_split=0.2
    )

    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )

    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )

    base_model = MobileNetV2(weights='imagenet', include_top=False,
                             input_shape=(img_size[0], img_size[1], 3))

    # Phase 1: Partial freeze
    fine_tune_at = 100
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False
    for layer in base_model.layers[fine_tune_at:]:
        layer.trainable = True

    # Build the top model
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        # Dropout 
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dense(train_generator.num_classes, activation='softmax')
    ])

    # Phase 1 compile: LR=1e-4
    optimizer = Adam(learning_rate=1e-4)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    print("------ Phase 1 training ------")
    model.fit(
        train_generator,
        epochs=epochs1,
        validation_data=val_generator,
        callbacks=[early_stop]
    )

    # Phase 2: Unfreeze more (or all) + lower LR
    base_model.trainable = True
    # Optional: unfreeze from layer 80, or 0 for all. Example:
    # for layer in base_model.layers[:80]:
    #     layer.trainable = False

    model.compile(
        optimizer=Adam(learning_rate=1e-5),  # smaller LR
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    print("------ Phase 2 fine-tuning ------")
    model.fit(
        train_generator,
        epochs=epochs2,
        validation_data=val_generator,
        callbacks=[early_stop]
    )

    model.save("solder_classifier_two_phase.keras")
    print("Saved two-phase model -> 'solder_classifier_two_phase.keras'")

def main():
    data_dir = "labeled_data"
    train_two_phase_finetuning(
        data_dir,
        batch_size=8,
        img_size=(224,224),
        epochs1=5,   # e.g. 5 epochs for phase 1
        epochs2=5    # e.g. 5 epochs for phase 2
    )

if __name__ == "__main__":
    main()


import tkinter as tk
from tkinter import ttk, filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np

class SolderingApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PCB Soldering QA/QC App")
        self.geometry("1000x600")

        # ----- CAMERA CAPTURE -----
        # is it device 0?
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera. Please check the camera connection.")

        self.last_frame = None      # Will hold the most recent camera frame in OpenCV format
        self.captured_image = None  # Holds the captured image (PIL format)

        # ----- UI ELEMENTS -----
        # Main frames for layout
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Camera feed label
        self.camera_label = ttk.Label(self.left_frame, text="Camera Feed")
        self.camera_label.pack(padx=10, pady=10)

        # Captured / Classified image label
        self.image_label = ttk.Label(self.right_frame, text="Captured / Classified Image")
        self.image_label.pack(padx=10, pady=10)

        # Buttons
        self.capture_button = ttk.Button(
            self.left_frame, text="Capture Image", command=self.capture_image
        )
        self.capture_button.pack(padx=10, pady=5)

        self.classify_button = ttk.Button(
            self.left_frame, text="Classify", command=self.run_classification
        )
        self.classify_button.pack(padx=10, pady=5)

        self.save_button = ttk.Button(
            self.left_frame, text="Save Image", command=self.save_classified_image
        )
        self.save_button.pack(padx=10, pady=5)

        # Start updating the camera feed
        self.update_camera_feed()

    def update_camera_feed(self):
        """Continuously capture frames from the camera and display them in the GUI."""
        ret, frame = self.cap.read()
        if ret:
            # Keep the latest frame in memory (OpenCV format)
            self.last_frame = frame

            # Convert the frame to a format Tkinter can display
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=pil_image)

            self.camera_label.imgtk = imgtk  # Keep a reference!
            self.camera_label.configure(image=imgtk)

        # Schedule the next update
        self.after(10, self.update_camera_feed)

    def capture_image(self):
        """Captures the current frame and displays it in the image_label."""
        if self.last_frame is not None:
            # Convert the last OpenCV frame to a PIL Image
            cv2image = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
            self.captured_image = Image.fromarray(cv2image)

            # Display it in the right panel
            imgtk = ImageTk.PhotoImage(image=self.captured_image)
            self.image_label.imgtk = imgtk
            self.image_label.configure(image=imgtk)

    def run_classification(self):
        """
       you would run inference model with yolo here,
        detect components/defects, and draw bounding boxes, etc.
        """
        if self.captured_image is not None:


            # Display the classified image in the UI
            imgtk = ImageTk.PhotoImage(image=?)
            self.image_label.imgtk = imgtk
            self.image_label.configure(image=imgtk)

    def save_classified_image(self):
        """
        Saves the classified image to a folder chosen by the user.
         specify a default directory, or let them choose any path.
        """
        if self.captured_image is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All Files", "*.*")]
            )
            if file_path:
                self.captured_image.save(file_path)

    def on_closing(self):
        """Release the camera and destroy the window properly."""
        self.cap.release()
        self.destroy()

def main():
    app = SolderingApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()