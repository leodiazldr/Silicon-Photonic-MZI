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
| `mmi_fdtd_results.mat` | Raw solver output, MATLAB v7.3, read by `h5py`; the mesh-accuracy-4 run, not committed |
| `mmi_fdtd_results_RawMesh.mat` | The mesh-accuracy-2 run, kept under a tagged name; also not committed |

## Running it

```lumerical
cd("path/to/MMI/FDTD");
main;
```

`main` builds the project, runs it, and writes `mmi_fdtd_results.mat` next to `step05_save_results.lsf`,
the file `filename` at the top of `fdtd_results.py` points at.

`step03_fdtd_region.lsf` ships with `mesh accuracy = 4`, and the table and the figures below are the run
saved in `mmi_fdtd_results.mat`, which is what these scripts produce, so re-running the flow reproduces
them. Drop the mesh accuracy to 2 for the cheaper cross-check, at the cost of the accuracy discussed in
[Mesh accuracy](#mesh-accuracy). See [Results](#results).

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

One run of the frozen design point with its output tapers and straight output guides, 101 frequency
points over 1500–1600 nm. The grid is uniform in frequency, so the sample nearest 1550 nm sits 
at 1550.4 nm; the EME value read against it is at 1550 nm. The MMI was solved
at both mesh settings, so the table carries both, and nothing but the mesh differs between the two
columns. The two output powers are equal to better than 2.1×10⁻⁵ in `|S|²` at either mesh setting, an
imbalance under 2×10⁻⁴ dB, as the mirror symmetry requires; at the shipped setting the insertion loss also
stays inside the 0.5 dB target across the whole 100 nm span, not only the 40 nm design bandwidth.

| Metric | Mesh accuracy 4 (ships) | Mesh accuracy 2 |
| ------ | ----------------------- | --------------- |
| Split at 1550 nm | `T_top = T_bot = 0.4886` → 48.9 % / 48.9 %, 97.7 % total | `T_top = T_bot = 0.4797` → 48.0 % / 48.0 %, 95.9 % total |
| Insertion loss at 1550 nm | **0.100 dB** | 0.180 dB |
| Insertion loss over 1500–1600 nm | 0.067 dB best (1535 nm), **0.470 dB worst** (1600 nm) | 0.061 dB best (1523 nm), 0.633 dB worst (1599 nm) |
| Band-averaged insertion loss | 0.114 dB over the 40 nm design band (1530–1570 nm), 0.179 dB over the full span | 0.178 dB over the 40 nm design band, 0.228 dB over the full span |
| Reflection at 1550 nm | −59.8 dB (`R = 1.1×10⁻⁶`) | −68.1 dB (`R = 1.5×10⁻⁷`) |
| Reflection over 1500–1600 nm | −75.6 to −35.6 dB (worst at 1505 nm) | −68.1 to −33.7 dB (worst at 1598 nm) |

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

- The mesh and the FDTD extents are starting points, so convergence still has to be checked.
- Like every solver folder here, the scripts `addpath("../../shared")`, so this folder must
  be run in place with `shared/` two levels up.
