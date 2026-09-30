# -*- coding: utf-8 -*-
"""
Created on Sat May  2 09:24:05 2026

@author: USUARIO
"""

"""
Plot bend losses and effective index difference from Lumerical FDE sweep results.

Reads the .mat file saved by the Lumerical script (matlabsave) using h5py.
Lumerical saves .mat files in HDF5 format (MATLAB v7.3), so h5py is the
appropriate reader.

Expected variables inside the file:
    - Rc_sweep      : radii of curvature [m]
    - dneff_vec     : |neff_straight - neff_bend|
    - powercoupling : mode overlap power coupling between straight and bent modes
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Load data with h5py
# ---------------------------------------------------------------
filename = "Bends/MODE/neff_Rc_sweep_Si.mat"

def load_var(h5file, name):
    """Read a dataset from an HDF5-based .mat file and return a 1D numpy array."""
    arr = np.array(h5file[name])
    # HDF5 .mat stores arrays transposed compared to MATLAB convention
    arr = arr.T
    return np.squeeze(arr)

with h5py.File(filename, "r") as f:
    # Uncomment to inspect contents:
    # print("Variables in file:", list(f.keys()))

    Rc_sweep      = load_var(f, "Rc_sweep")        # [m]
    dneff_vec     = load_var(f, "dneff_vec")
    powercoupling = load_var(f, "powercoupling")

# Ensure real-valued floats (h5py may return complex or compound types)
Rc_sweep      = np.asarray(Rc_sweep, dtype=float)
dneff_vec     = np.asarray(dneff_vec, dtype=float)
powercoupling = np.asarray(powercoupling, dtype=float)

um = 1e-6

# ---------------------------------------------------------------
# Compute losses
# ---------------------------------------------------------------
# Mode mismatch loss (two transitions: straight -> bend -> straight)
LossMM = -10.0 * np.log10(powercoupling**2)

# Propagation / scattering loss: 2 dB/cm over a quarter-circle bend
PropagationLoss_dB_per_m = 200          # 2 dB/cm = 200 dB/m
LossP = PropagationLoss_dB_per_m * 2 * np.pi * Rc_sweep / 4.0

LossTotal = LossMM + LossP

# ---------------------------------------------------------------
# Find optimum radius (minimum total loss)
# ---------------------------------------------------------------
idx_opt = np.argmin(LossTotal)
Rc_opt = Rc_sweep[idx_opt] / um
print(f"Optimum bend radius: {Rc_opt:.2f} um  "
      f"(Total loss = {LossTotal[idx_opt]:.4f} dB)")

# ---------------------------------------------------------------
# Plot 1: Losses vs radius of curvature
# ---------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(7, 5))

ax1.loglog(Rc_sweep / um, LossMM,    'o-', label="Mode mismatch loss")
ax1.loglog(Rc_sweep / um, LossP,     's-', label="Scattering loss (2 dB/cm)")
ax1.loglog(Rc_sweep / um, LossTotal, '^-', label="Total loss", linewidth=2)

ax1.axvline(Rc_opt, color='k', linestyle='--', alpha=0.6,
            label=f"Optimum R = {Rc_opt:.1f} µm")

ax1.set_xlabel("Radius of curvature [µm]")
ax1.set_ylabel("Loss [dB]")
ax1.set_title("Bend loss vs radius of curvature ($Si$)")
ax1.grid(True, which="both", linestyle=":", alpha=0.6)
ax1.legend()
fig1.tight_layout()
fig1.savefig("Bends/MODE/bend_loss_vs_radius.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot 2: Effective index difference vs radius of curvature
# ---------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(7, 5))

ax2.semilogy(Rc_sweep / um, dneff_vec, 'o-', color='tab:red')
ax2.set_xlabel("Radius of curvature [µm]")
ax2.set_ylabel(r"$|\Delta n_{\mathrm{eff}}|$")
ax2.set_title("Effective index difference ($Si$)")
ax2.grid(True, which="both", linestyle=":", alpha=0.6)
fig2.tight_layout()
fig2.savefig("Bends/MODE/bend_neff_shift_vs_radius.png", dpi=300, bbox_inches="tight")

plt.show()
