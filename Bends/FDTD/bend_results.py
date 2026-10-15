# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 2026

@author: USUARIO
"""

"""
3D FDTD characterisation of the Bezier S-bend, from the results saved by
step05_save_results.lsf.

The port group excites the input port only, so the S-parameters are the column for input
excitation: S_in is the reflection and S_out the transmission. The bend is reciprocal, so
that column describes the device in both directions, and the phase of S_out is what the
MZI model needs to line the bend up against a waveguide of the same length.

The power transmission is |S_out|^2 and the insertion loss is -10*log10(T).

Expected variables:
    - lambda : wavelength [m]
    - S_in   : complex S-parameter at the input port (reflection)
    - S_out  : complex S-parameter at the output port (transmission)
    - T      : |S_out|^2
    - R      : |S_in|^2
    - IL     : -10*log10(T) [dB]
    - mon_x  : monitor x axis [m]
    - mon_y  : monitor y axis [m]
    - mon_E2 : |E|^2 on the monitor plane
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

LAMBDA0_NM = 1550.0  # design wavelength

filename = "Bends/FDTD/bend_fdtd_results_MeshAcc2.mat"


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
    lam    = read_vector(f, "lambda")
    S_in   = read_complex(f, "S_in")
    S_out  = read_complex(f, "S_out")
    T      = read_vector(f, "T")
    R      = read_vector(f, "R")
    IL     = read_vector(f, "IL")
    mon_x  = read_vector(f, "mon_x")
    mon_y  = read_vector(f, "mon_y")
    mon_E2 = np.array(f["mon_E2"])

nm = 1e-9
um = 1e-6
lam_nm = lam / nm

# a floor keeps a nulled port from producing -inf
T_dB = 10 * np.log10(np.maximum(T, 1e-30))
R_dB = 10 * np.log10(np.maximum(R, 1e-30))

i0 = int(np.argmin(np.abs(lam_nm - LAMBDA0_NM)))

print("=== Bezier S-bend, 3D FDTD ===")
print(f"  points      : {len(lam_nm)}")
print(f"  range       : {lam_nm.min():.1f} - {lam_nm.max():.1f} nm")
print(f"  IL at 1550  : {IL[i0]:.4f} dB")
print(f"  IL worst    : {IL.max():.4f} dB  (at {lam_nm[IL.argmax()]:.1f} nm)")
print(f"  min T       : {T.min():.4f}")
print(f"  max R       : {R.max():.6f}  ({R_dB.max():.1f} dB)")
print(f"  phase S_out : {np.angle(S_out[i0]):.4f} rad at 1550 nm")

print("\n  lambda (nm)      T          R          IL (dB)")
for l in np.arange(lam_nm.min(), lam_nm.max() + 1e-6, 10.0):
    i = int(np.argmin(np.abs(lam_nm - l)))
    print(f"  {lam_nm[i]:8.1f}   {T[i]:.4f}     {R[i]:.6f}   {IL[i]:6.4f}")

# ---------------------------------------------------------------
# Transmission and reflection across the band
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(lam_nm, T_dB, '-', color='tab:blue', label='$|S_{21}|^2$ (transmission)')
ax.plot(lam_nm, R_dB, '-', color='tab:orange', label='$|S_{11}|^2$ (reflection)')
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('dB')
ax.set_title('S-bend 3D FDTD $|S|^2$-parameters')
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig("Bends/FDTD/bend_S2-params.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# |E|^2 field profile at the design wavelength
# ---------------------------------------------------------------
# The monitor runs at a single frequency, so mon_E2 is already one plane; the squeeze
# keeps the code correct if the global monitor frequency count is raised later.
E2 = np.squeeze(np.abs(mon_E2))

if E2.ndim == 2:
    # orient so the array is indexed [y, x] for pcolormesh
    if E2.shape[0] == len(mon_x) and E2.shape[1] == len(mon_y):
        E2 = E2.T
    elif E2.shape[0] != len(mon_y) or E2.shape[1] != len(mon_x):
        print(f"\n  note: monitor array {E2.shape} does not match "
              f"x/y lengths {len(mon_x)}/{len(mon_y)}; plotting as-is")

    E2_norm = E2 / E2.max()

    fig2, ax2 = plt.subplots(figsize=(9, 4))
    mesh = ax2.pcolormesh(mon_x / um, mon_y / um, E2_norm, cmap="inferno",
                          shading="auto")
    fig2.colorbar(mesh, ax=ax2, label='$|E|^2$ (normalised)')
    ax2.set_xlabel(r'x [$\mu$m]')
    ax2.set_ylabel(r'y [$\mu$m]')
    ax2.set_title(f'$|E|^2$ at {lam_nm[i0]:.0f} nm')
    ax2.set_aspect('equal')
    fig2.tight_layout()
    fig2.savefig("Bends/FDTD/bend_field_profile.png", dpi=300,
                 bbox_inches="tight")
else:
    print(f"\n  note: |E|^2 profile is {E2.ndim}-dimensional; skipping the field figure")

plt.show()
