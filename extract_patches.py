#!/usr/bin/env python3
import cv2
import os
import numpy as np

from image_seg import select_joint_method_fixed
# Removed crop_to_pcb import since it's no longer used

def extract_solder_patches(input_image_path, output_dir):
    """
    1) Loads the image
    2) Runs the Select Joint pipeline to get bounding boxes
    3) For each box, saves a patch as a .png into output_dir
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1) Load the image
    raw_img = cv2.imread(input_image_path)
    if raw_img is None:
        raise ValueError(f"Could not read image {input_image_path}")

    # Directly process the original image without cropping
    bgr_eq, boxes = select_joint_method_fixed(
        input_image_path,
        do_hist_eq=True,
        otsu_invert=True,
        value_low_thresh=80,
        median_ksize=3,
        morph_open_ksize=4,
        morph_close_ksize=5,
        min_box_size=15,
        max_box_size=500
    )

    print(f"Detected {len(boxes)} bounding boxes in {input_image_path}")

    # 3) Crop each bounding box and save the patch
    base_name = os.path.splitext(os.path.basename(input_image_path))[0]
    for i, (x, y, w, h) in enumerate(boxes):
        patch = bgr_eq[y:y+h, x:x+w]
        patch_filename = f"{base_name}_patch_{i}.png"
        patch_path = os.path.join(output_dir, patch_filename)
        cv2.imwrite(patch_path, patch)
        print(f"Saved patch -> {patch_path}")

def main():
    # Example usage: process a single image
    images = ["test6.jpg","test2.png"]

    for img_file in images:
        extract_solder_patches(img_file, output_dir="unlabeled_patches")

if __name__ == "__main__":
    main()