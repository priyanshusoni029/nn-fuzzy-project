"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems
Vectorized Facial Metric Telemetry Module (EAR & MAR)
================================================================================
Implements vectorized Euclidean distance geometry using NumPy.
Formulation References:
- EAR: Soukupová and Čech (2016), "Real-Time Eye Blink Detection using Facial Landmarks"
- MAR: Vertical-to-Horizontal lip separation ratio
"""

import numpy as np


def calculate_ear(eye_points: np.ndarray) -> float:
    """
    Computes Eye Aspect Ratio (EAR) using vectorized Euclidean distance norms.
    
    Formula:
        EAR = (||P2 - P6|| + ||P3 - P5||) / (2 * ||P1 - P4||)
        
    Args:
        eye_points (np.ndarray): Shape (6, 2) containing 2D (x, y) coordinates:
                                 [P1, P2, P3, P4, P5, P6]
                                 
    Returns:
        float: Computed Eye Aspect Ratio
    """
    # Vertical Euclidean distances
    dist_v1 = np.linalg.norm(eye_points[1] - eye_points[5])
    dist_v2 = np.linalg.norm(eye_points[2] - eye_points[4])

    # Horizontal Euclidean distance
    dist_h = np.linalg.norm(eye_points[0] - eye_points[3])

    # Guard against division by zero (degenerate coordinates)
    if dist_h < 1e-6:
        return 0.0

    ear = float((dist_v1 + dist_v2) / (2.0 * dist_h))
    return ear


def calculate_mar(mouth_points: np.ndarray) -> float:
    """
    Computes Mouth Aspect Ratio (MAR) using 8 lip landmark points.
    
    Formula:
        MAR = (||P2 - P8|| + ||P3 - P7|| + ||P4 - P6||) / (2 * ||P1 - P5||)
        
    Args:
        mouth_points (np.ndarray): Shape (8, 2) containing coordinates:
                                   [P1, P2, P3, P4, P5, P6, P7, P8]
                                   
    Returns:
        float: Computed Mouth Aspect Ratio
    """
    # Three vertical distances across the inner/outer lip aperture
    dist_v1 = np.linalg.norm(mouth_points[1] - mouth_points[7])  # (P2, P8)
    dist_v2 = np.linalg.norm(mouth_points[2] - mouth_points[6])  # (P3, P7)
    dist_v3 = np.linalg.norm(mouth_points[3] - mouth_points[5])  # (P4, P6)

    # Horizontal mouth width distance
    dist_h = np.linalg.norm(mouth_points[0] - mouth_points[4])   # (P1, P5)

    if dist_h < 1e-6:
        return 0.0

    mar = float((dist_v1 + dist_v2 + dist_v3) / (2.0 * dist_h))
    return mar
