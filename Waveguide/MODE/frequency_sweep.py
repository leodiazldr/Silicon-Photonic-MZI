# -*- coding: utf-8 -*-
"""
Created on Fri May  1 19:48:15 2026

@author: USUARIO
"""

"""
Plot effective index (neff) and group index (ng) vs wavelength
from the Lumerical FDE frequency sweep saved in 'frequency_sweep_si.mat'.

The .mat file is saved by Lumerical in HDF5 format, so we use h5py.
Polynomial fits (linear and quadratic) are also computed and plotted.
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Load .mat file (HDF5 format)
# ---------------------------------------------------------------
filename = "Waveguide/MODE/frequency_sweep_si.mat"

with h5py.File(filename, "r") as f:
    # Lumerical stores complex arrays as compound datasets with 'real' and 'imag'
    def read_complex(dset):
        arr = dset[()]
        if arr.dtype.names and 'real' in arr.dtype.names:
            return arr['real'] + 1j * arr['imag']
        return arr

    neff   = np.squeeze(read_complex(f['neff']))
    lambda_ = np.squeeze(read_complex(f['lambda']))
    ng     = np.squeeze(read_complex(f['ng']))
    lambda_vg = np.squeeze(read_complex(f['lambda_vg']))
#    D = np.squeeze(read_complex(f['D']))
#    lambda_D = np.squeeze(read_complex(f['lambda_D']))

# Take real parts and convert to micrometers
neff = np.real(neff)
ng = np.real(ng)
#D = np.real(D) * 1e6 # (ps/km/nm)
lambda_um = np.real(lambda_) * 1e6
lambda_vg_um = np.real(lambda_vg) * 1e6
#lambda_D_um = np.real(lambda_D) * 1e6

# Sort by wavelength (Lumerical stores by frequency, so order may be reversed)
idx = np.argsort(lambda_um)
lambda_um = lambda_um[idx] - 1.55
neff = neff[idx]

idx2 = np.argsort(lambda_vg_um)
lambda_vg_um = lambda_vg_um[idx2] - 1.55
ng = ng[idx2]

#idx3 = np.argsort(lambda_D_um)
#lambda_D_um = lambda_D_um[idx3]
#D = D[idx3]

# ---------------------------------------------------------------
# Polynomial fits
# ---------------------------------------------------------------
# neff fits
p1_neff = np.polyfit(lambda_um, neff, 1)
p2_neff = np.polyfit(lambda_um, neff, 2)

lam_fit = np.linspace(lambda_um.min(), lambda_um.max(), 200)
neff_lin  = np.polyval(p1_neff, lam_fit)
neff_quad = np.polyval(p2_neff, lam_fit)

# ng fits
p1_ng = np.polyfit(lambda_vg_um, ng, 1)
p2_ng = np.polyfit(lambda_vg_um, ng, 2)

lam_fit_ng = np.linspace(lambda_vg_um.min(), lambda_vg_um.max(), 200)
ng_lin  = np.polyval(p1_ng, lam_fit_ng)
ng_quad = np.polyval(p2_ng, lam_fit_ng)

print("=== Effective index fits ===")
print(f"Linear:    neff = {p1_neff[0]:.6f}*lam + {p1_neff[1]:.6f}")
print(f"Quadratic: neff = {p2_neff[0]:.6f}*lam^2 + {p2_neff[1]:.6f}*lam^1 + {p2_neff[2]:.6f}")

print("\n=== Group index fits ===")
print(f"Linear:    ng = {p1_ng[0]:.6f}*lam + {p1_ng[1]:.6f}")
print(f"Quadratic: ng = {p2_ng[0]:.6f}*lam^2 + {p2_ng[1]:.6f}*lam^1 + {p2_ng[2]:.6f}")

# ---------------------------------------------------------------
# Plot effective index
# ---------------------------------------------------------------
plt.figure(figsize=(7, 5))
plt.plot(lambda_um, neff, 'o', label='FDE data', markersize=6)
plt.plot(lam_fit, neff_lin,  '--', label='Linear fit')
plt.plot(lam_fit, neff_quad, '-',  label='Quadratic fit')
plt.xlabel('Wavelength (µm)')
plt.ylabel('Effective index $n_\\mathrm{eff}$')
plt.title('Effective index vs wavelength ($Si$ 500x220 nm)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("Waveguide/MODE/waveguide_neff_vs_wavelength.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot group index
# ---------------------------------------------------------------
plt.figure(figsize=(7, 5))
plt.plot(lambda_vg_um, ng, 'o', color='C3', label='FDE data', markersize=6)
plt.plot(lam_fit_ng, ng_lin,  '--', label='Linear fit')
plt.plot(lam_fit_ng, ng_quad, '-',  label='Quadratic fit')
plt.xlabel('Wavelength (µm)')
plt.ylabel('Group index $n_g$')
plt.title('Group index vs wavelength ($Si$ 500x220 nm)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("Waveguide/MODE/waveguide_ng_vs_wavelength.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot dispersion
# ---------------------------------------------------------------
#plt.figure(figsize=(7, 5))
#plt.plot(lambda_D_um, D, 'o', color='C3', label='FDE data', markersize=6)
#plt.xlabel('Wavelength (µm)')
#plt.ylabel('Dispersion parameter D (ps/km/nm)')
#plt.title('Dispersion parameter vs wavelength ($Si_3N_4$ 1000x400 nm)')
#plt.legend()
#plt.grid(True)
#plt.tight_layout()

plt.show()
