# Carrier-Depletion PN Junction Phase Shifter

Lateral PN junction driven in reverse bias, forming the phase-shifting arm of the MZI.
Simulated in Lumerical **CHARGE**: a drift-diffusion solver for the carrier distribution under
bias, plus a small-signal AC analysis for the junction capacitance. The carrier maps produced
here are what [`../MODE/`](../MODE/README.md) imports for the electro-optic calculation.

| Target | Value |
| ------ | ----- |
| V_π·L | < 3 V·cm |
| Insertion loss (π shift) | < 5 dB |
| 3 dB EO bandwidth | > 10 GHz |
| Extinction ratio | > 20 dB |

## Physical principle

Silicon has no linear electro-optic (Pockels) effect because it is centrosymmetric, so
modulation relies on the **free-carrier plasma dispersion** effect (Soref–Bennett):

```
Δn = -8.8e-22·ΔN_e - 8.5e-18·(ΔN_h)^0.8
Δα =  8.5e-18·ΔN_e + 6.0e-18·ΔN_h        [cm^-1]
```

Applying reverse bias to the PN junction *widens the depletion region*, removing free
carriers from a growing volume of silicon. Because removing carriers *raises* the local
index, the effective index of the guided mode increases and the accumulated phase shifts:

```
Δφ(V) = (2π/λ)·Δn_eff(V)·L
```

The response is not limited by carrier lifetime — the depletion layer moves on the
dielectric relaxation timescale — which is what makes GHz operation possible. The bandwidth
is set by the RC time constant, `f_3dB = 1/(2πRC)`.

Full derivation in [`../../MZI/PN Phase Shifter Theory.md`](../../MZI/PN%20Phase%20Shifter%20Theory.md).

## Design parameters

| Parameter | Value | Notes |
| --------- | ----- | ----- |
| Waveguide width | 0.5 µm | single-mode TE at 1550 nm |
| Device layer | 220 nm | SOI |
| Junction offset | 0 nm | at mode center; main efficiency/loss trade-off |
| N_A / N_D | 2×10¹⁷ / 1×10¹⁷ cm⁻³ | asymmetric; moderate doping in the ridge |
| N⁺ / P⁺ | 2×10¹⁹ cm⁻³ | contact regions, placed off the mode |
| Bias | 0 to −1.5 V reverse | anode negative, cathode grounded; 21 points |

## Coordinate system

CHARGE's 2D solver works in the x-y plane with z as a uniform thickness, so the waveguide
cross-section is mapped onto it:

| CHARGE axis | Physical direction |
| ----------- | ------------------ |
| x | lateral (across the waveguide width) |
| y | vertical (BOX / Si / cladding stack) |
| z | propagation (uniform thickness) |

## Files

| File | Section | Purpose |
| ---- | ------- | ------- |
| `main.lsf` | — | Driver; calls the steps in order |
| `step01_setup.lsf` | 1 | Units, device dimensions, doping levels, bias sweep settings |
| `step02_materials.lsf` | 2 | Electrical models: semiconductor / insulator / conductor |
| `step03_geometry.lsf` | 3 | BOX, silicon slab and ridge, metal contacts, cladding |
| `step04_solver_and_monitors.lsf` | 4 | 2D drift-diffusion solver and monitors |
| `step05_contacts.lsf` | 5 | Ohmic anode and cathode |
| `step06_doping.lsf` | 6 | p / n / p⁺ / n⁺ regions and junction position |
| `step07_dc_sweep.lsf` | 7 | Anode sweep 0 → −1.5 V; writes `charge_sweep.mat` |
| `step08_ac_setup.lsf` | 8 | Small-signal AC mode, frequency sweep, AC drive on the anode |
| `step09_ac_sweep.lsf` | 9 | Re-runs the bias sweep under AC; writes `ac_sweep.mat` |
| `depletion_vs_bias.ipynb` | — | Post-processing: extracts W_dep(V) from the DC sweep |
| `capacitance_vs_bias.py` | — | Post-processing: extracts C(V), R(V) and f_3dB(V) from the AC sweep |
| `width_vs_bias.png` | — | Result figure produced by the notebook |
| `capacitance_vs_bias.png` | — | Result figure: junction capacitance versus bias |
| `resistance_vs_bias.png` | — | Result figure: small-signal resistance versus bias |
| `capacitance_vs_frequency.png` | — | Result figure: capacitance spectrum at selected biases |
| `charge_sweep.mat` | — | DC sweep output; consumed by the notebook **and by `../MODE/`** |
| `ac_sweep.mat` | — | AC sweep output; consumed by `capacitance_vs_bias.py` |

## Running it

In Lumerical CHARGE:

```lumerical
cd("path/to/PhaseShifter/CHARGE");
main;
```

Each `stepNN_*.lsf` is called by its base name and all steps share one global workspace.
To re-run a single stage:

```lumerical
step06_doping;
```

`main` runs the DC sweep and then the AC sweep, writing `charge_sweep.mat` and
`ac_sweep.mat` to the working directory.

The notebook and the Python script address the working directory differently, which is a
consequence of how each is run:

- `depletion_vs_bias.ipynb` is opened in this folder and reads `charge_sweep.mat` by bare
  filename.
- `capacitance_vs_bias.py` addresses both its input and its figures with paths relative to
  the repository root, so it must be run from there.

```bash
pip install -r requirements.txt   # from the repository root
python PhaseShifter/CHARGE/capacitance_vs_bias.py
```

## Results

The notebook extracts the depletion width by locating where the majority-carrier
concentration recovers to 50 % of the local bulk doping, measured from the point where the
electron and hole densities cross (the metallurgical junction). Over the swept range
(0 → −1.5 V, 21 points) it grows from 152 nm to 285 nm:

| Bias (V) | W_dep (nm) | | Bias (V) | W_dep (nm) | | Bias (V) | W_dep (nm) |
| -------- | ---------- | --- | -------- | ---------- | --- | -------- | ---------- |
| 0.000 | 152.1 | | −0.525 | 208.6 | | −1.050 | 253.6 |
| −0.075 | 159.6 | | −0.600 | 215.1 | | −1.125 | 260.1 |
| −0.150 | 167.6 | | −0.675 | 221.1 | | −1.200 | 265.6 |
| −0.225 | 175.6 | | −0.750 | 226.1 | | −1.275 | 271.1 |
| −0.300 | 185.1 | | −0.825 | 232.1 | | −1.350 | 275.6 |
| −0.375 | 193.6 | | −0.900 | 239.6 | | −1.425 | 279.6 |
| −0.450 | 202.1 | | −0.975 | 247.1 | | −1.500 | 284.6 |

The curve is plotted in `width_vs_bias.png`.

### Simulation vs. theory

For an abrupt junction with a uniform doping step the width has a closed form. For the
asymmetric profile used here (`N_A = 2×10¹⁷`, `N_D = 1×10¹⁷ cm⁻³`) the built-in potential is

```
V_bi = (kT/q)·ln( N_A·N_D / n_i² ) = 0.83 V          (n_i = 1.5×10¹⁰ cm⁻³)
```

and the depletion width is

```
W = sqrt( 2·ε_s·(V_bi − V)·(N_A + N_D) / (q·N_A·N_D) )
```

| Bias (V) | W_dep, theory (nm) | W_dep, simulation (nm) | Difference |
| -------- | ------------------ | ---------------------- | ---------- |
| 0.00 | 126.9 | 152.1 | +25.2 nm (+19.8 %) |
| −0.75 | 175.1 | 226.1 | +51.0 nm (+29.1 %) |
| −1.50 | 212.6 | 284.6 | +72.0 nm (+33.9 %) |

The simulation reproduces the *shape* of the closed-form result: a one-parameter fit
`W_sim ≈ 197·sqrt(0.59 − V) nm` matches all 21 points to within 2.4 nm, so the drift-diffusion
solution follows the expected `sqrt(V_bi − V)` law. What it does not reproduce is the
magnitude — the simulated width runs 20 % high at 0 V and 34 % high at −1.5 V. Two properties
of the model account for the offset:

- **The ridge doping is not a uniform step.** [`step06_doping.lsf`](step06_doping.lsf) builds
  the p and n regions with `addimplant` as Pearson-IV depth profiles (`range` = 110 nm, peak at
  the top surface), not as uniform blocks. The concentration at the junction is therefore below
  the nominal `N_A` / `N_D` and falls further with depth, and lower effective doping means a
  wider depletion region. Fitting an effective uniform doping reproduces the simulation with
  ≈ 0.70 × nominal at 0 V and ≈ 0.56 × nominal at −1.5 V — the drift is the signature of a
  graded profile rather than a step. The fitted `V_bi` of 0.59 V is below the nominal 0.83 V
  for the same reason.
- **The extraction criterion reads a smoothed edge.** The 50 %-recovery point sits roughly one
  Debye length beyond the ideal edge on each side. With `L_D = sqrt(ε_s·kT/(q²N)) ≈ 13 nm` at
  `1×10¹⁷ cm⁻³` and `≈ 9 nm` at `2×10¹⁷ cm⁻³`, that is a systematic ~20 nm of extra width —
  which on its own accounts for most of the 25 nm offset at 0 V.

So the agreement is qualitative rather than quantitative: the physics is captured, and the
residual has a clear origin in the graded profile and the edge criterion rather than being a
mesh artefact. Matching the magnitude would need a profile-aware model that integrates the
actual implant depth profile instead of quoting a single doping level.

## Junction capacitance

The depletion-width result above covers the carrier model. The AC sweep asks a different
question: how much charge has to be moved to change that depletion width — that is, what the
junction looks like as a capacitor to a driving signal.

**Why the small-signal AC solver rather than dQ/dV.** Differencing the contact charge between
adjacent DC bias points also yields a capacitance, and it costs nothing extra to compute. But
it returns only `C`, and the answer is sensitive to how finely the bias is stepped. The AC
solver instead solves for the small-signal admittance `Y(f) = dI/dV` at every bias point over
a log frequency sweep: the imaginary part gives the capacitance and the real part gives the
resistance, and the resistance is what the RC bandwidth estimate needs.

[`step08_ac_setup.lsf`](step08_ac_setup.lsf) switches the solver to the AC analysis and sets a
1 kHz – 1 PHz (10¹⁵ Hz) log sweep; [`step09_ac_sweep.lsf`](step09_ac_sweep.lsf) re-applies the same
bias grid as the DC sweep so the two curves line up point for point, runs, and saves the raw
admittance. The extraction is left to [`capacitance_vs_bias.py`](capacitance_vs_bias.py) rather
than done inside the solver script, so that the choice of frequency for the quasi-static
read can be changed without re-running CHARGE:

```
Y = dI/dV_anode        C = Im(Y)/(2πf)        R = 1/Re(Y)
```

CHARGE's 2D solver reports extensive quantities per unit length along the uniform z direction,
so `C` is a capacitance per unit length; the script reports it in fF/µm, which is numerically
the same as pF/mm.

**What the resistance is, and what it is not.** In reverse bias the junction conducts almost
nothing, so at low frequency `1/Re(Y)` is the junction's *shunt* resistance — enormous, and
unrelated to the modulation speed. The series resistance of the doped regions appears in the
high-frequency asymptote instead: for a junction `Y_j = G_j + jωC_j` in series with `R_s`, the
admittance seen at the contact is `Y_j/(1 + R_s·Y_j)`, which tends to `1/R_s` as ω grows. The
script therefore takes `C` from the low-frequency plateau and `R` from the top of the sweep,
and prints a warning if the sweep did not reach that plateau. The `f_3dB` derived this way is a
lumped RC estimate for the intrinsic junction: it ignores the contact-pad capacitance and the
driver impedance, so treat it as an upper bound rather than a circuit-level answer.

Three figures come out of the script: `capacitance_vs_bias.png` (the C(V) curve the design
needs), `resistance_vs_bias.png` (the same resistance at the bottom and top of the frequency
sweep, which shows how far apart the shunt- and series-limited regimes are), and
`capacitance_vs_frequency.png` (the C(f) roll-off at selected biases).

## Next steps

Remaining design sweeps in this folder:

- [ ] Sweep doping from 1×10¹⁷ to 5×10¹⁸ cm⁻³, including the asymmetric split
  (`N_A` ≠ `N_D`) now in `step01_setup.lsf`
- [ ] Sweep junction offset from 0 to ±200 nm

Task 3.2 (electro-optic) is implemented in [`../MODE/`](../MODE/README.md). That folder imports
`charge_sweep.mat` as an np-density grid attribute, applies the Soref–Bennett conversion
through an index-perturbation material, and sweeps the bias to obtain `n_eff(V)`, the loss and
`V_π·L`. Run the DC sweep here first, then that folder's `main.lsf`.

## References

1. Soref, R. A., & Bennett, B. R. (1987). Electrooptical effects in silicon. *IEEE J. Quantum Electron.*, 23(1), 123–129.
2. Reed, G. T., Mashanovich, G., Gardes, F. Y., & Thomson, D. J. (2010). Silicon optical modulators. *Nature Photonics*, 4(8), 518–526.
3. Chrostowski, L., & Hochberg, M. (2015). *Silicon Photonics Design: From Devices to Systems*. Cambridge University Press, ch. 5.
4. Sze, S. M., & Ng, K. K. (2006). *Physics of Semiconductor Devices*. Wiley, ch. 2–3.
