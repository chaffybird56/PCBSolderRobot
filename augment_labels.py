#!/usr/bin/env python3
import os
import cv2
import numpy as np
import random

############################
# 1) Define your augmentations
############################

def rotate_image(image, angle):
    """Rotate the image by a given angle."""
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h))
    return rotated

def flip_image(image, mode):
    """Flip image horizontally (mode=1) or vertically (mode=0)."""
    return cv2.flip(image, mode)

def adjust_brightness_contrast(image, brightness=30, contrast=50):
    """
    Adjust brightness and contrast of the image.
    brightness in [-127, +127], contrast in [-127, +127].
    """
    img = np.int16(image)
    img = img * (contrast / 127 + 1) - contrast + brightness
    img = np.clip(img, 0, 255)
    return np.uint8(img)


############################
# 2) Decide how many augmented images you want per real patch
############################

def augment_image(image):
    """
    Given an input patch,
    randomly choose an augmentation or combination of augmentations.
    """
    # We'll pick one or two transformations randomly
    transformations = []

    # E.g., 50% chance to rotate
    if random.random() < 0.5:
        angle = random.choice([90, 180, 270])
        transformations.append(("rot", angle))

    # 50% chance to flip horizontally
    if random.random() < 0.5:
        transformations.append(("flip_h", 1))

    # 30% chance to flip vertically
    if random.random() < 0.3:
        transformations.append(("flip_v", 0))

    # 50% chance to do brightness/contrast
    if random.random() < 0.5:
        brightness = random.randint(-50, 50)   # range of brightness
        contrast = random.randint(-30, 30)    # range of contrast
        transformations.append(("bri_con", (brightness, contrast)))

    # 30% chance for gaussian blur
    if random.random() < 0.3:
        transformations.append(("blur", (5,5)))

    # 30% chance for random noise
    if random.random() < 0.3:
        transformations.append(("noise", None))

    out_img = image.copy()
    # Apply each selected transformation in sequence
    for t_name, param in transformations:
        if t_name == "rot":
            out_img = rotate_image(out_img, param)
        elif t_name == "flip_h":
            out_img = flip_image(out_img, 1)
        elif t_name == "flip_v":
            out_img = flip_image(out_img, 0)
        elif t_name == "bri_con":
            brightness, contrast = param
            out_img = adjust_brightness_contrast(out_img, brightness, contrast)
    return out_img

def main():
    labeled_data_dir = "labeled_data"
    # We have subfolders: 'good', 'bad', 'missing'

    classes = ["good", "bad", "missing"]
    # For each class subfolder, read all images, do augmentation

    # We'll define how many augmented images we want per real patch
    # Example: if we do 2 augmentations per original
    augment_per_patch = 7

    for cls in classes:
        class_folder = os.path.join(labeled_data_dir, cls)
        if not os.path.exists(class_folder):
            continue

        patch_files = [f for f in os.listdir(class_folder)
                       if f.lower().endswith((".png", ".jpg"))]

        for patch_file in patch_files:
            patch_path = os.path.join(class_folder, patch_file)
            img = cv2.imread(patch_path)
            if img is None:
                print(f"Could not read {patch_path}")
                continue

            # Create some augmented versions
            for i in range(augment_per_patch):
                aug_img = augment_image(img)
                base_name, ext = os.path.splitext(patch_file)
                aug_filename = f"{base_name}_aug{i}{ext}"
                aug_path = os.path.join(class_folder, aug_filename)
                cv2.imwrite(aug_path, aug_img)
                print(f"Saved augmented patch -> {aug_path}")

    print("Augmentation completed for all classes!")

if __name__ == "__main__":
    main()
