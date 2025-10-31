#!/usr/bin/env python3
import cv2
import numpy as np
import os
import tensorflow as tf

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# Import the same morphological segmentation function used to train
from image_seg import select_joint_method_fixed

def load_classifier(model_path="solder_classifier.keras"):
    """
    Loads the trained CNN model (e.g., your MobileNetV2-based classifier).
    """
    model = tf.keras.models.load_model(model_path)
    return model

def run_inference_on_image(input_image, model_path="solder_classifier.keras"):
    """
    1) Detect bounding boxes on 'input_image' using the morphological pipeline.
    2) Crop each box, run the trained classifier to get "good"/"bad"/"missing" predictions.
    3) Draw the predicted label on the overlay, save final result as e.g. 'inference_result.png'.
    """
    # 1. Load the trained classifier
    model = load_classifier(model_path)

    # 2. Use the morphological pipeline to get bounding boxes
    #    (No cropping to PCB – we rely on dilation, etc. as per your updated code.)
    bgr_eq, boxes = select_joint_method_fixed(
        input_image,
        do_hist_eq=False,
        otsu_invert=True,
        value_low_thresh=80,
        median_ksize=3,
        morph_open_ksize=4,
        morph_close_ksize=5,
        min_box_size=15,
        max_box_size=500,
        morph_dilate_ksize=9,
        morph_dilate_iterations=2
    )
    print(f"Detected {len(boxes)} bounding boxes in {input_image}")

    # 3. Prepare a class_names list matching the alphabetical order of training folders
    #    E.g., if subfolders were labeled_data/bad, labeled_data/good, labeled_data/missing
    #    then alphabetical is: ["bad", "good", "missing"]
    class_names = ["bad", "good", "missing"]

    # 4. Create an overlay to draw the predictions
    overlay = bgr_eq.copy()

    for i, (x, y, w, h) in enumerate(boxes):
        # Crop the patch from the bounding box
        patch = bgr_eq[y:y+h, x:x+w]

        # Preprocess for MobileNetV2
        patch_resized = cv2.resize(patch, (224, 224))
        patch_array = np.expand_dims(patch_resized, axis=0).astype("float32")
        patch_array = preprocess_input(patch_array)  # scale to match training

        # 5. Classify
        preds = model.predict(patch_array)  # shape: (1, 3)
        class_idx = np.argmax(preds[0])
        class_label = class_names[class_idx]
        confidence = preds[0][class_idx]

        # Determine the color: red for 'missing', yellow for others
        if class_label == "missing":
            color = (0, 0, 255)  # Red in BGR
        else:
            color = (0, 255, 255)  # Yellow in BGR

        # Print or draw info
        print(f"Box #{i}: {class_label} ({confidence*100:.1f}%)")
        cv2.putText(
            overlay, f"{class_label} {confidence*100:.1f}%",
            (x, max(y-5, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            color, 2
        )
        cv2.rectangle(overlay, (x, y), (x+w, y+h), color, 2)

    # 6. Save the final overlay
    out_name = "inference_result.png"
    cv2.imwrite(out_name, overlay)
    print(f"Saved inference overlay -> {out_name}")

def main():
    test_image = "test2.png"
    run_inference_on_image(test_image, "solder_classifier_two_phase.keras")

if __name__ == "__main__":
    main()