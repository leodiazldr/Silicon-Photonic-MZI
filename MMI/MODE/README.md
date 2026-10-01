# 1×2 MMI Splitter — Design and Optimization

Self-imaging 1×2 multimode interferometer, used as the 50/50 splitter and combiner of the
MZI. Designed in Lumerical **MODE** using the **EME** (eigenmode expansion) solver.

| Target             | Value                    |
| ------------------ | ------------------------ |
| Splitting ratio    | 50:50 ± 1 %              |
| Insertion loss     | < 0.5 dB                 |
| Bandwidth          | > 40 nm around 1550 nm   |
| Phase between outputs | 0 (in-phase)          |

## Design point

| Parameter | Value |
| --------- | ----- |
| MMI width `W_MMI` | 4.0 µm |
| Effective width `W_e` | 4.16 µm |
| MMI length `L_MMI` | **14.00 µm** — from the length sweep; 14.79 µm from the FDE-refined beat length, 19.4 µm from the slab formula |
| Output offset `d_y` | **1.019 µm** — from the `d_y` sweep; `W_e/4 = 1.039 µm` analytically |
| Output separation | 2·`d_y` = 2.038 µm |
| Tapers | linear, 0.5 → 1.0 µm; 8 µm input, 5 µm output |
| Lead waveguides | 10 µm, both sides |

The width was fixed after running the `d_y` sweep at `W_MMI = 4 µm` and 5 µm; the 4 µm case gave the
lower loss, plausibly because these taper polygons are a better match to the 4 µm body. Only the
4 µm sweep output is kept in the repository — the 5 µm run was exploratory.

## Why an MMI rather than a directional coupler

MMIs are broadband (self-imaging depends on mode beating rather than evanescent coupling),
tolerant to fabrication error (no critical gap dimension to control), and give better
splitting uniformity.

## Design equations

For a symmetric, centered-input 1×2 general-interference MMI:

| Quantity | Expression | Meaning |
| -------- | ---------- | ------- |
| Effective width | `W_e = W_MMI + (λ/π)·(n_c/n_r)^(2σ)/√(n_r²−n_c²)` | Goos–Hänchen correction; σ = 0 for TE |
| Beat length | `L_π = 4 n_r W_e² / (3 λ)` | Distance over which modes 0 and 1 accumulate a π relative phase |
| MMI length | `L_MMI = 3 L_π / 8` | First two-fold image |
| Output offset | `d_y = W_e / 4` | Position of each output image |

`L_MMI = 3L_π/8` follows from the fact that, for a centered input, only the even modes are
excited, so the field exactly reproduces itself every `3L_π/4` and forms two equal images
at the half-period `3L_π/8`. See [`../../MZI/MMI Theory.md`](../../MZI/MMI%20Theory.md) for
the full derivation.

## Why EME instead of FDTD

EME divides the device into cells along the propagation direction and expands the field in
the local eigenmodes of each cell. Three consequences matter here:

- **Mode beating is the physics of the device**, and EME represents it directly rather than
  resolving it on a spatial grid.
- **Length sweeps are essentially free.** Once the modes of each cell are computed, changing
  the MMI length only changes a propagation phase — so the 31-point sweep in `step09` runs
  in seconds. The same sweep in FDTD would mean rebuilding and re-running the simulation
  each time.
- **It is 3D-accurate** for structures whose cross-section changes slowly, which is true of
  tapers and straight MMI bodies.

## Files

| File | Section | Purpose |
| ---- | ------- | ------- |
| `main.lsf` | — | Driver; calls the steps in order |
| `step01_setup.lsf` | 1 | Units, platform constants, material names |
| `step02_mmi_design.lsf` | 2 | Analytical `W_MMI`, `L_π`, `L_MMI`, `d_y` |
| `step03_geometry.lsf` | 3 | Builds waveguides, tapers, MMI body, BOX, cladding |
| `step04_fde_mode_check.lsf` | 4 | FDE mode count; refines `L_MMI` from simulated `β₀ − β₁` |
| `step05_eme_setup.lsf` | 5 | EME region and the five cell groups |
| `step06_eme_ports.lsf` | 6 | One input port, two output ports |
| `step07_eme_monitors.lsf` | 7 | 2D field-profile monitor |
| `step08_run_simulation.lsf` | 8 | Propagate, then sweep wavelength across the C-band |
| `step09_length_sweep.lsf` | 9 | Sweep `L_MMI` over ±20 % via an EME propagation sweep |
| `step10_sweep_analysis.lsf` | 10 | Pick the optimum length; report IL and balance |
| `step11_wavelength_sweep.lsf` | 11 | Broadband verification at the optimal length |
| `step12_dy_sweep.lsf` | 12 | Sweep the output offset `d_y`, rebuilding the geometry per point |
| `length_sweep.py` | — | Plots IL and split versus length from `length_sweep.mat` |
| `wavelength_sweep.py` | — | Plots transmission, IL and imbalance versus wavelength |
| `dy_sweep.py` | — | Plots IL and imbalance versus `d_y` |
| `*.mat` | — | Sweep outputs, written by `step09`, `step11` and `step12` |
| `*.png` | — | The four result figures, written by the Python scripts |
| `reference/varfdtd_reference.lsf` | — | Superseded varFDTD attempt, kept for reference |

## Running it

In Lumerical MODE:

```lumerical
cd("path/to/MMI/MODE");
main;
```

Lumerical's interpreter has no `include`, so each `stepNN_*.lsf` is called by its base name
and all steps share one global workspace. To re-run one stage without rebuilding everything,
call it directly from the script prompt:

```lumerical
step04_fde_mode_check;
```

The setup begins with `addpath("../../shared")` followed by `materials;`, so the folder must
be run in place with `shared/` two levels up.

## Post-processing

Each sweep writes its curves to a `.mat` file with `matlabsave`, and a Python script turns
that file into a figure. Install the dependencies once (`pip install -r requirements.txt` at
the repository root), then run any of them from the root:

```bash
python MMI/MODE/length_sweep.py
python MMI/MODE/wavelength_sweep.py
python MMI/MODE/dy_sweep.py
```

Each script prints a table of the values at the optimum and writes its figure next to itself.
They read the `.mat` files with `h5py`, because `matlabsave` writes MATLAB v7.3 (HDF5).

| Script | Reads | Writes | Shows |
| ------ | ----- | ------ | ----- |
| `length_sweep.py` | `length_sweep.mat` | `mmi_il_vs_length.png` | IL and both port transmissions vs `L_MMI` |
| `wavelength_sweep.py` | `wavelength_sweep.mat` | `mmi_transmission_vs_wavelength.png` | IL and both port transmissions across the C-band |
| `wavelength_sweep.py` | `wavelength_sweep.mat` | `mmi_imbalance_vs_wavelength.png` | splitting imbalance across the C-band |
| `dy_sweep.py` | `dy_sweep.mat` | `mmi_il_vs_dy.png` | IL and imbalance vs `d_y` |

## Design flow

The flow splits into a build half and a solve-and-optimise half:

- **Build and refine** (`step01`–`step04`) — units and platform constants, the analytical sizing,
  the geometry, and an FDE mode check that replaces the analytical beat length with the simulated
  one and rebuilds the geometry around it.
- **Solve and optimise** (`step05`–`step12`) — EME setup, ports and monitors, the first run with
  its wavelength sweep, then the length sweep and the optimum it picks, the broadband check at
  that length, and the output-offset sweep.

Note that `step02` deliberately uses the bulk silicon index in the slab formula, which
ignores vertical confinement and therefore is only approximate.
`step04` replaces it with a beat length derived from the true eigenmodes and rebuilds the
geometry accordingly — so the length that `step05` onwards operate on is the refined value.
The correction is large: `L_π` falls from 51.7 µm to 39.4 µm and `L_MMI` from 19.4 µm to 14.8 µm,
which is why the sweeps exist rather than the formula being trusted.

## Results

The three sweeps have been run, and their `.mat` outputs and the four figures are committed.

| Metric | Result |
| ------ | ------ |
| Optimal length (`step09`) | **14.00 µm** by minimum IL; IL at the FDE-analytic 14.79 µm is 0.450 dB |
| Optimal output offset (`step12`) | **1.019 µm** by minimum IL; IL at the analytic `W_e/4` = 1.039 µm is 0.128 dB |
| Split at the optimum | `T_top = T_bot = 0.4864` → 48.6 % / 48.6 %, 97.3 % total |
| Imbalance | zero to within 7×10⁻⁹ dB |
| Insertion loss at 1550 nm | 0.120 dB |
| Insertion loss, 1530–1570 nm | 0.219 dB worst case, 0.162 dB mean |
| Insertion loss, 1500–1600 nm | 0.501 dB worst case (1597 nm), 0.239 dB mean |

![Insertion loss and split versus MMI length](mmi_il_vs_length.png)

![Insertion loss versus output offset](mmi_il_vs_dy.png)

![Transmission across the C-band](mmi_transmission_vs_wavelength.png)

![Splitting imbalance across the C-band](mmi_imbalance_vs_wavelength.png)

The imbalance curve is flat at zero because it has to be: a centred-input 1×2 MMI whose output
ports sit symmetrically about the axis is mirror-symmetric, so the two output powers are equal by
construction, and the simulation reproduces that to 10⁻⁹ dB. Read that curve as a consistency check
on the port setup rather than as a design property. The `d_y` sweep is about total transmission,
and the optimum it finds is shallow — 0.007 dB separates the swept offset from the analytic one —
so `d_y` is a weak parameter in this design.

The length sweep's minimum is broad and, at the 0.1 dB level, not smooth: neighbouring points near
the optimum read 0.122, 0.120, 0.278 and 0.200 dB, which is EME discretisation rather than physics.
`step10` selects the single lowest point. A more defensible rule — judge candidates on the
band-averaged or worst-case insertion loss and prefer the flat part of the curve — is the one
recorded as step 6 of the component-optimisation workflow in
[`../../MZI/Plan.md` §5](../../MZI/Plan.md).

## Status

**The sweeps are run and the design point is set.** The length sweep (`step09`–`step10`) picks
`L_MMI = 14.00 µm`; the output-offset sweep (`step12`) picks `d_y = 1.019 µm`, which is applied in
`step02_mmi_design.lsf`; and the wavelength sweep (`step11`) confirms the split and the loss across
the C-band. Both targets are met over the design bandwidth — 50:50 exactly, by symmetry, and
insertion loss below 0.5 dB with 0.12 dB at 1550 nm and 0.219 dB worst case over 40 nm.

Remaining work, in the order it should be done:

- [ ] Verify the taper length is sufficient by doubling it and confirming the loss does not move
- [ ] Sweep the input taper width, then re-sweep `L_MMI` around the new optimum
- [ ] Sweep the output taper width
- [ ] Repeat the length and wavelength sweeps with ±10–20 nm of width bias, and select on the
      band-averaged or worst-case insertion loss instead of the single-point minimum
- [ ] Re-run the `d_y` sweep after any of the above changes the geometry — it needs a full rebuild
      per point, so it is the most expensive step to repeat
- [ ] Export the S-parameter matrix for INTERCONNECT
- [ ] Validate one design point in 3D FDTD

This list is the component-optimisation sequence written out in
[`../../MZI/Plan.md` §5](../../MZI/Plan.md) — the version of it meant to be reused on the next
component, so the MMI is where the recipe is exercised rather than the reason for it.

## Reference

Soldano, L. B., & Pennings, E. C. M. (1995). Optical multi-mode interference devices based on
self-imaging: principles and applications. *Journal of Lightwave Technology*, 13(4), 615–627.
