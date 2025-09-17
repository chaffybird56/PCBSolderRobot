# Autonomous PCB Soldering Robot

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Robot.png" width="28" height="28" /> Overview

A CoreXY robot that **soldiers through-hole joints** end-to-end and performs **QA/QC** with a Raspberry Pi vision stack and a **MobileNetV2** classifier (Good / Bad / Missing). Built as a capstone project; **awarded 1st place**.

<table>
  <tr>
    <td align="center">
      <img src="assets/gifs/soldering_action.gif" width="430" alt="Soldering in action"><br>
      <em>Soldering a joint</em>
    </td>
    <td align="center">
      <img src="assets/gifs/axis_motion.gif" width="430" alt="CNC axis motion demo"><br>
      <em>CoreXY/Z motion & steppers</em>
    </td>
  </tr>
</table>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Symbols/Sparkles.png" width="24" height="24" /> Highlights

- **Electromechanical soldering:** CoreXY XY + Z toolhead + motorized solder feed for precise wire advance.
- **Vision + ML QA/QC:** Pi 4 + Pi HQ Camera + 100× microscope lens; MobileNetV2 (TFLite) classifies each joint in ~30 ms.
- **Operator dashboard:** Tkinter GUI overlays labels/confidences, logs CSVs; designed to close the loop to firmware for **auto re-solder**.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Travel%20and%20places/Factory.png" width="24" height="24" /> System Architecture

**Mechanical (CoreXY + Z + feed).**  
Rigid V-slot frame; **12 mm Y-rods** (stiffness), **8 mm X-rods** (low moving mass), GT2 belts. Toolhead integrates temperature-controlled iron + geared solder-wire feed. An adjustable tray fixtures different PCB sizes.

<table>
  <tr>
    <td align="center">
      <img src="assets/fig02_toolhead_cad.png" width="430" alt="Toolhead CAD"><br><em>Toolhead CAD</em>
    </td>
    <td align="center">
      <img src="assets/fig03_corexy_cad.png" width="430" alt="CoreXY CAD"><br><em>CoreXY CAD</em>
    </td>
  </tr>
</table>

Additional fixtures:
- **Electronics enclosure** with PSU, regulation and control PCBs  
- **Adjustable PCB tray + tracks** for repeatable placement

<img src="assets/fig05_enclosure.png" width="640" alt="Electronics enclosure">
<img src="assets/fig06_tray.png" width="640" alt="Adjustable PCB tray">
<img src="assets/fig07_tracks.png" width="640" alt="Tray tracks (side view)">

**Electronics (motion, power, solder feed).**  
Custom board: **Raspberry Pi Pico** + **TMC2209** drivers. 24 V rail with 5 V buck. **UART** exposes current, microstepping and diagnostics for smooth, consistent motion and gentle feed control.

<img src="assets/fig08_electronics_pcb.png" width="800" alt="Motion / regulation / feed PCB">

**Firmware (C++ / PlatformIO).**  
CoreXY kinematics, limits, and a **dynamic-derivative** control strategy for smooth starts/stops. We migrated from “variable step” to **variable motor speed** for stability. UART utilities enable driver telemetry and (next rev) closed-loop re-solder from the Pi.

**Vision hardware (Pi coprocessor).**  
**Pi 4 + Pi HQ Camera + 100× lens** at a fixed working distance; **LED ring** fill lighting to reduce glare and stabilize exposure. Data-collection used a legacy camera stack; the final inference GUI runs on newer Pi OS (Picamera2).

<img src="assets/fig01_modules.png" width="800" alt="Module overview">

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Microscope.png" width="24" height="24" /> Vision & ML

**Acquisition & pre-processing.**  
8 MP frames → histogram equalization → **BGR→HSV** → **Otsu** on Hue (to isolate solder) + **V-channel gating** (suppress dim pixels) → median filter → segmentation → **224×224** crops per joint. Robust to lighting and finish variances.

<img src="assets/fig09_preprocess.png" width="800" alt="Pre-processing steps">

**Classifier (3-class MobileNetV2).**  
TensorFlow Lite **MobileNetV2** (α = 0.75) outputs **Good / Bad / Missing**. Splitting Missing from Bad clarifies actions: **add solder** (Missing) vs **wick/reflow** (Bad/bridged). Compact model keeps latency low on Pi.

<img src="assets/fig10_inference.png" width="800" alt="Detection + classification">
<img src="assets/fig11_curves.png" width="640" alt="Training curves">
<img src="assets/fig12_confusion.png" width="640" alt="Confusion matrix">

**Dataset & augmentation.**  
IEEE trainee PCBs + in-house captures under the LED rig; LabelImg annotations. Rotations, flips, Gaussian noise, and spatter/dropout (~7× expansion) to generalize across angles, pad geometry, reflectivity and minor lighting shifts.

**Operator dashboard.**  
**Tkinter** GUI renders live boxes, per-joint class/confidence, FPS, and logs every decision to CSV. Inputs: **camera / image / video**. Designed to publish UART messages to the Pico for **auto re-solder**.

<p align="center">
  <img src="assets/gifs/vision_setup.gif" width="700" alt="Vision setup: camera, lens, lighting, GUI">
</p>

**Performance.**  
~**30 ms/joint** on Pi 4 with the pre-processing + TFLite pipeline enables practical operator-in-the-loop QA.

<img src="assets/fig13_multi_boards.png" width="800" alt="Multiple boards assessed">

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Symbols/Check%20Mark%20Button.png" width="22" height="22" /> Results
- Repeatable imaging at ~10″ working distance; uniform LED fill reduces glare.  
- Consistent segmentation with accurate 3-class decisions and clear overlays/logs.  
- Full motion + solder-feed proof-of-concept with UART telemetry for safety and tuning.

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Time/Hourglass%20Done.png" width="22" height="22" /> Next
- **Unify** capture + inference (Picamera2 end-to-end).  
- **Close the loop:** UART-triggered re-solder routines.  
- **Accelerate** on Jetson/Coral; **expand** dataset with more boards/edge-cases.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/People/Handshake.png" width="24" height="24" /> Team
Arji Thaiyib, Arjun Bhatia, **Ahmad Choudhry**, Abdullah Hafeez, Mayar Aljayoush  
Supervisors: Dr. S. Shirani, Dr. C. Chen

## License
Released under the **MIT License** — see [LICENSE](LICENSE).
