# -*- coding: utf-8 -*-
"""
Created on Sat May  2 13:09:06 2026

@author: USUARIO
"""

"""
Cubic Bézier curves for low-loss waveguide bends.

Control points:
    P0 = (0, 0)
    P1 = (R*(1-delta), 0)
    P2 = (R, R*delta)
    P3 = (R, R)

For delta = 0   -> straight segments meeting at the corner (sharp).
For delta = 1   -> P1 = (0,0), P2 = (R,R): purely diagonal control.
Intermediate delta values give smooth bends with gradually varying curvature,
which reduces mode-mismatch loss compared to a circular arc (which has
discontinuous curvature at the straight-to-bend interface).

The radius of curvature of a parametric curve (x(t), y(t)) is:
    rho(t) = ( x'^2 + y'^2 )^(3/2) / | x' y'' - y' x'' |
"""

import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
# Cubic Bézier helpers
# ---------------------------------------------------------------
def bezier_points(R, delta):
    """Return the 4 control points of the cubic Bézier as a (4,2) array."""
    P0 = np.array([0.0,            0.0])
    P1 = np.array([R * (1 - delta), 0.0])
    P2 = np.array([R,               R * delta])
    P3 = np.array([R,               R])
    return np.vstack([P0, P1, P2, P3])


def bezier_curve(t, R, delta):
    """Cubic Bézier B(t), its first and second derivatives."""
    P = bezier_points(R, delta)
    P0, P1, P2, P3 = P[0], P[1], P[2], P[3]

    one_t = 1.0 - t
    # B(t)
    B = (one_t**3)[:, None]   * P0 \
      + (3*one_t**2 * t)[:, None] * P1 \
      + (3*one_t   * t**2)[:, None] * P2 \
      + (t**3)[:, None]            * P3

    # B'(t) = 3(1-t)^2 (P1-P0) + 6(1-t)t (P2-P1) + 3 t^2 (P3-P2)
    dB = 3*(one_t**2)[:, None]    * (P1 - P0) \
       + 6*(one_t * t)[:, None]   * (P2 - P1) \
       + 3*(t**2)[:, None]        * (P3 - P2)

    # B''(t) = 6(1-t)(P2 - 2P1 + P0) + 6t(P3 - 2P2 + P1)
    ddB = 6*(one_t)[:, None] * (P2 - 2*P1 + P0) \
        + 6*(t)[:, None]     * (P3 - 2*P2 + P1)

    return B, dB, ddB


def radius_of_curvature(t, R, delta):
    """Radius of curvature rho(t) along the Bézier."""
    _, dB, ddB = bezier_curve(t, R, delta)
    xp,  yp  = dB[:, 0],  dB[:, 1]
    xpp, ypp = ddB[:, 0], ddB[:, 1]

    num = (xp**2 + yp**2)**1.5
    den = np.abs(xp * ypp - yp * xpp)

    # Avoid division by zero (near inflection points or zero-velocity points)
    rho = np.where(den > 1e-15, num / np.maximum(den, 1e-15), np.inf)
    return rho


# ---------------------------------------------------------------
# Plot
# ---------------------------------------------------------------
R = 10.0                                  # bend radius (arbitrary units, e.g. µm)
deltas = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.45]
t = np.linspace(0.0, 1.0, 1000)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# --- Bezier curves in (x, y) ---
# Reference: circular quarter-arc of radius R for comparison
theta = np.linspace(1.5*np.pi, 2*np.pi, 500)
x_arc = R*np.cos(theta)
y_arc = R + R*np.sin(theta)
ax1.plot(x_arc, y_arc, 'k--', lw=1.2, label="Circular arc (R)")

cmap = plt.cm.viridis
for i, d in enumerate(deltas):
    B, _, _ = bezier_curve(t, R, d)
    color = cmap(i / max(1, len(deltas) - 1))
    ax1.plot(B[:, 0], B[:, 1], color=color, lw=2,
             label=fr"$\delta = {d:.2f}$")

ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_title(f"Cubic Bézier curves (R = {R} um)")
ax1.set_aspect("equal", adjustable="box")
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(fontsize=8, loc="upper left")

# --- Radius of curvature vs t ---
for i, d in enumerate(deltas):
    rho = radius_of_curvature(t, R, d)
    color = cmap(i / max(1, len(deltas) - 1))
    ax2.plot(t, rho, color=color, lw=2, label=fr"$\delta = {d:.2f}$")

ax2.axhline(R, color='k', linestyle='--', lw=1.2,
            label=f"Circular arc radius = {R} um")
ax2.set_xlabel("t")
ax2.set_ylabel(r"Radius of curvature $\rho(t)$")
ax2.set_title("Radius of curvature along the curve")
ax2.set_yscale("log")
ax2.grid(True, which="both", linestyle=":", alpha=0.6)
ax2.legend(fontsize=8)

# Cap y-axis sensibly (rho -> infinity at endpoints for delta < 1)
ax2.set_ylim(bottom=R*0.3)

fig.tight_layout()
fig.savefig("Bends/bezier_curves.png", dpi=300, bbox_inches="tight")
plt.show()


# ---------------------------------------------------------------
# Quick report: minimum radius of curvature for each delta
# ---------------------------------------------------------------
print(f"{'delta':>8s}  {'min rho':>10s}  {'min rho / R':>12s}")
for d in deltas:
    rho = radius_of_curvature(t, R, d)
    rho_min = np.nanmin(rho)
    print(f"{d:8.2f}  {rho_min:10.4f}  {rho_min/R:12.4f}")
