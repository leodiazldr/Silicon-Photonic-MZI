# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 2026

@author: USUARIO
"""

"""
Transmission, insertion loss and splitting imbalance across the C-band, from the EME
wavelength sweep saved in 'wavelength_sweep.mat' by step11_wavelength_sweep.lsf.

The sweep is taken at the MMI length that minimised the insertion loss in step10, so
it is the broadband check: the 50:50 split and the low insertion loss are only useful
if they hold across the band, not just at 1550 nm.

Expected variables:
    - lam        : wavelength [m]
    - T2_vs_lam  : |s12|^2, transmission to the top output
    - T3_vs_lam  : |s13|^2, transmission to the bottom output
    - IL_vs_lam  : -10*log10(T_top + T_bot) [dB]
    - Imb_vs_lam : |10*log10(T_top / T_bot)| [dB]
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

TARGET_IL_DB  = 0.5     # MMI insertion-loss target
TARGET_IMB_DB = 0.087   # 50:50 +/- 1% expressed in dB
TARGET_BW_NM  = 40.0    # bandwidth over which both targets have to hold
LAMBDA0_NM    = 1550.0  # design wavelength

filename = "MMI/MODE/wavelength_sweep.mat"

with h5py.File(filename, "r") as f:
    lam        = np.ravel(np.array(f["lam"]))
    T2_vs_lam  = np.ravel(np.array(f["T2_vs_lam"]))
    T3_vs_lam  = np.ravel(np.array(f["T3_vs_lam"]))
    IL_vs_lam  = np.ravel(np.array(f["IL_vs_lam"]))
    Imb_vs_lam = np.ravel(np.array(f["Imb_vs_lam"]))

nm = 1e-9
lam_nm = lam / nm

T_top_dB = 10 * np.log10(np.maximum(T2_vs_lam, 1e-30))
T_bot_dB = 10 * np.log10(np.maximum(T3_vs_lam, 1e-30))

print("=== MMI wavelength sweep ===")
print(f"  points     : {len(lam_nm)}")
print(f"  range      : {lam_nm.min():.1f} - {lam_nm.max():.1f} nm")
print(f"  max IL     : {IL_vs_lam.max():.3f} dB "
      f"(target < {TARGET_IL_DB:.1f} dB -> "
      f"{'met' if IL_vs_lam.max() < TARGET_IL_DB else 'not met'})")
print(f"  max Imb    : {Imb_vs_lam.max():.3f} dB "
      f"(target < {TARGET_IMB_DB:.3f} dB -> "
      f"{'met' if Imb_vs_lam.max() < TARGET_IMB_DB else 'not met'})")

# Bandwidth is the contiguous band around the design wavelength over which BOTH
# targets hold. Taking the min/max of every passing point instead would overstate
# the result whenever the band is broken by a failing point.
ok = (IL_vs_lam < TARGET_IL_DB) & (Imb_vs_lam < TARGET_IMB_DB)
i0 = int(np.argmin(np.abs(lam_nm - LAMBDA0_NM)))

if ok[i0]:
    lo = i0
    while lo - 1 >= 0 and ok[lo - 1]:
        lo -= 1
    hi = i0
    while hi + 1 < len(ok) and ok[hi + 1]:
        hi += 1
    bw_nm = lam_nm[hi] - lam_nm[lo]
    print(f"  both targets met  : {lam_nm[lo]:.1f} - {lam_nm[hi]:.1f} nm "
          f"({bw_nm:.1f} nm, target > {TARGET_BW_NM:.0f} nm -> "
          f"{'met' if bw_nm > TARGET_BW_NM else 'not met'})")
else:
    print(f"  both targets met  : not at {LAMBDA0_NM:.0f} nm")

print("\n  lambda (nm)   T_top      T_bot      IL (dB)   Imb (dB)")
for l in np.arange(lam_nm.min(), lam_nm.max() + 1e-6, 10.0):
    i = int(np.argmin(np.abs(lam_nm - l)))
    print(f"  {lam_nm[i]:8.1f}   {T2_vs_lam[i]:.4f}     {T3_vs_lam[i]:.4f}     "
          f"{IL_vs_lam[i]:6.3f}    {Imb_vs_lam[i]:6.3f}")

# ---------------------------------------------------------------
# Transmission and insertion loss across the band
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(lam_nm, T_top_dB, '-', color='tab:blue', label='$T_{top}$ (port 2)')
ax.plot(lam_nm, T_bot_dB, '-', color='tab:green', label='$T_{bot}$ (port 3)')
ax.plot(lam_nm, IL_vs_lam, '-', color='tab:red', label='insertion loss')
ax.axhline(TARGET_IL_DB, color='gray', linestyle=':', alpha=0.8,
           label=f'IL target ({TARGET_IL_DB:.1f} dB)')
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('dB')
ax.set_title('MMI transmission and insertion loss across the C-band')
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig("MMI/MODE/mmi_transmission_vs_wavelength.png", dpi=300,
            bbox_inches="tight")

# ---------------------------------------------------------------
# Splitting imbalance across the band
# ---------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(7, 5))
ax2.plot(lam_nm, Imb_vs_lam, '-', color='tab:purple')
ax2.axhline(TARGET_IMB_DB, color='tab:red', linestyle=':', alpha=0.8,
            label=f'50:50 $\\pm$ 1 % ({TARGET_IMB_DB:.3f} dB)')
ax2.set_xlabel('Wavelength [nm]')
ax2.set_ylabel('Splitting imbalance [dB]')
ax2.set_title('MMI splitting imbalance across the C-band')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(fontsize=9)
fig2.tight_layout()
fig2.savefig("MMI/MODE/mmi_imbalance_vs_wavelength.png", dpi=300,
             bbox_inches="tight")

plt.show()
