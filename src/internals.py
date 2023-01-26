#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Internal functions belonging to `opensimplex_loops.py`.
"""
__author__ = "Dennis van Gils"
__authoremail__ = "vangils.dennis@gmail.com"
__url__ = "https://github.com/Dennis-van-Gils/opensimplex-loops"
# pylint: disable=invalid-name

from typing import Union

import numpy as np
from opensimplex.internals import _noise4

try:
    from numba import njit, prange
except ImportError:
    prange = range

    def njit(*args, **kwargs):  # pylint: disable=unused-argument
        def wrapper(func):
            return func

        return wrapper


try:
    from numba_progress import ProgressBar
except ImportError:
    ProgressBar = None


@njit(
    cache=True,
    parallel=True,
    nogil=True,
)
def _looping_animated_2D_image(
    N_frames: int,
    N_pixels_x: int,
    N_pixels_y: int,
    t_step: float,
    x_step: float,
    y_step: float,
    dtype: type,
    perm: np.ndarray,
    progress_hook: Union[ProgressBar, None] = None,
) -> np.ndarray:
    noise = np.empty((N_frames, N_pixels_y, N_pixels_x), dtype=dtype)
    t_radius = N_frames * t_step / (2 * np.pi)
    t_factor = 2 * np.pi / N_frames

    for t_i in prange(N_frames):
        t = t_i * t_factor
        t_cos = t_radius * np.cos(t)
        t_sin = t_radius * np.sin(t)

        for y_i in prange(N_pixels_y):
            y = y_i * y_step

            for x_i in prange(N_pixels_x):
                x = x_i * x_step
                noise[t_i, y_i, x_i] = _noise4(x, y, t_sin, t_cos, perm)

        if progress_hook is not None:
            progress_hook.update(1)

    return noise


@njit(
    cache=True,
    parallel=True,
    nogil=True,
)
def _looping_animated_closed_1D_curve(
    N_frames: int,
    N_pixels_x: int,
    t_step: float,
    x_step: float,
    dtype: type,
    perm: np.ndarray,
    progress_hook: Union[ProgressBar, None] = None,
) -> np.ndarray:
    noise = np.empty((N_frames, N_pixels_x), dtype=dtype)
    t_radius = N_frames * t_step / (2 * np.pi)
    x_radius = N_pixels_x * x_step / (2 * np.pi)
    t_factor = 2 * np.pi / N_frames
    x_factor = 2 * np.pi / N_pixels_x

    for t_i in prange(N_frames):
        t = t_i * t_factor
        t_cos = t_radius * np.cos(t)
        t_sin = t_radius * np.sin(t)

        for x_i in prange(N_pixels_x):
            x = x_i * x_factor
            x_cos = x_radius * np.cos(x)
            x_sin = x_radius * np.sin(x)
            noise[t_i, x_i] = _noise4(x_sin, x_cos, t_sin, t_cos, perm)

        if progress_hook is not None:
            progress_hook.update(1)

    return noise


@njit(
    cache=True,
    parallel=True,
    nogil=True,
)
def _tileable_2D_image(
    N_pixels_x: int,
    N_pixels_y: int,
    x_step: float,
    y_step: float,
    dtype: type,
    perm: np.ndarray,
    progress_hook: Union[ProgressBar, None] = None,
) -> np.ndarray:
    noise = np.empty((N_pixels_y, N_pixels_x), dtype=dtype)
    x_radius = N_pixels_x * x_step / (2 * np.pi)
    y_radius = N_pixels_y * y_step / (2 * np.pi)
    x_factor = 2 * np.pi / N_pixels_x
    y_factor = 2 * np.pi / N_pixels_y

    for y_i in prange(N_pixels_y):
        y = y_i * y_factor
        y_cos = y_radius * np.cos(y)
        y_sin = y_radius * np.sin(y)

        for x_i in prange(N_pixels_x):
            x = x_i * x_factor
            x_cos = x_radius * np.cos(x)
            x_sin = x_radius * np.sin(x)
            noise[y_i, x_i] = _noise4(x_sin, x_cos, y_sin, y_cos, perm)

        if progress_hook is not None:
            progress_hook.update(1)

    return noise
