"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Course Project
Driver Drowsiness Alert System - Main Application Entry Point
================================================================================
Orchestrates:
1. Video capture via OpenCV
2. Real-time 3D facial landmark regression via MediaPipe (vision/landmark_tracker)
3. Vectorized Euclidean distance telemetry (vision/telemetry)
4. Mamdani Fuzzy Inference System & Centroid Defuzzification (fis/controller)
5. Advanced Driver Assistance (ADAS) HUD graphics rendering (utils/visualizer)
================================================================================
"""

import sys
import cv2

from config.settings import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)
from fis.controller import DrowsinessFISController
from utils.visualizer import DriverHUDVisualizer
from vision.landmark_tracker import FaceMeshTracker


def main():
    print("=" * 70)
    print("  EEE1004: Driver Drowsiness Alert System (Neuro-Fuzzy Architecture)")
    print("  Initializing Computer Vision Pipeline & Fuzzy Inference Engine...")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # 1. Initialize Subsystem Modules
    # --------------------------------------------------------------------------
    tracker = FaceMeshTracker(max_num_faces=1, refine_landmarks=True)
    fis_controller = DrowsinessFISController()
    hud = DriverHUDVisualizer()

    # --------------------------------------------------------------------------
    # 2. Hardware Video Stream Initialization
    # --------------------------------------------------------------------------
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        # Fallback without CAP_DSHOW if camera backend fails
        cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print(f"[!] Error: Could not access video capture device at index {CAMERA_INDEX}.")
        print("    Please check webcam permissions or update CAMERA_INDEX in config/settings.py.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    window_title = "Driver Drowsiness Alert System - EEE1004 (Neuro-Fuzzy)"
    cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

    print("[✓] Camera initialized successfully.")
    print("[✓] Press 'q' or 'ESC' in the video window to terminate execution.")
    print("-" * 70)

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[!] Warning: Empty video frame received. Reconnecting...")
                break

            # ------------------------------------------------------------------
            # 3. Vision & Landmark Telemetry Extraction (Neural Feature Regressor)
            # ------------------------------------------------------------------
            telemetry, _ = tracker.process_frame(frame)

            # ------------------------------------------------------------------
            # 4. Fuzzy Inference System (Fuzzification, Rules & Defuzzification)
            # ------------------------------------------------------------------
            if telemetry and telemetry.get('face_detected', False):
                ear = telemetry['avg_ear']
                mar = telemetry['mar']
                alert_score, _ = fis_controller.evaluate(ear, mar)
            else:
                # No face detected in frame (e.g. driver looking away)
                alert_score = 30.0

            # ------------------------------------------------------------------
            # 5. Render Real-Time ADAS Heads-Up Display (HUD)
            # ------------------------------------------------------------------
            annotated_frame = hud.draw_hud(frame, telemetry, alert_score)
            cv2.imshow(window_title, annotated_frame)

            # ------------------------------------------------------------------
            # 6. User Keyboard Event Handling
            # ------------------------------------------------------------------
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("\n[!] User termination signal received.")
                break

    except KeyboardInterrupt:
        print("\n[!] Keyboard interrupt detected.")
    finally:
        # ----------------------------------------------------------------------
        # 7. Safe Resource Cleanup & Deallocation
        # ----------------------------------------------------------------------
        print("[✓] Releasing camera and neural network resources...")
        cap.release()
        tracker.release()
        cv2.destroyAllWindows()
        print("[✓] Application terminated cleanly.")


if __name__ == "__main__":
    main()
