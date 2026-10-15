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

## Files

| File | Purpose |
| ---- | ------- |
| `main.lsf` | Driver; imports the design point, builds the project, runs and saves |
| `step01_setup.lsf` | Units, material names, `matlabload` of the design point |
| `step02_geometry.lsf` | MMI structure group: input waveguide, tapers, body, output waveguides, BOX, cladding |
| `step03_fdtd_region.lsf` | FDTD region, mesh accuracy, shut-off |
| `step04_sources_monitors.lsf` | Three S-parameter ports (input and the two output waveguides) and a field profile monitor |
| `step05_save_results.lsf` | Runs the simulation; saves the S-parameters, transmission and field profile |
| `fdtd_results.py` | Post-processing: reads the `.mat`, prints the band summary, plots the transmission, reflection and insertion loss, and the field map |
| `mmi_fdtd_results.mat` | Raw solver output, MATLAB v7.3, read by `h5py`; the run the scripts reproduce; not committed |
| `mmi_fdtd_results_MeshAcc3.mat` | The same run one step down in mesh, kept under a tagged name; also not committed |
| `mmi_fdtd_results_MeshAcc2.mat` | The same run at the coarsest setting, kept under a tagged name; also not committed |

## Running it

```lumerical
cd("path/to/MMI/FDTD");
main;
```

`main` builds the project, runs it, and writes `mmi_fdtd_results.mat` next to `step05_save_results.lsf`,
the file `filename` at the top of `fdtd_results.py` points at.

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

## Mesh accuracy

The same geometry was solved at three mesh accuracies, 2, 3 and 4, with the FDTD region and the
wavelength grid held fixed, so the mesh is the only thing that differs between the runs. The
insertion loss at 1550 nm falls from 0.180 dB at the coarse end to 0.114 dB in the middle and
0.100 dB at the shipped setting: a first step of 0.065 dB and a second of 0.014 dB, a factor of
about five smaller, so the series is settling rather than still moving. The per-port transmission
reads the same way, 0.4797, 0.4870 and 0.4886, and the total 95.9 %, 97.4 % and 97.7 %.

The reflection is the one quantity that is not monotone in the mesh: at 1550 nm the middle setting
reads 5.3×10⁻⁶ against 1.1×10⁻⁶ at the shipped one and 1.5×10⁻⁷ at the coarse end. That is noise at
the −50 dB level rather than a trend, and all three stay better than −33 dB across the span. The
three also sample the field profile monitor on grids that scale with the mesh, 1259 × 141 and
1761 × 196 against 2262 × 248, so the field map is drawn at the coarser resolution whenever a
coarser run is the one plotted.

The finest run is the one kept, since the two steps put it 0.014 dB from the middle run and 0.079 dB
from the coarse one, both well inside the 0.5 dB budget, and no run finer than it exists on this
geometry. The way the steps shrink, 0.065 dB and then 0.014 dB, would place the continuum value about
0.004 dB below the shipped figure if the trend held, but that is an extrapolation from two steps
rather than a measurement.

## Results

One run of the frozen design point with its output tapers and straight output guides, 101 frequency
points over 1500–1600 nm. The grid is uniform in frequency, so the sample nearest 1550 nm sits at
1550.4 nm; the EME value read against it is at 1550 nm. The table carries all three mesh settings,
and nothing but the mesh differs between the columns. The two output powers agree to better than
2.8×10⁻⁵ in `|S|²` at every setting, an imbalance under 2.5×10⁻⁴ dB, as the mirror symmetry requires.
At the shipped setting the insertion loss also stays inside the 0.5 dB target across the whole 100 nm
span, not only the 40 nm design bandwidth, and the middle setting does too, on 0.486 dB at the red end
against 0.470 dB; the coarse run does not, leaving the target from 1593 nm to 1600 nm.

| Metric | Mesh accuracy 4 (ships) | Mesh accuracy 3 | Mesh accuracy 2 |
| ------ | ----------------------- | --------------- | --------------- |
| Split at 1550 nm | `T_top = T_bot = 0.4886` → 48.9 % / 48.9 %, 97.7 % total | `T_top = T_bot = 0.4870` → 48.7 % / 48.7 %, 97.4 % total | `T_top = T_bot = 0.4797` → 48.0 % / 48.0 %, 95.9 % total |
| Insertion loss at 1550 nm | **0.100 dB** | 0.114 dB | 0.180 dB |
| Insertion loss over 1500–1600 nm | 0.067 dB best (1535 nm), **0.470 dB worst** (1600 nm) | 0.064 dB best (1527 nm), 0.486 dB worst (1600 nm) | 0.061 dB best (1523 nm), 0.633 dB worst (1599 nm) |
| Band-averaged insertion loss | 0.114 dB over the 40 nm design band (1530–1570 nm), 0.179 dB over the full span | 0.127 dB over the 40 nm design band, 0.187 dB over the full span | 0.178 dB over the 40 nm design band, 0.228 dB over the full span |
| Reflection at 1550 nm | −59.8 dB (`R = 1.1×10⁻⁶`) | −52.8 dB (`R = 5.3×10⁻⁶`) | −68.1 dB (`R = 1.5×10⁻⁷`) |
| Reflection over 1500–1600 nm | −75.6 to −35.6 dB (worst at 1505 nm) | −68.9 to −37.1 dB (worst at 1501 nm) | −68.1 to −33.7 dB (worst at 1598 nm) |

Read against the EME result for the same design point (0.069 dB and `T = 0.4921` per port at 1550 nm,
in [`../MODE/`](../MODE/)), the shipped run agrees to 0.03 dB in insertion loss and 0.004 in per-port
transmission, where the coarse run reads 0.11 dB above the same figure. That agreement is what this build
exists to establish: EME assumes a piecewise-uniform structure along the propagation axis and a finite
mode set, and the 3D FDTD run, which assumes neither, reproduces the loss.

`fdtd_results.py` writes the three figures below; `T_top` and `T_bot` are to be read directly
against the EME `s12`/`s13` of the same design point.

| Figure | Shows |
| ------ | ----- |
| `mmi_fdtd_S2-params.png` | the two output transmissions `T_top`, `T_bot` and the reflection `R` across the band |
| `mmi_fdtd_transmission_vs_wavelength.png` | `T_top`, `T_bot` and the insertion loss, against the 0.5 dB target |
| `mmi_fdtd_field_profile.png` | the field intensity at 1550 nm (inferno): the two-fold image forming in the body and the split into the two output tapers |

## Caveats

- Like every solver folder here, the scripts `addpath("../../shared")`, so this folder must
  be run in place with `shared/` two levels up.
