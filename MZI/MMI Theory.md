# MMI Coupler Theory

## 1. The Multimode Interferometer

A multimode interferometer (MMI) is a passive photonic component that splits or combines optical signals by exploiting the self-imaging principle in a multimode waveguide. When light enters a sufficiently wide waveguide from a single-mode input, the abrupt widening excites multiple guided modes of the multimode section. These modes propagate with **different propagation constants** (different effective indices), accumulating different phase delays as they travel. At certain periodic distances, the superposition of these modes reconstructs single or multiple images of the input field — this is the self-imaging (or Talbot) effect, adapted from diffractive optics to guided-wave structures.

The MMI is preferred over directional couplers for the MZI splitter/combiner because:

- **Broadband operation**: the self-imaging condition depends on mode beating, which is inherently less wavelength-sensitive than evanescent coupling.
- **Fabrication tolerance**: MMIs are robust to small variations in width and length; directional couplers require precise gap control (typically 100–200 nm gaps are hard to reproduce).
- **Uniform splitting**: 50:50 splitting ratios achievable with < 1% imbalance across 40+ nm bandwidth.

## 2. Geometry and Mode Decomposition

Consider a 1×2 MMI (the type used in this project). The structure consists of:

- A single-mode input waveguide of width $w$, centered at $y = 0$
- A multimode section of width $W_{\text{MMI}}$ and length $L_{\text{MMI}}$
- Two single-mode output waveguides at $y = \pm d_y$

At the junction where the narrow input waveguide opens into the wide multimode section ($z = 0$), the incoming fundamental TE mode $\Phi_{\text{in}}(y)$ is projected onto the set of guided modes supported by the multimode waveguide:

$$
\Phi_{\text{in}}(y) = \sum_{\nu = 0}^{M-1} c_\nu \, \psi_\nu(y)
$$

where $\psi_\nu(y)$ is the lateral field profile of mode $\nu$ in the MMI section, $M$ is the number of guided modes, and $c_\nu$ are the **excitation coefficients** given by the overlap integral:

$$
c_\nu = \frac{\int \Phi_{\text{in}}(y) \, \psi_\nu^*(y) \, dy}{\int |\psi_\nu(y)|^2 \, dy}
$$

Because the input waveguide is centered at $y = 0$, and the structure is laterally symmetric, the input field is an **even function** of $y$. Consequently, **only even-order modes** ($\nu = 0, 2, 4, \dots$) are excited — the overlap integral with odd (antisymmetric) modes vanishes identically.

The lateral modes of a deeply etched rib waveguide are well approximated by the modes of a slab waveguide with Dirichlet boundary conditions at the effective walls:

$$
\psi_\nu(y) \approx \sin\!\left[\frac{(\nu + 1)\,\pi}{W_e}\left(y + \frac{W_e}{2}\right)\right], \quad \nu = 0, 1, 2, \dots
$$

where $W_e$ is the **effective width** of the MMI. $W_e$ is slightly larger than the physical width $W_{\text{MMI}}$ due to the **Goos–Hänchen shift** at the dielectric boundaries:

$$
W_e = W_{\text{MMI}} + \left(\frac{\lambda_0}{\pi}\right) \left(\frac{n_c}{n_r}\right)^{2\sigma} (n_r^2 - n_c^2)^{-1/2}
$$

with $\sigma = 0$ for TE and $\sigma = 1$ for TM, $n_r$ the core (silicon) index, and $n_c$ the cladding (oxide) index.

### Parity Classification

Shifting the origin to the center of the MMI ($y \in [-W_e/2, \, W_e/2]$), the modes take the form:

$$
\begin{aligned}
\nu \text{ even (e.g., } 0, 2, 4\dots): \quad & \psi_\nu(y) \propto \cos\!\left[\frac{(\nu + 1)\pi\,y}{W_e}\right] \quad \text{(even / symmetric)} \\[6pt]
\nu \text{ odd (e.g., } 1, 3, 5\dots): \quad & \psi_\nu(y) \propto \sin\!\left[\frac{(\nu + 1)\pi\,y}{W_e}\right] \quad \text{(odd / antisymmetric)}
\end{aligned}
$$

With a centered symmetric input, **only $\nu = 0, 2, 4, 6, \dots$ are excited**.

## 3. Propagation Constants and the Beat Length

Each mode $\nu$ propagates along $z$ with its own propagation constant $\beta_\nu = k_0 \, n_{\text{eff},\nu}$, where $k_0 = 2\pi/\lambda_0$. For a step-index multimode waveguide, under the paraxial (or effective-index) approximation:

$$
\beta_\nu \approx k_0\,n_r - \frac{(\nu + 1)^2\,\pi\,\lambda_0}{4\,n_r\,W_e^2}
$$

The difference in propagation constants between the fundamental mode ($\nu = 0$) and mode $\nu$ is:

$$
\beta_0 - \beta_\nu \approx \frac{\nu(\nu + 2)\,\pi}{3 L_\pi}
$$

where $L_\pi$ is the **beat length** between the two lowest-order modes — the distance over which they accumulate a relative phase of $\pi$:

$$
L_\pi \equiv \frac{\pi}{\beta_0 - \beta_1} \approx \frac{4\,n_r\,W_e^2}{3\,\lambda_0}
$$

$L_\pi$ is the fundamental length scale of the MMI. All imaging properties are expressed in multiples of $L_\pi$.

### Significance of $L_\pi$ for Design

$L_\pi \propto W_e^2 / \lambda_0$. This quadratic dependence on width is the key to MMI design: **making the MMI wider increases the mode count and increases the beat length**. A wider MMI also excites more higher-order modes, and if the number of modes is insufficient to resolve the images, the splitting uniformity degrades. A rule of thumb is $M \geq N + 1$, where $N$ is the number of outputs, giving $M \geq 3$ for a 1×2 MMI.

## 4. The Field at Distance $z$

At a distance $z$ inside the MMI, the total field is the coherent superposition of all excited modes, each having accumulated its propagation phase:

$$
\Phi(y, z) = e^{-j\beta_0 z} \sum_{\nu=0}^{M-1} c_\nu \, \psi_\nu(y) \; \exp\!\big[j(\beta_0 - \beta_\nu)z\big]
$$

The common phase factor $e^{-j\beta_0 z}$ is a global phase that does not affect the intensity distribution. The imaging properties are determined by the **relative phases** between modes:

$$
\Delta\varphi_\nu(z) = (\beta_0 - \beta_\nu)\,z = \frac{\nu(\nu + 2)\,\pi}{3}\,\frac{z}{L_\pi}
$$

For the even modes that are actually excited ($\nu = 0, 2, 4, \dots$), two lengths are of special importance:

| $\nu$ | $\nu(\nu+2)$ | $\Delta\varphi_\nu$ at $z = 3L_\pi/8$ | $\Delta\varphi_\nu$ at $z = 3L_\pi/2$ |
|-------|-------------|---------------------------------------|---------------------------------------|
| 0     | 0           | $0$                                   | $0$                                   |
| 2     | 8           | $\pi$                                 | $4\pi \equiv 0$                       |
| 4     | 24          | $3\pi \equiv \pi$                     | $12\pi \equiv 0$                      |
| 6     | 48          | $6\pi \equiv 0$                       | $24\pi \equiv 0$                      |

Read the two columns separately — they describe two different devices:

**At $z = 3L_\pi/8$** the relative phases follow the pattern $0, \pi, \pi, 0, \dots$. With these signs the even modes interfere *destructively at the centre* ($y = 0$) and *constructively at $y = \pm W_e/4$*. That is exactly the **two-fold image**: two equal copies of the input, side by side, with a null between them. This is the length of a 1×2 splitter.

**At $z = 3L_\pi/2$** every excited mode has accumulated an integer multiple of $2\pi$ and is therefore back in phase with mode 0. The field reproduces the input profile *at the centre*, $y = 0$ — a **single (1-fold) direct image**. No splitting occurs here.

The distinction matters: $3L_\pi/8$ and $3L_\pi/2$ are both special lengths, but only the former gives two outputs. Confusing them is the single most common error in 1×2 MMI design, and it produces a device roughly four times too long that images instead of splitting.

## 5. Self-Imaging: The 1×2 General Interference MMI

There are three self-imaging mechanisms (Soldano & Pennings, 1995):

| Mechanism | Input position | Modes excited | $N$-fold image length |
|-----------|---------------|---------------|----------------------|
| **General** | anywhere; here centre ($y = 0$) | even only (for centred input) | $L = \dfrac{3L_\pi}{4N}$ |
| **Paired** | $y = \pm W_e/6$ | restricted subset | $L = \dfrac{L_\pi}{N}$ |
| **Symmetric** | centre, with $W$ chosen so only $\nu = 0, 3, 6,\dots$ propagate | restricted subset | $L = \dfrac{3L_\pi}{4N}$ |

For our **1×2 general interference MMI**, the first two-fold image ($N = 2$) occurs at:

$$
\boxed{L_{\text{MMI}} = \frac{3L_\pi}{4 \cdot 2} = \frac{3L_\pi}{8}}
$$

At this length, the field reconstructs **two identical copies** of the input mode, located at:

$$
y = \pm \frac{W_e}{4}
$$

These two images have equal amplitude but, crucially, **they are in phase** (relative phase difference $\Delta\phi = 0$). This follows from the symmetry of the device: with a centered input and symmetric output ports, the device is invariant under $y \to -y$, which swaps the two output ports. For a truly symmetric structure, the complex transmission coefficients to the two outputs must be identical, including phase.

### Derivation of the Image Positions

At $z = 3L_\pi/8$, using the relative phases from the table in Section 4 and writing the modes with the $\cos$ profiles of Section 2:

$$
\Phi(y, 3L_\pi/8) \propto c_0 \cos\!\frac{\pi y}{W_e} - c_2 \cos\!\frac{3\pi y}{W_e} - c_4 \cos\!\frac{5\pi y}{W_e} + c_6 \cos\!\frac{7\pi y}{W_e} + \dots
$$

Evaluating this at the three points of interest:

- at $y = 0$: the terms alternate in sign and cancel strongly → a **null**
- at $y = \pm W_e/4$: the $\cos$ factors are all $\pm 1/\sqrt{2}$ and the alternating phases conspire so that every term adds with the *same* sign → a **maximum**
- at $y = \pm W_e/2$: every even mode vanishes (Dirichlet condition at the walls)

so the field consists of two peaks at $y = \pm W_e/4$ separated by a dip — the two-fold image. Since $\Phi(-y) = \Phi(y)$ at every $z$, the two peaks are necessarily equal in amplitude *and* phase.

## 6. Effective Index and Mode Count

The **effective refractive index** of each mode is:

$$
n_{\text{eff},\nu} = \frac{\beta_\nu}{k_0}
$$

The fundamental mode ($\nu = 0$) has the highest effective index because its field is most confined to the high-index silicon core. Higher-order modes have lower effective indices — they "see" more of the lower-index cladding. The index difference between adjacent modes is approximately:

$$
n_{\text{eff},\nu} - n_{\text{eff},\nu+1} \approx \frac{(2\nu + 3)\,\lambda_0}{8\,n_r\,W_e^2}
$$

For our SOI MMI at 1550 nm (Si core, SiO₂ cladding, 220 nm thickness, $W_{\text{MMI}} = 5$ µm, $n_r = 3.4777$), the leading modes have effective indices in the neighborhood of $n_{\text{eff},0} \approx 2.85$, falling by roughly 0.05–0.1 per order.

The number of guided TE modes supported by the MMI section can be estimated from the V-parameter:

$$
M \approx \frac{2\,W_e}{\lambda_0}\sqrt{n_r^2 - n_c^2}
$$

For $W_e \approx 5.16$ µm, $\lambda_0 = 1.55$ µm, $n_r \approx 3.478$, $n_c \approx 1.444$, this gives $M \approx 21$ slab modes. In practice the 220 nm slab height and the rib structure reduce the *vertically single-mode* count, but it comfortably exceeds the minimum of $M \geq 3$ needed for a 1×2 MMI.

## 7. Phase Relationship Between Output Ports

For a **symmetric, centered-input 1×2 general interference MMI** ($L = 3L_\pi/8$, input at $y = 0$, outputs at $y = \pm W_e/4$), the two outputs are **in phase**: $\Delta\varphi = 0$.

### Why Symmetry Dictates In-Phase Outputs

The argument is geometric, and it does not depend on the mode bookkeeping at all. The device is symmetric under the reflection $y \to -y$. This symmetry operation maps:

- The input waveguide (at $y = 0$) → itself
- Output port A (at $y = +d$) → Output port B (at $y = -d$)

If the structure is invariant under this transformation, and the input field is also invariant (it lies on the symmetry axis), then the full solution of Maxwell's equations at every point in the device must satisfy:

$$
\mathbf{E}(y, z) = \mathbf{E}(-y, z)
$$

In particular, the fields at the two output ports are identical: $E_A = E_B$, meaning identical amplitude **and** identical phase. A phase difference between the two outputs would require breaking this symmetry — an asymmetric input, a shifted junction, or unequal output waveguides. Note that this holds at *every* $z$, for any symmetric MMI length; it is not special to $3L_\pi/8$.

### Consistency with the Mode Phases

The symmetry argument and the modal picture must agree, and they do. At $z = 3L_\pi/8$ the relative phases of the excited modes are $0, \pi, \pi, 0, \dots$ (Section 4). Two points are worth noting:

- The phase pattern is **symmetric about $y = 0$**: it contains no term that is odd in $y$, so the resulting field remains an even function and the two images stay in phase. An antisymmetric phase distribution — which is what would produce a $\pi$ between the ports — cannot be generated from a centred input.
- Mode 2 and mode 4 pick up a relative phase of $\pi$ at this length. This is precisely what pushes the field energy away from the centre and into the two side lobes, i.e. it is the mechanism that *creates* the split. It is not a phase difference *between* the ports.

So $\Delta\varphi = 0$ between the two outputs is guaranteed by symmetry, while the internal $\pi$ phases among the higher-order modes are what shape the two-fold image in the first place.

### Practical Verification in Lumerical

The phase relationship can be verified directly in simulation. After running the EME sweep, the S-parameters $S_{21}$ and $S_{31}$ can be examined. For a symmetric, lossless, equal-split MMI:

$$
\begin{aligned}
S_{21} &= \frac{1}{\sqrt{2}} \, e^{j\varphi_2} \\
S_{31} &= \frac{1}{\sqrt{2}} \, e^{j\varphi_3}
\end{aligned}
$$

where $\varphi_2 - \varphi_3 \approx 0$ (within numerical tolerance, typically < 1°).

### Consequence for the MZI

If both the splitter and combiner MMIs have $\Delta\varphi = 0$ between their ports, the MZI transfer function for a balanced interferometer is:

$$
P_{\text{out}} = P_{\text{in}} \cos^2\!\left(\frac{\Delta\phi_{\text{arm}}}{2}\right)
$$

where $\Delta\phi_{\text{arm}}$ is the phase difference introduced between the two arms (by the carrier-depletion phase shifter in arm 1, while arm 2 is passive). With no applied voltage ($\Delta\phi_{\text{arm}} = 0$), all power returns to the central output of the combiner — this is the **constructive interference** condition. Applying a $\pi$ phase shift in arm 1 switches the output to the **destructive interference** condition ($P_{\text{out}} \approx 0$ for a perfectly balanced MZI). This is the working principle of the MZI modulator.

## 8. Design Equations for the 1×2 SOI MMI

### Step-by-Step Design Procedure

**Step 1 — Choose MMI width**: Wide enough to support at least $M \geq 3$ TE modes. For 220 nm SOI at 1550 nm:

$$
W_{\text{MMI}} \approx 4\text{–}6 \ \mu\text{m}
$$

The upper bound is set by the desired compactness and by the fact that extremely wide MMIs have closely spaced high-order modes that can degrade imaging quality.

**Step 2 — Compute effective width** (Goos–Hänchen correction):

$$
W_e = W_{\text{MMI}} + \frac{\lambda_0}{\pi}\left(\frac{n_c}{n_r}\right)^{2\sigma} \frac{1}{\sqrt{n_r^2 - n_c^2}}
$$

For TE ($\sigma = 0$): $W_e \approx W_{\text{MMI}} + 0.16 \ \mu\text{m}$ (a small correction for high-index-contrast SOI).

**Step 3 — Compute the beat length**:

$$
L_\pi \approx \frac{4\,n_r\,W_e^2}{3\,\lambda_0}
$$

For the design point $W_{\text{MMI}} = 4$ µm, with $n_r = 3.4777$ and $\lambda_0 = 1.55$ µm:
$W_e = 4.156$ µm → $L_\pi \approx \frac{4 \times 3.4777 \times (4.156)^2}{3 \times 1.55} \approx 51.7$ µm.

**Step 4 — MMI length** (first two-fold image):

$$
L_{\text{MMI}} = \frac{3L_\pi}{8} \approx 19.4 \ \mu\text{m}
$$

**Step 5 — Output waveguide positions**:

$$
d_y = \pm \frac{W_e}{4} \approx \pm 1.04 \ \mu\text{m}
$$

These analytical values are starting points. The slab formula uses the bulk silicon index and so ignores vertical confinement, and the correction is not small: `step04_fde_mode_check.lsf` replaces $L_\pi$ with the value from the simulated eigenmodes, which for $W_{\text{MMI}} = 4$ µm takes $L_\pi$ from 51.7 µm to 39.4 µm and $L_{\text{MMI}}$ from 19.4 µm to 14.8 µm. The sweeps then run $\pm 20\%$ in $L_{\text{MMI}}$ (11.8–17.7 µm) and $\pm 0.10$ µm in $d_y$ around the refined values, since the effective-index model remains approximate when applied to the actual 3D rib structure.

### Sanity Check on the Length Scale

It is worth knowing the failure mode, because it is easy to verify a length analytically before running anything. For $W_{\text{MMI}} = 4$ µm:

| Candidate length | Formula | Slab estimate | FDE-refined | What it actually produces |
|---|---|---|---|---|
| Two-fold image | $3L_\pi/8$ | ≈ 19 µm | 14.8 µm | **Two outputs at $\pm W_e/4$ — the splitter** |
| Single image | $3L_\pi/2$ | ≈ 78 µm | 59 µm | One output at $y = 0$ — no splitting |

Published SOI 1×2 MMIs with 4–6 µm bodies come out at roughly 20–40 µm on the slab estimate. A design in the 100 µm class should be treated as a red flag rather than a result.

### Current Script Parameters

`step01_setup.lsf` and `step02_mmi_design.lsf` set:

| Parameter | Current value | Comment |
|-----------|--------------|---------|
| $W_{\text{MMI}}$ | 4.0 µm | Design point, chosen after running the $d_y$ sweep at 4 µm and 5 µm |
| $L_{\text{MMI}}$ | 14.0 µm | From the length sweep; 14.8 µm from the FDE-refined beat length, 19.4 µm from the slab formula |
| $d_y$ | 1.019 µm | From the $d_y$ sweep; $W_e/4 = 1.039$ µm analytically |
| $L_{\text{taper,in}}$ | 8.0 µm | Input taper |
| $L_{\text{taper,out}}$ | 5.0 µm | Output taper |

## 9. Taper Design

The transition between the narrow input/output waveguides (0.5 µm) and the wide MMI section (4–6 µm) should be gradual to minimize mode-mismatch loss and suppress excitation of radiation modes. Common taper geometries:

The design uses **linear tapers**, with the width varying as $W(z) = W_{\text{wg}} + (W_{\text{MMI}} - W_{\text{wg}})(z / L_{\text{taper}})$: simple to fabricate, and adequate for this width ratio. A **parabolic profile**, $W(z) = W_{\text{wg}} + (W_{\text{MMI}} - W_{\text{wg}})(z / L_{\text{taper}})^2$, would smooth the transition further and can reduce insertion loss by 0.1–0.2 dB at the same length, but the linear tapers already meet the loss target, so the parabolic variant was left out of scope.

Typical taper length: $L_{\text{taper}} \approx 5$–$10$ µm. The taper should be adiabatic — the change in waveguide width over one beat length of the local mode should be much smaller than the beat length itself. A good starting point is $L_{\text{taper}} \geq 10 \times (W_{\text{MMI}} - W_{\text{wg}})$.

## 10. Summary

- The MMI splits light by decomposing the input mode into the guided modes of a wide waveguide, each accumulating a mode-dependent phase delay during propagation.
- The beat length $L_\pi \approx 4 n_r W_e^2/(3\lambda_0)$ is the fundamental design parameter.
- For a **1×2 general interference MMI**: $L_{\text{MMI}} = 3L_\pi/8$, output ports at $y = \pm W_e/4$. This is the *first two-fold image*, at one quarter of the single-image length $3L_\pi/2$.
- **Phase difference between outputs is zero** for a symmetric centered-input MMI, enforced by the $y \to -y$ symmetry. This can and should be confirmed in the EME simulation.
- Current design point for $W_{\text{MMI}} = 4$ µm: $W_e \approx 4.16$ µm, $L_\pi \approx 51.7$ µm on the slab estimate and 39.4 µm from the simulated eigenmodes, $L_{\text{MMI}} = 14.0$ µm and $d_y = 1.019$ µm from the sweeps.
- Taper length should be included in the optimization sweep; the linear profile already meets the insertion-loss target, so the parabolic variant was left out of scope.

---

## References

- Soldano, L. B., & Pennings, E. C. M. (1995). Optical multi-mode interference devices based on self-imaging: principles and applications. *Journal of Lightwave Technology*, 13(4), 615–627. — **The canonical MMI theory paper.**
- Bachmann, M., Besse, P. A., & Melchior, H. (1994). General self-imaging properties in N × N multimode interference couplers including phase relations. *Applied Optics*, 33(18), 3905–3911.
- Ulrich, R., & Ankele, G. (1975). Self-imaging in homogeneous planar optical waveguides. *Applied Physics Letters*, 27(6), 337–339. — Earliest formulation of the Talbot effect in guided-wave optics.
- Chrostowski, L., & Hochberg, M. (2015). *Silicon Photonics Design: From Devices to Systems*. Cambridge University Press. Chapter 4.
- Reed, G. T., & Knights, A. P. (2004). *Silicon Photonics: An Introduction*. Wiley. Chapter 4.
