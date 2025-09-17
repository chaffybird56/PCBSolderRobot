# Autonomous PCB Soldering Robot

## 🤖 Overview
A CNC precision 3-axis automated PCB soldering system with vision processing and AI solder recognition for in-app QA/QC. Built as a capstone project; **awarded 1st place**.

<!-- Soldering action (GitHub attachment player). Keep the URL on its own line. -->
https://github.com/user-attachments/assets/3e60dc63-2b64-4922-9cd8-233fcee57446

---

## ✨ Highlights
- **Mechanical:** Belt-driven **Core XY** stage with **leadscrew Z-axis** and a **stepper-gun solder dispenser** for precise wire feed and tip placement.
- **Electronics:** Custom **Altium** PCB integrating **TMC2209** motor drivers, endstops/limit sensors, and a **5 V buck** for regulated logic rails.
- **Firmware:** C++/PlatformIO with **UART** telemetry for current limiting, microstepping and diagnostics; motion planner with **dynamic error handling** and soft-limits.
- **Vision:** **Raspberry Pi** + HQ camera under controlled **LED ring** lighting; manual **bounding-box labeling** of solder joints and dataset augmentation for robustness.
- **Machine Learning:** Morphological pre-processing + **MobileNetV2** (TFLite) for real-time **Good / Bad / Missing** joint classification.
- **App:** Tkinter GUI with live video/image inputs, overlays, per-joint confidences, and CSV logging for on-the-fly assessment and future **auto re-solder**.

<!-- High-level modules overview for fast context -->
<p align="center"><img src="assets/fig01_modules.png" width="680" alt="System modules overview"></p>

---

## 🏭 System Architecture

### Mechanical (CoreXY + Z + feeder)
Rigid V-slot frame; **12 mm Y-rods** for stiffness, **8 mm X-rods** to reduce moving mass, **GT2 belts** on XY; Z by leadscrew. Toolhead integrates a temperature-controlled iron with a **geared solder-wire feeder**. A kitted tray fixtures boards repeatably.

<table>
  <tr>
    <td align="center" valign="top" width="50%">
      <img src="assets/fig02_toolhead_cad.png" width="380" alt="Toolhead CAD"><br>
      <sub><b>Toolhead CAD.</b> Iron + geared feed align wire right at the pad; compact, low-mass carriage.</sub>
    </td>
    <td align="center" valign="top" width="50%">
      <img src="assets/fig03_corexy_cad.png" width="380" alt="CoreXY CAD"><br>
      <sub><b>CoreXY CAD.</b> Belt routing with idlers for symmetric tension; X-rail rides on 8 mm rods.</sub>
    </td>
  </tr>
</table>

### Additional fixtures
<table>
  <tr>
    <td align="center" valign="top" width="50%">
      <img src="assets/fig05_enclosure.png" width="360" alt="Electronics enclosure"><br>
      <sub><b>Electronics enclosure.</b> Houses PSU, control PCB, and thermal/EMI shielding for stable operation.</sub>
    </td>
    <td align="center" valign="top" width="50%">
      <img src="assets/fig06_tray.png" width="360" alt="Adjustable PCB tray"><br>
      <sub><b>Adjustable PCB tray.</b> Locates boards against hard stops; repeatable datum for imaging and soldering.</sub>
    </td>
  </tr>
</table>


### Electronics (motion, power, solder feed)
Custom controller: **Raspberry Pi Pico + TMC2209** drivers on a single board; **24 V** motion rail with **5 V** buck for logic. UART access to driver current, microstepping, and diagnostics enables safe current limits and smooth feeds.

<p align="center"><img src="assets/fig08_electronics_pcb.png" width="640" alt="Motion/regulation/feeder PCB"></p>

### Firmware (C++ / PlatformIO)
- CoreXY kinematics and soft/hard limit handling  
- **Variable motor speed** (vs. variable steps) for stable ramps  
- **UART** utilities for telemetry & tuning (foundation for future **auto re-solder**)

<!-- Axis motion demo in the architecture section -->
https://github.com/user-attachments/assets/a4e11ffc-5575-4b82-93a4-2864e2e326f1

---

## 🔬 Vision & ML

<!-- Move vision demo higher in this section -->
https://github.com/user-attachments/assets/8a706253-764e-4d3b-9e51-ec0bf89ef5b5

### Acquisition & pre-processing
Lighting-controlled captures (Pi HQ + microscope lens + LED ring) → histogram equalization → **BGR→HSV** → **Otsu** threshold on Hue to isolate solder → **V-channel gating** to drop dim pixels → median filter → morphological cleanup → per-joint crops at **224×224**.

<table>
  <tr>
    <td align="center" width="50%">
      <img src="assets/fig09_preprocess.png" width="360" alt="Pre-processing steps"><br>
      <sub><b>Fig 09.</b> Pre-processing pipeline stabilizes appearance across glare/finish.</sub>
    </td>
    <td align="center" width="50%">
      <img src="assets/fig10_inference.png" width="360" alt="Detection + classification overlay"><br>
      <sub><b>Fig 10.</b> Detection + classification overlays with per-joint labels and confidences.</sub>
    </td>
  </tr>
</table>


### Labeling & dataset
- **Manual labeling** in LabelImg with rectangular boxes around each solder joint; class set: **Good**, **Bad** (e.g., bridges/voids/insufficient wetting), **Missing** (pad present, solder absent).  
- **Augmentation:** rotations, flips, Gaussian noise, slight blur, exposure jitter, and random spatter/dropout (~×7 expansion) to generalize across pad geometry and lighting.  
- **Splits:** balanced train/val/test with class weights to mitigate skew; crops normalized before inference.

### Classifier & training
- **MobileNetV2 (α = 0.75)** in TFLite for low-latency inference on Pi; trained on augmented crops.  
- Loss: categorical cross-entropy with early stopping; metrics tracked per-class to ensure **Missing** stays separable from **Bad**.

<table>
  <tr>
    <td align="center" width="50%">
      <img src="assets/fig11_curves.png" width="420" alt="Training curves"><br>
      <sub><b>Fig 11.</b> Loss/accuracy vs. epochs (early stopping around convergence).</sub>
    </td>
    <td align="center" width="50%">
      <img src="assets/fig12_confusion.png" width="420" alt="Confusion matrix"><br>
      <sub><b>Fig 12.</b> Confusion matrix; clear separation for <i>Missing</i> vs <i>Bad</i>.</sub>
    </td>
  </tr>
</table>


### Operator app
Tkinter GUI accepts **camera / image / video** inputs, renders detections with class/confidence, shows FPS, and writes **CSV logs**. Interface is structured to publish UART messages to the Pico for **closed-loop re-solder** in the next revision.

<p align="center">
  <img src="assets/fig13_multi_boards.png" width="680" alt="Batch assessment across multiple boards">
  <br>
  <sub><b>Fig 13.</b> Batch assessment: per-joint labels and confidences across multiple boards; results logged to CSV for QA review and future closed-loop re-solder.</sub>
</p>


---

## ✅ Results
- Repeatable imaging at ~10″ working distance with low-glare LED fill
- Robust segmentation + accurate **3-class** decisions; clear overlays & logs
- Full motion + solder-feed PoC with UART telemetry for safety and tuning

## ⏳ Next
- Unify capture + inference on Picamera2 end-to-end  
- Close the loop: UART-triggered re-solder routines  
- Accelerate on Jetson/Coral; expand dataset with more boards/edge-cases

---

## 🤝 Team
Arji Thaiyib, Arjun Bhatia, **Ahmad Choudhry**, Abdullah Hafeez, Mayar Aljayoush  
Supervisors: Dr. S. Shirani, Dr. C. Chen

## License
Released under the **MIT License** — see [LICENSE](LICENSE).
