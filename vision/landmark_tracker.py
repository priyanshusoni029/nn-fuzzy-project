"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Unit 1 & 2 Application
Deep Neural Facial Landmark Tracker (MediaPipe FaceLandmarker Tasks API)
================================================================================
Performs 468+ point 3D facial coordinate regression on real-time video streams,
slicing landmarks corresponding to eye and mouth contours.
Compatible with Python 3.14+ and MediaPipe Tasks API.
"""

import os
import cv2
import mediapipe as mp
import numpy as np

from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarker, FaceLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode

from config.settings import (
    LEFT_EYE_LANDMARKS,
    RIGHT_EYE_LANDMARKS,
    MOUTH_LANDMARKS,
    MODEL_PATH,
)
from .telemetry import calculate_ear, calculate_mar


class FaceMeshTracker:
    """
    Neural facial landmark pipeline encapsulating MediaPipe FaceLandmarker Tasks API.
    """
    def __init__(self, model_path: str = MODEL_PATH, max_num_faces: int = 1, refine_landmarks: bool = True, **kwargs):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"[!] Model file not found at: {model_path}\n"
                "    Please ensure 'models/face_landmarker.task' exists."
            )

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionTaskRunningMode.IMAGE,
            num_faces=max_num_faces,
            min_face_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = FaceLandmarker.create_from_options(options)

    def process_frame(self, frame: np.ndarray) -> tuple[dict | None, np.ndarray]:
        """
        Processes a single BGR frame, extracts facial landmarks, and computes telemetry.
        
        Args:
            frame (np.ndarray): BGR image frame from camera
            
        Returns:
            tuple: (telemetry_dict or None if no face detected, all_landmarks_pixel_coords)
        """
        h, w = frame.shape[:2]

        # Convert OpenCV BGR to RGB and create MediaPipe Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks or len(result.face_landmarks) == 0:
            return None, np.empty((0, 2), dtype=np.int32)

        # Extract primary detected face
        face_landmarks = result.face_landmarks[0]

        # Convert normalized coordinates (0.0 to 1.0) into discrete pixel coordinates
        landmarks_pixel = np.array([
            [int(lm.x * w), int(lm.y * h)] for lm in face_landmarks
        ], dtype=np.int32)

        # Slice relevant landmark subsets for left eye, right eye, and mouth
        left_eye_pts = landmarks_pixel[LEFT_EYE_LANDMARKS]
        right_eye_pts = landmarks_pixel[RIGHT_EYE_LANDMARKS]
        mouth_pts = landmarks_pixel[MOUTH_LANDMARKS]

        # Compute instantaneous aspect ratios via vectorized telemetry
        left_ear = calculate_ear(left_eye_pts)
        right_ear = calculate_ear(right_eye_pts)
        avg_ear = float((left_ear + right_ear) / 2.0)
        mar = calculate_mar(mouth_pts)

        telemetry = {
            'left_ear': left_ear,
            'right_ear': right_ear,
            'avg_ear': avg_ear,
            'mar': mar,
            'left_eye_pts': left_eye_pts,
            'right_eye_pts': right_eye_pts,
            'mouth_pts': mouth_pts,
            'face_detected': True
        }

        return telemetry, landmarks_pixel

    def release(self):
        """Releases underlying neural network resources."""
        if hasattr(self, 'landmarker') and self.landmarker:
            self.landmarker.close()
