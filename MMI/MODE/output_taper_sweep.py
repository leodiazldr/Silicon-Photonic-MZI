# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 2026

@author: USUARIO
"""

"""
Insertion loss and splitting versus the output taper width, from the sweep saved in
'output_taper_width_sweep.mat' by step12_output_taper_sweep.lsf.

The output tapers open from the output waveguides (0.5 um) to a width at the MMI face,
and the width they reach there sets how well they pick up the two-fold image. The sweep
is +/-20% about the as-built value, which step02 ties to the body as W_MMI/4.

Both tapers are widened by the same amount, so the device stays mirror-symmetric and the
two output powers are equal by construction: the split column is a port-setup check, not
a design property, and the sweep's real objective is total transmission.

Expected variables:
    - output_width_sweep_vec : taper width at the MMI face [m]
    - T_top_vs_out_width     : |s12|^2, transmission to the top output
    - T_bot_vs_out_width     : |s13|^2, transmission to the bottom output
    - IL_vs_out_width        : -10*log10(T_top + T_bot) [dB]
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

TARGET_IL_DB  = 0.5    # MMI insertion-loss target
TARGET_IMB_DB = 0.087  # 50:50 +/- 1% expressed in dB: |10*log10(1.01/0.99)|

filename = "MMI/MODE/output_taper_width_sweep.mat"

with h5py.File(filename, "r") as f:
    # ravel() is order-agnostic, so it works whether Lumerical stored these as
    # rows or as columns
    output_width_sweep_vec = np.ravel(np.array(f["output_width_sweep_vec"]))
    T_top_vs_out_width     = np.ravel(np.array(f["T_top_vs_out_width"]))
    T_bot_vs_out_width     = np.ravel(np.array(f["T_bot_vs_out_width"]))
    IL_vs_out_width        = np.ravel(np.array(f["IL_vs_out_width"]))

um = 1e-6
width_um = output_width_sweep_vec / um

# step12 builds the sweep symmetrically about the as-built width, so the sweep
# centre is that value
width_asbuilt = 0.5 * (width_um.min() + width_um.max())

# transmittances in dB, with a floor so a nulled port cannot produce -inf
T_top_dB = 10 * np.log10(np.maximum(T_top_vs_out_width, 1e-30))
T_bot_dB = 10 * np.log10(np.maximum(T_bot_vs_out_width, 1e-30))
Imb_dB   = np.abs(T_top_dB - T_bot_dB)

idx_opt     = int(np.argmin(IL_vs_out_width))
idx_asbuilt = int(np.argmin(np.abs(width_um - width_asbuilt)))

print("=== MMI output taper width sweep ===")
print(f"  points             : {len(width_um)}")
print(f"  width range        : {width_um.min():.4f} - {width_um.max():.4f} um")
print(f"  as-built width     : {width_asbuilt:.4f} um (sweep centre, W_MMI/4)")
print(f"  best width (min IL): {width_um[idx_opt]:.4f} um")
print(f"  T_top at best      : {T_top_vs_out_width[idx_opt]:.4f}  ({T_top_dB[idx_opt]:+.2f} dB)")
print(f"  T_bot at best      : {T_bot_vs_out_width[idx_opt]:.4f}  ({T_bot_dB[idx_opt]:+.2f} dB)")
print(f"  IL at best         : {IL_vs_out_width[idx_opt]:.3f} dB "
      f"(target < {TARGET_IL_DB:.1f} dB -> "
      f"{'met' if IL_vs_out_width[idx_opt] < TARGET_IL_DB else 'not met'})")
print(f"  imbalance at best  : {Imb_dB[idx_opt]:.3f} dB "
      f"(target < {TARGET_IMB_DB:.3f} dB -> "
      f"{'met' if Imb_dB[idx_opt] < TARGET_IMB_DB else 'not met'})")
print(f"  gain over as-built : {IL_vs_out_width[idx_asbuilt] - IL_vs_out_width[idx_opt]:+.4f} dB "
      f"({IL_vs_out_width[idx_asbuilt]:.4f} -> {IL_vs_out_width[idx_opt]:.4f} dB)")

print("\n   width (um)   T_top      T_bot      IL (dB)   Imb (dB)")
for i in range(len(width_um)):
    print(f"  {width_um[i]:8.4f}   {T_top_vs_out_width[i]:.4f}     {T_bot_vs_out_width[i]:.4f}     "
          f"{IL_vs_out_width[i]:6.3f}    {Imb_dB[i]:6.3f}")

# ---------------------------------------------------------------
# Insertion loss and the two port transmissions versus taper width
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(width_um, T_top_dB, 'o-', color='tab:blue', label='$T_{top}$ (port 2)')
ax.plot(width_um, T_bot_dB, '^-', color='tab:green', label='$T_{bot}$ (port 3)')
ax.plot(width_um, IL_vs_out_width, 'd-', color='tab:red', label='insertion loss')
ax.axvline(width_asbuilt, color='gray', linestyle=':', alpha=0.8,
           label=f'as-built $W_{{MMI}}/4$ ({width_asbuilt:.4f} $\\mu$m)')
ax.axvline(width_um[idx_opt], color='k', linestyle='--', alpha=0.6,
           label=f'min IL at {width_um[idx_opt]:.4f} $\\mu$m')
ax.axhline(TARGET_IL_DB, color='gray', linestyle='--', linewidth=0.8, alpha=0.6,
           label=f'IL target ({TARGET_IL_DB:.1f} dB)')
ax.set_xlabel(r'Output taper width at the MMI face [$\mu$m]')
ax.set_ylabel('dB')
ax.set_title('MMI insertion loss and split versus output taper width')
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig("MMI/MODE/mmi_il_vs_out_width.png", dpi=300, bbox_inches="tight")

plt.show()
