"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Cockpit HUD Renderer
================================================================================
Draws real-time ADAS HUD with temporal persistence gating:
- Filters out natural blinks (<2.0s) and speech/chewing (<2.5s)
- Live duration countdown on HUD
- Acoustic alarm triggers strictly on confirmed microsleep
"""

import time
import winsound
import cv2
import numpy as np

from config.settings import (
    ALERT_THRESHOLD_CAUTION,
    ALERT_THRESHOLD_CRITICAL,
    EYE_CLOSED_TIME_THRESHOLD,
    YAWN_TIME_THRESHOLD,
)


class DriverHUDVisualizer:
    """
    Renders real-time telemetry, facial contours, and alert states on OpenCV frames.
    """
    def __init__(self):
        self.last_beep_time = 0.0
        self.beep_cooldown = 1.0
        self.frame_counter = 0

        # Temporal duration tracking (Blink & Speech Filters)
        self.eye_closed_start_time = None
        self.yawn_start_time = None

    def draw_hud(self, frame: np.ndarray, telemetry: dict | None, alert_score: float) -> np.ndarray:
        h, w = frame.shape[:2]
        self.frame_counter += 1
        canvas = frame.copy()
        now = time.time()

        # ----------------------------------------------------------------------
        # 1. Temporal Persistence Logic (Blink & Yawn Filtering)
        # ----------------------------------------------------------------------
        eye_closed_duration = 0.0
        yawn_duration = 0.0

        if telemetry and telemetry.get('face_detected', False):
            ear_val = telemetry['avg_ear']
            mar_val = telemetry['mar']

            # Eye Closure Duration Tracker:
            # An EAR <= 0.21 indicates eyes are closed/blinking
            if ear_val <= 0.21:
                if self.eye_closed_start_time is None:
                    self.eye_closed_start_time = now
                eye_closed_duration = now - self.eye_closed_start_time
            else:
                self.eye_closed_start_time = None
                eye_closed_duration = 0.0

            # Yawn Duration Tracker:
            # A MAR >= 0.62 indicates a wide open mouth
            if mar_val >= 0.62:
                if self.yawn_start_time is None:
                    self.yawn_start_time = now
                yawn_duration = now - self.yawn_start_time
            else:
                self.yawn_start_time = None
                yawn_duration = 0.0
        else:
            self.eye_closed_start_time = None
            self.yawn_start_time = None

        # Confirmed Microsleep: Closed continuously for >= 2.0 seconds
        is_microsleep = eye_closed_duration >= EYE_CLOSED_TIME_THRESHOLD

        # Confirmed Sustained Yawn: Open continuously for >= 2.5 seconds
        is_sustained_yawn = yawn_duration >= YAWN_TIME_THRESHOLD

        # ----------------------------------------------------------------------
        # 2. Draw Facial Contours
        # ----------------------------------------------------------------------
        if telemetry and telemetry.get('face_detected', False):
            eye_color = (0, 0, 255) if eye_closed_duration > 0 else (0, 255, 200)
            cv2.polylines(canvas, [telemetry['left_eye_pts']], isClosed=True, color=eye_color, thickness=1)
            cv2.polylines(canvas, [telemetry['right_eye_pts']], isClosed=True, color=eye_color, thickness=1)

            mouth_color = (0, 165, 255) if is_sustained_yawn else (255, 200, 0)
            cv2.polylines(canvas, [telemetry['mouth_pts']], isClosed=True, color=mouth_color, thickness=1)

        # ----------------------------------------------------------------------
        # 3. Semi-Transparent Telemetry Card (Top-Left)
        # ----------------------------------------------------------------------
        overlay = canvas.copy()
        card_w, card_h = 330, 185
        cv2.rectangle(overlay, (10, 10), (10 + card_w, 10 + card_h), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.75, canvas, 0.25, 0, canvas)
        cv2.rectangle(canvas, (10, 10), (10 + card_w, 10 + card_h), (80, 80, 80), 1)

        # ----------------------------------------------------------------------
        # 4. Status Determination (Gated by Duration)
        # ----------------------------------------------------------------------
        if is_microsleep:
            status_text = "STATUS: CRITICAL MICROSLEEP!"
            status_color = (0, 0, 255)      # Red
        elif is_sustained_yawn or alert_score >= ALERT_THRESHOLD_CAUTION:
            if is_sustained_yawn:
                status_text = "STATUS: YAWN DETECTED (CAUTION)"
            else:
                status_text = "STATUS: CAUTION / DROWSY"
            status_color = (0, 255, 255)    # Yellow
        else:
            status_text = "STATUS: SAFE / ALERT"
            status_color = (0, 255, 0)      # Green

        # Render Text on Telemetry Card
        cv2.putText(canvas, "DRIVER VIGILANCE FIS", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(canvas, status_text, (20, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.48, status_color, 2)

        ear_val = telemetry['avg_ear'] if telemetry else 0.0
        mar_val = telemetry['mar'] if telemetry else 0.0
        cv2.putText(canvas, f"Eye Aspect Ratio (EAR): {ear_val:.3f}", (20, 76), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (220, 220, 220), 1)
        cv2.putText(canvas, f"Mouth Aspect Ratio (MAR): {mar_val:.3f}", (20, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (220, 220, 220), 1)
        cv2.putText(canvas, f"Fuzzy Alert Score: {alert_score:.1f}%", (20, 116), cv2.FONT_HERSHEY_SIMPLEX, 0.48, status_color, 2)

        # Live Timer HUD Readouts (Proves blink/speech filtering)
        timer_text = f"Eye Closed: {eye_closed_duration:.1f}s / {EYE_CLOSED_TIME_THRESHOLD:.1f}s"
        timer_color = (0, 0, 255) if eye_closed_duration >= 1.0 else (180, 180, 180)
        cv2.putText(canvas, timer_text, (20, 136), cv2.FONT_HERSHEY_SIMPLEX, 0.44, timer_color, 1)

        # ----------------------------------------------------------------------
        # 5. Alert Level Horizontal Gauge Bar
        # ----------------------------------------------------------------------
        bar_x, bar_y = 20, 155
        bar_w, bar_h = 290, 16
        cv2.rectangle(canvas, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
        fill_w = int((alert_score / 100.0) * bar_w)
        cv2.rectangle(canvas, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), status_color, -1)
        cv2.rectangle(canvas, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (120, 120, 120), 1)

        # ----------------------------------------------------------------------
        # 6. Critical Flashing Alert & Acoustic Alarm (GATED BY 2.0s MICROSLEEP)
        # ----------------------------------------------------------------------
        if is_microsleep:
            # Flashing screen border
            if self.frame_counter % 6 < 3:
                cv2.rectangle(canvas, (0, 0), (w - 1, h - 1), (0, 0, 255), 8)
                banner_overlay = canvas.copy()
                cv2.rectangle(banner_overlay, (0, h - 60), (w, h), (0, 0, 180), -1)
                cv2.addWeighted(banner_overlay, 0.8, canvas, 0.2, 0, canvas)
                cv2.putText(canvas, "CRITICAL: MICROSLEEP DETECTED! WAKE UP!",
                            (w // 2 - 250, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            # Sound acoustic alarm (only when eye closure persists >= 2.0 seconds)
            if now - self.last_beep_time > self.beep_cooldown:
                try:
                    winsound.Beep(2500, 250)
                except Exception:
                    pass
                self.last_beep_time = now

        return canvas
