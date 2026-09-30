# -*- coding: utf-8 -*-
"""
Created on Fri May  1 11:51:10 2026

@author: USUARIO
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

# ---- Load data using h5py (MATLAB v7.3 / HDF5 format) ----
filename = "Waveguide/MODE/wg_width_sweep.mat"

with h5py.File(filename, "r") as f:
    # h5py loads arrays transposed relative to MATLAB convention -> transpose back
    wg_width_sweep = np.array(f["wg_width_sweep"]).squeeze()  # in meters
    neff           = np.array(f["neff"]).T                    # -> (N, n_modes)
    ng             = np.array(f["ng"]).T                      # -> (N, n_modes)
    te_fraction    = np.array(f["te_fraction"]).T             # -> (N, n_modes)

# Lumerical may store neff/ng as complex (compound dtype with 'real'/'imag' fields)
def to_complex(arr):
    if arr.dtype.names is not None and 'real' in arr.dtype.names:
        return arr['real'] + 1j * arr['imag']
    return arr

neff        = to_complex(neff)
ng          = to_complex(ng)
te_fraction = to_complex(te_fraction)

# Take real magnitude for plotting (guided modes are essentially real)
neff_real        = np.real(neff) if np.iscomplexobj(neff) else neff
te_fraction_real = np.real(te_fraction) if np.iscomplexobj(te_fraction) else te_fraction

nm = 1e-9
widths_nm = wg_width_sweep / nm
N, n_modes = neff_real.shape

print(f"Loaded data: {N} widths × {n_modes} modes")
print(f"Width range: {widths_nm.min():.0f} – {widths_nm.max():.0f} nm")

# ---- Mask entries where no mode was found (neff ≈ 0) ----
mask = np.abs(neff_real) > 1e-3
neff_plot = np.where(mask, np.abs(neff_real), np.nan)
te_frac   = np.where(mask, te_fraction_real, np.nan)

# =================================================================
# Plot — Continuous colormap encoding TE fraction
# =================================================================

n_clad = 1.444

# ---- Detect single-mode region from the data ----
# Count the number of guided modes (neff > n_clad) for each width
guided = (neff_plot > n_clad)              # boolean (N, n_modes)
n_guided = np.nansum(guided, axis=1)       # number of guided modes per width

single_mode_mask = (n_guided == 2)
sm_widths = widths_nm[single_mode_mask]

print("Number of guided modes per width:")
for w, ng_count in zip(widths_nm, n_guided):
    print(f"  w = {w:5.0f} nm  ->  {ng_count} guided mode(s)")

fig, ax = plt.subplots(figsize=(8, 6))

ax.axhline(n_clad, color='gray', ls='--', lw=1,
           label=f'SiO$_2$ index ({n_clad})')

# ---- Yellow shaded single-mode region ----
if sm_widths.size > 0:
    # Extend the band by half a step on each side so it's visually clear
    if len(widths_nm) > 1:
        dw = widths_nm[1] - widths_nm[0]
    else:
        dw = 0
    w_min = sm_widths.min() - dw / 2
    w_max = sm_widths.max() + dw / 2
    ax.axvspan(w_min, w_max, color='gold', alpha=0.25,
                label='Single-mode region', zorder=-1)

# Connecting lines (gray) so the eye can follow each mode
for m in range(n_modes):
    ax.plot(widths_nm, neff_plot[:, m], color='lightgray', lw=0.7, zorder=0)

te_done = tm_done = hyb_done = False
TE0 = []
widths_TE0_nm = []
for m in range(n_modes):
    for i in range(N):
        y = neff_plot[i, m]
        if np.isnan(y):
            continue
        tf = te_frac[i, m]
        if tf > 0.5:
            if m == 0:
                TE0.append(y)
                widths_TE0_nm.append(widths_nm[i])
            ax.plot(widths_nm[i], y, 'o', color='tab:red',
                     label='TE' if not te_done else "")
            te_done = True
        elif tf < 0.5:
            ax.plot(widths_nm[i], y, 's', color='tab:blue',
                     label='TM' if not tm_done else "")
            tm_done = True
        else:
            ax.plot(widths_nm[i], y, '^', color='tab:green',
                     label='Hybrid' if not hyb_done else "")
            hyb_done = True

ax.set_xlabel('Waveguide width (nm)')
ax.set_ylabel('Effective index $n_\\mathrm{eff}$')
ax.set_title('TE vs TM mode classification ($Si$)')
ax.set_ylim(1.4, 3.5)
#ax.set_xlim(0, 3000)
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig("Waveguide/MODE/waveguide_modes_vs_width.png", dpi=300, bbox_inches="tight")
plt.show()
