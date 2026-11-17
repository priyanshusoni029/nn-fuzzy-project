"""
================================================================================
EEE1004: Neural Networks and Fuzzy Systems - Final Report & Viva Visualizer
================================================================================
Generates high-resolution Matplotlib figures:
1. 2D Overlapping Membership Function Curves (EAR, MAR, Alert Level)
2. 3D Control Surface (EAR x MAR -> Alert Level) via Centroid Defuzzification
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# Add project root to sys.path to allow running from any working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import UNIVERSE_EAR, UNIVERSE_MAR, UNIVERSE_ALERT
from fis.controller import DrowsinessFISController
from fis.membership import create_fuzzy_variables


def plot_membership_functions(save_path="membership_functions.png"):
    """Plots and saves the 2D membership curves for EAR, MAR, and Alert Level."""
    ear, mar, alert = create_fuzzy_variables()

    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(10, 11))
    plt.subplots_adjust(hspace=0.45)

    # --- Plot 1: EAR Membership Functions ---
    ax0.plot(ear.universe, ear['Closed'].mf, 'r', linewidth=2, label='Closed (trapmf)')
    ax0.plot(ear.universe, ear['Drooping'].mf, 'orange', linewidth=2, label='Drooping (trimf)')
    ax0.plot(ear.universe, ear['Wide_Awake'].mf, 'g', linewidth=2, label='Wide Awake (trapmf)')
    ax0.set_title('Eye Aspect Ratio (EAR) Input Membership Functions', fontsize=12, fontweight='bold')
    ax0.set_xlabel('EAR Value (dimensionless)', fontsize=10)
    ax0.set_ylabel('Degree of Membership', fontsize=10)
    ax0.grid(True, linestyle='--', alpha=0.6)
    ax0.legend(loc='center right')
    ax0.set_ylim(-0.05, 1.05)

    # --- Plot 2: MAR Membership Functions ---
    ax1.plot(mar.universe, mar['Normal'].mf, 'g', linewidth=2, label='Normal (trapmf)')
    ax1.plot(mar.universe, mar['Speaking'].mf, 'b', linewidth=2, label='Speaking (trimf)')
    ax1.plot(mar.universe, mar['Yawning'].mf, 'r', linewidth=2, label='Yawning (trapmf)')
    ax1.set_title('Mouth Aspect Ratio (MAR) Input Membership Functions', fontsize=12, fontweight='bold')
    ax1.set_xlabel('MAR Value (dimensionless)', fontsize=10)
    ax1.set_ylabel('Degree of Membership', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='center right')
    ax1.set_ylim(-0.05, 1.05)

    # --- Plot 3: Consequent Alert Level ---
    ax2.plot(alert.universe, alert['Low'].mf, 'g', linewidth=2, label='Low Alert (trapmf)')
    ax2.plot(alert.universe, alert['Moderate'].mf, 'orange', linewidth=2, label='Moderate Alert (trimf)')
    ax2.plot(alert.universe, alert['High'].mf, 'r', linewidth=2, label='High Alert (trapmf)')
    ax2.set_title('Consequent Output: Driver Alert Level (Centroid Defuzzification)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Alert Level [0 - 100]', fontsize=10)
    ax2.set_ylabel('Degree of Membership', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='center right')
    ax2.set_ylim(-0.05, 1.05)

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[✓] Saved Membership Functions plot to: {save_path}")


def plot_control_surface(save_path="fuzzy_control_surface_3d.png"):
    """Computes and renders the 3D control surface mapping (EAR x MAR -> Alert Level)."""
    controller = DrowsinessFISController()

    # Discretize grid for 3D mesh evaluation
    ear_vals = np.linspace(UNIVERSE_EAR[0], UNIVERSE_EAR[1], 35)
    mar_vals = np.linspace(UNIVERSE_MAR[0], UNIVERSE_MAR[1], 35)
    ear_grid, mar_grid = np.meshgrid(ear_vals, mar_vals)
    alert_grid = np.zeros_like(ear_grid)

    for i in range(ear_grid.shape[0]):
        for j in range(ear_grid.shape[1]):
            score, _ = controller.evaluate(ear_grid[i, j], mar_grid[i, j])
            alert_grid[i, j] = score

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(
        ear_grid, mar_grid, alert_grid,
        cmap='viridis',
        edgecolor='none',
        alpha=0.9
    )

    ax.set_title('3D Fuzzy Control Surface (EAR × MAR → Alert Level)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Eye Aspect Ratio (EAR)', fontsize=10, labelpad=10)
    ax.set_ylabel('Mouth Aspect Ratio (MAR)', fontsize=10, labelpad=10)
    ax.set_zlabel('Alert Level (0-100)', fontsize=10, labelpad=10)

    # Colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label('Alert Level Scalar', fontsize=10)

    ax.view_init(elev=28, azim=-125)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[✓] Saved 3D Control Surface plot to: {save_path}")


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    plots_dir = os.path.join(project_root, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    mf_path = os.path.join(plots_dir, "membership_functions.png")
    surface_path = os.path.join(plots_dir, "fuzzy_control_surface_3d.png")
    
    plot_membership_functions(mf_path)
    plot_control_surface(surface_path)
