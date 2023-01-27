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
def _polar_loop_rectangle(
    N_polar: int,
    N_rect_x: int,
    N_rect_y: int,
    step_polar: float,
    step_rect_x: float,
    step_rect_y: float,
    dtype: type,
    perm: np.ndarray,
    progress_hook: Union[ProgressBar, None] = None,
) -> np.ndarray:
    noise = np.empty((N_polar, N_rect_y, N_rect_x), dtype=dtype)
    radius = N_polar * step_polar / (2 * np.pi)
    factor = 2 * np.pi / N_polar

    # Polar loop
    for idx_t in prange(N_polar):
        t = idx_t * factor
        t_cos = radius * np.cos(t)
        t_sin = radius * np.sin(t)

        # Linear traversal y
        for idx_y in prange(N_rect_y):
            y = idx_y * step_rect_y

            # Linear traversal x
            for idx_x in prange(N_rect_x):
                x = idx_x * step_rect_x
                noise[idx_t, idx_y, idx_x] = _noise4(x, y, t_sin, t_cos, perm)

        if progress_hook is not None:
            progress_hook.update(1)

    return noise


@njit(
    cache=True,
    parallel=True,
    nogil=True,
)
def _double_polar_loop(
    N_polar_1: int,
    N_polar_2: int,
    step_polar_1: float,
    step_polar_2: float,
    dtype: type,
    perm: np.ndarray,
    progress_hook: Union[ProgressBar, None] = None,
) -> np.ndarray:
    noise = np.empty((N_polar_2, N_polar_1), dtype=dtype)
    radius_1 = N_polar_1 * step_polar_1 / (2 * np.pi)
    radius_2 = N_polar_2 * step_polar_2 / (2 * np.pi)
    factor_1 = 2 * np.pi / N_polar_1
    factor_2 = 2 * np.pi / N_polar_2

    # Polar loop 2
    for idx_2 in prange(N_polar_2):
        val_2 = idx_2 * factor_2
        cos_2 = radius_2 * np.cos(val_2)
        sin_2 = radius_2 * np.sin(val_2)

        # Polar loop 1
        for idx_1 in prange(N_polar_1):
            val_1 = idx_1 * factor_1
            cos_1 = radius_1 * np.cos(val_1)
            sin_1 = radius_1 * np.sin(val_1)
            noise[idx_2, idx_1] = _noise4(sin_1, cos_1, sin_2, cos_2, perm)

        if progress_hook is not None:
            progress_hook.update(1)

    return noise
