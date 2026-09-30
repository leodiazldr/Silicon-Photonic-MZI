# Carrier-Depletion PN Junction Phase Shifter Theory

*Phase 3 of the MZI BB84 modulator project. Complements [[MMI Theory]] and the numbered CHARGE
scripts in [`../PhaseShifter/CHARGE/`](../PhaseShifter/CHARGE/).*

## 1. Why Silicon Needs a Special Modulation Mechanism

Silicon is centrosymmetric, so it has **no linear electro-optic (Pockels) effect** — its second-order susceptibility $\chi^{(2)}$ vanishes. The Kerr effect ($\chi^{(3)}$) is too weak at practical voltages, and the Franz–Keldysh effect requires impractically large fields. Two mechanisms remain:

| Mechanism                          | Physical basis                                                    | Speed | Notes                                        |
| ---------------------------------- | ----------------------------------------------------------------- | ----- | -------------------------------------------- |
| **Thermo-optic**                   | $\mathrm{d}n/\mathrm{d}T \approx 1.8\times10^{-4}\ \text{K}^{-1}$ | µs–ms | Slow; used for bias trimming, not modulation |
| **Free-carrier plasma dispersion** | Carriers change $n$ and $\alpha$                                  | GHz   | The standard for high-speed modulators       |

Within the free-carrier family there are two operating regimes:

- **Carrier injection** (forward-biased PIN diode): large $\Delta n$, but limited by carrier recombination lifetime (~ns), so slow and lossy.
- **Carrier depletion** (reverse-biased PN junction): smaller $\Delta n$, but the response is set by the depletion-layer dynamics and the RC time constant, not carrier lifetime → **GHz bandwidth**. This is the regime used here.

## 2. Plasma Dispersion Effect (Soref–Bennett Model)

The empirical Soref–Bennett model (1987) relates free-carrier density changes to changes in refractive index and absorption. At $\lambda = 1550$ nm:

$$
\Delta n = -8.8\times10^{-22}\,\Delta N_e \;-\; 8.5\times10^{-18}\,(\Delta N_h)^{0.8}
$$

$$
\Delta \alpha = 8.5\times10^{-18}\,\Delta N_e \;+\; 6.0\times10^{-18}\,\Delta N_h \qquad [\text{cm}^{-1}]
$$

with $\Delta N_e$ and $\Delta N_h$ in $\text{cm}^{-3}$.

Three facts drive the whole design:

1. **Adding carriers lowers the index** ($\Delta n < 0$ for $\Delta N > 0$). Conversely, *removing* carriers (depleting a region) *raises* the local index.
2. **Holes are more effective than electrons** per carrier (the $0.8$ power and the larger prefactor).
3. **Adding carriers increases absorption** ($\Delta\alpha > 0$). Depletion therefore *reduces* absorption inside the depletion region — but the surrounding still-doped regions remain lossy.

## 3. PN Junction Fundamentals

### 3.1 Doping

- **Donors** (n-type, e.g. phosphorus): concentration $N_D$.
- **Acceptors** (p-type, e.g. boron): concentration $N_A$.
- **Contact regions** are heavily doped ($\text{p}^+$, $\text{n}^+ \sim 10^{20}\ \text{cm}^{-3}$) to form low-resistance ohmic contacts with the metal vias. They are placed far from the optical mode to limit excess loss.

### 3.2 Built-In Potential

At thermal equilibrium, diffusion of carriers across the junction is balanced by the built-in electric field:

$$
V_{bi} = \frac{kT}{q}\ln\!\left(\frac{N_A N_D}{n_i^2}\right)
$$

with $n_i(\text{Si}) \approx 1.5\times10^{10}\ \text{cm}^{-3}$ and $kT/q \approx 25.9$ mV at 300 K. For the asymmetric profile used in this project, $N_A = 2\times10^{17}$ and $N_D = 1\times10^{17}\ \text{cm}^{-3}$, this gives $V_{bi} \approx 0.83$ V.

### 3.3 Depletion Region

Near the junction, carriers recombine/diffuse away, leaving behind **ionized dopant atoms** that form a space-charge region (the depletion layer) depleted of free carriers. For an abrupt junction, the depletion width under applied bias $V$ is:

$$
W_{\text{dep}} = \sqrt{\frac{2\,\varepsilon_s\,(V_{bi} - V)\,(N_A + N_D)}{q\,N_A N_D}}
$$

with $\varepsilon_s = 11.7\,\varepsilon_0 \approx 1.04\times10^{-10}$ F/m. For a symmetric junction ($N_A = N_D = N$) this reduces to the familiar $W_{\text{dep}} = \sqrt{4\varepsilon_s (V_{bi} - V) / (qN)}$.

Under reverse bias ($V < 0$) the term $V_{bi} - V$ grows, so the depletion layer widens. **This widening is the modulation mechanism**: a growing volume of silicon is emptied of carriers as the reverse bias increases.

### 3.4 What the Simulation Gives

The formula above assumes a uniform doping step, which the fabricated device (and the model) does not have. The CHARGE drift-diffusion simulation returns 152 nm at 0 V growing to 285 nm at −1.5 V, against 127 nm and 213 nm from the closed form — the same $\sqrt{V_{bi} - V}$ shape, 20–34 % wider in magnitude:

| Bias $V$ | $W_{\text{dep}}$, theory | $W_{\text{dep}}$, simulation | Difference |
|----------|--------------------------|------------------------------|------------|
| 0 V      | 126.9 nm                 | 152.1 nm                     | +19.8 %    |
| −0.75 V  | 175.1 nm                 | 226.1 nm                     | +29.1 %    |
| −1.5 V   | 212.6 nm                 | 284.6 nm                     | +33.9 %    |

The offset comes from the graded Pearson-IV doping profile implemented in [`../PhaseShifter/CHARGE/step06_doping.lsf`](../PhaseShifter/CHARGE/step06_doping.lsf) — so the concentration at the junction is below the nominal peak — together with a carrier-recovery edge criterion that reads about one Debye length beyond the ideal edge. The full discussion and the measured $W_{\text{dep}}(V)$ curve are in [`../PhaseShifter/CHARGE/README.md`](../PhaseShifter/CHARGE/README.md).

The takeaway for the rest of this note: the closed-form junction model is good enough for *sizing* and for predicting trends (wider depletion with reverse bias, lower capacitance, more efficient phase shift), but the efficiency and loss numbers used for the design come from the simulation, not from the formula.

## 4. How Depletion Modulates the Optical Phase

The optical mode is guided by the waveguide, whose center is placed at (or near) the junction. As reverse bias grows:

1. The depletion region expands into the doped silicon.
2. Free carriers ($\Delta N_e, \Delta N_h < 0$) are removed from that volume.
3. Via Soref–Bennett, the local index **increases** ($\Delta n > 0$) in the depletion volume.
4. The effective index of the mode increases accordingly.
5. The accumulated phase $\Delta\varphi = (2\pi/\lambda)\,\Delta n_{\text{eff}}\,L$ shifts.

Because the process is purely electrostatic (no carrier injection or recombination required), the response time is set by how fast the depletion layer can move — i.e. by the RC time constant — giving GHz-scale operation.

## 5. From Local $\Delta n(x,z)$ to $\Delta n_{\text{eff}}$

The Soref–Bennett equations give a *local* index change at each point of the cross-section. The mode does not sample it uniformly, so the relevant quantity is the **mode-weighted overlap integral** (first-order perturbation theory):

$$
\Delta n_{\text{eff}} = \frac{\displaystyle\iint \Delta n(x,z)\,\big|E(x,z)\big|^2\,\mathrm{d}x\,\mathrm{d}z}{\displaystyle\iint \big|E(x,z)\big|^2\,\mathrm{d}x\,\mathrm{d}z}
$$

and similarly for the loss:

$$
\Delta \alpha_{\text{eff}} = \frac{\displaystyle\iint \Delta \alpha(x,z)\,\big|E(x,z)\big|^2\,\mathrm{d}x\,\mathrm{d}z}{\displaystyle\iint \big|E(x,z)\big|^2\,\mathrm{d}x\,\mathrm{d}z}
$$

where $\Delta n(x,z)$ and $\Delta \alpha(x,z)$ are computed point-by-point from the local carrier-density change using Soref–Bennett. **This overlap integral is the hand-off between CHARGE and MODE**: CHARGE produces the carrier maps, MODE computes the mode profile, and their overlap gives $\Delta n_{\text{eff}}$, $\Delta \alpha_{\text{eff}}$.

The immediate design consequence: the junction should sit where the mode intensity is largest (the waveguide center) to maximize $\Delta n_{\text{eff}}$. This is why the junction offset is a key optimization parameter.

## 6. Phase Shift and the $V_\pi L$ Figure of Merit

The phase shift over a modulator of length $L$ is:

$$
\Delta\varphi(V) = \frac{2\pi}{\lambda}\,\Delta n_{\text{eff}}(V)\,L
$$

The **voltage–length product** $V_\pi L$ is the voltage required to produce a $\pi$ phase shift, multiplied by the device length:

$$
V_\pi L = V_\pi \times L = \frac{\lambda}{2\,\left(\partial \Delta n_{\text{eff}}/\partial V\right)_{\text{per unit length}}}
$$

It is the standard efficiency metric because it is (approximately) independent of length: a shorter device needs proportionally more voltage. Typical silicon carrier-depletion modulators achieve $V_\pi L \approx 1$–$3\ \text{V}\cdot\text{cm}$. For a 2 mm device this corresponds to $V_\pi \approx 5$–$15$ V.

## 7. Bandwidth: the RC Limit

Depletion modulators are not limited by carrier lifetime, so their bandwidth is set by the electrical RC time constant:

$$
f_{3\text{dB}} = \frac{1}{2\pi\,R\,C}
$$

- **Capacitance** is the junction capacitance: $C = \varepsilon_s A / W_{\text{dep}}$, where $A$ is the junction area. Because $W_{\text{dep}}$ grows with reverse bias, $C$ *decreases* with bias (a voltage-dependent capacitance).
- **Series resistance** $R$ comes from the metal contacts, the vias, and the lightly-doped silicon slab that carries current to the junction.

Reducing $R$ and $C$ simultaneously is the central electrical trade-off. Typical numbers: junction area $0.22\ \mu\text{m} \times 1\ \text{mm} = 220\ \mu\text{m}^2$, $C \approx 0.5$ pF, $R \approx 50\ \Omega$ → $f_{3\text{dB}} \approx 7$ GHz.

## 8. Design Trade-Offs

| Parameter | High value | Low value |
|-----------|-----------|-----------|
| **Doping $N_A, N_D$** | More efficient ($\Delta n_{\text{eff}}$ per volt larger) but higher optical loss and higher capacitance | Lower loss, lower $C$, but less efficient |
| **Junction offset** | At mode center → maximum overlap → maximum $\Delta n_{\text{eff}}$, but maximum overlap with remaining doped carriers → higher loss | Offset → lower loss, lower efficiency |
| **Device length $L$** | Lower $V_\pi$ required, but more loss and area | Compact, but higher drive voltage |

The classic triangle is **efficiency vs. optical loss vs. bandwidth** — improving one usually costs the other two. The optimization in Task 3.3 sweeps this space to find the best compromise against the targets below.

## 9. CHARGE Simulation Methodology (Task 3.1)

CHARGE is a **drift-diffusion** solver: it self-consistently solves Poisson's equation together with the electron and hole continuity equations to obtain $n(\mathbf{r})$, $p(\mathbf{r})$, and the electrostatic potential $V(\mathbf{r})$. It is *not* an optical solver — it is purely electrical.

The Task 3.1 workflow (the numbered scripts in [`../PhaseShifter/CHARGE/`](../PhaseShifter/CHARGE/README.md)):

1. **Geometry**: build the 220 nm silicon slab between oxide BOX and cladding in the cross-section plane.
2. **Doping**: place the p, n (moderate) and $\text{p}^+$, $\text{n}^+$ (heavy) regions, with the junction offset a free parameter.
3. **Contacts**: add ohmic contacts on the $\text{p}^+$ (anode) and $\text{n}^+$ (cathode) regions.
4. **Equilibrium**: run at $V = 0$ and verify the built-in potential $\approx V_{bi}$.
5. **DC sweep**: sweep the anode from 0 to −1.5 V (reverse bias), re-solving at each point.
6. **Export**: save the 2D maps $n(x,z)$, $p(x,z)$, $V(x,z)$ at each bias — these feed the MODE electro-optic simulation in Task 3.2.

The outputs to carry forward: carrier-density maps as functions of bias, from which $\Delta n(x,z)$ and $\Delta \alpha(x,z)$ are computed via Soref–Bennett.

## 10. Design Targets (from the project plan)

| Metric | Typical Si carrier-depletion | This project's target |
|--------|------------------------------|-----------------------|
| $V_\pi L$ | 1–3 V·cm | < 3 V·cm |
| Insertion loss ($\pi$ shift) | 2–5 dB | < 5 dB |
| 3 dB EO bandwidth | 10–40 GHz | > 10 GHz |
| Extinction ratio | > 20 dB | > 20 dB |

---

## References

- Soref, R. A., & Bennett, B. R. (1987). Electrooptical effects in silicon. *IEEE J. Quantum Electron.*, 23(1), 123–129. — The canonical plasma-dispersion paper.
- Reed, G. T., Mashanovich, G., Gardes, F. Y., & Thomson, D. J. (2010). Silicon optical modulators. *Nature Photonics*, 4(8), 518–526. — Overview of Si modulator physics.
- Chrostowski, L., & Hochberg, M. (2015). *Silicon Photonics Design: From Devices to Systems*. Cambridge University Press. Chapter 5 (modulators).
- Sze, S. M., & Ng, K. K. (2006). *Physics of Semiconductor Devices*. Wiley. Chapters 2–3 (PN junction fundamentals).
