# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 2026

@author: USUARIO
"""

"""
Insertion loss and splitting imbalance versus the output-port offset d_y, from the
sweep saved in 'dy_sweep.mat' by step12_dy_sweep.lsf.

d_y moves the two output waveguides and their ports, so unlike the length sweep each
point is a full geometry rebuild and a fresh EME run. The analytical starting point is
d_y = W_e/4, which is where the slab formula puts the two-fold image; this sweep is
the check that the image really sits there, and the sweep in step12 is built
symmetrically about that value.

Expected variables:
    - dy_sweep_vec : output offset [m]
    - T_top_vs_dy  : |s12|^2, transmission to the top output
    - T_bot_vs_dy  : |s13|^2, transmission to the bottom output
    - IL_vs_dy     : -10*log10(T_top + T_bot) [dB]
    - Imb_vs_dy    : |10*log10(T_top / T_bot)| [dB]
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

TARGET_IL_DB  = 0.5    # MMI insertion-loss target
TARGET_IMB_DB = 0.087  # 50:50 +/- 1% expressed in dB

filename = "MMI/MODE/dy_sweep.mat"

with h5py.File(filename, "r") as f:
    dy_sweep_vec = np.ravel(np.array(f["dy_sweep_vec"]))
    T_top_vs_dy  = np.ravel(np.array(f["T_top_vs_dy"]))
    T_bot_vs_dy  = np.ravel(np.array(f["T_bot_vs_dy"]))
    IL_vs_dy     = np.ravel(np.array(f["IL_vs_dy"]))
    Imb_vs_dy    = np.ravel(np.array(f["Imb_vs_dy"]))

um = 1e-6
dy_um = dy_sweep_vec / um

# step12 builds the sweep symmetrically about the analytical offset
dy_center = 0.5 * (dy_um.min() + dy_um.max())

idx_opt = int(np.argmin(IL_vs_dy))

print("=== MMI output-offset (d_y) sweep ===")
print(f"  points            : {len(dy_um)}")
print(f"  d_y range         : {dy_um.min():.3f} - {dy_um.max():.3f} um")
print(f"  analytical d_y    : {dy_center:.3f} um (sweep centre)")
print(f"  best d_y (min IL) : {dy_um[idx_opt]:.3f} um")
print(f"  T_top at best d_y : {T_top_vs_dy[idx_opt]:.4f}")
print(f"  T_bot at best d_y : {T_bot_vs_dy[idx_opt]:.4f}")
print(f"  IL  at best d_y   : {IL_vs_dy[idx_opt]:.3f} dB "
      f"(target < {TARGET_IL_DB:.1f} dB -> "
      f"{'met' if IL_vs_dy[idx_opt] < TARGET_IL_DB else 'not met'})")
print(f"  Imb at best d_y   : {Imb_vs_dy[idx_opt]:.3f} dB "
      f"(target < {TARGET_IMB_DB:.3f} dB -> "
      f"{'met' if Imb_vs_dy[idx_opt] < TARGET_IMB_DB else 'not met'})")
print(f"  shift from centre : {(dy_um[idx_opt] - dy_center) * 1000:+.0f} nm")

print("\n   d_y (um)   T_top      T_bot      IL (dB)   Imb (dB)")
for i in range(len(dy_um)):
    print(f"  {dy_um[i]:7.3f}   {T_top_vs_dy[i]:.4f}     {T_bot_vs_dy[i]:.4f}     "
          f"{IL_vs_dy[i]:6.3f}    {Imb_vs_dy[i]:6.3f}")

# ---------------------------------------------------------------
# Insertion loss and imbalance versus offset, on twin axes
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(dy_um, IL_vs_dy, 'd-', color='tab:red', label='insertion loss')
ax.axvline(dy_center, color='gray', linestyle=':', alpha=0.8,
           label=f'analytical $W_e/4$ ({dy_center:.3f} $\\mu$m)')
ax.axvline(dy_um[idx_opt], color='k', linestyle='--', alpha=0.6,
           label=f'min IL at {dy_um[idx_opt]:.3f} $\\mu$m')
ax.set_xlabel(r'Output offset $d_y$ [$\mu$m]')
ax.set_ylabel('Insertion loss [dB]')
ax.grid(True, linestyle=':', alpha=0.6)

# one legend for both axes
handles = ax.get_legend_handles_labels()[0]
labels  = ax.get_legend_handles_labels()[1]
ax.legend(handles, labels, fontsize=9, loc='upper center')

ax.set_title(r'MMI insertion loss and balance versus output offset $d_y$')
fig.tight_layout()
fig.savefig("MMI/MODE/mmi_il_vs_dy.png", dpi=300, bbox_inches="tight")

plt.show()
