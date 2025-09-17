# Autonomous PCB Soldering Robot

> A CoreXY robot that **soldiers through-hole joints** end-to-end and performs **QA/QC** with a Raspberry Pi vision stack and a **MobileNetV2** classifier (Good / Bad / Missing). Built as a capstone project; awarded 1st place.

<p align="center">
  <img src="assets/gifs/soldering_action.gif" width="85%" alt="Soldering in action"/>
</p>

---

## TL;DR

- **Electromechanical soldering**: CoreXY XY gantry + Z toolhead + motorized solder-wire feed for precise through-hole joints.
- **Vision + ML QA/QC**: Pi 4 + Pi HQ Camera + 100× microscope lens; MobileNetV2 (TFLite) classifies each joint in **~30 ms**.
- **Operator dashboard**: Tkinter GUI overlays labels & confidences, logs to CSV; structured to close the loop to firmware for **auto re-solder** in the next revision.

**Why it matters (quick context):** low-volume teams (labs, aerospace/medical proto lines, startups) still spend real time on **manual TH solder + inspection**. This system integrates **mechanics, motion control, vision, and ML** so one platform can (1) place consistent joints and (2) flag **Bad**/**Missing** cases immediately, speeding touch-ups and improving repeatability without a large SMT line.

---

## System architecture

**Mechanical (CoreXY + Z + feed).**  
A rigid V-slot frame with 12 mm Y-rods (stiffness), 8 mm X-rods (low moving mass), and GT2 belts. The toolhead combines a temperature-controlled iron and a geared solder-feed so wire advances precisely into the joint. A rail-adjustable tray fixtures PCBs of varying sizes.

<p align="center">
  <img src="assets/fig02_toolhead_cad.png" width="49%" alt="Toolhead CAD"/>
  <img src="assets/fig03_corexy_cad.png" width="49%" alt="CoreXY CAD"/>
</p>

**Demo (axis motion detail).**  
A short motion clip illustrating kinematics and stepper behavior (captured pre-final assembly):
<p align="center">
  <img src="assets/gifs/axis_motion.gif" width="70%" alt="CNC axis motion demo"/>
</p>

**Electronics (motion, power, solder feed).**  
Custom control board with **Raspberry Pi Pico** + **TMC2209** drivers. 24 V rail (with 5 V buck) powers XY/Z and the solder-feed. **UART** exposes driver current, microstepping, and diagnostics for consistent motion and gentle, repeatable feed.

![Electronics enclosure](assets/fig05_enclosure.png)
![Motion / regulation / solder-feed PCB](assets/fig08_electronics_pcb.png)

**Firmware (C++ / PlatformIO).**  
CoreXY kinematics, limit handling, and a **dynamic-derivative control** scheme for smooth starts/stops. We migrated from “variable step” to **variable motor speed** for stability and cleaner trajectories. UART utilities enable (a) driver telemetry and (b) future **auto re-solder** triggers from the Pi.

**Vision hardware (Pi coprocessor).**  
**Pi 4 + Pi HQ Camera + 100× microscope lens**, fixed working distance, and **LED ring fill lighting** for uniform, glare-reduced captures. Data collection used a legacy stack for camera drivers; the final inference GUI runs on newer Pi OS with Picamera2.

![Module overview](assets/fig01_modules.png)

---

## Vision & ML

**Acquisition & pre-processing.**  
8 MP frames → histogram equalization → **BGR→HSV** → **Otsu** on Hue to isolate solder + **V-channel gating** to suppress dim pixels → median filter → segmentation → **224×224** crops per joint. These steps stabilize input across lighting and finish variations.

![Pre-processing steps](assets/fig09_preprocess.png)

**Classifier (3-class MobileNetV2).**  
TensorFlow-Lite **MobileNetV2** (α = 0.75) classifies each crop as **Good / Bad / Missing**. Explicitly separating **Missing** makes operator actions obvious: add solder (Missing) vs. wick/reflow (Bad/bridged). The compact model keeps latency low on a Pi while maintaining practical accuracy.

![Detection + classification](assets/fig10_inference.png)
![Training curves](assets/fig11_curves.png)
![Confusion matrix](assets/fig12_confusion.png)

**Dataset & augmentation.**  
Images from IEEE trainee boards + in-house captures under the LED rig; bounding boxes labeled in LabelImg. Augmentations—rotations, flips, Gaussian noise, spatter/dropout (≈7× expansion)—improve generalization across joint angle, pad geometry, reflectivity, and minor lighting drift.

**Operator dashboard.**  
A **Tkinter** GUI renders live boxes, per-joint class/confidence, FPS, and logs to CSV. Inputs include **camera / image / video**. The UI design anticipates UART messages back to the Pico for **closed-loop re-solder** (future).

<p align="center">
  <img src="assets/gifs/vision_setup.gif" width="80%" alt="Vision setup: camera, lens, lighting, GUI"/>
</p>

**Performance.**  
With the pre-processing pipeline and the TFLite model, **~30 ms/joint** inference on Pi 4 enables efficient operator-in-the-loop QA on multi-board batches.

![Multiple boards assessed](assets/fig13_multi_boards.png)

---

## Results (v1)

- Repeatable imaging at a ~10″ working distance with uniform LED fill lighting.  
- Consistent segmentation and accurate 3-class decisions with clear overlays/logs.  
- Full motion + solder-feed proof-of-concept; UART telemetry for safety/tuning and future autonomy.

---

## Limitations & next steps

- **Unify** capture + inference on one OS stack (Picamera2 end-to-end).  
- **Close the loop**: issue UART commands for automatic re-solder on **Bad/Missing** detections.  
- **Accelerate** inference (Jetson/Coral) and **expand** the dataset with more boards & edge cases.

---

## Team & acknowledgments

Arji Thaiyib, Arjun Bhatia, **Ahmad Choudhry**, Abdullah Hafeez, Mayar Aljayoush  
Supervisors: Dr. S. Shirani, Dr. C. Chen

---

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.
