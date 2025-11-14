🎞️ Raspberry Pi Cinefilm Reel Scanner
High-resolution frame-by-frame digitisation of 9.5mm / 8mm film reels using a Raspberry Pi

This project is a DIY cinefilm digitisation system built using a Raspberry Pi, a stepper-driven transport mechanism, and a sprocket-hole photointerrupter for precise capture timing.
It captures every frame using rpicam-jpeg (Camera Module V2 – Sony IMX219) and saves the images for later alignment and stabilization via OpenCV (see film-frame-aligner).

Designed to offer reliable, repeatable, and fully automated film scanning using inexpensive hardware.

🚀 Features

🎥 Automated frame advance using TMC2209 + NEMA17

🔦 IR photointerrupter detection for sprocket holes

🧠 Debounced, edge-triggered capture logic

📸 Pi Camera V2 (IMX219) still capture via rpicam-jpeg

🧾 Adjustable:

ROI (capture crop)

Shutter (µs)

Gain (ISO equivalent)

AWB gains

Stepper speed

📂 Saves frames directly to:

USB flash drive

External NAS

SD card

🟢 Optional GPIO LED indicator for capture feedback

🛡 Sensor timeout protection (stops if film stops moving)

⚠️ Important Note on Old Film & IR Sensitivity

Many vintage film stocks are extremely IR-transmissive, especially older Pathé 9.5mm film.
This means:

Sprocket holes may not block IR light effectively

Film variances (age, exposure, degradation) cause inconsistent transparency

Photointerrupter must be finely tuned with:

Correct IR LED brightness

Correct phototransistor sensitivity

Careful mechanical alignment

Shielding from ambient light

Expect to adjust the potentiometer frequently between reels.
If detection becomes unstable:

Increase/decrease IR LED brightness (resistor change)

Re-adjust sensitivity

Re-align film height through the interrupter

🛠 Hardware Required
Component	Purpose
Raspberry Pi 4B (or Pi 3/5)	Main controller
Raspberry Pi Camera V2 (Sony IMX219)	3280×2464 still capture
TMC2209 Stepper Driver	Smooth microstepping
NEMA17 Stepper Motor	Film transport
IR LED + Resistor (e.g. 330 Ω)	Light source for sprocket detection
Phototransistor / Photo-interrupter	Detects sprocket holes
Potentiometer (0–10 kΩ)	Adjusts IR receiver sensitivity
GPIO indicator LED Shows when frames are captured
USB flash drive or NAS Storage for image files

Optional:

Ferrite rings for noise suppression

Light baffling around IR sensor

3D-printed film guides

🔌 Wiring Overview
IR LED:
 Pi 3.3V ──[330Ω]──► IR LED ►── GND

Phototransistor:
 Collector ───► GPIO17
 Emitter   ───► GND
 (Potentiometer inline for sensitivity)

Stepper:
 GPIO5  ──► TMC2209 DIR
 GPIO6  ──► TMC2209 STEP
 GND    ──► COMMON GND

Indicator LED:
 GPIO26 ──► LED (with 330Ω resistor) ─► GND

📸 Capture Script

This repository includes:

PiCineFilmReelScanner.py

A full end-to-end real-time film scan script featuring:

Stepper motor control loop

Sprocket hole detection

Debounced capture logic

IR tuning

Frame naming and auto-numbering

Timeout protections

LED capture indicator

Fully adjustable exposure, gain, white balance

This file is ready to run on a Raspberry Pi as-is.

🧠 Shutter Explanation

The shutter parameter in rpicam-jpeg:

--shutter <value>


is in microseconds (µs).

Examples:

Value	Exposure
5000 µs	0.005 s (5 ms)
20000 µs	0.02 s
100000 µs	0.1 s

So your:

SHUTTER = "5000"


means 5000 microseconds, not milliseconds or nanoseconds. This would be equivalent to 1/200 conventional shutter speed.

▶️ Running the Script
1. Install rpicam apps (if needed)
sudo apt install rpicam-apps

2. Create mount point for storage
sudo mkdir -p /media/user/FOOTAGE
sudo mount -o uid=1000,gid=1000 /dev/sda1 /media/user/FOOTAGE

3. Launch inside tmux (recommended)
tmux
python3 PiCineFilmReelScanner.py


Detach safely:

Ctrl + B, then D


Reattach later:

tmux attach

🎯 Output

Captured frames are saved as:

/media/user/FOOTAGE/footageBatch01/frame_00000.jpg
...


These are then aligned later using an OpenCV script (not included in this repo, but part of your workflow).

🛠 Troubleshooting
Issue	Cause	Fix
Missed sprocket detections:	Film too transparent	Reduce LED brightness, adjust potentiometer, improve alignment
False triggers:	Ambient IR contamination	Add shielding, reduce LED current
Blurry frames:	Shutter too long, film still moving	Increase light intensity; or reduce SHUTTER value
Permission errors saving frames:	USB mounted as root	Use uid=1000,gid=1000 mount option
Script stops mid-reel:	No sprocket detection for N seconds	Adjust MAX_SENSOR_TIMEOUT


📦 Future Improvements

Dual-sensor error-checking

Machine learning sprocket detection

Optional camera preview on Windows using ffplay

RGB histogram-based auto-exposure

Automatic exposure ramping per-reel

🧑‍💻 Author

Sean Burrage — Inverness, Scotland
Film scanning, mechanics, electronics, image processing
from 2016 → current day

🪪 License

MIT License
Feel free to modify, fork, share, or build upon this project.
