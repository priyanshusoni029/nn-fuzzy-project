"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Unit 4
Fuzzification & Membership Function Definition Module
================================================================================
Defines input antecedents and output consequents using triangular (trimf)
and trapezoidal (trapmf) membership functions over specified universes of discourse.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from config.settings import (
    UNIVERSE_EAR,
    UNIVERSE_MAR,
    UNIVERSE_ALERT,
    MF_EAR_CLOSED,
    MF_EAR_DROOPING,
    MF_EAR_WIDE_AWAKE,
    MF_MAR_NORMAL,
    MF_MAR_SPEAKING,
    MF_MAR_YAWNING,
    MF_ALERT_LOW,
    MF_ALERT_MODERATE,
    MF_ALERT_HIGH,
)


def create_fuzzy_variables():
    """
    Constructs and returns Antecedents and Consequent with their Membership Functions.
    
    Returns:
        tuple: (ear_antecedent, mar_antecedent, alert_consequent)
    """
    # --------------------------------------------------------------------------
    # 1. Define Universes of Discourse (Discretized NumPy ranges)
    # --------------------------------------------------------------------------
    ear_universe = np.arange(UNIVERSE_EAR[0], UNIVERSE_EAR[1] + UNIVERSE_EAR[2], UNIVERSE_EAR[2])
    mar_universe = np.arange(UNIVERSE_MAR[0], UNIVERSE_MAR[1] + UNIVERSE_MAR[2], UNIVERSE_MAR[2])
    alert_universe = np.arange(UNIVERSE_ALERT[0], UNIVERSE_ALERT[1] + UNIVERSE_ALERT[2], UNIVERSE_ALERT[2])

    # --------------------------------------------------------------------------
    # 2. Declare Linguistic Variables (Antecedents = Inputs, Consequent = Output)
    # --------------------------------------------------------------------------
    ear = ctrl.Antecedent(ear_universe, 'EAR')
    mar = ctrl.Antecedent(mar_universe, 'MAR')
    alert = ctrl.Consequent(alert_universe, 'Alert_Level')

    # --------------------------------------------------------------------------
    # 3. Formulate Membership Functions for EAR (Unit 4 - Fuzzification)
    # --------------------------------------------------------------------------
    ear['Closed'] = fuzz.trapmf(ear.universe, MF_EAR_CLOSED)
    ear['Drooping'] = fuzz.trimf(ear.universe, MF_EAR_DROOPING)
    ear['Wide_Awake'] = fuzz.trapmf(ear.universe, MF_EAR_WIDE_AWAKE)

    # --------------------------------------------------------------------------
    # 4. Formulate Membership Functions for MAR
    # --------------------------------------------------------------------------
    mar['Normal'] = fuzz.trapmf(mar.universe, MF_MAR_NORMAL)
    mar['Speaking'] = fuzz.trimf(mar.universe, MF_MAR_SPEAKING)
    mar['Yawning'] = fuzz.trapmf(mar.universe, MF_MAR_YAWNING)

    # --------------------------------------------------------------------------
    # 5. Formulate Membership Functions for Consequent (Alert Level: 0 to 100)
    # --------------------------------------------------------------------------
    alert['Low'] = fuzz.trapmf(alert.universe, MF_ALERT_LOW)
    alert['Moderate'] = fuzz.trimf(alert.universe, MF_ALERT_MODERATE)
    alert['High'] = fuzz.trapmf(alert.universe, MF_ALERT_HIGH)

    return ear, mar, alert
