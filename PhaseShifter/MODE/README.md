# PN Junction Phase Shifter, Electro-Optic Response

The second half of the phase-shifter model. [`../CHARGE/`](../CHARGE/README.md) produces the
carrier distribution at each bias voltage; this folder puts that distribution back into the
optical model and asks what it does to the guided mode, how much the effective index moves,
how much loss it costs, and what phase-shifting efficiency that buys.

Modelled in Lumerical **MODE** with the **FDE** solver.

| Parameter | Value |
| --------- | ----- |
| Waveguide | 500 nm × 220 nm Si rib |
| Wavelength | 1550 nm, fundamental TE |
| Bias sweep | 0 to −5 V, 21 points (imported from the CHARGE sweep) |
| Carrier model | `n` / `p` imported from `charge_sweep.mat`, Soref–Bennett conversion |
| FDE window | `2*lateral_half` = 4.0 µm × 4.0 µm, Metal (equals the imported carrier map extent) |

## Getting the carrier map into the optical model

Two objects make this work. A grid attribute of type **np density**
holds the imported `n` and `p` fields as a spatial dataset; an **index perturbation material**
converts those densities into a complex index change. A plain material is not sensitive to
imported data: assigning ordinary silicon to the ridge here would silently produce a
bias-independent effective index, which is a failure mode that looks like a physical result.

The conversion model is **Soref–Bennett**, the same one quoted in the theory note, with the
base material set to the *lossless* dispersive silicon model from
[`../../shared/materials.lsf`](../../shared/materials.lsf). That choice is intentional: Palik
silicon carries its own absorption, which would put a fixed offset on the loss curve and make
the bias-dependent part harder to read. With a lossless base, everything imaginary in the
result is free-carrier absorption.

The charge data is one dataset with the bias voltage as a parameter, so stepping through bias
points is a matter of setting a parameter index on the grid attribute rather than loading a new
file for each one.

## Coordinates have to match

The charge map is placed by coordinates, not by any structural link to the CHARGE file. If the
waveguide sits even a few tens of nanometres away from where it sat in CHARGE, the carriers
land in the wrong place. The geometry is therefore not redefined here: every run of
[`../CHARGE/step01_setup.lsf`](../CHARGE/step01_setup.lsf) writes `charge_params.mat` next to
the CHARGE scripts, and [`step01_setup.lsf`](step01_setup.lsf) loads it with `matlabload`. The
bias grid travels in the same file, because the index used to select a carrier map is an index
into the CHARGE sweep and has to keep its ordering. The convention is identical in both:

| Axis | Physical direction |
| ---- | ------------------ |
| x | lateral, 0 at the waveguide centre |
| y | vertical, 0 at the BOX/silicon interface (silicon occupies 0 → 220 nm) |
| z | propagation (uniform; the FDE solve is 2D in x–y) |

The second constraint is the FDE window, and here the two solvers are made to agree exactly.
CHARGE's monitor data covers its simulation region (x ∈ [−2.0, +2.0] µm, and y over a 4 µm
span centred on the waveguide), while any part of the mode falling outside that box would see
unperturbed silicon, diluting the computed index change in a way that looks like a physical
result. `step04_fde_setup.lsf` therefore sets the FDE region to `2*lateral_half` in both
directions about the same centre, so the carrier map fills the window with no unperturbed
margin.

Nothing from the CHARGE cross-section is dropped: `step03_geometry.lsf` reproduces the BOX,
slab, ridge, cladding and both metal contacts at their CHARGE coordinates. The ridge *and* the
slab are assigned the perturbed material, so the imported carriers modulate the index wherever
the map has data. Because the contacts' inner edge sits at ±1.5 µm, inside the ±2.0 µm window,
aluminium absorption is part of the computed loss; see the caveat under
[Results](#results).

## Index and loss come out of the same solve

FDE returns a complex effective index. The real part is the phase:

```
Δφ(V) = (2π/λ)·Δn_eff(V)·L
```

and the imaginary part is absorption, `α = 4π·Im(n_eff)/λ`. Because the perturbation material
returns a complex index change, both curves come out of the same bias sweep, which is the
practical argument for importing the carriers rather than estimating Δn and Δα separately.

Lumerical script matrices are real, so the two parts are collected into separate arrays and
recombined in Python.

## V_π·L

The figure of merit the design target is quoted against is `V_π·L`, the voltage-length product
needed for a π phase shift. Setting `(2π/λ)·|Δn_eff|·L = π` gives

```
V_π·L = λ / (2·|dn_eff/dV|)
```

evaluated from the slope of `n_eff(V)`. The slope is not constant: it is steepest near zero
bias and flattens as the junction depletes, so
[`neff_vs_bias.py`](neff_vs_bias.py) reports both the per-interval values and a single number
from the mean slope over the whole swing. The mean-slope number is the one to quote when
comparing designs; the per-interval curve is what shows how the device would actually be
biased.

## INTERCONNECT compact model

[`step06_export_interconnect.lsf`](step06_export_interconnect.lsf) turns the sweep into the data
card the MZI system model consumes. The element is INTERCONNECT's **Optical Modulator Measured
(OM)** with `measurement type = effective index`, which reads three whitespace-separated columns:

| Column | Quantity |
| ------ | -------- |
| 1 | Bias voltage [V], ascending from `V_bias_start` to `V_bias_stop` |
| 2 | `Re(n_eff) - Re(n_eff at 0 V)` |
| 3 | `Im(n_eff)`, absolute |

The real part is a change referenced to equilibrium, because the element adds the modulation
phase to whatever the arm already carries; an absolute index here would bake in a phase offset
that belongs to the arm lengths. The imaginary part stays absolute, so the insertion loss at
0 V is part of the model. As noted under Results, that loss still contains the aluminium
contribution.

The card is written to `phase_shifter_neff_vs_V.txt` in this folder. In the element, set
`input parameter = table`, `load from file = true`, `measurement filename` to that file,
`measurement type = effective index`, `frequency = 193.414 THz` (the 1550 nm solve point), and
the mode to TE. The modulation-port voltage is the anode-to-cathode bias, so keep the source
within the swept −5 → 0 V range; outside it the element has no data.

The interaction `length` is an element property because the card is per metre. With
`V_π·L = 2.03 V·cm`, the voltage for a π shift is `V_π·L / length`: at the full swing the index
change is 1.91×10⁻⁴, so a length of about 4.1 mm puts π at the −5 V end of the sweep. The
1 mm in [`neff_vs_bias.py`](neff_vs_bias.py) is the insertion-loss example, not a phase-shift
design point.

The card is single-frequency. The OM element holds one `frequency`, and the dispersion of the
rest of the arm continues to come from the waveguide data card in [`../../MZI/`](../../MZI/).

## Files

| File | Purpose |
| ---- | ------- |
| `main.lsf` | Driver; calls the steps in order |
| `step01_setup.lsf` | Units, geometry and bias grid loaded from `../CHARGE/charge_params.mat`, FDE window, paths |
| `step02_materials.lsf` | Imports `charge_sweep.mat` as an np-density grid attribute; creates the Soref–Bennett perturbation material |
| `step03_geometry.lsf` | BOX, slab, perturbed ridge, cladding |
| `step04_fde_setup.lsf` | FDE region, mesh, modal settings, and a reference solve at equilibrium |
| `step05_bias_sweep.lsf` | Sweeps the bias, solving the mode at each point; writes `neff_vs_bias.mat` |
| `step06_export_interconnect.lsf` | Writes the INTERCONNECT card from `neff_vs_bias.mat` |
| `phase_shifter_neff_vs_V.txt` | INTERCONNECT data card: Optical Modulator Measured, effective index |
| `neff_vs_bias.py` | Post-processing: `n_eff(V)`, `Δn_eff(V)`, loss(V), `V_π·L(V)` and four figures |
| `neff_vs_bias.mat` | Sweep output, consumed by the Python script; solver output, not committed |
| `neff_vs_bias.png` | Result figure: effective index versus bias |
| `dneff_vs_bias.png` | Result figure: index modulation versus bias |
| `loss_vs_bias.png` | Result figure: free-carrier absorption versus bias |
| `vpi_L_vs_bias.png` | Result figure: `V_π·L` versus bias, with the target marked |

## Running it

Two files from CHARGE have to exist first. `../CHARGE/charge_params.mat` is written by
`../CHARGE/step01_setup.lsf`, and `../CHARGE/charge_sweep.mat` by `../CHARGE/step07_dc_sweep.lsf`;
running `../CHARGE/main.lsf` produces both. Loading the parameters before the sweep would build
the right cross-section for a carrier map that does not exist yet, so run the CHARGE flow first.

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

`main.lsf` also writes `phase_shifter_neff_vs_V.txt`. That step is post-processing of
`neff_vs_bias.mat`, so `step05` has to have run; the element settings that consume the card are
in [INTERCONNECT compact model](#interconnect-compact-model).

**The np-density API is the part of this workflow most likely to have moved between releases.**
Both the grid attribute and the perturbation material are created by name, and the property
strings used here are the ones Lumerical 2020 R2.4 accepts. If a step fails on another release,
these are the two places to look first:

- `step02_materials.lsf`, the grid attribute type string, the perturbation material, and the
  `"np density model"` property that selects the Soref–Bennett model.
- `step05_bias_sweep.lsf`, the bias-index property, which follows the pattern
  `<swept quantity>_index` (`V_anode_index` here). The name can be read off the grid
  attribute's property table in the GUI.

`step04` prints a reference solve at equilibrium before the sweep starts. That is the sanity
check: if the field map does not look like the familiar TE mode of a 500 × 220 nm strip and
`n_eff` does not come out near 2.56, the problem is in the geometry, mesh or perturbed material,
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
window (inner edge ±1.5 µm against a ±2.0 µm window), so `loss_vs_bias.png` mixes free-carrier
absorption with whatever the metal contributes. Both terms are wanted in a device-level loss
figure, but they are not separated here: the way to isolate the free-carrier part is to re-run
with the contacts excluded from the FDE region.

### Current results

The numbers are for the asymmetric profile (`N_A = 1×10¹⁸`, `N_D = 5×10¹⁷ cm⁻³`) over
0 → −5 V, 21 points, the bias grid the CHARGE sweep exports.

| Metric | Value | Target |
| ------ | ----- | ------ |
| `n_eff` at equilibrium (0 V) | 2.561322 | — |
| `n_eff` at −5 V | 2.561513 | — |
| `Δn_eff` over the full swing | 1.91×10⁻⁴ | — |
| `dn_eff/dV` (mean over 0 → −5 V) | 3.8×10⁻⁵ V⁻¹ | — |
| `V_π·L` (mean slope) | **2.03 V·cm** | < 3 V·cm, met |
| `V_π·L` best bias interval | ≈ 1.2 V·cm (near 0 V) | — |
| Free-carrier loss | 8.75 dB/cm at 0 V → 5.25 dB/cm at −5 V | 0.88 dB over 1 mm, inside the 5 dB budget |

Two things about the shape of these curves are worth reading off the figures. The index change
is **not linear in bias**: `dneff_vs_bias.png` is steepest near 0 V and flattens with reverse
bias, which is the same behaviour the junction itself shows: the depletion width grows as
`sqrt(V_bi − V)`, so most of the depletion per volt is bought near equilibrium. That is why the
per-interval `V_π·L` in `vpi_L_vs_bias.png` ranges from ≈ 1.2 to ≈ 3.1 V·cm across the sweep,
and why the mean-slope number (2.03 V·cm), not any single interval, is the figure to quote.

The loss runs the other way: highest at 0 V (8.75 dB/cm), where the depletion region is narrowest
and the most doped silicon overlaps the mode, and falling to 5.25 dB/cm at −5 V. Over a 1 mm
shifter that is 0.88 dB against a 5 dB device budget shared with the MMI and bends, so the
free-carrier term is not the loss bottleneck. As noted above, this figure also contains the
aluminium contribution.

## Status

**Complete.** The flow runs end to end on the CHARGE sweep in `../CHARGE/charge_sweep.mat`
(0 → −5 V, 21 points) and produces the table, the four figures and the INTERCONNECT card.

Kept here as known limitations rather than open work:

- The aluminium contacts are inside the solve window, so the loss figure mixes the free-carrier
  and metal contributions. Separating them means re-running with the contacts excluded from the
  FDE region.
- The np-density property names are the ones Lumerical 2020 R2.4 accepts; another release may
  name the same properties differently.
- The loss curve is non-flat and bias-dependent, which is the signature that the perturbation
  material is returning the Soref–Bennett absorption term as intended.
- The INTERCONNECT card is single-frequency by construction: the OM element holds one
  `frequency`, so a wavelength-resolved modulator model would need a separate card per
  wavelength.

The electro-optic response is exported as a compact model. The MZI-level power budget,
which brings `V_π·L` and this loss term together with the MMI and bend contributions, is
assembled in INTERCONNECT from this card and the passive-component data cards.

## See also

- [`../CHARGE/README.md`](../CHARGE/README.md), the carrier model this folder consumes, and
  the source of the design targets.
- [`../../shared/materials.lsf`](../../shared/materials.lsf), the Si and SiO₂ models used here.
- [`../../General/PN Phase Shifter Theory.md`](../../General/PN%20Phase%20Shifter%20Theory.md), the
  full derivation of the plasma-dispersion effect and the `V_π·L` figure of merit.
- [`../CHARGE/README.md#references`](../CHARGE/README.md#references), Soref & Bennett (1987),
  Reed et al. (2010), Chrostowski & Hochberg (2015).
