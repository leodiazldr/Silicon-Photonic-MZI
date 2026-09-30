# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 2026

@author: USUARIO
"""

"""
Insertion loss and splitting versus MMI length, from the EME propagation sweep saved
in 'length_sweep.mat' by step09_length_sweep.lsf.

The length is swept +/-20% around the analytical L_MMI = 3*L_pi/8. Because the sweep
is run as an EME propagation sweep on the MMI body cell group alone, every point
reuses the same mode decomposition, and a fine grid is cheap.

Expected variables:
    - L_sweep_vec : MMI length [m]
    - T_top_vs_L  : |s12|^2, transmission to the top output
    - T_bot_vs_L  : |s13|^2, transmission to the bottom output
    - IL_vs_L     : -10*log10(T_top + T_bot) [dB]
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

TARGET_IL_DB  = 0.5    # MMI insertion-loss target
TARGET_IMB_DB = 0.087  # 50:50 +/- 1% expressed in dB: |10*log10(1.01/0.99)|

filename = "MMI/MODE/length_sweep.mat"

with h5py.File(filename, "r") as f:
    # ravel() is order-agnostic, so it works whether Lumerical stored these as
    # rows or as columns
    L_sweep_vec = np.ravel(np.array(f["L_sweep_vec"]))
    T_top_vs_L  = np.ravel(np.array(f["T_top_vs_L"]))
    T_bot_vs_L  = np.ravel(np.array(f["T_bot_vs_L"]))
    IL_vs_L     = np.ravel(np.array(f["IL_vs_L"]))

um = 1e-6
L_um = L_sweep_vec / um

# transmittances in dB, with a floor so a nulled port cannot produce -inf
T_top_dB = 10 * np.log10(np.maximum(T_top_vs_L, 1e-30))
T_bot_dB = 10 * np.log10(np.maximum(T_bot_vs_L, 1e-30))
Imb_dB   = np.abs(T_top_dB - T_bot_dB)

idx_opt = int(np.argmin(IL_vs_L))

print("=== MMI length sweep ===")
print(f"  points            : {len(L_um)}")
print(f"  length range      : {L_um.min():.2f} - {L_um.max():.2f} um")
print(f"  best L (min IL)   : {L_um[idx_opt]:.2f} um")
print(f"  T_top at best L   : {T_top_vs_L[idx_opt]:.4f}  ({T_top_dB[idx_opt]:+.2f} dB)")
print(f"  T_bot at best L   : {T_bot_vs_L[idx_opt]:.4f}  ({T_bot_dB[idx_opt]:+.2f} dB)")
print(f"  IL  at best L     : {IL_vs_L[idx_opt]:.3f} dB "
      f"(target < {TARGET_IL_DB:.1f} dB -> "
      f"{'met' if IL_vs_L[idx_opt] < TARGET_IL_DB else 'not met'})")
print(f"  imbalance at best : {Imb_dB[idx_opt]:.3f} dB "
      f"(target < {TARGET_IMB_DB:.3f} dB -> "
      f"{'met' if Imb_dB[idx_opt] < TARGET_IMB_DB else 'not met'})")

print("\n   L (um)   T_top      T_bot      IL (dB)   Imb (dB)")
for i in range(len(L_um)):
    print(f"  {L_um[i]:6.2f}   {T_top_vs_L[i]:.4f}     {T_bot_vs_L[i]:.4f}     "
          f"{IL_vs_L[i]:6.3f}    {Imb_dB[i]:6.3f}")

# ---------------------------------------------------------------
# Insertion loss and the two port transmissions versus length
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(L_um, T_top_dB, 'o-', color='tab:blue', label='$T_{top}$ (port 2)')
ax.plot(L_um, T_bot_dB, '^-', color='tab:green', label='$T_{bot}$ (port 3)')
ax.plot(L_um, IL_vs_L, 'd-', color='tab:red', label='insertion loss')
ax.axvline(L_um[idx_opt], color='k', linestyle='--', alpha=0.6,
           label=f'min IL at {L_um[idx_opt]:.2f} $\\mu$m')
ax.axhline(TARGET_IL_DB, color='gray', linestyle=':', alpha=0.8,
           label=f'IL target ({TARGET_IL_DB:.1f} dB)')
ax.set_xlabel(r'MMI length [$\mu$m]')
ax.set_ylabel('dB')
ax.set_title('MMI insertion loss and split versus length')
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig("MMI/MODE/mmi_il_vs_length.png", dpi=300, bbox_inches="tight")

plt.show()
