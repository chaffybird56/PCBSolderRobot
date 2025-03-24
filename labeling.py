#!/usr/bin/env python3
import cv2
import os

# Now we have 3 categories:
LABELS = {
    "g": "good",
    "b": "bad",
    "m": "missing"
}

def label_patches(unlabeled_dir, labeled_dir="labeled_data"):
    """
    Shows each patch. Press:
       'g' -> good
       'b' -> bad
       'm' -> missing
    The patch is moved to labeled_data/good, labeled_data/bad, or labeled_data/missing.
    """
    if not os.path.exists(labeled_dir):
        os.makedirs(labeled_dir)

    # Make sure each label subfolder exists
    for label_name in LABELS.values():
        label_folder = os.path.join(labeled_dir, label_name)
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)

    patch_files = [f for f in os.listdir(unlabeled_dir)
                   if f.lower().endswith((".png", ".jpg"))]
    patch_files.sort()

    print("Labeling Instructions:")
    for key, lbl in LABELS.items():
        print(f"Press '{key}' for {lbl}")

    for patch_file in patch_files:
        patch_path = os.path.join(unlabeled_dir, patch_file)
        img = cv2.imread(patch_path)
        if img is None:
            print(f"Skipping {patch_file}, cannot read image.")
            continue

        cv2.imshow("Label Patch", img)
        key = cv2.waitKey(0) & 0xFF  # wait for a key

        key_char = chr(key)
        if key_char in LABELS:
            label_str = LABELS[key_char]
            # Move the patch to the correct folder
            out_subdir = os.path.join(labeled_dir, label_str)
            out_path = os.path.join(out_subdir, patch_file)
            os.rename(patch_path, out_path)
            print(f"{patch_file} labeled as '{label_str}' -> {out_path}")
        else:
            print(f"Invalid key pressed ({key_char}), skipping or re-showing.")
            # We could either break here, or continue to next patch

    cv2.destroyAllWindows()

def main():
    # We labeled the patches in 'unlabeled_patches'
    label_patches("unlabeled_patches", labeled_dir="labeled_data")

if __name__ == "__main__":
    main()
