# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 2026

@author: USUARIO
"""

"""
Effective index, free-carrier loss and V_pi*L versus bias, from the Lumerical
FDE bias sweep saved in 'neff_vs_bias.mat'.

The .mat file is saved by Lumerical in HDF5 format (MATLAB v7.3), so h5py is the
reader. Expected variables:
    - V          : bias vector [V], same grid as the CHARGE sweep
    - neff_real  : Re(neff) at each bias point
    - neff_imag  : Im(neff) at each bias point (= k, extinction coefficient)
    - alpha      : propagation loss [1/m]
    - alpha_dB_cm: the same in dB/cm
    - V_pi_L     : V_pi*L per bias interval [V cm]

V_pi*L is the standard phase-shifter figure of merit: a pi phase shift needs
(2*pi/lambda)*|dneff|*L = pi, so V_pi*L = lambda/(2*|dneff/dV|). It is evaluated
per bias interval here, because dneff/dV is not constant - it is steepest near
zero bias and flattens as the junction depletes. The script also reports a
single value from a linear fit over the whole range, which is the number to
quote when comparing designs.
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Load .mat file (HDF5 format)
# ---------------------------------------------------------------
filename = "PhaseShifter/MODE/neff_vs_bias.mat"

def load_var(h5file, name):
    """Read a dataset from an HDF5-based .mat file and return a 1D numpy array."""
    arr = np.array(h5file[name])
    # HDF5 .mat stores arrays transposed compared to MATLAB convention
    arr = arr.T
    return np.squeeze(arr)

with h5py.File(filename, "r") as f:
    # Uncomment to inspect contents:
    # print("Variables in file:", list(f.keys()))

    V         = load_var(f, "V")
    neff_real = load_var(f, "neff_real")
    neff_imag = load_var(f, "neff_imag")
    alpha_dB_cm = load_var(f, "alpha_dB_cm")
    V_pi_L    = load_var(f, "V_pi_L")

V         = np.asarray(V, dtype=float)
neff_real = np.asarray(neff_real, dtype=float)
neff_imag = np.asarray(neff_imag, dtype=float)
V_pi_L    = np.asarray(V_pi_L, dtype=float)
alpha_dB_cm = np.asarray(alpha_dB_cm, dtype=float)

# The sweep was generated as linspace(V_start, V_stop), so it already runs
# ascending from the deepest reverse bias up to 0 V and the arrays read left to
# right. V_pi_L is defined between neighbouring points and therefore has one
# fewer entry; it belongs to the interval midpoints.
V_mid = 0.5 * (V[:-1] + V[1:])

# Reference state: the equilibrium point, V = 0.
i_ref = int(np.argmin(np.abs(V)))
dneff = neff_real - neff_real[i_ref]

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("=== Effective index vs bias ===")
print(f"  equilibrium (V = {V[i_ref]:+.2f} V): neff = {neff_real[i_ref]:.6f}, "
      f"k = {neff_imag[i_ref]:.3e}")
for v, n, dn, a in zip(V, neff_real, dneff, alpha_dB_cm):
    print(f"  V = {v:+.2f} V   neff = {n:.6f}   dneff = {dn:+.6f}   "
          f"loss = {a:.2f} dB/cm")

# Design targets for this device
TARGET_VPI_L   = 3.0      # V cm
TARGET_LOSS_DB = 5.0      # dB, insertion loss over the whole modulator
DEVICE_LENGTH_CM = 0.1    # 1 mm of phase shifter

best = int(np.argmin(V_pi_L))
print("\n=== Phase-shift efficiency ===")
print(f"  V_pi*L, best interval : {V_pi_L[best]:.3f} V cm "
      f"(between {V[best]:+.2f} and {V[best + 1]:+.2f} V)")

# A single number for the whole range: from the total index change and the total
# voltage swing. This is the honest design figure, since it averages over the
# bias dependence rather than quoting the most favourable interval.
span_V = abs(V[-1] - V[0])
slope_mean = abs(neff_real[-1] - neff_real[0]) / span_V          # per volt
lambda0 = 1.55e-6
V_pi_L_fit = lambda0 / (2 * slope_mean) * 100                     # V cm
print(f"  V_pi*L, mean slope   : {V_pi_L_fit:.3f} V cm "
      f"(over the full {span_V:.1f} V swing)")
print(f"  target: < {TARGET_VPI_L:.1f} V cm -> "
      f"{'met' if V_pi_L_fit < TARGET_VPI_L else 'not met'}")

# The loss target is an insertion-loss budget for the whole modulator, so it has
# to be converted using a device length before it can be compared with a dB/cm
# figure. This is also only the free-carrier term: the MMI and bend contributions
# are measured in the other project folders and share the same budget.
loss_device = np.max(alpha_dB_cm) * DEVICE_LENGTH_CM
print(f"\n  free-carrier loss over {DEVICE_LENGTH_CM * 10:.1f} mm of shifter: "
      f"{loss_device:.2f} dB (peak {np.max(alpha_dB_cm):.2f} dB/cm)")
print(f"  insertion-loss budget: < {TARGET_LOSS_DB:.1f} dB for the whole device, "
      f"shared with the MMI and bends")

# ---------------------------------------------------------------
# Plot 1: effective index vs bias
# ---------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(7, 5))
ax1.plot(V, neff_real, 'o-', color='tab:blue')
ax1.axhline(neff_real[i_ref], color='k', linestyle='--', alpha=0.5,
            label=f"equilibrium $n_\\mathrm{{eff}}$ = {neff_real[i_ref]:.6f}")
ax1.set_xlabel("Bias voltage [V]")
ax1.set_ylabel("Effective index $n_\\mathrm{eff}$")
ax1.set_title("Effective index vs reverse bias ($Si$ 500x220 nm)")
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend()
fig1.tight_layout()
fig1.savefig("PhaseShifter/MODE/neff_vs_bias.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot 2: index change vs bias
# ---------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(7, 5))
ax2.plot(V, dneff * 1e4, 's-', color='tab:green')
ax2.set_xlabel("Bias voltage [V]")
ax2.set_ylabel(r"$\Delta n_\mathrm{eff}$ [$10^{-4}$]")
ax2.set_title("Index modulation vs reverse bias")
ax2.grid(True, linestyle=":", alpha=0.6)
fig2.tight_layout()
fig2.savefig("PhaseShifter/MODE/dneff_vs_bias.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot 3: free-carrier loss vs bias
# ---------------------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(7, 5))
ax3.plot(V, alpha_dB_cm, '^-', color='tab:red')
ax3.axhline(TARGET_LOSS_DB / DEVICE_LENGTH_CM, color='k', linestyle='--', alpha=0.6,
            label=f"budget if all {TARGET_LOSS_DB:.0f} dB is here ({DEVICE_LENGTH_CM*10:.0f} mm)")
ax3.set_xlabel("Bias voltage [V]")
ax3.set_ylabel("Free-carrier loss [dB/cm]")
ax3.set_title("Free-carrier absorption vs reverse bias")
ax3.grid(True, linestyle=":", alpha=0.6)
ax3.legend()
fig3.tight_layout()
fig3.savefig("PhaseShifter/MODE/loss_vs_bias.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot 4: V_pi*L vs bias
# ---------------------------------------------------------------
fig4, ax4 = plt.subplots(figsize=(7, 5))
ax4.semilogy(V_mid, V_pi_L, 'd-', color='tab:purple', label="per bias interval")
ax4.axhline(V_pi_L_fit, color='k', linestyle='--', alpha=0.6,
            label=f"mean slope = {V_pi_L_fit:.2f} V cm")
ax4.axhline(TARGET_VPI_L, color='tab:red', linestyle=':', alpha=0.8,
            label=f"target {TARGET_VPI_L:.0f} V cm")
ax4.set_xlabel("Bias voltage [V]")
ax4.set_ylabel(r"$V_\pi L$ [V$\cdot$cm]")
ax4.set_title(r"$V_\pi L$ figure of merit vs reverse bias")
ax4.grid(True, which="both", linestyle=":", alpha=0.6)
ax4.legend(fontsize=9)
fig4.tight_layout()
fig4.savefig("PhaseShifter/MODE/vpi_L_vs_bias.png", dpi=300, bbox_inches="tight")

plt.show()
