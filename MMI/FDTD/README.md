# 1×2 MMI, 3D FDTD validation build

A scaffold that reconstructs the optimised 1×2 MMI in a full 3D FDTD simulation and
post-processes the result, to cross-check the EME result from [`../MODE/`](../MODE/). It
validates one design point; it is not a re-optimisation, and it performs no parameter sweep.

## Design point

The geometry is not defined here. It is imported from `../MODE/mmi_design_point.mat`, which is
written by `../MODE/step14_save_design.lsf`. That file carries the design point as built in the MODE
flow plus the sweep optima; this build uses the optima, the MMI length `L_opt` = 22.162 µm, the
output offset `dy_opt` = 1.2690 µm, and the two taper widths `width_opt` = 1.3333 µm (input) and
`width_out_opt` = 1.3833 µm (output).

That `.mat` is not committed (see [Post-processing](../MODE/README.md#post-processing)), so a fresh
clone has to regenerate it before this build will run.

Regenerate it in the MODE folder after any change to the optimisation:

```lumerical
cd("path/to/MMI/MODE");
step14_save_design;
```

## Files

| File | Purpose |
| ---- | ------- |
| `main.lsf` | Driver; imports the design point, builds the project, runs and saves |
| `step01_setup.lsf` | Units, material names, `matlabload` of the design point |
| `step02_geometry.lsf` | MMI structure group: waveguides, tapers, body, BOX, cladding |
| `step03_fdtd_region.lsf` | FDTD region, mesh accuracy, shut-off |
| `step04_sources_monitors.lsf` | Three S-parameter ports and a field profile monitor |
| `step05_save_results.lsf` | Runs the simulation; saves the S-parameters, transmission and field profile |
| `fdtd_results.py` | Post-processing: reads the `.mat`, prints the band summary, plots the transmission, reflection and insertion loss, and the field map |

## Running it

```lumerical
cd("path/to/MMI/FDTD");
main;
```

`main` builds the project, runs it, and writes `mmi_fdtd_results.mat` next to
`step05_save_results.lsf`, the file `filename` at the top of `fdtd_results.py` points at.

`step03_fdtd_region.lsf` ships with `mesh accuracy = 5`, the setting the quoted results come from, so
the script as committed reproduces them. The convergence check behind that choice is under
[Caveats](#caveats).

To inspect the layout before spending the run, comment out the `step05_save_results;` call,
build with `main`, then call `step05_save_results;` on its own afterwards.

The port group's active source must be the input port (`source`). FDTD excites one port mode
at a time, so a single run gives the S-column for input excitation, which is all a passive
splitter needs.

Then post-process, from the repository root:

```bash
python MMI/FDTD/fdtd_results.py
```

## Post-processing

`fdtd_results.py` reads the `.mat` with `h5py` (Lumerical writes MATLAB v7.3, i.e. HDF5) and
prints the same kind of band summary as the EME scripts in [`../MODE/`](../MODE/): the number
of frequency points, the wavelength range, the worst-case insertion loss and reflection
against target, and a table every 10 nm carrying `T_top`, `T_bot`, the reflection, the
insertion loss and the imbalance.

The imbalance is read back from the file and tabulated, but it is not plotted: a
centred-input 1×2 MMI with its output ports placed symmetrically is mirror-symmetric, so
`T_top = T_bot` by construction, and the column verifies the port setup rather than
measuring a design property.

## Results

One run of the frozen design point, 101 frequency points over 1500–1600 nm, at mesh accuracy 5. The
two output powers are equal to better than 3×10⁻⁵ in `|S|²`, as the mirror symmetry requires, and
the insertion loss stays inside the 0.5 dB target across the whole 100 nm span, not only the 40 nm
design bandwidth.

| Metric | Result |
| ------ | ------ |
| Split at 1550 nm | `T_top = T_bot = 0.4883` → 48.8 % / 48.8 %, 97.7 % total |
| Insertion loss at 1550 nm | **0.103 dB** |
| Insertion loss over 1500–1600 nm | 0.077 dB best (1535 nm), **0.42 dB worst** (1600 nm) |
| Reflection at 1550 nm | −39.7 dB (`R = 1.1×10⁻⁴`) |
| Reflection over 1500–1600 nm | −41.7 to −37.0 dB |

Read against the EME result for the same design point (0.069 dB and `T = 0.4921` per port at
1550 nm, in [`../MODE/`](../MODE/)), the two solvers agree to 0.03 dB in insertion loss and 0.004 in
per-port transmission. That agreement is what this build exists to establish: EME assumes a
piecewise-uniform structure along the propagation axis and a finite mode set, and the 3D FDTD run,
which assumes neither, reproduces the loss.

`fdtd_results.py` writes the three figures below; `T_top` and `T_bot` are to be read directly
against the EME `s12`/`s13` of the same design point.

| Figure | Shows |
| ------ | ----- |
| `mmi_fdtd_S2-params.png` | the two output transmissions `T_top`, `T_bot` and the reflection `R` across the band |
| `mmi_fdtd_transmission_vs_wavelength.png` | `T_top`, `T_bot` and the insertion loss, against the 0.5 dB target |
| `mmi_fdtd_field_profile.png` | the field intensity at 1550 nm (inferno): the two-fold image forming in the body and the split into the two output tapers |

## Caveats

- The mesh and the FDTD extents are starting points, so the run was checked for convergence rather
  than trusted at one setting. The same geometry at mesh accuracies 2, 3 and 5 gives 0.171, 0.123
  and 0.103 dB of insertion loss at 1550 nm, and 0.481, 0.486 and 0.488 per port: monotone in the
  mesh, with the step from 2 to 3 worth 0.048 dB and from 3 to 5 only 0.020 dB, which puts the
  finest run within about 0.02 dB of the converged value. `step03_fdtd_region.lsf` ships at the
  finest setting, `mesh accuracy = 5`, so the committed script reproduces the numbers above;
  dropping it back to 2 is the cheap version of this check, at a cost of about 0.07 dB.
- The ports return S-parameters and `step05` takes `|S|²` as the transmission. Only the input
  port is excited, so the file holds one S-column (input excitation), not the full matrix; for
  the full matrix, excite each port in turn with the S-parameter sweep.
- The field profile is sampled at every frequency as well as every grid point, so the results
- Like every solver folder here, the scripts `addpath("../../shared")`, so this folder must
  be run in place with `shared/` two levels up.
