#!/usr/bin/env python3
# =============================================================================
# Cinefilm Digitizer – Frame Capture Module
#
# Description:
#   Controls stepper motor motion and captures individual film frames based on
#   sprocket detection via a photointerrupter. Images are captured using the
#   'rpicam-jpeg' utility with precise shutter, gain, and ROI control.
#
# Hardware:
#   - Raspberry Pi 4B
#   - IMX219 camera module
#   - TMC2209 + NEMA17 stepper motor
#   - IR LED + phototransistor (sprocket detection)
#
# Author: Sean Burrage (Inverness, Scotland)
# Started: 2025
# Grey hairs acquired: 2000+
# License: MIT
# =============================================================================

# SPDX-FileCopyrightText: 2025 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT

import threading
import time
import board
import RPi.GPIO as GPIO
from digitalio import DigitalInOut, Direction
import subprocess
from pathlib import Path

# ========== CONFIGURATION ==========
SENSOR_PIN = 17  # GPIO input for photo interrupter
STEP_PIN = board.D6
DIR_PIN = board.D5
OUTPUT_DIR = Path("/media/user/FOOTAGE/footageBatch01")
ROI = "0.34,0.38,0.4,0.4" # You will need to find a ROI that suits your needs
SHUTTER = "5000" # in microseconds (1 / 1,000,000 of a second), so 5000 is equivalent to 1/200 
GAIN = "1" # it's equivalent to ISO x 100. Increase to 2 or 3 if you need brighter exposures without slowing your shutter
AWBGAINS = "1.2,2.0"
STEP_DELAY = 0.06  # in seconds - 0.06 give a nice slow run with sharper images allwing for slower shutter. 0.03 will be much faster, though blurring may occur if your light source is not strong enough
#DRCLEVEL = "medium"
#QLEV = 95
CTIMEOUT = "1"
MIN_INTERVAL = 0.2  # minimum seconds between captures, to avoid some false triggers
MAX_SENSOR_TIMEOUT = 30  # seconds without detection before aborting, for example, if it reaches the end of the reel.
# ===================================

# Custom exception
class SensorTimeoutError(Exception):
    pass

# Ensure output folder exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

# LED output (on GPIO 27)
LED_PIN = 26
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)  # start off

# Setup motor pins
DIR = DigitalInOut(DIR_PIN)
DIR.direction = Direction.OUTPUT
DIR.value = True  # Set motor direction

STEP = DigitalInOut(STEP_PIN)
STEP.direction = Direction.OUTPUT

# Stepper motor background loop
def stepper_loop(delay):
    while True:
        STEP.value = True
        time.sleep(delay)
        STEP.value = False
        time.sleep(delay)

threading.Thread(target=stepper_loop, args=(STEP_DELAY,), daemon=True).start()

frame_counter = 0
beam_last = GPIO.input(SENSOR_PIN)
last_capture_time = time.time()

# Main photo capture loop
try:
    print("Starting capture loop...")
    while True:
        state = GPIO.input(SENSOR_PIN)
        now = time.time()

        # Falling edge detection and cooldown window
        if beam_last == GPIO.HIGH and state == GPIO.LOW:
            if now - last_capture_time > MIN_INTERVAL:
                GPIO.output(LED_PIN, GPIO.HIGH)
                filename = OUTPUT_DIR / f"frame_{frame_counter:05d}.jpg"
                print(f"Capturing {filename}...")

                result = subprocess.run([
                    "rpicam-jpeg",
                    "--output", str(filename),
                    "--roi", ROI,
                    "--shutter", SHUTTER,
                    "--gain", GAIN,
                    "--awbgains", AWBGAINS,
                    "--immediate",
                    "--timeout", CTIMEOUT
                ])

                if result.returncode != 0:
                    print(f"⚠️ Warning: Capture failed at frame {frame_counter}")

                frame_counter += 1
                last_capture_time = now
                GPIO.output(LED_PIN, GPIO.LOW)

        # Timeout check
        if now - last_capture_time > MAX_SENSOR_TIMEOUT:
            raise SensorTimeoutError(f"No sensor detection in {MAX_SENSOR_TIMEOUT} seconds. Aborting...")

        beam_last = state
        time.sleep(0.005)

except KeyboardInterrupt:
    print("Exiting gracefully (keyboard interrupt).")

except SensorTimeoutError as e:
    print(f"❌ {e}")

finally:
    GPIO.cleanup()
