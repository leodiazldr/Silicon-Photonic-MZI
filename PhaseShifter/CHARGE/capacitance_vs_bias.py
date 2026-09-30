# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 2026

@author: USUARIO
"""

"""
Junction capacitance, resistance and RC bandwidth from the Lumerical CHARGE
small-signal AC sweep saved in 'ac_sweep.mat'.

The .mat file is saved by Lumerical in HDF5 format (MATLAB v7.3), so h5py is
the reader. The AC result is a group holding the small-signal current dI, the
small-signal voltage dV_anode, the frequency vector f and the DC bias vector
V_anode.

From the admittance Y = dI/dV_anode:
    C = Im(Y) / (2*pi*f)      junction capacitance
    R = 1 / Re(Y)             small-signal resistance seen at the anode

UNITS: CHARGE's 2D solver reports extensive quantities per unit length along the
uniform z direction, so C below is a capacitance per unit length (F/m) and R is
an ohms-metre (ohm*m). Both are converted for display: C in fF/um (numerically
the same as pF/mm).

CAVEAT ON f_3dB: in reverse bias the junction conducts almost nothing, so at low
frequency 1/Re(Y) is the junction's shunt resistance, which is enormous and has
nothing to do with the modulation bandwidth. The series resistance that actually
sets the RC limit only shows up in the high-frequency asymptote of the
admittance. The bandwidth printed at the end is therefore computed from
C at the low-frequency plateau and R at the highest frequency. Treat it as an
order-of-magnitude estimate, not a substitute for a dedicated RF extraction.
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# Load .mat file (HDF5 format)
# ---------------------------------------------------------------
filename = "PhaseShifter/CHARGE/ac_sweep.mat"


def read_complex(dset):
    """Lumerical stores complex arrays as compound datasets with real/imag."""
    arr = dset[()]
    if arr.dtype.names and 'real' in arr.dtype.names:
        return arr['real'] + 1j * arr['imag']
    return arr


def find_dataset(h5file, *names):
    """
    Locate a dataset anywhere in the file by basename.

    Lumerical nests the AC result inside a group whose name comes from the
    contact, and that group name is not worth hard-coding: a recursive search
    finds 'dI' wherever it sits and stays correct if the result is renamed.
    """
    hits = []

    def collect(path, obj):
        if isinstance(obj, h5py.Dataset) and path.split("/")[-1] in names:
            hits.append(path)

    h5file.visititems(collect)
    if not hits:
        raise KeyError(
            f"None of {names} found in {filename}. "
            f"Contents: {list(h5file.keys())}"
        )
    # Prefer the shortest path (shallowest in the tree) if there are several.
    return sorted(hits, key=len)[0]


with h5py.File(filename, "r") as f:
    # Uncomment to inspect the structure of the file:
    # f.visititems(lambda p, o: print(p, o))

    dI  = np.squeeze(read_complex(f[find_dataset(f, "dI")]))
    dV  = np.squeeze(read_complex(f[find_dataset(f, "dV_anode", "dV")]))
    fq  = np.squeeze(np.array(f[find_dataset(f, "f")], dtype=float))
    Vdc = np.squeeze(np.array(f[find_dataset(f, "V_anode", "V")], dtype=float))

dV = np.asarray(dV, dtype=complex)

# ---------------------------------------------------------------
# Put the arrays in a known orientation: (n_bias, n_frequency)
# ---------------------------------------------------------------
if dI.ndim == 1:
    # A single bias point was swept: one row.
    dI = dI[np.newaxis, :]
elif dI.ndim == 2 and dI.shape[0] != Vdc.size and dI.shape[1] == Vdc.size:
    dI = dI.T

if dV.ndim == 1:
    dV = dV[:, np.newaxis]

n_bias, n_freq = dI.shape
assert n_freq == fq.size, (
    f"dI has {n_freq} frequency points but f has {fq.size}"
)
print(f"AC data: {n_bias} bias points x {n_freq} frequencies")
print(f"Bias range: {Vdc.min():.2f} to {Vdc.max():.2f} V")
print(f"Frequency range: {fq.min():.3e} to {fq.max():.3e} Hz")

# ---------------------------------------------------------------
# Admittance split
# ---------------------------------------------------------------
with np.errstate(divide="ignore", invalid="ignore"):
    Y = dI / dV

C = np.imag(Y) / (2 * np.pi * fq[np.newaxis, :])     # F/m
R = 1.0 / np.real(Y)                                  # ohm*m

# Quasi-static capacitance: the low-frequency plateau. Taking the median over the
# lowest decade keeps one noisy point from setting the value.
low_decade = fq <= fq.min() * 10.0
C_low = np.median(C[:, low_decade], axis=1)
C_fF_per_um = C_low * 1e9        # 1 F/m = 1e9 fF/um

print("\n=== Junction capacitance ===")
for v, c in zip(Vdc, C_fF_per_um):
    print(f"  V = {v:+.2f} V   C = {c:.3f} fF/um")

i_zero = int(np.argmin(np.abs(Vdc)))
i_max = int(np.argmax(np.abs(Vdc)))
print(f"\n  C at {Vdc[i_zero]:+.2f} V (nearly unbiased): {C_fF_per_um[i_zero]:.3f} fF/um")
print(f"  C at {Vdc[i_max]:+.2f} V (deepest reverse): {C_fF_per_um[i_max]:.3f} fF/um")
print(f"  ratio C(0 V)/C(V_max): {C_fF_per_um[i_zero] / C_fF_per_um[i_max]:.2f}")

# ---------------------------------------------------------------
# Series resistance and RC bandwidth
# ---------------------------------------------------------------
# 1/Re(Y) is NOT the resistance that sets the modulation speed at low frequency:
# in reverse bias the junction conducts almost nothing, so Re(Y) there is the
# junction's shunt conductance and the resistance is enormous. The series
# resistance of the doped regions appears in the high-frequency asymptote
# instead. For a junction Y_j = G_j + j*w*C_j in series with R_s, the admittance
# seen at the contact is Y_j/(1 + R_s*Y_j), which tends to 1/R_s as w grows.
R_at_max_f = 1.0 / np.real(Y[:, -1])
R_prev = 1.0 / np.real(Y[:, -2])

# Sanity check that the sweep actually reached that plateau. If the last two
# frequency points still disagree, f_max is below the RC cutoff and the
# resistance below is not yet the series resistance - extend the sweep.
flat = np.abs(R_at_max_f / R_prev - 1.0) < 0.05
if not np.all(flat):
    bad = np.where(~flat)[0]
    print(f"\n  WARNING: 1/Re(Y) has not flattened by f_max at {bad.size} bias "
          f"point(s). The series resistance below is not converged there; raise "
          f"'log stop frequency' in step08_ac_setup.lsf.")

f_3dB = 1.0 / (2 * np.pi * R_at_max_f * C_low)

print("\n=== Series resistance and RC bandwidth ===")
for v, r, f3 in zip(Vdc, R_at_max_f, f_3dB):
    print(f"  V = {v:+.2f} V   R_s = {r:.4g} ohm*m   f_3dB = {f3 / 1e9:.1f} GHz")
print(f"\n  Best f_3dB: {np.max(f_3dB) / 1e9:.1f} GHz at "
      f"{Vdc[int(np.argmax(f_3dB))]:+.2f} V")
print(f"Worst f_3dB: {np.min(f_3dB) / 1e9:.1f} GHz at "
      f"{Vdc[int(np.argmin(f_3dB))]:+.2f} V")
print("  Note: this is a lumped RC estimate from the small-signal admittance. "
      "It ignores the\n  contact pad capacitance and the driver impedance, so "
      "treat it as an upper bound on the\n  intrinsic junction bandwidth.")

# ---------------------------------------------------------------
# Plot 1: capacitance vs bias
# ---------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(7, 5))
ax1.plot(Vdc, C_fF_per_um, 'o-', color='tab:blue')
ax1.set_xlabel("Bias voltage [V]")
ax1.set_ylabel("Junction capacitance [fF/µm]")
ax1.set_title("PN junction capacitance vs reverse bias")
ax1.grid(True, linestyle=":", alpha=0.6)
fig1.tight_layout()
fig1.savefig("PhaseShifter/CHARGE/capacitance_vs_bias.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot 2: resistance vs bias, low and high frequency
# ---------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(7, 5))
ax2.semilogy(Vdc, np.abs(R[:, 0]), 'o-', color='tab:orange',
             label=f"f = {fq[0]:.0e} Hz (shunt-limited)")
ax2.semilogy(Vdc, np.abs(R[:, -1]), 's-', color='tab:red',
             label=f"f = {fq[-1]:.0e} Hz (series resistance)")
ax2.set_xlabel("Bias voltage [V]")
ax2.set_ylabel(r"$1/\mathrm{Re}(Y)$ [$\Omega\cdot$m]")
ax2.set_title("Small-signal resistance vs reverse bias")
ax2.grid(True, which="both", linestyle=":", alpha=0.6)
ax2.legend()
fig2.tight_layout()
fig2.savefig("PhaseShifter/CHARGE/resistance_vs_bias.png", dpi=300, bbox_inches="tight")

# ---------------------------------------------------------------
# Plot 3: capacitance spectrum at a few bias points
# ---------------------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(7, 5))
picks = np.unique(np.linspace(0, n_bias - 1, 5).astype(int))
for i in picks:
    ax3.semilogx(fq, C[i, :] * 1e9, '-', label=f"V = {Vdc[i]:+.2f} V")
ax3.set_xlabel("Frequency [Hz]")
ax3.set_ylabel("Capacitance [fF/µm]")
ax3.set_title("Capacitance spectrum at selected bias points")
ax3.grid(True, which="both", linestyle=":", alpha=0.6)
ax3.legend(fontsize=9)
fig3.tight_layout()
fig3.savefig("PhaseShifter/CHARGE/capacitance_vs_frequency.png", dpi=300, bbox_inches="tight")

plt.show()
