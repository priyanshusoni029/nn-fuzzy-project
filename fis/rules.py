"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Unit 5
Fuzzy Rule Base & Implication Matrix Module
================================================================================
Defines the 3x3 Mamdani IF-THEN linguistic rules connecting facial telemetry
(EAR, MAR) to Driver Alert Levels using T-norm (Minimum) conjunction.
"""

from skfuzzy import control as ctrl


def create_fuzzy_rules(ear, mar, alert):
    r"""
    Constructs the 9-rule Mamdani Rule Base for driver vigilance assessment.
    
    Rule Matrix (3x3):
    ----------------------------------------------------------------
    EAR \ MAR      | Normal         | Speaking       | Yawning
    ----------------------------------------------------------------
    Wide_Awake     | Low Alert      | Low Alert      | Moderate Alert
    Drooping       | Moderate Alert | Moderate Alert | High Alert
    Closed         | High Alert     | High Alert     | High Alert
    ----------------------------------------------------------------
    
    Args:
        ear: Antecedent for Eye Aspect Ratio
        mar: Antecedent for Mouth Aspect Ratio
        alert: Consequent for Driver Alert Level
        
    Returns:
        list: Collection of compiled skfuzzy.control.Rule objects
    """
    rules = [
        # --- Category 1: Wide Awake Driver Conditions ---
        ctrl.Rule(ear['Wide_Awake'] & mar['Normal'], alert['Low']),
        ctrl.Rule(ear['Wide_Awake'] & mar['Speaking'], alert['Low']),
        ctrl.Rule(ear['Wide_Awake'] & mar['Yawning'], alert['Moderate']),

        # --- Category 2: Drooping / Drowsy Eyelid Conditions ---
        ctrl.Rule(ear['Drooping'] & mar['Normal'], alert['Moderate']),
        ctrl.Rule(ear['Drooping'] & mar['Speaking'], alert['Moderate']),
        ctrl.Rule(ear['Drooping'] & mar['Yawning'], alert['High']),

        # --- Category 3: Closed Eyes / Microsleep Conditions ---
        ctrl.Rule(ear['Closed'] & mar['Normal'], alert['High']),
        ctrl.Rule(ear['Closed'] & mar['Speaking'], alert['High']),
        ctrl.Rule(ear['Closed'] & mar['Yawning'], alert['High']),
    ]

    return rules
