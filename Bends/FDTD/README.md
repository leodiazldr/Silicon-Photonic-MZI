# Bézier S-bend, 3D FDTD

A 3D FDTD characterisation of the low-loss Bézier bend introduced in
[`../bezier_curves.py`](../bezier_curves.py). The geometry study there showed
that a cubic Bézier ramps its curvature smoothly from 0 to a minimum and back to
0, unlike a circular arc, whose curvature jumps at the straight-to-arc junction.
The FDE sweep in [`../MODE/`](../MODE/) turned that shape into a loss estimate;
this folder puts a bend of the same family through a full-vector solver and
returns its two-port S-parameters, so it can be dropped into the MZI model as a
component of its own.

**Note:** The loss considered here is due to mode mismatching. Losses due to light scattering are not considered here.

| Parameter | Value |
| --------- | ----- |
| Waveguide | 500 nm × 220 nm Si strip |
| Solver | FDTD (3D), 1550 nm TE |
| Radius `R` | 13 µm |
| Shape `δ` | 0.2 |
| S span | axial 2R = 26 µm, lateral offset R = 13 µm |
| Wavelength | 1500 – 1600 nm (C-band), 101 points |
| Mesh accuracy | 2, chosen against 3 (see [Mesh accuracy](#mesh-accuracy)) |
| Figure of merit | band-averaged insertion loss; two-port S-parameters |

## The S-bend geometry

The bend is a Bézier path through six poles, in the order the script passes them
to `addwaveguide`:

```
P0=(0,0),  P1=(Rδ,0),  P2=(R,Rδ),  P3=(R,R(1-δ)),  P4=(R(2-δ),R),  P5=(2R,R)
```

The pole count fixes the degree, so this is a single Bézier of degree five, not
a chain of cubics. `P0-P1` and `P4-P5` are horizontal, so the path leaves and
arrives tangent to the propagation axis, and `P2-P3` is vertical, so the turn is
at its steepest at the midpoint. The pole set is symmetric about `(R, R/2)`, so
the path is too: it crosses that point on a vertical tangent.

The curve is scaled so the lateral offset equals the radius: the bend rises by
`R = 13 µm` over an axial run of `2R = 26 µm`. `δ` sets how far the poles pull
off the corner: as `δ → 0` they bunch onto the two straight leads and the path
degenerates towards a right-angle step at the midpoint, while larger `δ` grows
the shoulders and spreads the turn out. `P2` stays below `P3` for `δ < 0.5`, and
`δ = 0.2` is the chosen value.

The path is 29.5 µm long between the leads, so with the two 5 µm leads the
guided path between the ports is 39.5 µm.

## How the flow is built

The flow is a `main.lsf` driver plus numbered steps, sharing one global
workspace, after the pattern of [`../../MMI/FDTD/`](../../MMI/FDTD/). Only one
bend is built, at the design `δ`, and the flow solves it at a single mesh
setting; the mesh comparison below comes from running the same flow twice.

| Step | Does |
| ---- | ---- |
| `step01_setup.lsf` | Units, platform constants, `R`, `δ` |
| `step02_geometry.lsf` | Leads, S-bend waveguide, BOX, cladding |
| `step03_fdtd_region.lsf` | FDTD region, mesh accuracy (`2`), shut-off |
| `step04_sources_monitors.lsf` | Two S-parameter ports and a field profile monitor |
| `step05_save_results.lsf` | Runs the simulation; writes `bend_fdtd_results.mat` |

## Files

| File | Purpose |
| ---- | ------- |
| `main.lsf` | Driver; runs the build, the solve and the save |
| `step01_setup.lsf` … `step05_save_results.lsf` | The numbered steps, called by `main` |
| `bend_results.py` | Post-processing: reads `bend_fdtd_results.mat`, prints the band summary, plots transmission/reflection and the field |
| `bend_fdtd_results.mat` | Raw solver output, MATLAB v7.3, read by `h5py`; not committed |
| `bend_fdtd_results_MeshAcc2.mat` | The mesh-accuracy-2 run, kept under a tagged name; also not committed |
| `bend_S2-params.png` | Result figure: `\|S\|²` vs wavelength |
| `bend_field_profile.png` | Result figure: `\|E\|²` over the bend at 1550 nm |

## Running it

In Lumerical (2020 R2.4), from this folder:

```lumerical
cd("path/to/Bends/FDTD");
main;
```

`main` builds the device and runs it once, writing `bend_fdtd_results.mat` next
to the scripts. `step03_fdtd_region.lsf` ships at `mesh accuracy = 2`, which is
the setting the S-parameters handed to INTERCONNECT come from; raise it to 3 for
a finer check of the same geometry, at the cost of a longer solve. To inspect the
layout before spending the solve, comment out the `step05_save_results` call and
run the build steps on their own.

Then post-process, from the repository root:

```bash
python Bends/FDTD/bend_results.py
```

## Post-processing

`bend_results.py` reads `bend_fdtd_results.mat` with `h5py` and reports the
insertion loss at 1550 nm, the worst-case loss over the band, the peak
reflection and the phase of the transmission, then plots `|S|²` against
wavelength and the `|E|²` field profile. The band summary is the figure of
merit, not the single lowest point: a single-frequency minimum
can sit on solver discretisation noise.

## Mesh accuracy

The bend was solved at mesh accuracy 3 and at mesh accuracy 2, with everything
else held fixed. The insertion loss at 1550 nm moves from 0.0253 dB to 0.0321 dB,
a shift of 0.007 dB, a fraction of the loss the bend carries at that wavelength:
the mesh is not what sets the loss. Across the band the two runs diverge a little
more, by up to 0.067 dB near 1531 nm and by 0.009 dB on average, closest at the
design wavelength and widest over 1500–1535 nm. Reflection is small at both
settings and roughly thirty times larger at the coarse mesh, 7.4×10⁻⁵ against
2.3×10⁻⁶ at 1550 nm, which is still noise in a loss budget.

`mesh accuracy = 2` is the setting kept: it is the cheaper solve, and the
difference it leaves is a fraction of the bend loss itself.
`step03_fdtd_region.lsf` ships at 2, and the two-port S-parameters handed to
INTERCONNECT are taken from that run. The coarse mesh also samples the field
monitor on a smaller grid, 815 × 332 against 1139 × 464, so the field map is
drawn at that resolution when the shipped run is the one plotted.

## Results

One solve of the single bend at the design shape, with the input port excited
and the output port reading the transmitted mode, over 101 frequency points
spread evenly in frequency across 1500–1600 nm (the sample nearest 1550 nm is at
1550.4 nm). The bend was solved at both mesh settings, so the table carries both;
nothing but the mesh differs between the two columns, and the right-hand one is
the shipped run, the one the INTERCONNECT S-parameters come from.

| Metric | Mesh accuracy 3 | Mesh accuracy 2 (ships) |
| ------ | --------------- | ----------------------- |
| Transmission at 1550 nm | `T = 0.9942` | `T = 0.9926` |
| Insertion loss at 1550 nm | 0.0253 dB | **0.0321 dB** |
| Insertion loss over 1500–1600 nm | 0.0237 dB best (1547 nm), 0.2383 dB worst (1506 nm) | 0.0240 dB best (1556 nm), **0.2156 dB worst** (1516 nm) |
| Band-averaged insertion loss | 0.041 dB over the 40 nm design band (1530–1570 nm), 0.089 dB over the full span | 0.060 dB over the 40 nm design band, 0.098 dB over the full span |
| Reflection at 1550 nm | 2.3×10⁻⁶, −56.4 dB | 7.4×10⁻⁵, **−41.3 dB** |
| Reflection over 1500–1600 nm | 2.5×10⁻⁸ to 5.6×10⁻⁵ (**−42.5 dB worst**, at 1595 nm) | 5.7×10⁻⁷ to 2.9×10⁻⁴ (**−35.4 dB worst**, at 1567 nm) |

Read against the FDE estimate in [`../MODE/`](../MODE/), the radius sweep there
puts the total loss of a 13 µm quarter arc at 0.0060 dB at 1550 nm (0.0019 dB of
mode mismatch plus 0.0041 dB of propagation over the arc, with its constant
2 dB/cm). The 0.025 dB and 0.032 dB above are four and five times larger but only
0.02 to 0.03 dB higher in absolute terms, and the two are not the same geometry:
the FDE figure is a quarter circle, this one is a 90° Bézier S-bend spanning
26 µm axially. Read the comparison as agreement in scale rather than as a
matched measurement.

| Figure | Shows |
| ------ | ----- |
| `bend_S2-params.png` | `T = \|S_out\|²` and `R = \|S_in\|²` against wavelength |
| `bend_field_profile.png` | `\|E\|²` at 1550 nm over the leads and the bend (inferno), where the mode follows the curve with no visible radiation into the cladding |

## See also

- [`../MODE/README.md`](../MODE/README.md), the FDE radius sweep and the Bézier
  curvature study this follows on from.
- [`../../MMI/FDTD/README.md`](../../MMI/FDTD/README.md), the MMI block the bend
  is paired with in the MZI.
- [`../../shared/materials.lsf`](../../shared/materials.lsf), the Si and SiO₂
  models.

## Reference

1. Cherchi, M., Ylinen, S., Harjanne, M., Kapulainen, M., & Aalto, T. (2013).
   Dramatic size reduction of waveguide bends on a micron-scale silicon photonic
   platform. *Optics Express*, 21(15), 17814–17823.
2. Chrostowski, L., & Hochberg, M. (2015). *Silicon Photonics Design: From
   Devices to Systems*. Cambridge University Press, ch. 4.
