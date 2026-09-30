# PN Junction Phase Shifter — Electro-Optic Response

The second half of the phase-shifter model. [`../CHARGE/`](../CHARGE/README.md) produces the
carrier distribution at each bias voltage; this folder puts that distribution back into the
optical model and asks what it does to the guided mode — how much the effective index moves,
how much loss it costs, and what phase-shifting efficiency that buys.

Modelled in Lumerical **MODE** with the **FDE** solver.

| Parameter | Value |
| --------- | ----- |
| Waveguide | 500 nm × 220 nm Si rib |
| Wavelength | 1550 nm, fundamental TE |
| Bias sweep | 0 to −1.5 V, 21 points (matches the CHARGE sweep) |
| Carrier model | `n` / `p` imported from `charge_sweep.mat`, Soref–Bennett conversion |
| FDE window | 3.0 µm × 3.0 µm, Metal (matches the CHARGE monitor region) |

## Getting the carrier map into the optical model

Two objects make this work, and neither is optional. A grid attribute of type **np density**
holds the imported `n` and `p` fields as a spatial dataset; an **index perturbation material**
converts those densities into a complex index change. A plain material is not sensitive to
imported data — assigning ordinary silicon to the ridge here would silently produce a
bias-independent effective index, which is a failure mode that looks like a physical result.

The conversion model is **Soref–Bennett**, the same one quoted in the theory note, with the
base material set to the *lossless* dispersive silicon model from
[`../../shared/materials.lsf`](../../shared/materials.lsf). That choice is deliberate: Palik
silicon carries its own absorption, which would put a fixed offset on the loss curve and make
the bias-dependent part harder to read. With a lossless base, everything imaginary in the
result is free-carrier absorption.

The charge data is one dataset with the bias voltage as a parameter, so stepping through bias
points is a matter of setting a parameter index on the grid attribute rather than loading a new
file for each one.

## Coordinates have to match, exactly

The charge map is placed by coordinates, not by any structural link to the CHARGE file. If the
waveguide sits even a few tens of nanometres away from where it sat in CHARGE, the carriers
land in the wrong place. The geometry in [`step01_setup.lsf`](step01_setup.lsf) is therefore
copied from CHARGE rather than re-derived, and the convention is identical in both:

| Axis | Physical direction |
| ---- | ------------------ |
| x | lateral, 0 at the waveguide centre |
| y | vertical, 0 at the BOX/silicon interface (silicon occupies 0 → 220 nm) |
| z | propagation (uniform; the FDE solve is 2D in x–y) |

The second constraint is the FDE window, and here the two solvers are made to agree exactly.
CHARGE's monitor data covers its simulation region — x ∈ [−1.5, +1.5] µm, and y over a 3 µm
span centred on the waveguide — while any part of the mode falling outside that box would see
unperturbed silicon, diluting the computed index change in a way that looks like a physical
result. `step04_fde_setup.lsf` therefore sets the FDE region to `2*lateral_half` in both
directions about the same centre, so the carrier map fills the window with no unperturbed
margin.

Nothing from the CHARGE cross-section is dropped: `step03_geometry.lsf` reproduces the BOX,
slab, ridge, cladding and both metal contacts at their CHARGE coordinates. The ridge *and* the
slab are assigned the perturbed material, so the imported carriers modulate the index wherever
the map has data. Because the contacts' inner edge sits at ±1.2 µm — inside the ±1.5 µm window —
aluminium absorption is part of the computed loss; see the caveat under
[Results](#results).

## Index and loss come out of the same solve

FDE returns a complex effective index. The real part is the phase:

```
Δφ(V) = (2π/λ)·Δn_eff(V)·L
```

and the imaginary part is absorption, `α = 4π·Im(n_eff)/λ`. Because the perturbation material
returns a complex index change, both curves come out of the same bias sweep — which is the
practical argument for importing the carriers rather than estimating Δn and Δα separately.

Lumerical script matrices are real, so the two parts are collected into separate arrays and
recombined in Python.

## V_π·L

The figure of merit the design target is quoted against is `V_π·L`, the voltage-length product
needed for a π phase shift. Setting `(2π/λ)·|Δn_eff|·L = π` gives

```
V_π·L = λ / (2·|dn_eff/dV|)
```

evaluated from the slope of `n_eff(V)`. The slope is not constant — it is steepest near zero
bias and flattens as the junction depletes — so
[`neff_vs_bias.py`](neff_vs_bias.py) reports both the per-interval values and a single number
from the mean slope over the whole swing. The mean-slope number is the one to quote when
comparing designs; the per-interval curve is what shows how the device would actually be
biased.

## Files

| File | Purpose |
| ---- | ------- |
| `main.lsf` | Driver; calls the steps in order |
| `step01_setup.lsf` | Units, geometry (copied from CHARGE), FDE window, bias grid, paths |
| `step02_materials.lsf` | Imports `charge_sweep.mat` as an np-density grid attribute; creates the Soref–Bennett perturbation material |
| `step03_geometry.lsf` | BOX, slab, perturbed ridge, cladding |
| `step04_fde_setup.lsf` | FDE region, mesh, modal settings, and a reference solve at equilibrium |
| `step05_bias_sweep.lsf` | Sweeps the bias, solving the mode at each point; writes `neff_vs_bias.mat` |
| `neff_vs_bias.py` | Post-processing: `n_eff(V)`, `Δn_eff(V)`, loss(V), `V_π·L(V)` and four figures |
| `neff_vs_bias.mat` | Sweep output, consumed by the Python script |
| `neff_vs_bias.png` | Result figure: effective index versus bias |
| `dneff_vs_bias.png` | Result figure: index modulation versus bias |
| `loss_vs_bias.png` | Result figure: free-carrier absorption versus bias |
| `vpi_L_vs_bias.png` | Result figure: `V_π·L` versus bias, with the target marked |

## Running it

`../CHARGE/charge_sweep.mat` has to exist first — run `../CHARGE/main.lsf`, or at least
`../CHARGE/step07_dc_sweep.lsf`, before anything here.

In Lumerical MODE, from this folder:

```lumerical
cd("path/to/PhaseShifter/MODE");
main;
```

The steps call `materials;` from the shared folder via `addpath("../../shared")`, so the
working directory matters. Then, from the repository root:

```bash
pip install -r requirements.txt
python PhaseShifter/MODE/neff_vs_bias.py
```

**The np-density API is the part of this workflow most likely to have moved between releases.**
Both the grid attribute and the perturbation material are created by name, and the property
strings used here are the ones Lumerical 2020 R2.4 accepts. If a step fails on another release,
these are the two places to look first:

- `step02_materials.lsf` — the grid attribute type string, the perturbation material, and the
  `"np density model"` property that selects the Soref–Bennett model.
- `step05_bias_sweep.lsf` — the bias-index property, which follows the pattern
  `<swept quantity>_index` (`V_anode_index` here). The name can be read off the grid
  attribute's property table in the GUI.

`step04` prints a reference solve at equilibrium before the sweep starts. That is the sanity
check: if the field map does not look like the familiar TE mode of a 500 × 220 nm strip and
`n_eff` does not come out near 2.4, the problem is in the geometry, mesh or perturbed material,
not in the sweep.

`step05` also prints a per-point line and warns if `n_eff` jumps by more than 0.05 between
adjacent bias points, which is the signature of the solver switching to a different mode. That
would otherwise appear much later as a plausible-looking spike in the `V_π·L` curve.

## Results

The four figures are produced by [`neff_vs_bias.py`](neff_vs_bias.py). The script prints the
full `n_eff`, `Δn_eff` and loss tables, the best and mean-slope `V_π·L`, and a comparison
against the design targets from [`../CHARGE/README.md`](../CHARGE/README.md).

One caveat carried into the output: the insertion-loss budget is a device-level number, while
the loss computed here is a per-unit-length free-carrier term. The script converts it using a
1 mm phase-shifter length before comparing, and the MMI and bend contributions measured in the
other project folders share the same budget.

A second caveat is specific to this geometry: the aluminium contacts sit inside the solve
window (inner edge ±1.2 µm against a ±1.5 µm window), so `loss_vs_bias.png` mixes free-carrier
absorption with whatever the metal contributes. Both terms are wanted in a device-level loss
figure, but they are not separated here — the way to isolate the free-carrier part is to re-run
with the contacts excluded from the FDE region.

### Current results

The sweep now in the repository is the asymmetric profile (`N_A = 2×10¹⁷`,
`N_D = 1×10¹⁷ cm⁻³`) over 0 → −1.5 V, 21 points — the same grid as the CHARGE sweep.

| Metric | Value | Target |
| ------ | ----- | ------ |
| `n_eff` at equilibrium (0 V) | 2.562790 | — |
| `n_eff` at −1.5 V | 2.562835 | — |
| `Δn_eff` over the full swing | 4.4×10⁻⁵ | — |
| `dn_eff/dV` (mean over 0 → −1.5 V) | 2.9×10⁻⁵ V⁻¹ | — |
| `V_π·L` (mean slope) | **2.63 V·cm** | < 3 V·cm — met |
| `V_π·L` best bias interval | ≈ 1.9 V·cm (near 0 V) | — |
| Free-carrier loss | 2.3 dB/cm at −1.5 V → 2.9 dB/cm at 0 V | ≪ budget |

Two things about the shape of these curves are worth reading off the figures. The index change
is **not linear in bias**: `dneff_vs_bias.png` is steepest near 0 V and flattens with reverse
bias, which is the same behaviour the junction itself shows — the depletion width grows as
`sqrt(V_bi − V)`, so most of the depletion per volt is bought near equilibrium. That is why the
per-interval `V_π·L` in `vpi_L_vs_bias.png` ranges from ≈ 1.9 to ≈ 3.7 V·cm across the sweep,
and why the mean-slope number (2.63 V·cm), not any single interval, is the figure to quote.

The loss runs the other way: highest at 0 V (2.9 dB/cm), where the depletion region is narrowest
and the most doped silicon overlaps the mode, and falling to 2.3 dB/cm at −1.5 V. Over a 1 mm
shifter that is 0.3 dB against a 5 dB device budget shared with the MMI and bends, so the
free-carrier term is not the loss bottleneck. As noted above, this figure also contains the
aluminium contribution.

## Status

**Complete.** The sweep has been run on the current profile and the four figures are up to
date; the phase-shifter model is not expected to change further, so these results can be quoted
as they stand.

Kept here as known limitations rather than open work:

- The aluminium contacts are inside the solve window, so the loss figure mixes the free-carrier
  and metal contributions. Separating them means re-running with the contacts excluded from the
  FDE region.
- The np-density property names are the ones Lumerical 2020 R2.4 accepts; another release may
  name the same properties differently.
- The loss curve is non-flat and bias-dependent, which is the signature that the perturbation
  material is returning the Soref–Bennett absorption term as intended.
- The equilibrium reference would need replacing with a proper mode-tracking scheme if the bias
  sweep ever had to run past −1.5 V, where mode order is less safe to assume.

Still to be folded into the MZI-level power budget: `V_π·L` and this loss term, alongside the
MMI and bend contributions.

## See also

- [`../CHARGE/README.md`](../CHARGE/README.md) — the carrier model this folder consumes, and
  the source of the design targets.
- [`../../shared/materials.lsf`](../../shared/materials.lsf) — the Si and SiO₂ models used here.
- [`../../MZI/PN Phase Shifter Theory.md`](../../MZI/PN%20Phase%20Shifter%20Theory.md) — the
  full derivation of the plasma-dispersion effect and the `V_π·L` figure of merit.
- [`../CHARGE/README.md#references`](../CHARGE/README.md#references) — Soref & Bennett (1987),
  Reed et al. (2010), Chrostowski & Hochberg (2015).
