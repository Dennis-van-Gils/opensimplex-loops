#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dennis van Gils (https://github.com/Dennis-van-Gils)
"""

import sys

try:
    from matplotlib import pyplot as plt
    from matplotlib import animation
except ImportError:
    sys.exit("This demo requires the `matplotlib` package.")

import numpy as np
import opensimplex_loops as osl

N_FRAMES = 50
N_PIXELS = 256
FEATURE_SIZE = 10.0

MEAN_RADIUS = 4
PERIMETER_LOOPS = 1

# Generate noise
curve_stack = osl.looping_animated_closed_1D_curve(
    N_frames=N_FRAMES,
    N_pixels_x=N_PIXELS,
    t_step=0.1,
    x_step=1 / FEATURE_SIZE,
    seed=3,
    verbose=True,
)

# Construct polar curve
theta = np.linspace(0, 2 * np.pi, N_PIXELS * PERIMETER_LOOPS, endpoint=False)
theta = np.append(theta, 2 * np.pi)  # Seamlessly close the curve


def calc_radius(frame_in):
    r = MEAN_RADIUS + np.tile(frame_in, PERIMETER_LOOPS)
    r = np.append(r, r[0])  # Seamlessly close the curve
    return r


# Plot
perfect_circle_len = 128
fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
ax.plot(
    np.linspace(0, 2 * np.pi, perfect_circle_len),
    np.ones(perfect_circle_len) * MEAN_RADIUS,
    color="red",
    linestyle="dashed",
    linewidth=1,
)
(curve,) = ax.plot(theta, calc_radius(curve_stack[0]), color="C0")
plt.tight_layout()
ax.grid(False)
ax.set_axis_off()
ax.set_ylim((0, MEAN_RADIUS + 1))
frame_text = ax.text(0, 1.02, "", transform=ax.transAxes)


def anim_init():
    curve.set_ydata(calc_radius(curve_stack[0]))
    frame_text.set_text("")
    return curve, frame_text


def anim_fun(j):
    curve.set_ydata(calc_radius(curve_stack[j]))
    frame_text.set_text(f"frame {j:03d}")
    return curve, frame_text


anim = animation.FuncAnimation(
    fig,
    anim_fun,
    frames=len(curve_stack),
    interval=40,
    init_func=anim_init,
    # blit=True,
)

plt.show()

# Export image to disk?
if 0:
    anim.save(
        "demo_looping_animated_circle.gif",
        dpi=120,
        writer="imagemagick",
        fps=25,
    )
