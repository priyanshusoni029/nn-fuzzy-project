"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Unit 4 & 5
Fuzzy Inference System Controller & Defuzzifier
================================================================================
Encapsulates Mamdani ControlSystemSimulation and executes Centroid
(Center of Gravity) defuzzification to produce a continuous Alert Level [0, 100].
"""

import numpy as np
from skfuzzy import control as ctrl

from config.settings import (
    UNIVERSE_EAR,
    UNIVERSE_MAR,
    DEFUZZIFICATION_METHOD,
)
from .membership import create_fuzzy_variables
from .rules import create_fuzzy_rules


class DrowsinessFISController:
    """
    Closed-loop Fuzzy Inference Controller for real-time driver drowsiness quantification.
    """
    def __init__(self):
        # 1. Initialize Linguistic Variables
        self.ear, self.mar, self.alert = create_fuzzy_variables()

        # 2. Defuzzification method (default: centroid)
        self.alert.defuzzify_method = DEFUZZIFICATION_METHOD

        # 3. Build Rule Base
        self.rules = create_fuzzy_rules(self.ear, self.mar, self.alert)

        # 4. Compile Control System
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)

    def evaluate(self, ear_value: float, mar_value: float) -> tuple[float, dict]:
        """
        Executes fuzzification, rule evaluation, aggregation, and centroid defuzzification.
        
        Args:
            ear_value (float): Real-time Eye Aspect Ratio
            mar_value (float): Real-time Mouth Aspect Ratio
            
        Returns:
            tuple: (crisp_alert_score: float [0, 100], telemetry_dict: dict)
        """
        # Safety Clamping: Ensure inputs do not exceed universe limits
        clamped_ear = float(np.clip(ear_value, UNIVERSE_EAR[0], UNIVERSE_EAR[1]))
        clamped_mar = float(np.clip(mar_value, UNIVERSE_MAR[0], UNIVERSE_MAR[1]))

        # Pass crisp numerical inputs into antecedents (Fuzzification)
        self.simulator.input['EAR'] = clamped_ear
        self.simulator.input['MAR'] = clamped_mar

        # Compute fuzzy inference & centroid defuzzification
        try:
            self.simulator.compute()
            alert_score = float(self.simulator.output['Alert_Level'])
        except Exception:
            # Fallback if evaluation is indeterminate (safety guarantee)
            alert_score = 50.0

        telemetry = {
            'raw_ear': ear_value,
            'raw_mar': mar_value,
            'clamped_ear': clamped_ear,
            'clamped_mar': clamped_mar,
            'alert_score': alert_score
        }

        return alert_score, telemetry
