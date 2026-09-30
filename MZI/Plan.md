# Silicon-Photonic MZI Platform — Component Library and Design Workflow

A component-level design and simulation project on 220 nm silicon-on-insulator, organised around a
Mach–Zehnder interferometer (MZI) for BB84 quantum key distribution state encoding.

The BB84 encoder is the worked example, not the limit of the project. Everything here is built the
way a programmable photonic circuit is built: a small library of reusable components, each one
designed analytically, verified numerically, optimised by parametric sweeping, checked for
robustness across the band and against fabrication bias, and finally composed into a system with a
loss budget. That workflow, and the component models it produces, transfer directly to
programmable photonic processors, photonic computing and optical reservoir computing; §3 sets out
which parts transfer as they stand and which would have to be added.

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

## 3. Applicability beyond quantum photonics

The reference device is an MZI phase encoder. The components it is built from are the same ones a
programmable photonic circuit is built from — an MZI *is* the elementary 2×2 cell of an
interferometer mesh, and a mesh is a programmable linear-optical processor.

| Component | Function in the BB84 encoder | Where the same component or model recurs |
| --------- | ---------------------------- | ---------------------------------------- |
| Single-mode waveguide, low-loss bends | Arm routing; `n_eff` and `n_g` set the phase and the dispersion | Every PIC. `n_g` sets the free-spectral range of ring-based banks, and routing loss is what limits how large a mesh can grow |
| 1×2 MMI splitter (50/50, in-phase) | Splitter and combiner of the MZI | The fixed-ratio coupler of a Reck/Clements MZI mesh; the 2×2 cell of a linear-optical processor; splitter trees in WDM and in reservoir readouts |
| Carrier-depletion PN phase shifter | Encodes the phase states, GHz-bandwidth | The reconfigurable phase element of a programmable mesh. This design is electro-optic for speed, but `V_π·L`, insertion loss and RC bandwidth are the same figures of merit any phase actuator is judged by, thermo-optic included |
| MZI (two MMIs plus a phase shifter) | The phase encoder itself | The 2×2 tunable coupler — the elementary gate of a programmable photonic processor, and the delay/interference element of photonic neural networks and optical reservoir computing |

**What transfers as it stands.** The passive library and its models (FDE `n_eff`/`n_g`, EME
S-parameters); the MMI design and optimisation flow, which is application-independent; the
electro-optic phase-shifter model, which returns exactly the quantities a mesh design needs from
its actuators; and the methodology itself — analytic sizing, numerical verification, sweeping,
robustness across band and width bias, then a budget.

**What a computing application would additionally need**, and which is therefore out of scope
here: composition of unit cells into a mesh (S-parameter composition or a system simulator) together
with unitary decomposition and calibration; for reservoir computing, a delay or feedback path, a
nonlinear element, and a readout weight bank; and, at scale, thermal crosstalk, drift and drive
electronics that a single MZI never encounters.

**Scope of the claim.** This repository does not attempt a computing demonstration, and does not
claim novelty in the components — every one of them is standard. The claim is narrower and is
verifiable from the repository: the component models, the solver setups and the optimisation
workflow are the reusable part, and they are the same ones a programmable-circuit or neuromorphic
design starts from.

---

## 4. Scope and status

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
| 1×2 MMI splitter | EME (MODE) | Swept and characterised — length, wavelength and output-offset sweeps run, figures committed; four robustness checks still open (§7.1) |
| PN junction phase shifter (electrical) | CHARGE drift-diffusion + AC | Complete |
| PN junction phase shifter (optical) | FDE (MODE) | Complete — V_π·L inside target |
| MZI system integration | INTERCONNECT | Not started |
| GDS layout | gdsfactory / KLayout | Not started |

---

## 5. Completed work

### 5.1 Waveguide (`Waveguide/MODE/`)

The 500 nm × 220 nm strip waveguide everything else is built on.

- 220 nm SOI stack with dispersive Si / SiO₂ models from `shared/materials.lsf`
- Width sweep 100–2000 nm in 50 nm steps, recording `n_eff`, `n_g` and the TE polarisation fraction
  of every mode found — which locates the single-mode window and shows where higher-order and
  cross-polarised modes appear
- Wavelength sweep at the nominal width across the C-band, giving `n_eff(λ)` and `n_g(λ)`

**Deliverable met:** mode profile, `n_eff` vs. width, `n_eff` vs. wavelength, single-mode condition
with fabrication tolerance.

### 5.2 Bends (`Bends/`)

- Mode-mismatch loss at the straight-to-bend junction versus radius of curvature, from an FDE
  overlap integral
- Bend loss model combining mismatch and propagation loss, giving an optimum radius
- Cubic Bézier curvature profile compared with a circular arc: the radius sweep brackets the
  minimum, since mismatch falls with radius while propagation loss grows

**Deliverable met:** bend loss vs. radius, minimum-radius specification, Bézier curvature study.

### 5.3 MMI splitter (`MMI/MODE/`)

Self-imaging 1×2 MMI — the 50/50 splitter and combiner of the MZI, and the component whose
optimisation is written up in §6 as the reusable procedure.

**Design targets:** 50:50 ± 1 %, insertion loss < 0.5 dB, bandwidth > 40 nm, in-phase outputs.

The design point is `W_MMI = 4.0 µm` with linear tapers (0.5 → 1.0 µm) on both sides, chosen after
the output-offset sweep was run at `W_MMI = 4 µm` and 5 µm and the 4 µm case gave the lower
insertion loss. The plausible reason is geometric rather than physical: at 4 µm the taper is
one-quarter of the MMI width instead of one-fifth, so the taper-to-body mode match is better with
the same taper polygons. That is a hypothesis about the taper, and §7.1 lists the sweep that would
settle it. The analytic sizing at this width gives `W_e = 4.16 µm`, `L_π = 51.7 µm`,
`L_MMI = 3L_π/8 = 19.4 µm` and `d_y = W_e/4 = 1.039 µm`.

The slab formula behind those numbers uses the bulk silicon index and so ignores vertical
confinement; step04 replaces the beat length with the simulated one. The correction is not small —
`L_π` falls from 51.7 µm to 39.4 µm, moving `L_MMI` from 19.4 µm to 14.8 µm — which is precisely
why the sweeps below exist rather than the formula being trusted.

| Sweep | Range and points | Figure of merit |
| ----- | ---------------- | --------------- |
| MMI length (`step09`) | 11.83 → 17.74 µm, 31 points (±20 % about 14.79 µm) | minimum insertion loss |
| Wavelength (`step11`) | 1500 → 1600 nm, 101 points, at the optimal length | IL and split across the band |
| Output offset `d_y` (`step12`) | 0.939 → 1.139 µm, 11 points (±0.10 µm about 1.039 µm) | minimum insertion loss |

**Results.** All three sweeps have been run and their figures are committed.

| Metric | Result |
| ------ | ------ |
| `L_MMI` (min IL) | 14.00 µm, vs 14.79 µm from the FDE-refined analytic value |
| `d_y` (min IL) | 1.019 µm, vs 1.039 µm analytic; adopted in `step02_mmi_design.lsf` |
| Split at the optimum | 48.6 % / 48.6 % (`T = 0.4864` per port) |
| Imbalance | zero to within 7×10⁻⁹ dB |
| Insertion loss at 1550 nm | **0.120 dB** |
| Insertion loss, 1530 → 1570 nm | 0.219 dB worst case |
| Insertion loss, 1500 → 1600 nm | 0.239 dB mean, 0.501 dB worst (at 1597 nm) |

Two of these deserve comment.

The **imbalance is identically zero**, not merely small. A centred-input 1×2 MMI with output ports
placed symmetrically about the axis is mirror-symmetric, so `T_top = T_bot` by construction; the
simulation reproduces that to 10⁻⁹ dB. The imbalance curve is therefore a consistency check on the
port setup rather than an optimisation target, and the `d_y` sweep's real function is to maximise
the summed transmission, not to balance the split. The optimum it finds is also shallow: moving
from the analytic `W_e/4` to the swept minimum is worth 0.007 dB, well inside the point-to-point
scatter of the sweep, so `d_y` is a weak parameter here and the analytic value would have served.

The **length sweep's minimum is broad and not smooth**. Point-to-point differences near the optimum
run to ~0.1 dB (0.122, 0.120, 0.278, 0.200 dB across neighbouring points), which is the EME
discretisation, not physics. Picking the single lowest point — which is what `step10` currently
does — therefore risks selecting simulation noise. §6 step 6 states the rule that should be used
instead: judge the candidate on the band-averaged or worst-case transmission and sit on the flat
part of the curve. The quoted 0.120 dB should be read as 0.12 dB to the accuracy the solver
supports.

The loss is also not flat in wavelength: 0.12 dB at 1550 nm rising to 0.50 dB at the top of the
C-band. Over the 40 nm the design targets, the worst case is 0.219 dB, so the bandwidth target is
met with margin; over the full 100 nm the worst case just touches 0.5 dB.

**Still outstanding:** nothing in the simulation flow, but four of the seven workflow steps in §6
are incomplete for this component. They are listed in §7.1.

### 5.4 Carrier-depletion phase modulator (`PhaseShifter/`)

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

### 5.5 Repository

- Component/solver layout (`<Component>/<Solver>/`) with a `main.lsf` driver plus numbered steps per
  solver, each folder carrying its own `README.md`
- Machine-specific Lumerical project files excluded; simulated data (`.mat`) and figures (`.png`)
  committed so every result in the READMEs can be inspected without a Lumerical licence
- Python post-processing for every sweep, reading the `.mat` files with `h5py`
- Design notes in `MZI/`

---

## 6. The component optimisation workflow

This is the reusable part of the project, stated independently of the MMI so that it can be applied
to the next component unchanged. It was worked out while optimising the MMI, and §5.3 reports where
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

## 7. Near-term work

### 7.1 Finish the MMI workflow

Four of the seven steps in §6 are incomplete for the MMI, and they are the same four that decide
whether the quoted 0.12 dB survives contact with fabrication:

- **Verify the taper length** (step 1) — doubling the input and output tapers and confirming the
  loss does not change. Cheap, and it retires an unverified assumption behind every other sweep.
- **Sweep the input taper width, then re-sweep `L_MMI`** (steps 3 and 5). This also tests the
  hypothesis behind the choice of `W_MMI = 4 µm`: if the 4 µm advantage comes from the
  taper-to-body width ratio, widening the taper at 5 µm should recover it.
- **Sweep the output taper width** (step 4), which is the remaining unswept geometry.
- **Width-bias robustness** (step 6) — repeat the length and wavelength sweeps with ±10–20 nm of
  width error. The MMI body is the least width-sensitive element; the tapers are the sensitive part,
  which is a further reason to sweep them.
- **Change the selection rule** in `step10_sweep_analysis.lsf` from the single-point minimum to the
  band-averaged or worst-case insertion loss over the flat region, for the reason given in §5.3.

### 7.2 Device-level power budget

Fold the measured component losses into one budget: waveguide propagation loss, two MMI insertion
losses, bend losses for the routing, and the phase shifter's free-carrier loss, against the 5 dB
insertion-loss target. This is the first calculation that treats the design as a system rather than
four independent components, and it is the natural bridge to §8.2. It is also the calculation that
a programmable-circuit design extends: the same budget over a mesh, where the MMIs are counted in
the hundreds.

---

## 8. Later

Consolidated here rather than dropped: each item is a genuine next step, but each depends on
something in §7 being finished first, or on tooling not yet set up.

### 8.1 FDTD validation of the optimised MMI

EME assumes the structure is piecewise-uniform along the propagation axis and decomposes the field
onto a finite set of modes. Both assumptions are worth checking once on the final geometry with a
full 3D FDTD run, comparing insertion loss and imbalance against the EME prediction. If time is
short, a 2D varFDTD cross-check is a cheaper partial substitute — the superseded implementation
under `MMI/MODE/reference/` is already set up for that.

### 8.2 INTERCONNECT system simulation

Build the MZI from the component models and verify BB84-relevant operation.

- Import the MMIs as S-parameter matrices, the phase shifter as a compact model (phase shift and
  insertion loss versus `V`), and the waveguides from the FDE results
- Two MMIs in series with matched arms, one arm carrying the phase shifter
- Simulate the DC transfer function (output power versus bias, over the −1.5 → 0 V range the shifter
  supports rather than the −5 V assumed originally), the extinction ratio, and the four BB84 phase
  states mapped to voltages

Fallback if the compact model proves fiddly: the same transfer function computed analytically in
Python from the simulated component parameters, which demonstrates the same result with less setup.

This is also the step that generalises furthest: composing S-parameters is how a mesh is simulated,
so the same machinery serves the computing applications in §3.

### 8.3 GDS layout

A fabrication-ready layout of the complete MZI modulator.

- gdsfactory with a layer map (Si waveguide, Si slab, metal, via) and the SiEPIC or foundry PDK
- Grating or edge couplers for fibre I/O, routing waveguides at the bend radius from `Bends/`, the
  two MMIs, matched arms, and the PN junction region with its implant windows, contacts, vias and
  GSG probe pads
- Test structures: alignment marks, a waveguide cutback for loss extraction, and a standalone
  phase-shifter structure to measure `V_π·L` independently
- Design rule checking, then export

### 8.4 Parabolic taper profile

Dropped from the current scope; revisit only if the linear tapers leave the MMI insertion loss short
of target. Swapping the taper polygons is a geometry-only change.

### 8.5 Doping and junction-offset sweeps

The trade-off studies described in §5.4. Worth doing only if a target is missed, or if the phase
shifter is reused in a design with a different bandwidth requirement.

---

## 9. Design targets

| Metric | Typical silicon carrier-depletion | This project's target | Result |
|--------|-----------------------------------|-----------------------|--------|
| `V_π·L` | 1–3 V·cm | < 3 V·cm | 2.63 V·cm |
| Insertion loss (π shift) | 2–5 dB | < 5 dB | 0.3 dB free-carrier over 1 mm, before MMI and bends |
| 3 dB EO bandwidth | 10–40 GHz | > 10 GHz | from the CHARGE RC estimate |
| Extinction ratio | > 20 dB | > 20 dB | device-level, needs §8.2 |
| MMI splitting ratio | — | 50:50 ± 1 % | 48.6 % / 48.6 % — met, and exact by symmetry |
| MMI insertion loss | — | < 0.5 dB | 0.120 dB at 1550 nm; 0.219 dB worst case over 40 nm; 0.501 dB worst case over the full C-band — met over the design bandwidth |
| MMI bandwidth | — | > 40 nm | met: worst-case IL 0.219 dB over 1530–1570 nm |

---

## 10. Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| The single-point IL minimum selected by `step10` overfits EME discretisation noise, since the curve is not smooth at the ~0.1 dB level | High | Low | Select on the band-averaged or worst-case IL over the flat region instead (§7.1) |
| The taper length is assumed adequate but has never been checked by doubling | Medium | Low | One extra run; a short taper appears as a constant loss offset |
| Width bias (±10–20 nm) has not been evaluated, so fabrication tolerance is unquantified | Medium | Medium | Perturb the widths and repeat the length and wavelength sweeps; the tapers, not the MMI body, are the sensitive part |
| EME's piecewise-uniform assumption is untested against a full-wave solver | Medium | Medium | 3D FDTD on one design point (§8.1); varFDTD as a cheaper partial substitute |
| The `d_y` sweep needs a geometry rebuild per point, so it is slower than the length sweep | Medium | Low | Already done; the offset turns out to be a weak parameter, so a coarse grid suffices |
| INTERCONNECT compact model proves fiddly to fit | Medium | Medium | Analytical MZI transfer function in Python from the simulated component parameters |
| GDS layout takes longer than estimated | Medium | Medium | Overlap layout work with the write-up; reduce layout scope (simpler test structures, fewer pads) |

---

## 11. Relation to the experimental thesis

| Thesis (experimental) | Side project (computational) |
|-----------------------|------------------------------|
| Free-space MZI with PBS | Integrated MZI with MMIs |
| Polarization encoding via QWP + HWP | Phase encoding via carrier depletion |
| Benchtop, discrete components | On-chip, monolithic |
| Breadboard-level integration | Foundry-ready GDS |
| BB84 using polarization analyzer | BB84 phase states from MZI output |

---

## 12. Prerequisites and setup

- [x] Lumerical licence including MODE (FDE + EME) and CHARGE
- [x] Python environment with `numpy`, `h5py`, `matplotlib`
- [ ] Install gdsfactory + KLayout for the layout stage (§8.3)
- [ ] Download SiEPIC PDK or obtain foundry PDK documentation (§8.3)
- [x] Public GitHub repository with the component/solver layout

---

## 13. Key references

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

**Programmable circuits and optical computing**

9. Bogaerts, W., Pérez, D., Capmany, J., Miller, D. A. B., Poon, J., Englund, D., Morichetti, F., & Melloni, A. (2020). Programmable photonic circuits. *Nature*, 586(7828), 207–216. — What a programmable photonic processor is, and why its unit cell is this project's MZI.
10. Pérez, D., Gasulla, I., Crudgington, L., Thomson, D. J., Khokhar, A. Z., Li, K., Cao, W., Mashanovich, G. Z., & Capmany, J. (2017). Multipurpose silicon photonics signal processor core. *Nature Communications*, 8, 636. — A reconfigurable silicon waveguide mesh, the platform-scale version of the same components.
11. Shen, Y., Harris, N. C., Skirlo, S., Prabhu, M., Baehr-Jones, T., Hochberg, M., Sun, X., Zhao, S., Larochelle, H., Englund, D., & Soljačić, M. (2017). Deep learning with coherent nanophotonic circuits. *Nature Photonics*, 11(7), 441–446. — An MZI mesh as a linear-optical processor.
12. Clements, W. R., Humphreys, P. C., Metcalf, B. J., Kolthammer, W. S., & Walmsley, I. A. (2016). Optimal design for universal multiport interferometers. *Optica*, 3(12), 1460–1465. — The mesh topology whose unit cell is the component designed here.

**Neuromorphic photonics and reservoir computing**

13. Shastri, B. J., Tait, A. N., Ferreira de Lima, T., Pernice, W. H. P., Bhaskaran, H., Wright, C. D., & Prucnal, P. R. (2021). Photonics for artificial intelligence and neuromorphic computing. *Nature Photonics*, 15(2), 102–114. — Where photonic computing is going and what the hardware requirements are.
14. Van der Sande, G., Brunner, D., & Soriano, M. C. (2017). Advances in photonic reservoir computing. *Nanophotonics*, 6(3), 561–576. — Reservoir computing with photonic hardware: what the delay, nonlinearity and readout stages require.
15. Vandoorne, K., Mechet, P., Van Vaerenbergh, T., Fiers, M., Morthier, G., Verstraeten, D., Schrauwen, B., Dambre, J., & Bienstman, P. (2014). Experimental demonstration of reservoir computing on a silicon photonics chip. *Nature Communications*, 5, 3541. — Reservoir computing built from exactly this platform.

---

*Original plan written 2026-07-24; revised 2026-09-30 to reflect completed work, the broadened
applicability of the component library and the workflow, and a realistic remaining scope.*
