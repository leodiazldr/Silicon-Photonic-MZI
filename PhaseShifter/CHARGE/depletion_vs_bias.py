# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 2026

@author: USUARIO
"""

"""
Depletion width vs. reverse bias from the Lumerical CHARGE DC sweep.

Reads 'charge_sweep.mat' with h5py (Lumerical writes MATLAB v7.3, which is
HDF5) and evaluates the depletion width on horizontal cuts through the ridge.

WHY SEVERAL CUTS: the p and n regions are ion implants, not uniform blocks.
step06_doping.lsf builds them with addimplant as Pearson-IV depth profiles with
the peak at the top of the ridge and a range of half the ridge thickness, so the
doping falls away with depth. The depletion width is therefore a function of
height, and a single-height number is a convention rather than a unique edge.
The script reports the mid-ridge cut as the headline value and the spread over
cuts at 25, 50 and 75 % of the ridge thickness.

EDGE CRITERION: on each cut, the metallurgical junction is where n and p cross.
The local levels are the majority-carrier concentrations a fixed offset from
that point, read on the same cut, so the implant profile enters through the
simulated data rather than through a nominal doping. The edge is the first point
outward from the junction where the majority carrier recovers to FRAC of that
local level (50 % by default). If an edge is not reached inside X_WINDOW, the
point is reported as NaN: the criterion has left the region where it means
anything, and silently reporting a clipped width would be worse. The same
criterion is applied to the reference point itself: if it falls inside the
depletion region its level is near zero and the recovery test would trivially
succeed at the junction, so that case is reported as NaN too.

INPUTS:  PhaseShifter/CHARGE/charge_sweep.mat   (DC sweep, CHARGE step07)
         PhaseShifter/CHARGE/charge_params.mat  (wg_thickness, CHARGE step01)
OUTPUT:  PhaseShifter/CHARGE/width_vs_bias.png

Run from the repository root:
    python PhaseShifter/CHARGE/depletion_vs_bias.py
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.tri as mtri

# ---------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------
CHARGE_FILE = "PhaseShifter/CHARGE/charge_sweep.mat"
PARAMS_FILE = "PhaseShifter/CHARGE/charge_params.mat"
FIGURE_FILE = "PhaseShifter/CHARGE/width_vs_bias.png"

X_WINDOW = 0.5       # um, half-width of the x range used on each cut
OFFSET = 0.20        # um, distance from the junction where the local level is read
FRAC = 0.50          # edge where the carrier recovers to FRAC * the local level
CUT_FRACTIONS = (0.25, 0.50, 0.75)   # of the ridge thickness, bottom to top


class SimpleNamespace:
    """Container that allows dot-notation access to dataset fields."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# ---------------------------------------------------------------
# .mat reader
# ---------------------------------------------------------------
def load_charge_mat(matfile):
    """
    Load a Lumerical CHARGE .mat file.

    Returns a list of point objects for a MATLAB struct array, or a namespace
    holding the fields of a single struct.
    """
    with h5py.File(matfile, "r") as f:
        keys = [k for k in f.keys() if not k.startswith("#")]

        base = f
        if len(keys) == 1 and isinstance(f[keys[0]], h5py.Group) and "x" not in f:
            base = f[keys[0]]
            base_keys = [k for k in base.keys() if not k.startswith("#")]
        else:
            base_keys = keys

        # MATLAB struct array: a dataset of object references, one per point.
        for k in base_keys:
            item = base[k]
            if isinstance(item, h5py.Dataset) and item.dtype == object:
                points = []
                for ref_row in np.atleast_1d(item[()]):
                    for ref in np.atleast_1d(ref_row):
                        if ref:
                            grp = f[ref]
                            fields = {}
                            for field in grp.keys():
                                if field.startswith("#"):
                                    continue
                                sub_item = grp[field]
                                if isinstance(sub_item, h5py.Dataset):
                                    val = sub_item[()]
                                    fields[field] = (np.squeeze(val)
                                                     if isinstance(val, np.ndarray)
                                                     else val)
                            points.append(SimpleNamespace(**fields))
                return points

        data = {}
        for k in base_keys:
            item = base[k]
            if isinstance(item, h5py.Dataset):
                val = item[()]
                data[k] = (np.squeeze(val)
                           if isinstance(val, np.ndarray) else val)
            elif isinstance(item, h5py.Group):
                if "value" in item:
                    val = item["value"][()]
                    data[k] = (np.squeeze(val)
                               if isinstance(val, np.ndarray) else val)
                else:
                    sub_dict = {}
                    for subk in item.keys():
                        if subk.startswith("#"):
                            continue
                        sub_item = item[subk]
                        if isinstance(sub_item, h5py.Dataset):
                            sub_val = sub_item[()]
                            sub_dict[subk] = (np.squeeze(sub_val)
                                              if isinstance(sub_val, np.ndarray)
                                              else sub_val)
                    data[k] = SimpleNamespace(**sub_dict)

        return SimpleNamespace(**data)


# ---------------------------------------------------------------
# Width on one cut
# ---------------------------------------------------------------
def crossing(conc, xq, start, step, level):
    """First index from start moving by step where conc >= level, else None."""
    indices = range(start, -1, -1) if step < 0 else range(start, len(xq))
    for k in indices:
        if conc[k] >= level:
            return xq[k]
    return None


def width_at_y(interp_n, interp_p, yv, xq):
    """
    Depletion width in nm on the horizontal cut at y = yv.

    Returns NaN when the carrier does not recover to FRAC of the local level
    inside X_WINDOW, meaning the edge is not contained in the extracted region,
    or when the point where the local level is read is itself inside the
    depletion region.
    """
    nq = np.ma.filled(interp_n(xq, np.full_like(xq, yv)), np.nan)
    pq = np.ma.filled(interp_p(xq, np.full_like(xq, yv)), np.nan)
    if np.all(np.isnan(nq)) or np.all(np.isnan(pq)):
        return np.nan

    j = int(np.nanargmin(np.abs(nq - pq)))
    xj = xq[j]
    level_p = pq[int(np.nanargmin(np.abs(xq - (xj - OFFSET))))]
    level_n = nq[int(np.nanargmin(np.abs(xq - (xj + OFFSET))))]

    # The reference point has to sit in the neutral region. If it fell inside the
    # depletion region the level would be near zero and the recovery test would
    # succeed at the junction itself, reporting a width of zero instead of a
    # failure. Requiring the reference to meet the same recovery criterion that
    # defines the edge rejects that case.
    max_p = np.nanmax(pq)
    max_n = np.nanmax(nq)
    if not (max_p > 0 and max_n > 0):
        return np.nan
    if level_p < FRAC * max_p or level_n < FRAC * max_n:
        return np.nan

    xp_edge = crossing(pq, xq, j, -1, FRAC * level_p)
    xn_edge = crossing(nq, xq, j, +1, FRAC * level_n)
    if xp_edge is None or xn_edge is None:
        return np.nan
    return (xn_edge - xp_edge) * 1000.0


def widths_at_cuts(x_um, y_um, elements, n, p, y_cuts):
    """Depletion width at each requested height, in nm."""
    x_um = np.ravel(x_um)
    y_um = np.ravel(y_um)

    elements = np.atleast_2d(elements)
    if elements.shape[0] == 3 and elements.shape[1] != 3:
        elements = elements.T

    tri = mtri.Triangulation(x_um, y_um, elements.astype(int) - 1)

    n_flat = np.ravel(n)
    p_flat = np.ravel(p)
    if n_flat.size != x_um.size:
        raise ValueError(
            f"n has {n_flat.size} values but the mesh has {x_um.size} nodes"
        )
    if p_flat.size != x_um.size:
        raise ValueError(
            f"p has {p_flat.size} values but the mesh has {x_um.size} nodes"
        )

    interp_n = mtri.LinearTriInterpolator(tri, n_flat)
    interp_p = mtri.LinearTriInterpolator(tri, p_flat)
    xq = np.linspace(-X_WINDOW, X_WINDOW, 2000)

    return np.array([width_at_y(interp_n, interp_p, yv, xq) for yv in y_cuts])


# ---------------------------------------------------------------
# Sweep file
# ---------------------------------------------------------------
def process_file(matfile, y_cuts):
    """Return (V_bias, widths) with widths shaped (n_bias, n_cuts)."""
    c = load_charge_mat(matfile)

    # Struct array: one sub-struct per bias point.
    if isinstance(c, list):
        V_bias = []
        widths = []
        for pt in c:
            V_bias.append(float(np.ravel(pt.V_anode)[0])
                          - float(np.ravel(pt.V_cathode)[0]))
            widths.append(widths_at_cuts(pt.x * 1e6, pt.y * 1e6, pt.elements,
                                         pt.n, pt.p, y_cuts))
        V_bias = np.array(V_bias)
        widths = np.array(widths)
        order = np.argsort(V_bias)
        return V_bias[order], widths[order]

    # Single struct: shared mesh, n/p with one column per bias point.
    x_um, y_um = np.ravel(c.x) * 1e6, np.ravel(c.y) * 1e6
    num_nodes = len(x_um)

    V_anode = np.atleast_1d(c.V_anode).astype(float)
    V_cathode = np.atleast_1d(c.V_cathode).astype(float)

    n_all = c.n if c.n.ndim > 1 else c.n.reshape(-1, 1)
    if n_all.shape[0] != num_nodes and n_all.shape[1] == num_nodes:
        n_all = n_all.T

    p_all = c.p if c.p.ndim > 1 else c.p.reshape(-1, 1)
    if p_all.shape[0] != num_nodes and p_all.shape[1] == num_nodes:
        p_all = p_all.T

    V_bias = V_anode - V_cathode if len(V_anode) == n_all.shape[1] else V_anode

    widths = np.array([
        widths_at_cuts(x_um, y_um, c.elements, n_all[:, i], p_all[:, i], y_cuts)
        for i in range(n_all.shape[1])
    ])
    return np.array(V_bias), widths


# ---------------------------------------------------------------
# Run
# ---------------------------------------------------------------
with h5py.File(PARAMS_FILE, "r") as f:
    wg_thickness = float(np.squeeze(f["wg_thickness"][()]))   # m

y_cuts = np.array([frac * wg_thickness * 1e6 for frac in CUT_FRACTIONS])  # um
i_mid = len(CUT_FRACTIONS) // 2
y_mid = y_cuts[i_mid]

labels = [f"{100 * frac:.0f}% ({y * 1e3:.0f} nm)"
          for frac, y in zip(CUT_FRACTIONS, y_cuts)]

V_bias, widths = process_file(CHARGE_FILE, y_cuts)

print(f"Ridge thickness: {wg_thickness * 1e9:.0f} nm")
print(f"Cuts at: {', '.join(labels)}")
print(f"Edge criterion: {100 * FRAC:.0f}% of the local level, read "
      f"{OFFSET * 1e3:.0f} nm from the junction")

print("\n=== Depletion width ===")
print("   Bias [V]   " + "".join(f"{lab:>15s}" for lab in labels)
      + f"{'spread':>10s}")
for i, v in enumerate(V_bias):
    row = ""
    for w in widths[i]:
        row += f"{w:15.1f}" if np.isfinite(w) else f"{'--':>15s}"
    finite = widths[i][np.isfinite(widths[i])]
    if finite.size and np.isfinite(widths[i, i_mid]) and widths[i, i_mid] > 0:
        spread = (finite.max() - finite.min()) / widths[i, i_mid] * 100.0
        row += f"{spread:9.1f}%"
    else:
        row += f"{'--':>10s}"
    print(f"  {v:+8.2f}   " + row)

mid = widths[:, i_mid]
band_lo = np.array([np.nanmin(row) if np.isfinite(row).any() else np.nan
                    for row in widths])
band_hi = np.array([np.nanmax(row) if np.isfinite(row).any() else np.nan
                    for row in widths])

ok = np.isfinite(mid) & np.isfinite(band_lo) & np.isfinite(band_hi) & (mid > 0)
if ok.any():
    spread_pct = (band_hi[ok] - band_lo[ok]) / mid[ok] * 100.0
    i_first = int(np.argmax(ok))
    i_last = len(ok) - 1 - int(np.argmax(ok[::-1]))
    print(f"\n  Mid-ridge width at {V_bias[i_first]:+.2f} V: {mid[i_first]:.1f} nm")
    print(f"  Mid-ridge width at {V_bias[i_last]:+.2f} V: {mid[i_last]:.1f} nm")
    print(f"  Largest spread over cuts: {spread_pct.max():.1f}%")
    print("  The spread measures the implant depth profile: a graded junction")
    print("  has no single edge, so the mid-ridge value is a convention.")

if np.any(~np.isfinite(widths)):
    bad = np.argwhere(~np.isfinite(widths))
    print(f"\n  WARNING: {bad.shape[0]} cut(s) did not reach the {100 * FRAC:.0f}% "
          f"level inside +/-{X_WINDOW} um.")
    print("  Those points are skipped; the edge lies outside the extracted "
          "region there.")

# ---------------------------------------------------------------
# Figure
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
ax.fill_between(V_bias, band_lo, band_hi, color="tab:blue", alpha=0.15,
                label="range over cuts through the ridge")
ax.plot(V_bias, mid, "o-", color="tab:blue",
        label=f"mid-ridge cut ({y_mid * 1e3:.0f} nm)")
ax.set_xlabel("Bias V_anode - V_cathode [V]")
ax.set_ylabel("Depletion width [nm]")
ax.set_title("Depletion width vs reverse bias")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(FIGURE_FILE, dpi=300, bbox_inches="tight")

print(f"\nSaved: {FIGURE_FILE}")
plt.show()
