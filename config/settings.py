"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Course Project
Configuration & Parameter Specification Module
================================================================================
Defines all physical camera settings, facial landmark topological indices,
mathematical universes of discourse, and fuzzy membership coordinates.
"""
import os

# ==============================================================================
# 1. Hardware & Video Stream Settings
# ==============================================================================
CAMERA_INDEX = 0          # Default system webcam (change to 1 if using external USB cam)
FRAME_WIDTH = 640         # Standard resolution to maintain high FPS on CPU
FRAME_HEIGHT = 480        # Standard 4:3 aspect ratio
TARGET_FPS = 30           # Real-time processing target

# Model Asset Path (MediaPipe FaceLandmarker Task)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "face_landmarker.task")

# ==============================================================================
# 2. MediaPipe Face Mesh Landmark Topological Indices
# 468-point 3D landmark mesh keypoint mappings for EAR and MAR calculation
# ==============================================================================
# Eye Aspect Ratio (EAR) 6-point indices (Soukupová & Čech formulation)
# Format: [P1_lateral, P2_sup_lat, P3_sup_med, P4_medial, P5_inf_med, P6_inf_lat]
LEFT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]

# Mouth Aspect Ratio (MAR) 8-point lip contour indices
# P1, P5 = horizontal mouth corners (61, 291)
# Vertical pairs: (P2, P8)=(39, 181), (P3, P7)=(0, 17), (P4, P6)=(269, 405)
MOUTH_LANDMARKS = [61, 39, 0, 269, 291, 405, 17, 181]

# ==============================================================================
# 3. Fuzzy Universes of Discourse (Unit 4 - Fuzzy Sets)
# Format: (start, stop, step_resolution)
# ==============================================================================
UNIVERSE_EAR = (0.00, 0.45, 0.005)    # Eye Aspect Ratio range
UNIVERSE_MAR = (0.00, 1.00, 0.01)     # Mouth Aspect Ratio range
UNIVERSE_ALERT = (0.0, 100.0, 0.5)    # Output Alert Level scalar range (0 to 100)

# ==============================================================================
# 4. Membership Function Parameters (Unit 4 - Fuzzification)
# Trapezoidal: [a, b, c, d] | Triangular: [a, b, c]
# Recalibrated to eliminate speech/eating overlap
# ==============================================================================
# Eye Aspect Ratio (EAR) Linguistic Sets: Closed, Drooping, Wide_Awake
MF_EAR_CLOSED = [0.00, 0.00, 0.16, 0.21]      # trapmf: Complete closure & blinks
MF_EAR_DROOPING = [0.18, 0.24, 0.29]          # trimf: Drowsy / heavy eyelids
MF_EAR_WIDE_AWAKE = [0.26, 0.31, 0.45, 0.45]  # trapmf: Alert, open eyes

# Mouth Aspect Ratio (MAR) Linguistic Sets: Normal, Speaking, Yawning
# Normal speech/chewing easily reaches 0.40-0.55; true yawning starts at 0.62+
MF_MAR_NORMAL = [0.00, 0.00, 0.30, 0.45]      # trapmf: Closed / resting mouth
MF_MAR_SPEAKING = [0.35, 0.48, 0.65]          # trimf: Natural conversational movement / eating
MF_MAR_YAWNING = [0.60, 0.72, 1.00, 1.00]     # trapmf: Deep fatigue yawn aperture

# Consequent Linguistic Sets: Low, Moderate, High Alert Level (0 to 100)
MF_ALERT_LOW = [0.0, 0.0, 20.0, 35.0]         # trapmf: Safe driving state
MF_ALERT_MODERATE = [25.0, 50.0, 75.0]        # trimf: Cautionary warning
MF_ALERT_HIGH = [65.0, 80.0, 100.0, 100.0]    # trapmf: Critical drowsiness alarm

# ==============================================================================
# 5. Temporal Persistence Thresholds (Prevents Blink & Speech False Alarms)
# ==============================================================================
DEFUZZIFICATION_METHOD = 'centroid'            # Center of Gravity (COG)
ALERT_THRESHOLD_CAUTION = 45.0                 # Yellow HUD indicator threshold
ALERT_THRESHOLD_CRITICAL = 70.0                # Red HUD alert threshold

# Time Duration Gates (in seconds):
EYE_CLOSED_TIME_THRESHOLD = 2.0                # Blinks (<0.4s) ignored; only beeps if closed >= 2.0s
YAWN_TIME_THRESHOLD = 2.5                      # Chewing/speaking (<0.6s) ignored; yawn must last >= 2.5s
