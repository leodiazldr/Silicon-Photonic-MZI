# Silicon-Photonic MZI Modulator on 220 nm SOI — Design Plan

A component-level design and simulation project on 220 nm silicon-on-insulator, organised around a
Mach–Zehnder interferometer (MZI) for BB84 quantum key distribution state encoding.

Each component is designed analytically, verified numerically, optimised by parametric sweeping,
and checked for robustness across the band and against fabrication bias. §5 states that workflow in
full, and §4 records the results of applying it.

**Revised 2026-09-30.** The original version, written 2026-07-24, was a 12-week schedule. This
version records what has actually been built — including the measured MMI results — and scopes the
remaining work to near-term, achievable steps, with the larger items consolidated under "Later".

---

## 1. What this project demonstrates

- The **full photonic design flow**: analytical sizing → numerical verification → parametric
  optimisation → robustness and tolerance analysis → system-level composition → layout.
- **Active and passive components**, not just one or the other: a carrier-depletion modulator whose
  electrical and optical models have to agree, alongside passive splitters and routing.
- **Two-solver coupling.** The phase shifter spans CHARGE (drift-diffusion) and MODE (FDE), with a
  carrier map travelling between them. Getting the coordinate conventions and the solve window to
  match between two solvers is the part of the flow that does not appear in a textbook.
- **Optimisation with a stated selection rule.** Every component here has a figure of merit, a
  sweep that measures it, and a recorded reason for the design point chosen.
- **Integrated photonics for quantum communication** — how a monolithic device replaces a
  benchtop interferometer.

It complements an experimental BB84 QKD thesis (free-space, polarization-encoded): the thesis
measures a discrete-component link, this project designs the integrated version of the same
function.

---

## 2. Platform

**Silicon photonics on 220 nm SOI.**

| Parameter       | Choice                                               |
| --------------- | ---------------------------------------------------- |
| Wafer           | SOI, 220 nm Si on 2 µm buried oxide                  |
| Foundry process | IME / AMF / AIM (standard 220 nm SOI)                |
| Wavelength      | 1550 nm (telecom C-band)                             |
| Polarization    | TE (single-mode)                                     |
| Modulator type  | Lateral PN junction, carrier depletion               |
| Layout tool     | gdsfactory (Python-based, parametric) or KLayout     |
| PDK             | SiEPIC PDK (open-source) or foundry PDK if available |
| Solver version  | Ansys Lumerical 2020 R2.4                            |

---

## 3. Scope and status

The design flow is organised by component. Two decisions made during the work are worth recording,
because they differ from the original plan:

- **EME rather than 3D FDTD for the MMI.** The eigenmode-expansion solver resolves the mode-beating
  physics that actually forms the image, and a length sweep becomes a propagation sweep on one cell
  group instead of a full rebuild and re-run per point. The superseded varFDTD implementation is
  kept under `MMI/MODE/reference/` for cross-checks.
- **Linear input/output tapers only.** The original plan called for comparing linear against
  parabolic taper profiles. The linear tapers meet the target, so the parabolic variant has been
  dropped from scope; it is noted under "Later" in case the device needs another fraction of a dB.

| Component | Method | Status |
| --------- | ------ | ------ |
| Single-mode waveguide | FDE (MODE) | Complete — width and wavelength sweeps |
| Low-loss bends | FDE (MODE) | Complete — radius sweep and Bézier curvature study |
| 1×2 MMI splitter | EME (MODE) | Swept and characterised — length, both taper widths, output offset and wavelength all swept, figures committed; 0.069 dB at 1550 nm in EME, 0.103 dB in the 3D FDTD cross-check. Taper-length check, a length re-sweep and the width-bias robustness checks still open (§6.1) |
| PN junction phase shifter (electrical) | CHARGE drift-diffusion + AC | Complete |
| PN junction phase shifter (optical) | FDE (MODE) | Complete — V_π·L inside target |
| MZI system integration | INTERCONNECT | Not started |
| GDS layout | gdsfactory / KLayout | Not started |

---

## 4. Completed work

### 4.1 Waveguide (`Waveguide/MODE/`)

The 500 nm × 220 nm strip waveguide everything else is built on.

- 220 nm SOI stack with dispersive Si / SiO₂ models from `shared/materials.lsf`
- Width sweep 100–2000 nm in 50 nm steps, recording `n_eff`, `n_g` and the TE polarisation fraction
  of every mode found — which locates the single-mode window and shows where higher-order and
  cross-polarised modes appear
- Wavelength sweep at the nominal width across the C-band, giving `n_eff(λ)` and `n_g(λ)`

**Deliverable met:** mode profile, `n_eff` vs. width, `n_eff` vs. wavelength, single-mode condition
with fabrication tolerance.

### 4.2 Bends (`Bends/`)

- Mode-mismatch loss at the straight-to-bend junction versus radius of curvature, from an FDE
  overlap integral
- Bend loss model combining mismatch and propagation loss, giving an optimum radius
- Cubic Bézier curvature profile compared with a circular arc: the radius sweep brackets the
  minimum, since mismatch falls with radius while propagation loss grows

**Deliverable met:** bend loss vs. radius, minimum-radius specification, Bézier curvature study.

### 4.3 MMI splitter (`MMI/MODE/`)

Self-imaging 1×2 MMI — the 50/50 splitter and combiner of the MZI, and the component whose
optimisation is written up in §5 as the reusable procedure.

**Design targets:** 50:50 ± 1 %, insertion loss < 0.5 dB, bandwidth > 40 nm, in-phase outputs.

The design point is `W_MMI = 5.0 µm` with linear tapers (0.5 → `W_MMI/4` = 1.25 µm) on both sides.
The taper end width is not an independent constant: it is tied to the body as `W_MMI/4`, so that the
taper-to-body ratio stays fixed when the width changes. That tie is a starting point rather than a
result — the two taper-width sweeps move it wider, to 1.3333 µm on the input and 1.3833 µm on the
output. The analytic sizing at this width gives `W_e = 5.156 µm`, `L_π = 79.53 µm`,
`L_MMI = 3L_π/8 = 29.82 µm` and `d_y = W_e/4 = 1.2890 µm`.

The slab formula behind those numbers uses the bulk silicon index and so ignores vertical
confinement; step04 replaces the beat length with the simulated one. The correction is not small —
`L_π` falls from 79.53 µm to 61.56 µm, moving `L_MMI` from 29.82 µm to 23.085 µm — which is precisely
why the sweeps below exist rather than the formula being trusted.

| Sweep | Range and points | Figure of merit |
| ----- | ---------------- | --------------- |
| MMI length (`step09`) | 18.47 → 27.70 µm, 31 points (±20 % about the FDE-refined 23.085 µm) | minimum insertion loss |
| Input taper width (`step10`) | 1.00 → 1.50 µm, 31 points (±20 % about `W_MMI/4`) | minimum insertion loss |
| Output offset `d_y` (`step11`) | 1.189 → 1.389 µm, 11 points (±0.10 µm about the analytic 1.2890 µm) | minimum insertion loss |
| Output taper width (`step12`) | 1.00 → 1.50 µm, 31 points (±20 % about `W_MMI/4`) | minimum insertion loss |
| Wavelength (`step13`) | 1500 → 1600 nm, 101 points, on the optimised geometry | IL and split across the band |

**Results.** All five sweeps have been run and the figures are committed.

| Metric | Result |
| ------ | ------ |
| `L_MMI` (min IL) | 22.162 µm, vs 23.085 µm from the FDE-refined analytic value |
| Input taper width (min IL) | 1.3333 µm, vs 1.25 µm as built |
| `d_y` (min IL) | 1.2690 µm, vs 1.2890 µm analytic |
| Output taper width (min IL) | 1.3833 µm, vs 1.25 µm as built |
| Split at the optimum | 49.2 % / 49.2 % (`T = 0.4921` per port) |
| Imbalance | zero to within 7×10⁻⁷ dB |
| Insertion loss at 1550 nm | **0.069 dB** |
| Insertion loss, 1530 → 1570 nm | 0.127 dB worst case |
| Insertion loss, 1500 → 1600 nm | 0.155 dB mean, 0.397 dB worst (at 1510 nm) |

Each sweep leaves the tree at its optimum, so the insertion loss falls in turn — 0.126 dB after the
length sweep, 0.104 dB after the input taper, 0.100 dB after the output offset, and 0.069 dB once
the output taper is set. A 3D FDTD run of the final design point in `MMI/FDTD/` returns 0.103 dB, so
the EME figure survives a change of solver.

Two of these deserve comment.

The **imbalance is identically zero**, not merely small. A centred-input 1×2 MMI with output ports
placed symmetrically about the axis is mirror-symmetric, so `T_top = T_bot` by construction; the
simulation reproduces that to 10⁻⁷ dB. The imbalance curve is therefore a consistency check on the
port setup rather than an optimisation target, and the `d_y` sweep's real function is to maximise
the summed transmission, not to balance the split. The optimum that sweep finds is shallow, and
`d_y` remains a weak parameter: the four optima all sit on plateaus rather than peaks.

The **length sweep's minimum is broad and not smooth**. Point-to-point differences near the optimum
run to a few tenths of a dB, which is the EME discretisation, not physics. Picking the single lowest
point — which is what `step09` currently does — therefore risks selecting simulation noise. §5 step 6
states the rule that should be used instead: judge the candidate on the band-averaged or worst-case
transmission and sit on the flat part of the curve. The quoted 0.069 dB should be read to the
accuracy the solver supports.

The loss is also not flat in wavelength: 0.069 dB at 1550 nm rising to 0.397 dB towards the edges of
the C-band. Over the 40 nm the design targets, the worst case is 0.127 dB, so the bandwidth target
is met with margin; over the full 100 nm both targets still hold, the worst case staying inside
0.5 dB.

**Still outstanding:** nothing in the simulation flow, but four of the seven workflow steps in §5
are incomplete for this component. They are listed in §6.1.

### 4.4 Carrier-depletion phase modulator (`PhaseShifter/`)

The core of the project, and the only component spanning two solvers.

**Physics:** reverse bias on a lateral PN junction widens the depletion region, removing free
carriers from a growing volume of silicon. Through Soref–Bennett plasma dispersion the local index
rises, so the guided mode accumulates phase:

```
Δn    = -8.8×10⁻²²·ΔN_e - 8.5×10⁻¹⁸·(ΔN_h)^0.8
Δα    =  8.5×10⁻¹⁸·ΔN_e + 6.0×10⁻¹⁸·ΔN_h        [cm⁻¹]
Δφ(V) = (2π/λ)·Δn_eff(V)·L
```

Because the depletion edge moves on the dielectric relaxation timescale rather than the carrier
lifetime, the bandwidth is RC-limited: `f_3dB = 1/(2πRC)` from the junction capacitance and the
series resistance.

**Electrical model (CHARGE). Complete.**

- Lateral PN junction in a 220 nm rib, asymmetric profile `N_A = 2×10¹⁷`, `N_D = 1×10¹⁷ cm⁻³`, with
  heavily doped p⁺/n⁺ contact regions placed off the mode
- Ridge doping implemented as Pearson-IV implants, matching how the foundry would form them
- DC sweep 0 → −1.5 V, 21 points, exporting the 2D carrier maps at each bias
- Depletion width extracted from the carrier maps: 152 nm at 0 V → 285 nm at −1.5 V
- Small-signal AC analysis over 1 kHz – 1 PHz, giving junction capacitance, series resistance and an
  RC bandwidth estimate

The depletion-width curve follows the closed-form `sqrt(V_bi − V)` law for an abrupt junction
(127 nm → 213 nm for the same doping) but runs 20–34 % wider — a consequence of the graded implant
profile and of an extraction criterion that reads about a Debye length beyond the ideal edge. That
comparison is worked through in `PhaseShifter/CHARGE/README.md`.

**Optical model (MODE). Complete.**

- Carrier maps imported as an np-density grid attribute and converted to a complex index change
  through a Soref–Bennett perturbation material with a lossless base, so everything imaginary in the
  result is free-carrier absorption
- Geometry and FDE window matched to the CHARGE cross-section and monitor region so the carriers
  land in the right place
- Bias sweep over the same 21 points, solving the mode at each: `n_eff(V)`, loss, and `V_π·L` from
  the slope of `n_eff(V)`

| Metric | Result | Target |
| ------ | ------ | ------ |
| `V_π·L` (mean slope) | **2.63 V·cm** | < 3 V·cm — met |
| `Δn_eff` over 0 → −1.5 V | 4.4×10⁻⁵ | — |
| Free-carrier loss | 2.3 → 2.9 dB/cm (0.3 dB over 1 mm) | < 5 dB device budget — met |
| 3 dB EO bandwidth | from the CHARGE RC estimate | > 10 GHz |

**Further optimisation is a trade-off study, not an open requirement.** The original plan called
for sweeping doping concentration and junction offset; the chosen profile already meets `V_π·L`,
loss and bandwidth targets simultaneously, and the response is sub-linear in bias, which is a
property of the junction rather than of the doping level. Those sweeps belong under "Later".

### 4.5 Repository

- Component/solver layout (`<Component>/<Solver>/`) with a `main.lsf` driver plus numbered steps per
  solver, each folder carrying its own `README.md`
- Machine-specific Lumerical project files and simulated data (`.mat`) excluded; the result figures
  (`.png`) are committed so every result in the READMEs can be inspected without a Lumerical licence
- Python post-processing for every sweep, reading the `.mat` files with `h5py`
- Design notes in `MZI/`

---

## 5. The component optimisation workflow

This is the reusable part of the project, stated independently of the MMI so that it can be applied
to the next component unchanged. It was worked out while optimising the MMI, and §4.3 reports where
each step currently stands for that component.

**Step 1 — Fix what the theory pins down, and verify the one assumption it does not.** Freeze the
parameters the analytic model gives reliably, but check once that the assumptions behind them hold.
For the MMI this means checking that the taper is long enough by doubling its length and confirming
the loss does not move: an over-short taper shows up as a constant offset in the loss floor, not as
a change of shape, so it contaminates every later sweep while being easy to overlook.

**Step 2 — Coarse sweep of the critical dimension around the analytic value.** Wide enough to see
the whole peak: ±20 % is the working default. The analytic value is a starting point, not a
prediction, and the correction can be large — here the FDE-refined `L_MMI` is 24 % shorter than the
slab estimate.

**Step 3 — Sweep the input coupling, then re-sweep the critical dimension.** The input taper sets
how much power enters the multimode region and with what phase, so changing it moves the optimum
length. Optimising them in sequence rather than together keeps each sweep interpretable.

**Step 4 — Sweep the output side: taper width and lateral position.** The lateral offset positions
the output ports on the two-fold image, and it is the one parameter in this design that cannot be
varied inside an EME propagation sweep, because it moves the output waveguides, their meshes and
the ports — so it needs a full geometry rebuild per point.

**Step 5 — Final fine sweep of the critical dimension** around the optimum that steps 3 and 4 have
moved to.

**Step 6 — Robustness, and choose the figure of merit that survives it.** Evaluate the optimum over
the full wavelength band, and with ±10–20 nm of waveguide width bias. Use the band-averaged
transmission, or the worst case, as the number the design is judged by, and if the peak is too
sharp, move to the flat part of the curve and give away a little peak loss in exchange for
tolerance. This is the step that turns an optimum into a manufacturable design point.

**Step 7 — Record the chosen point and the reason.** Every value in `step02_mmi_design.lsf` carries
either its analytic origin or the sweep that produced it, so the design point can be re-derived.

Steps 1–7 are component-generic: for a microring they become the gap, the radius, the bus coupling,
the back-reflection and the thermal tuning range; for a phase shifter they become doping, junction
offset, contact placement and drive. The point of writing them down is that they were the same
seven steps in each case.

---

## 6. Near-term work

### 6.1 Finish the MMI workflow

Four of the seven steps in §5 are still incomplete for the MMI, and they are the ones that decide
whether the quoted 0.069 dB survives contact with fabrication:

- **Verify the taper length** (step 1) — doubling the input and output tapers and confirming the
  loss does not change. Cheap, and it retires an unverified assumption behind every other sweep.
- **Re-sweep `L_MMI`** (steps 3 and 5). The input taper sets how much power enters the multimode
  region and with what phase, so widening it to 1.3333 µm may have moved the length optimum; the
  fine re-sweep those two steps call for, the counterpart to `step09`, has not been run.
- **Width-bias robustness, and the figure of merit that survives it** (step 6) — repeat the length
  and wavelength sweeps with ±10–20 nm of width error, and change the selection rule at the end of
  `step09_length_sweep.lsf` from the single-point minimum to the band-averaged or worst-case
  insertion loss over the flat region. The MMI body is the least width-sensitive element; the tapers
  are the sensitive part, which is a further reason they were swept.

Steps 2 and 4 are closed: the input-taper (`step10`), output-taper (`step12`) and `d_y` (`step11`)
sweeps are done, and each left the insertion loss lower than the one before.

### 6.2 Device-level power budget

Fold the measured component losses into one budget: waveguide propagation loss, two MMI insertion
losses, bend losses for the routing, and the phase shifter's free-carrier loss, against the 5 dB
insertion-loss target. This is the first calculation that treats the design as a system rather than
four independent components, and it is the natural bridge to §7.2.

---

## 7. Later

Consolidated here rather than dropped: each item is a genuine next step, but each depends on
something in §6 being finished first, or on tooling not yet set up.

### 7.1 FDTD validation of the optimised MMI — done

EME assumes the structure is piecewise-uniform along the propagation axis and decomposes the field
onto a finite set of modes. Both assumptions were checked once on the final geometry with a full 3D
FDTD run in `MMI/FDTD/`, comparing insertion loss and reflection against the EME prediction. The two
solvers agree to 0.03 dB in insertion loss and 0.004 in per-port transmission — 0.103 dB against
0.069 dB at 1550 nm — and the mesh was checked for convergence rather than trusted at one setting.

Kept here as a record; it is no longer outstanding work. The superseded 2D varFDTD implementation
under `MMI/MODE/reference/` remains available as a cheaper partial substitute for any future
geometry.

### 7.2 INTERCONNECT system simulation

Build the MZI from the component models and verify BB84-relevant operation.

- Import the MMIs as S-parameter matrices, the phase shifter as a compact model (phase shift and
  insertion loss versus `V`), and the waveguides from the FDE results
- Two MMIs in series with matched arms, one arm carrying the phase shifter
- Simulate the DC transfer function (output power versus bias, over the −1.5 → 0 V range the shifter
  supports rather than the −5 V assumed originally), the extinction ratio, and the four BB84 phase
  states mapped to voltages

Fallback if the compact model proves fiddly: the same transfer function computed analytically in
Python from the simulated component parameters, which demonstrates the same result with less setup.

### 7.3 GDS layout

A fabrication-ready layout of the complete MZI modulator.

- gdsfactory with a layer map (Si waveguide, Si slab, metal, via) and the SiEPIC or foundry PDK
- Grating or edge couplers for fibre I/O, routing waveguides at the bend radius from `Bends/`, the
  two MMIs, matched arms, and the PN junction region with its implant windows, contacts, vias and
  GSG probe pads
- Test structures: alignment marks, a waveguide cutback for loss extraction, and a standalone
  phase-shifter structure to measure `V_π·L` independently
- Design rule checking, then export

### 7.4 Parabolic taper profile

Dropped from the current scope; revisit only if the linear tapers leave the MMI insertion loss short
of target. Swapping the taper polygons is a geometry-only change.

### 7.5 Doping and junction-offset sweeps

The trade-off studies described in §4.4. Worth doing only if a target is missed, or if the phase
shifter is reused in a design with a different bandwidth requirement.

---

## 8. Design targets

| Metric | Typical silicon carrier-depletion | This project's target | Result |
|--------|-----------------------------------|-----------------------|--------|
| `V_π·L` | 1–3 V·cm | < 3 V·cm | 2.63 V·cm |
| Insertion loss (π shift) | 2–5 dB | < 5 dB | 0.3 dB free-carrier over 1 mm, before MMI and bends |
| 3 dB EO bandwidth | 10–40 GHz | > 10 GHz | from the CHARGE RC estimate |
| Extinction ratio | > 20 dB | > 20 dB | device-level, needs §7.2 |
| MMI splitting ratio | — | 50:50 ± 1 % | 49.2 % / 49.2 % — met, and exact by symmetry |
| MMI insertion loss | — | < 0.5 dB | 0.069 dB at 1550 nm (0.103 dB in 3D FDTD); 0.127 dB worst case over 40 nm; 0.397 dB worst case over the full C-band — met across the whole band |
| MMI bandwidth | — | > 40 nm | met: worst-case IL 0.127 dB over 1530–1570 nm |

---

## 9. Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| The single-point IL minimum selected by `step09` overfits EME discretisation noise, since the curve is not smooth at the few-tenths-of-a-dB level | High | Low | Select on the band-averaged or worst-case IL over the flat region instead (§6.1) |
| The taper length is assumed adequate but has never been checked by doubling | Medium | Low | One extra run; a short taper appears as a constant loss offset |
| Width bias (±10–20 nm) has not been evaluated, so fabrication tolerance is unquantified | Medium | Medium | Perturb the widths and repeat the length and wavelength sweeps; the tapers, not the MMI body, are the sensitive part |
| EME's piecewise-uniform assumption was untested against a full-wave solver | Low | Low | Done: 3D FDTD on the final design point agrees to 0.03 dB (§7.1); varFDTD remains a cheaper partial substitute |
| The `d_y` sweep needs a geometry rebuild per point, so it is slower than the length sweep | Medium | Low | Already done; the offset turns out to be a weak parameter, so a coarse grid suffices |
| INTERCONNECT compact model proves fiddly to fit | Medium | Medium | Analytical MZI transfer function in Python from the simulated component parameters |
| GDS layout takes longer than estimated | Medium | Medium | Overlap layout work with the write-up; reduce layout scope (simpler test structures, fewer pads) |

---

## 10. Relation to the experimental thesis

| Thesis (experimental) | Side project (computational) |
|-----------------------|------------------------------|
| Free-space MZI with PBS | Integrated MZI with MMIs |
| Polarization encoding via QWP + HWP | Phase encoding via carrier depletion |
| Benchtop, discrete components | On-chip, monolithic |
| Breadboard-level integration | Foundry-ready GDS |
| BB84 using polarization analyzer | BB84 phase states from MZI output |

---

## 11. Prerequisites and setup

- [x] Lumerical licence including MODE (FDE + EME) and CHARGE
- [x] Python environment with `numpy`, `h5py`, `matplotlib`
- [ ] Install gdsfactory + KLayout for the layout stage (§7.3)
- [ ] Download SiEPIC PDK or obtain foundry PDK documentation (§7.3)
- [x] Public GitHub repository with the component/solver layout

---

## 12. Key references

**Component physics and platform**

1. Soref, R. A., & Bennett, B. R. (1987). Electrooptical effects in silicon. *IEEE J. Quantum Electron.*, 23(1), 123–129. — The canonical plasma dispersion paper.
2. Reed, G. T., Mashanovich, G., Gardes, F. Y., & Thomson, D. J. (2010). Silicon optical modulators. *Nature Photonics*, 4(8), 518–526. — Overview of Si modulator physics.
3. Chrostowski, L., & Hochberg, M. (2015). *Silicon Photonics Design: From Devices to Systems*. Cambridge University Press. — The Si photonics design textbook. Chapters 4 (waveguides), 5 (modulators), and 10 (layout) are essential.
4. Soldano, L. B., & Pennings, E. C. M. (1995). Optical multi-mode interference devices based on self-imaging: principles and applications. *J. Lightwave Technol.*, 13(4), 615–627. — MMI theory.
5. Harris, N. C., Ma, Y., Mower, J., Baehr-Jones, T., Englund, D., Hochberg, M., & Galland, C. (2014). Efficient, compact and low loss thermo-optic phase shifter in silicon. *Optics Express*, 22(9), 10487–10493. — The alternative phase actuator, and the same figures of merit (`V_π·L`, loss, bandwidth) applied to it.

**Quantum photonic integration**

6. Bennett, C. H., & Brassard, G. (1984). Quantum cryptography: Public key distribution and coin tossing. *Proc. IEEE ICCSSP*. — The original BB84 paper.
7. Sibson, P., et al. (2017). Integrated silicon photonics for high-speed quantum key distribution. *Optica*, 4(2), 172–177. — Example of a Si photonic QKD transmitter. This design is conceptually related.
8. Wang, J., et al. (2020). Integrated photonic quantum technologies. *Nature Photonics*, 14, 273–284. — Review of integrated quantum photonics.

---

*Original plan written 2026-07-24; revised 2026-09-30 to reflect completed work and a realistic
remaining scope.*
