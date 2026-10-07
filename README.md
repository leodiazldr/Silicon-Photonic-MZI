# Silicon-Photonic MZI Modulator on 220 nm SOI

Design and simulation of a silicon-photonic Mach–Zehnder interferometer (MZI) modulator for
BB84 quantum key distribution state encoding: single-mode waveguides, low-loss bends, 1×2
multimode interference (MMI) splitters, and a GHz-bandwidth carrier-depletion phase shifter,
on a commercial 220 nm SOI process.

---

## Platform

Silicon photonics on 220 nm SOI, simulated in Ansys Lumerical (MODE, FDTD, CHARGE, INTERCONNECT),
with gdsfactory and KLayout as the intended layout tools.

| Parameter       | Choice                                       |
| --------------- | -------------------------------------------- |
| Wafer           | SOI, 220 nm Si on 2 µm buried oxide          |
| Process         | IME / AMF / AIM (standard 220 nm SOI)        |
| Wavelength      | 1550 nm (telecom C-band)                     |
| Polarization    | TE (single-mode)                             |
| Modulator type  | Lateral PN junction, carrier depletion       |
| Layout tool     | gdsfactory (Python) or KLayout               |
| PDK             | SiEPIC PDK or foundry PDK if available       |

## Repository structure

Components are grouped by function, and each component gets one sub-directory per solver
used on it, so `<Component>/<Solver>/` holds the design scripts for that solver, its
post-processing, and its own `README.md`.

```
.
├── shared/                     Shared material definitions and helpers
│   ├── materials.lsf           Creates the dispersive Si / SiO2 / SiN models used by all sims
│   └── materials/              Sampled material data (SiN, Palik, Luke, Kischkat, …)
│
├── Waveguide/                  Single-mode strip waveguide (the building block)
│   └── MODE/                   FDE
│       ├── main.lsf            Cross-section and fundamental TE mode
│       ├── width_sweep.lsf     Width sweep → wg_width_sweep.mat
│       ├── width_sweep.py      Post-processing for the width sweep
│       ├── frequency_sweep.lsf Wavelength sweep → frequency_sweep_si.mat
│       ├── frequency_sweep.py  Post-processing for the wavelength sweep
│       └── README.md
│
├── Bends/                      Low-loss waveguide bends
│   ├── bezier_curves.py        Cubic Bézier bends vs circular arcs, curvature analysis
│   └── MODE/                   FDE
│       ├── mode_mismatch_Rc_sweep.lsf  Straight↔bend overlap vs radius of curvature
│       ├── bend_loss_analysis.py       Loss model, optimum radius, figures
│       └── README.md
│
├── MMI/                        1×2 MMI splitter / combiner
│   ├── MODE/                   EME
│   │   ├── main.lsf            Driver; calls step01…step14 in order
│   │   ├── step01_setup.lsf    Platform constants
│   │   ├── …
│   │   ├── step11_dy_sweep.lsf Output-offset sweep, rebuilding the geometry per point
│   │   ├── step14_save_design.lsf  Writes the design point → mmi_design_point.mat/.txt
│   │   ├── length_sweep.py     Post-processing (IL and split vs length)
│   │   ├── wavelength_sweep.py Post-processing (transmission, IL, imbalance vs λ)
│   │   ├── dy_sweep.py         Post-processing (IL and imbalance vs d_y)
│   │   ├── input_taper_sweep.py   Post-processing (IL and split vs input taper width)
│   │   ├── output_taper_sweep.py  Post-processing (IL and split vs output taper width)
│   │   ├── *.png               The result figures
│   │   ├── reference/          Superseded varFDTD implementation, kept for cross-checks
│   │   └── README.md
│   └── FDTD/                   3D FDTD validation build of one design point
│       ├── main.lsf            Driver; imports the design point, builds, runs and saves
│       ├── step01_setup.lsf    matlabload of ../MODE/mmi_design_point.mat
│       ├── step02_geometry.lsf 3D structure at the optimised L, d_y and taper widths
│       ├── step03_fdtd_region.lsf  FDTD region
│       ├── step04_sources_monitors.lsf  Three S-parameter ports and a field profile
│       ├── step05_save_results.lsf  Runs the sim; saves S-parameters and monitor data
│       ├── fdtd_results.py     Post-processing (band summary, |S|²-params, T/IL, |E|² map)
│       ├── *.png               The three result figures
│       └── README.md
│
├── PhaseShifter/               Carrier-depletion PN junction
│   ├── CHARGE/                 Drift-diffusion: carrier maps and junction capacitance
│   │   ├── main.lsf            Driver; calls step01…step09 in order
│   │   ├── step01_setup.lsf    Platform constants and design parameters
│   │   ├── …
│   │   ├── depletion_vs_bias.ipynb  Post-processing (W_dep vs bias)
│   │   ├── capacitance_vs_bias.py   Post-processing (C(V), R(V), f_3dB(V))
│   │   ├── *.mat               Generated sweep output, not committed; charge_sweep.mat
│   │   │                       is consumed by the notebook and by MODE/
│   │   └── README.md
│   └── MODE/                   FDE: the electro-optic response
│       ├── main.lsf            Driver; calls step01…step05 in order
│       ├── step02_materials.lsf    Carrier maps → np-density grid attribute
│       ├── step05_bias_sweep.lsf   Mode solve per bias point → neff_vs_bias.mat
│       ├── neff_vs_bias.py     Post-processing (n_eff, loss, V_pi·L)
│       └── README.md
│
└── MZI/                        Design notes (Obsidian vault)
    ├── Plan.md
    ├── MMI Theory.md
    └── PN Phase Shifter Theory.md
```

Lumerical project files (`*.lms`, `*.ldev`, `*.fsp`), logs, movie exports and simulation data
(`*.mat`) are excluded via [`.gitignore`](.gitignore): they are large, machine-specific, and
regenerate whenever a simulation is saved or its post-processing script is re-run. What *is*
committed is the result figures (`*.png`) and the INTERCONNECT data card (`*.ldf`), so every curve
in the results sections below can be inspected without a Lumerical licence. The solver data behind
the figures is not committed and has to be regenerated by re-running the steps.

## Components

### Single-mode waveguide: `Waveguide/`

The 500 nm × 220 nm strip waveguide that everything else is built on. Solved in Lumerical
MODE (FDE) for the fundamental TE mode, then swept in width and in wavelength to confirm the
single-mode condition holds across the C-band with usable fabrication tolerance.

See [`Waveguide/MODE/README.md`](Waveguide/MODE/README.md).

### Low-loss bends: `Bends/`

Bend loss is the dominant routing penalty once a device has more than a few turns. Two
approaches are compared: a conventional circular arc, whose curvature jumps discontinuously
at the straight-to-bend junction, and a cubic Bézier, whose curvature varies smoothly so the
mode-mismatch loss is lower. The FDE sweep finds the radius that minimises the sum of
mode-mismatch and propagation loss.

See [`Bends/MODE/README.md`](Bends/MODE/README.md).

### 1×2 MMI splitter: `MMI/`

Self-imaging 1×2 multimode interferometer, the 50/50 splitter and combiner of the MZI.
Optimized in Lumerical MODE using the EME (eigenmode expansion) solver, which resolves
the mode-beating physics directly and makes length sweeps essentially free.

Design targets: 50:50 ± 1 %, insertion loss < 0.5 dB, bandwidth > 40 nm, in-phase outputs.

The design point is a `W_MMI = 5 µm` body with linear tapers. The analytic sizing at that width is
`L_MMI = 3L_π/8 ≈ 29.8 µm` and `d_y = W_e/4 ≈ 1.29 µm`; an FDE solve replaces the bulk-index beat
length with the simulated one (79.53 µm → 61.56 µm, and `L_MMI` with it, to 23.085 µm). Four sweeps
then set the final geometry, `L_MMI = 22.162 µm`, `d_y = 1.2690 µm`, the input taper widened from
`W_MMI/4 = 1.25 µm` to 1.3333 µm and the output taper from 1.25 µm to 1.3833 µm, which between them
take the insertion loss from 0.126 dB to 0.069 dB at 1550 nm.

The optimised design point is frozen to `mmi_design_point.mat` by `step14_save_design.lsf` and
rebuilt in 3D FDTD in [`MMI/FDTD/`](MMI/FDTD/README.md) for a single-point validation of the
EME result.

See [`MMI/MODE/README.md`](MMI/MODE/README.md), [`MMI/FDTD/README.md`](MMI/FDTD/README.md) and
[`MZI/MMI Theory.md`](MZI/MMI%20Theory.md).

### Carrier-depletion phase shifter: `PhaseShifter/`

Lateral PN junction driven in reverse bias. Depleting carriers from the junction region raises
the local refractive index (Soref–Bennett plasma dispersion), shifting the phase of the guided
mode. This is the only component that spans two solvers, so it gets two folders: the electrical
model and the optical one, with a `.mat` carrier map travelling between them.

- **`PhaseShifter/CHARGE/`**: drift-diffusion. Builds the doping profile, sweeps the reverse
  bias and records the carrier distribution at each point, and runs a small-signal AC analysis
  for the junction capacitance and series resistance.
- **`PhaseShifter/MODE/`**: FDE. Imports that carrier map as an np-density grid attribute,
  converts it to a complex index change through a Soref–Bennett perturbation material, and
  solves the optical mode at each bias point to obtain `n_eff(V)` and the loss.

Design targets: V_π·L < 3 V·cm, insertion loss < 5 dB, 3 dB bandwidth > 10 GHz.

See [`PhaseShifter/CHARGE/README.md`](PhaseShifter/CHARGE/README.md),
[`PhaseShifter/MODE/README.md`](PhaseShifter/MODE/README.md) and
[`MZI/PN Phase Shifter Theory.md`](MZI/PN%20Phase%20Shifter%20Theory.md).

## Results so far

### Waveguide

The width sweep runs 100–2000 nm in 50 nm steps and, at each width, records the effective and group indices
and the TE polarisation fraction of every mode it finds. Counting the guided modes per width
locates the single-mode window, and classifying each mode by its polarisation fraction shows
where higher-order and cross-polarised modes appear. The wavelength sweep then fixes the
width at the nominal 500 nm and returns `n_eff(λ)` and `n_g(λ)` across the C-band.

![Guided modes versus waveguide width](Waveguide/MODE/waveguide_modes_vs_width.png)

![Effective index versus wavelength](Waveguide/MODE/waveguide_neff_vs_wavelength.png)

### Bends

Bend loss is a trade-off rather than a monotonic function of radius: the mode-mismatch loss
at the straight-to-bend junctions falls as the radius grows, while the propagation loss over
the arc grows linearly with it. The sweep brackets the minimum.

![Bend loss versus radius of curvature](Bends/MODE/bend_loss_vs_radius.png)

A cubic Bézier bend is the alternative to a circular arc. Its curvature ramps smoothly from
zero, so the mode is never asked to follow the curvature discontinuity that a straight-to-arc
junction presents.

![Cubic Bézier curvature profile](Bends/bezier_curves.png)

### Phase shifter

The PN junction is modelled in CHARGE on an asymmetric profile (`N_A = 2×10¹⁷`,
`N_D = 1×10¹⁷ cm⁻³`) swept from 0 to −1.5 V. Extracting the depletion width from the carrier
maps gives `W_dep` growing from 152 nm at 0 V to 285 nm at −1.5 V. The closed-form
abrupt-junction result for the same doping is 127 nm → 213 nm, so the simulation follows the
expected `sqrt(V_bi − V)` law but runs 20–34 % wider: the ridge doping is a graded Pearson-IV
implant rather than a uniform step, and the extraction criterion reads roughly a Debye length
beyond the ideal edge. The comparison is worked through in
[`PhaseShifter/CHARGE/README.md`](PhaseShifter/CHARGE/README.md).

![Depletion width versus reverse bias](PhaseShifter/CHARGE/width_vs_bias.png)

The same junction is then characterised as a capacitor by a small-signal AC sweep. The
capacitance is taken from the low-frequency plateau of `Y(f) = dI/dV` rather than by
differencing charge between DC bias points, because the admittance also carries the series
resistance that the RC bandwidth estimate needs, and because it does not depend on how finely
the bias is stepped. `C(V)` falls monotonically as the depletion region widens, and the
capacitance spectrum shows where the RC roll-off begins.

![Junction capacitance versus reverse bias](PhaseShifter/CHARGE/capacitance_vs_bias.png)

![Capacitance spectrum at selected biases](PhaseShifter/CHARGE/capacitance_vs_frequency.png)

`PhaseShifter/MODE/` closes the loop: importing those carrier maps into the optical model
gives `n_eff(V)`, and hence both the phase shift and the free-carrier loss at each bias. Those
two curves are the whole phase-shifter trade-off: the same carrier removal that raises the
index also absorbs light, so they are deliberately extracted from a single sweep and plotted
against the same bias axis, together with the `V_π·L` figure of merit derived from the slope of
`n_eff(V)`.

The result is `V_π·L = 2.63 V·cm` from the mean slope over the full 0 → −1.5 V swing, inside the
3 V·cm target. The index change over that swing is `Δn_eff = 4.4×10⁻⁵`, and it is strongly
sub-linear in bias: most of the depletion is bought near equilibrium, so the per-interval
`V_π·L` ranges from about 1.9 to 3.7 V·cm across the sweep. Free-carrier loss is 2.3 dB/cm at
−1.5 V rising to 2.9 dB/cm at 0 V, which is 0.3 dB over a 1 mm shifter against a 5 dB device
budget.

![V_π·L versus reverse bias](PhaseShifter/MODE/vpi_L_vs_bias.png)

![Effective index versus reverse bias](PhaseShifter/MODE/neff_vs_bias.png)

The phase-shifter model is complete and these results are not expected to change.

### MMI

The splitter geometry starts from self-imaging theory, `L_MMI = 3L_π/8`, output ports at
`±W_e/4`, and the EME solver then refines it. An FDE solve replaces the bulk-index guess for
the beat length `L_π`, and a propagation sweep over the MMI body picks the length that
minimises insertion loss. EME is what makes that affordable: changing the MMI length only
changes a propagation phase, so the 31-point sweep runs in seconds rather than the full
rebuild FDTD would need at every point.

Five sweeps set the design, each saved to a `.mat` file by the Lumerical step and plotted by a
Python script:

| Sweep | Saved by | Plotted by | Figure |
| ----- | -------- | ---------- | ------ |
| MMI length | `step09_length_sweep.lsf` | `length_sweep.py` | `mmi_il_vs_length.png` |
| Input taper width | `step10_input_taper_sweep.lsf` | `input_taper_sweep.py` | `mmi_il_vs_in_width.png` |
| Output offset `d_y` | `step11_dy_sweep.lsf` | `dy_sweep.py` | `mmi_il_vs_dy.png` |
| Output taper width | `step12_output_taper_sweep.lsf` | `output_taper_sweep.py` | `mmi_il_vs_out_width.png` |
| Wavelength (C-band) | `step13_wavelength_sweep.lsf` | `wavelength_sweep.py` | `mmi_transmission_vs_wavelength.png`, `mmi_imbalance_vs_wavelength.png` |

All five have now been run and all six figures are committed. Each sweep moves one parameter and
leaves the tree at its optimum, so the loss falls in turn: 0.126 dB after the length sweep, 0.104 dB
after the input taper, 0.100 dB after the output offset, and 0.069 dB once the output taper is set.

| Metric | Result |
| ------ | ------ |
| Split at the optimum | 49.2 % / 49.2 % (`T = 0.4921` per port) |
| Imbalance | zero to within 7×10⁻⁷ dB |
| Insertion loss at 1550 nm | **0.069 dB** |
| Insertion loss over 40 nm (1530–1570 nm) | 0.127 dB worst case |
| Insertion loss over the C-band | 0.155 dB mean, 0.397 dB worst (1510 nm) |

![Insertion loss and split versus MMI length](MMI/MODE/mmi_il_vs_length.png)

![Insertion loss and split versus input taper width](MMI/MODE/mmi_il_vs_in_width.png)

![Insertion loss versus output offset d_y](MMI/MODE/mmi_il_vs_dy.png)

![Insertion loss and split versus output taper width](MMI/MODE/mmi_il_vs_out_width.png)

![Transmission across the C-band](MMI/MODE/mmi_transmission_vs_wavelength.png)

![Splitting imbalance across the C-band](MMI/MODE/mmi_imbalance_vs_wavelength.png)

Two features of these curves are worth reading off directly. The imbalance is identically zero,
which is a property rather than a measurement: a centred-input 1×2 MMI with its output ports placed
symmetrically is mirror-symmetric, so `T_top = T_bot` by construction and the curve verifies the
port setup. And all four optima are shallow: the length sweep is flat to within 0.07 dB over ±0.3 µm
of its minimum, the input taper to within 0.003 dB over 1.30–1.35 µm, and the output taper varies by
0.0005 dB between 1.3833 µm and 1.40 µm, so the
design sits on plateaus rather than peaks and fabrication scatter can move a parameter without
moving the loss. What remains is robustness rather than optimisation: the taper-length check, a
re-sweep of the length now that the tapers have moved, and the ±10–20 nm width-bias sweeps, with the
selection rule still to be changed from the single-point minimum to the band-averaged or worst-case
loss ([`MZI/Plan.md` §5](MZI/Plan.md), step 6).

### MMI in 3D FDTD

The frozen design point is exported to `mmi_design_point.mat` by `step14_save_design.lsf`, then
rebuilt in full 3D FDTD and run at 101 frequency points across 1500–1600 nm. The split is 50:50 to
within the resolution of the plotted curves; a centred-input 1×2 MMI with symmetric outputs is
mirror-symmetric, so it has to be, and the insertion loss stays under the 0.5 dB target across the
whole 100 nm span: 0.08 dB over the flat part of the band, 0.10 dB at 1550 nm and 0.42 dB worst case
at 1600 nm, against 0.069 dB at 1550 nm for the same point in EME. Reflection sits at −40 dB or
better over most of the band. Running the same geometry at three mesh accuracies, 2, 3 and 5,
gives 0.17, 0.12 and 0.10 dB at 1550 nm, so the figure is mesh-converged to about 0.02 dB.

![3D FDTD S-squared parameters](MMI/FDTD/mmi_fdtd_S2-params.png)

![3D FDTD field profile at 1550 nm](MMI/FDTD/mmi_fdtd_field_profile.png)

The field map is the clearest check on the geometry: the input taper feeds the body, a two-fold
image forms inside it, and the two output tapers pick that image up, which is exactly the
self-imaging picture the design equations assume. The full set of figures, the numbers behind them
and the caveats are in [`MMI/FDTD/README.md`](MMI/FDTD/README.md).

## Running the simulations

Each component/solver folder contains a `main.lsf` driver and a set of numbered step files.
Lumerical's script interpreter does not support `include`, so the step files are written
as script *functions*: the driver calls each by name, and they share a single global
workspace.

In Lumerical MODE or CHARGE:

```lumerical
cd("path/to/MMI/MODE");
main;
```

The driver starts with `switchtolayout` and `deleteall`. Where a component needs the shared
optical materials it issues `addpath("../../shared")` followed by `materials;` before any
geometry is built; the CHARGE flow builds its electrical models from scratch instead and
needs no path setup. Because the step files are called by their base name, a folder has to
be run in place, with `shared/` two levels up. This is why every solver folder sits at
`<Component>/<Solver>/` rather than at the component root, the depth is what makes
`../../shared` resolve.

The post-processing scripts are the other way round: they address their inputs and their
figures from the repository root, so they are run as
`python PhaseShifter/MODE/neff_vs_bias.py` from the top of the tree. The one exception is
`PhaseShifter/CHARGE/depletion_vs_bias.ipynb`, which is opened in its own folder.

To re-run a single stage without rebuilding everything, run the steps individually from the
script prompt, e.g. `step04_fde_mode_check;`.

## Requirements

- Ansys Lumerical 2020 R2 or later, with MODE (FDE + EME) and CHARGE licences enabled
- Python 3.9+ with `numpy`, `h5py`, `matplotlib` for the post-processing scripts

```bash
pip install -r requirements.txt
```

## Status

| Phase | Description                  | Status         |
| ----- | ---------------------------- | -------------- |
| 1     | Waveguide and bend design    | Complete (width and wavelength sweeps, and the bend radius study; the bend `R_opt` is provisional, see [`Bends/MODE/README.md`](Bends/MODE/README.md)) |
| 2     | MMI splitters                | Swept and characterised (length, both taper widths, output offset and wavelength all swept; 0.069 dB at 1550 nm in EME, 0.10 dB in the 3D FDTD cross-check). Taper-length check, a length re-sweep and the width-bias robustness checks still open, see [`MZI/Plan.md` §6.1](MZI/Plan.md) |
| 3     | Carrier-depletion modulator  | Complete (depletion width, junction capacitance and electro-optic response all simulated; V_π·L inside target) |
| 4     | MZI system integration       | Not started    |
| 5     | GDS layout                   | Not started    |
| 6     | Documentation and repository | In progress    |

## References

1. Soldano, L. B., & Pennings, E. C. M. (1995). Optical multi-mode interference devices based on self-imaging. *J. Lightwave Technol.*, 13(4), 615–627.
2. Soref, R. A., & Bennett, B. R. (1987). Electrooptical effects in silicon. *IEEE J. Quantum Electron.*, 23(1), 123–129.
3. Reed, G. T., Mashanovich, G., Gardes, F. Y., & Thomson, D. J. (2010). Silicon optical modulators. *Nature Photonics*, 4(8), 518–526.
4. Chrostowski, L., & Hochberg, M. (2015). *Silicon Photonics Design: From Devices to Systems*. Cambridge University Press.
5. Bennett, C. H., & Brassard, G. (1984). Quantum cryptography: Public key distribution and coin tossing. *Proc. IEEE ICCSSP*.
