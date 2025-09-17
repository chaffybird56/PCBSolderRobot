# Autonomous PCB Soldering Robot

## 🤖 Overview

A CoreXY robot that **solders through-hole joints** end-to-end and performs **QA/QC** with a Raspberry Pi vision stack and a **MobileNetV2** classifier (Good / Bad / Missing). Built as a capstone project; **awarded 1st place**.

<!-- Paste your soldering video attachment URL on its own line below, then keep the <video> tag. -->
<!-- Example of the URL shape: h

https://github.com/user-attachments/assets/3e60dc63-2b64-4922-9cd8-233fcee57446

ttps://github.com/user-attachments/assets/xxxxxxxxxxxxxxxx -->
<video src="(https://github.com/user-attachments/assets/3e60dc63-2b64-4922-9cd8-233fcee57446)"
       width="700" autoplay loop muted playsinline></video>

---

## ✨ Highlights

- **Electromechanical soldering:** CoreXY XY + Z toolhead + motorized solder feed for precise wire advance.
- **Vision + ML QA/QC:** Pi 4 + Pi HQ Camera + 100× microscope lens; MobileNetV2 (TFLite) classifies each joint in ~30 ms.
- **Operator dashboard:** Tkinter GUI overlays labels/confidences, logs CSVs; designed to close the loop to firmware for **auto re-solder**.

<!-- Moved modules overview up for quick context -->
<p align="center">
  <img src="assets/fig01_modules.png" width="720" alt="Module overview">
</p>

---

## 🏭 System Architecture

**Mechanical (CoreXY + Z + feed).**  
Rigid V-slot frame; **12 mm Y-rods** (stiffness), **8 mm X-rods** (low moving mass), GT2 belts. The toolhead integrates a temperature-controlled iron + geared solder-wire feed. An adjustable tray fixtures different PCB sizes consistently.

<table>
  <tr>
    <td align="center">
      <img src="assets/fig02_toolhead_cad.png" width="420" alt="Toolhead CAD"><br><em>Toolhead CAD</em>
    </td>
    <td align="center">
      <img src="assets/fig03_corexy_cad.png" width="420" alt="CoreXY CAD"><br><em>CoreXY CAD</em>
    </td>
  </tr>
</table>

**Additional fixtures**
<p align="center">
  <img src="assets/fig05_enclosure.png" width="640" alt="Electronics enclosure"><br>
  <img src="assets/fig06_tray.png" width="640" alt="Adjustable PCB tray">
</p>

**Electronics (motion, power, solder feed).**  
Custom board: **Raspberry Pi Pico** + **TMC2209** drivers. 24 V rail with 5 V buck. **UART** exposes current, microstepping and diagnostics for smooth, consistent motion and gentle feed control.

<p align="center">
  <img src="assets/fig08_electronics_pcb.png" width="720" alt="Motion / regulation / feed PCB">
</p>

**Firmware (C++ / PlatformIO).**  
CoreXY kinematics, limit handling, and a **dynamic-derivative** control strategy for smooth starts/stops. We migrated from “variable step” to **variable motor speed** for stability. UART utilities enable driver telemetry and (next rev) closed-loop re-solder from the Pi.

<!-- Axis motion demo in this section -->
<video src="(https://github.com/user-attachments/assets/a4e11ffc-5575-4b82-93a4-2864e2e326f1)"
       width="700" autoplay loop muted playsinline></video>


---

## 🔬 Vision & ML

**Acquisition & pre-processing.**  
8 MP frames → histogram equalization → **BGR→HSV** → **Otsu** on Hue (to isolate solder) + **V-channel gating** (suppress dim pixels) → median filter → segmentation → **224×224** crops per joint.

<p align="center">
  <img src="assets/fig09_preprocess.png" width="720" alt="Pre-processing steps">
</p>

**Classifier (3-class MobileNetV2).**  
TensorFlow Lite **MobileNetV2** (α = 0.75) outputs **Good / Bad / Missing**. Splitting **Missing** from **Bad** clarifies actions: **add solder** (Missing) vs **wick/reflow** (Bad/bridged). The compact model keeps latency low on Pi.

<p align="center">
  <img src="assets/fig10_inference.png" width="720" alt="Detection + classification"><br>
  <img src="assets/fig11_curves.png" width="600" alt="Training curves"><br>
  <img src="assets/fig12_confusion.png" width="600" alt="Confusion matrix">
</p>

**Operator dashboard.**  
**Tkinter** GUI renders live boxes, per-joint class/confidence, FPS, and logs every decision to CSV. Inputs: **camera / image / video**. Designed to publish UART messages to the Pico for **auto re-solder**.

<!-- Vision setup demo here -->
<video src="(https://github.com/user-attachments/assets/8a706253-764e-4d3b-9e51-ec0bf89ef5b5)"
       width="700" autoplay loop muted playsinline></video>

**Performance.**  
~**30 ms/joint** on Pi 4 with the pre-processing + TFLite pipeline enables practical operator-in-the-loop QA.

<p align="center">
  <img src="assets/fig13_multi_boards.png" width="720" alt="Multiple boards assessed">
</p>

---

## ✅ Results
- Repeatable imaging at ~10″ working distance; uniform LED fill reduces glare.  
- Consistent segmentation with accurate 3-class decisions and clear overlays/logs.  
- Full motion + solder-feed proof-of-concept with UART telemetry for safety and tuning.

## ⏳ Next
- **Unify** capture + inference (Picamera2 end-to-end).  
- **Close the loop:** UART-triggered re-solder routines.  
- **Accelerate** on Jetson/Coral; **expand** dataset with more boards/edge-cases.

---

## 🤝 Team
Arji Thaiyib, Arjun Bhatia, **Ahmad Choudhry**, Abdullah Hafeez, Mayar Aljayoush  
Supervisors: Dr. S. Shirani, Dr. C. Chen

## License
Released under the **MIT License** — see [LICENSE](LICENSE).
