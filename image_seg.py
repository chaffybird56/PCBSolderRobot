import cv2
import numpy as np
import os

def select_joint_method_fixed(
    image_path,
    do_hist_eq=False,
    otsu_invert=True,       # If True, do THRESH_BINARY_INV+OTSU on Hue instead of THRESH_BINARY+OTSU
    value_low_thresh=80,    # Low-threshold gating on the Value channel
    median_ksize=3,
    # Additional morph to fix holes or remove specks
    morph_open_ksize=4,
    morph_close_ksize=5,
    # bounding box filters
    min_box_size=15,
    max_box_size=500,
    # NEW: optional dilation settings
    morph_dilate_ksize=9,
    morph_dilate_iterations=2
):
    """
    Revised 'Select Joint' pipeline:
      1) Histogram Equalization (optional)
      2) BGR->HSV
      3) Hue -> Otsu threshold (with optional invert)
      4) Value -> Low threshold gating
      5) Merge masks (bitwise AND)
      6) Morphological opening/closing
      7) Median filter
      8)  morphological dilation to enlarge detected regions
      9) Find contours, filter out outliers
      10) Return bounding boxes

    Saves intermediate images for debug.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Could not find image at: {image_path}")

    # 1) Load image
    bgr_img = cv2.imread(image_path)
    if bgr_img is None:
        raise ValueError("Could not read image file. Check format.")

    # Optional histogram eq
    if do_hist_eq:
        yuv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2YUV)
        yuv[..., 0] = cv2.equalizeHist(yuv[..., 0])
        bgr_eq = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    else:
        bgr_eq = bgr_img.copy()

    # 2) Convert to HSV
    hsv = cv2.cvtColor(bgr_eq, cv2.COLOR_BGR2HSV)
    h_channel = hsv[..., 0]  # hue
    v_channel = hsv[..., 2]  # value

    # 3) Hue -> Otsu threshold
    otsu_flag = cv2.THRESH_BINARY_INV if otsu_invert else cv2.THRESH_BINARY
    _, mask_hue = cv2.threshold(
        h_channel, 0, 255,
        otsu_flag + cv2.THRESH_OTSU
    )
    cv2.imwrite("otsu_hue.png", mask_hue)

    # 4) Value -> low threshold gating
    _, mask_value = cv2.threshold(
        v_channel, value_low_thresh, 255,
        cv2.THRESH_BINARY
    )
    cv2.imwrite("low_thresh_value.png", mask_value)

    # 5) Merge masks with AND
    merged_mask = cv2.bitwise_and(mask_hue, mask_value)
    cv2.imwrite("mask_merged.png", merged_mask)

    # 6) Additional morphological opening/closing
    if morph_close_ksize > 0:
        close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_close_ksize, morph_close_ksize))
        merged_mask = cv2.morphologyEx(merged_mask, cv2.MORPH_CLOSE, close_kernel, iterations=1)

    if morph_open_ksize > 0:
        open_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_open_ksize, morph_open_ksize))
        merged_mask = cv2.morphologyEx(merged_mask, cv2.MORPH_OPEN, open_kernel, iterations=1)

    # 7) Median filter (size=3 from the paper)
    filtered_mask = cv2.medianBlur(merged_mask, median_ksize)
    cv2.imwrite("mask_filtered.png", filtered_mask)

    # 8) NEW: Optional morphological dilation to enlarge the detected regions
    # Increasing ksize or iterations will make bounding boxes bigger
    if morph_dilate_ksize > 0 and morph_dilate_iterations > 0:
        dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_dilate_ksize, morph_dilate_ksize))
        dilated_mask = cv2.dilate(filtered_mask, dilate_kernel, iterations=morph_dilate_iterations)
        cv2.imwrite("mask_dilated.png", dilated_mask)
    else:
        dilated_mask = filtered_mask

    # 9) Contour detection
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bounding_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Filter out small or large boxes
        if w < min_box_size or h < min_box_size:
            continue
        if w > max_box_size or h > max_box_size:
            continue

        bounding_boxes.append((x, y, w, h))

    return bgr_eq, bounding_boxes

def main():
    image_path = "test2.png"
    bgr_img, boxes = select_joint_method_fixed(
        image_path,
        do_hist_eq=False,
        otsu_invert=True,
        value_low_thresh=80,
        median_ksize=3,
        morph_open_ksize=4,
        morph_close_ksize=5,
        min_box_size=15,
        max_box_size=500,
        # Try increasing these if you want even larger boxes
        morph_dilate_ksize=9,
        morph_dilate_iterations=2
    )

    print(f"Found {len(boxes)} bounding boxes after final step.")

    # Draw detected bounding boxes for visual check
    output_img = bgr_img.copy()
    for (x, y, w, h) in boxes:
        cv2.rectangle(output_img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imwrite("final_bboxes.png", output_img)
    print("Saved 'final_bboxes.png' bounding box overlay.")

if __name__ == "__main__":
    main()