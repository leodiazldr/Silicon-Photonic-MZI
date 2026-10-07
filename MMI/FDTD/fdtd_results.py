# -*- coding: utf-8 -*-
"""
Created on Tue Oct 6 2026

@author: USUARIO
"""

"""
3D FDTD validation of the 1x2 MMI, from the results saved by step05_save_results.lsf.

The port group excites the input port only, so the S-parameters are the column for input
excitation: S_src is the reflection, S_top and S_bot the two outputs. The power
transmission is |S|^2 and the insertion loss is -10*log10(T_top + T_bot), defined exactly
as in the EME post-processing in ../MODE/ so the two sets of figures can be read side by
side.

The last figure is the |E|^2 field profile of the 'monitor' object at the design
wavelength: it shows where the two-fold image forms inside the MMI body and how it feeds
the two output tapers.

Expected variables:
    - lambda   : wavelength [m]
    - S_src    : complex S-parameter at the input port (reflection)
    - S_top    : complex S-parameter at the top output
    - S_bot    : complex S-parameter at the bottom output
    - T_top    : |S_top|^2
    - T_bot    : |S_bot|^2
    - R        : |S_src|^2
    - IL       : -10*log10(T_top + T_bot) [dB]
    - imbalance: 10*log10(T_top) - 10*log10(T_bot) [dB]
    - mon_x    : monitor x axis [m]
    - mon_y    : monitor y axis [m]
    - mon_E2   : |E|^2 on the monitor plane, with a frequency axis
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

TARGET_IL_DB  = 0.5     # MMI insertion-loss target
TARGET_BW_NM  = 40.0    # bandwidth over which both targets have to hold
LAMBDA0_NM    = 1550.0  # design wavelength

filename = "MMI/FDTD/mmi_fdtd_results.mat"


def read_vector(f, key):
    """Read a root dataset as a flat real array."""
    return np.ravel(np.array(f[key]))


def read_complex(f, key):
    """MATLAB v7.3 stores complex arrays as a compound real/imag datatype."""
    arr = np.array(f[key])
    if arr.dtype.names and "real" in arr.dtype.names and "imag" in arr.dtype.names:
        arr = arr["real"] + 1j * arr["imag"]
    return np.ravel(arr)


with h5py.File(filename, "r") as f:
    lam      = read_vector(f, "lambda")
    S_src    = read_complex(f, "S_src")
    S_top    = read_complex(f, "S_top")
    S_bot    = read_complex(f, "S_bot")
    T_top    = read_vector(f, "T_top")
    T_bot    = read_vector(f, "T_bot")
    R        = read_vector(f, "R")
    IL       = read_vector(f, "IL")
    Imb_dB   = np.abs(read_vector(f, "imbalance"))
    mon_x    = read_vector(f, "mon_x")
    mon_y    = read_vector(f, "mon_y")
    mon_E2   = np.array(f["mon_E2"])

nm = 1e-9
um = 1e-6
lam_nm = lam / nm

# a floor keeps a nulled port from producing -inf
T_top_dB = 10 * np.log10(np.maximum(T_top, 1e-30))
T_bot_dB = 10 * np.log10(np.maximum(T_bot, 1e-30))
R_dB     = 10 * np.log10(np.maximum(R, 1e-30))

print("=== MMI 3D FDTD validation ===")
print(f"  points     : {len(lam_nm)}")
print(f"  range      : {lam_nm.min():.1f} - {lam_nm.max():.1f} nm")
print(f"  max IL     : {IL.max():.3f} dB "
      f"(target < {TARGET_IL_DB:.1f} dB -> "
      f"{'met' if IL.max() < TARGET_IL_DB else 'not met'})")
print(f"  max R      : {R.max():.4f}  ({R_dB.max():.1f} dB)")

# Bandwidth is the contiguous band around the design wavelength over which BOTH targets
# hold. Taking the min/max of every passing point instead would overstate the result
# whenever the band is broken by a failing point.
i0 = int(np.argmin(np.abs(lam_nm - LAMBDA0_NM)))

print("\n  lambda (nm)   T_top      T_bot      R          IL (dB)   Imb (dB)")
for l in np.arange(lam_nm.min(), lam_nm.max() + 1e-6, 10.0):
    i = int(np.argmin(np.abs(lam_nm - l)))
    print(f"  {lam_nm[i]:8.1f}   {T_top[i]:.4f}     {T_bot[i]:.4f}     "
          f"{R[i]:.4f}     {IL[i]:6.3f}    {Imb_dB[i]:6.3f}")

# ---------------------------------------------------------------
# Transmission, reflection and insertion loss across the band
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(lam_nm, T_top_dB, '-', color='tab:blue', label='$|S|^2_{12}$')
ax.plot(lam_nm, T_bot_dB, '-', color='tab:green', label='$|S|^2_{13}$')
ax.plot(lam_nm, R_dB, '-', color='tab:orange', label='$|S|^2_{11}$ (reflection)')
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('dB')
ax.set_title('MMI 3D FDTD $|S|^2$-parameters')
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig("MMI/FDTD/mmi_fdtd_S2-params.png", dpi=300,
            bbox_inches="tight")

# ---------------------------------------------------------------
# Transmission and insertion loss across the band
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(lam_nm, T_top_dB, '-', color='tab:blue', label='$|S|^2_{12}$')
ax.plot(lam_nm, T_bot_dB, '-', color='tab:green', label='$|S|^2_{13}$')
ax.plot(lam_nm, IL, '-', color='tab:red', label='insertion loss')
ax.axhline(TARGET_IL_DB, color='gray', linestyle=':', alpha=0.8,
           label=f'IL target ({TARGET_IL_DB:.1f} dB)')
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('dB')
ax.set_title('MMI 3D FDTD transmission and insertion loss')
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig("MMI/FDTD/mmi_fdtd_transmission_vs_wavelength.png", dpi=300,
            bbox_inches="tight")

# ---------------------------------------------------------------
# |E|^2 field profile at the design wavelength
# ---------------------------------------------------------------
# The monitor records at every frequency, so mon_E2 carries a frequency axis. Its
# position is not fixed in the Lumerical dataset, so find the axis whose length matches
# the sweep and slice it at the design wavelength rather than assuming an order.
E2 = np.abs(mon_E2)
i0 = int(np.argmin(np.abs(lam_nm - LAMBDA0_NM)))
freq_axes = [k for k, size in enumerate(E2.shape) if size == len(lam_nm)]
if freq_axes:
    E2 = np.take(E2, i0, axis=freq_axes[0])
E2 = np.squeeze(E2)

if E2.ndim == 2:
    # orient so the array is indexed [y, x] for pcolormesh
    if E2.shape[0] == len(mon_x) and E2.shape[1] == len(mon_y):
        E2 = E2.T
    elif E2.shape[0] != len(mon_y) or E2.shape[1] != len(mon_x):
        print(f"\n  note: monitor array {E2.shape} does not match "
              f"x/y lengths {len(mon_x)}/{len(mon_y)}; plotting as-is")

    E2_norm = E2 / E2.max()

    fig3, ax3 = plt.subplots(figsize=(9, 4))
    mesh = ax3.pcolormesh(mon_x / um, mon_y / um, E2_norm, cmap="inferno",
                          shading="auto")
    fig3.colorbar(mesh, ax=ax3, label='$|E|^2$ (normalised)')
    ax3.set_xlabel(r'x [$\mu$m]')
    ax3.set_ylabel(r'y [$\mu$m]')
    ax3.set_title(f'$|E|^2$ at {lam_nm[i0]:.0f} nm')
    ax3.set_aspect('equal')
    fig3.tight_layout()
    fig3.savefig("MMI/FDTD/mmi_fdtd_field_profile.png", dpi=300,
                 bbox_inches="tight")
else:
    print(f"\n  note: |E|^2 profile is {E2.ndim}-dimensional after removing the "
          f"frequency axis; skipping the field figure")

plt.show()
