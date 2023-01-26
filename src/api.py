from typing import Union
import time

import numpy as np
from internals import (
    _looping_animated_2D_image,
    _looping_animated_closed_1D_curve,
    _tileable_2D_image,
)
from opensimplex.api import DEFAULT_SEED
from opensimplex.internals import _init

try:
    from numba_progress import ProgressBar
except ImportError:
    ProgressBar = None

"""
Higher-level OpenSimplex noise functions by Dennis van Gils.

Inspired by [Coding Challenge #136.1: Polar Perlin Noise Loops]
(https://www.youtube.com/watch?v=ZI1dmHv3MeM) from [The Coding Train]
(https://www.youtube.com/c/TheCodingTrain).
"""


def progress_bar_wrapper(
    noise_fun: callable,
    noise_kwargs: list,
    verbose: bool = True,
    total: int = 1,
):
    if verbose:
        print(f"{'Generating noise...':30s}")
        tick = time.perf_counter()

    if (ProgressBar is None) or (not verbose):
        out = noise_fun(**noise_kwargs)
    else:
        with ProgressBar(total=total, dynamic_ncols=True) as numba_progress:
            out = noise_fun(**noise_kwargs, progress_hook=numba_progress)

    if verbose:
        print(f"done in {(time.perf_counter() - tick):.2f} s")

    return out


def looping_animated_2D_image(
    N_frames: int = 200,
    N_pixels_x: int = 1000,
    N_pixels_y: Union[int, None] = None,
    t_step: float = 0.1,
    x_step: float = 0.01,
    y_step: Union[float, None] = None,
    dtype: type = np.double,
    seed: int = DEFAULT_SEED,
    verbose: bool = True,
) -> np.ndarray:
    """Generates a stack of seamlessly-looping animated 2D images drawn from
    OpenSimplex noise.

    The algorithm uses OpenSimplex noise in 4 dimensions. The first two
    dimensions are used to describe a plane in space, which gets projected onto
    the 2D image. The last two dimensions are used to describe a circle in
    time.

    :param N_frames:   Number of time frames (int, default=200)
    :param N_pixels_x: Number of pixels on the x-axis (int, default=1000)
    :param N_pixels_y: Number of pixels on the y-axis. When set to None
                       `N_pixels_y` will be set equal to `N_pixels_x`.
                       (int | None, default=None)
    :param t_step:     Time step (float, default=0.1)
    :param x_step:     Spatial step in the x-direction (float, default=0.01)
    :param y_step:     Spatial step in the y-direction. When set to None
                       `y_step` will be set equal to `x_step`.
                       (float | None, default=None)
    :param dtype:      Return type of the noise array elements. To reduce the
                       memory footprint one can change from the default
                       `numpy.double` to e.g. `numpy.float32`.
                       (type, default=numpy.double)
    :param seed:       Seed value of the OpenSimplex noise (int, default=3)
    :param verbose:    Print 'Generating noise...' to the terminal? If the
                       `numba` and `numba_progress` packages are found a
                       progress bar will also be shown.
                       (bool, default=True)
    :return: The 2D image stack as 3D array [time, y-pixel, x-pixel] containing
             the OpenSimplex noise values as floating points. The output is
             garantueed to be in the range [-1, 1], but the exact extrema cannot
             be known a-priori and are probably quite smaller than [-1, 1].
    """

    perm, _ = _init(seed)

    out = progress_bar_wrapper(
        noise_fun=_looping_animated_2D_image,
        noise_kwargs={
            "N_frames": N_frames,
            "N_pixels_x": N_pixels_x,
            "N_pixels_y": N_pixels_y if N_pixels_y is not None else N_pixels_x,
            "t_step": t_step,
            "x_step": x_step,
            "y_step": y_step if y_step is not None else x_step,
            "dtype": dtype,
            "perm": perm,
        },
        verbose=verbose,
        total=N_frames,
    )

    return out


def looping_animated_closed_1D_curve(
    N_frames: int = 200,
    N_pixels_x: int = 1000,
    t_step: float = 0.1,
    x_step: float = 0.01,
    dtype: type = np.double,
    seed: int = DEFAULT_SEED,
    verbose: bool = True,
) -> np.ndarray:
    """Generates a stack of seamlessly-looping animated 1D curves, each curve in
    turn also closing up seamlessly back-to-front, all drawn from OpenSimplex
    noise.

    The algorithm uses OpenSimplex noise in 4 dimensions. The first two
    dimensions are used to describe a circle in space, which gets projected onto
    the 1D curve. The last two dimensions are used to describe a circle in time.

    :param N_frames:   Number of time frames (int, default=200)
    :param N_pixels_x: Number of pixels of the curve (int, default=1000)
    :param t_step:     Time step (float, default=0.1)
    :param x_step:     Spatial step in the x-direction (float, default=0.01)
    :param dtype:      Return type of the noise array elements. To reduce the
                       memory footprint one can change from the default
                       `numpy.double` to e.g. `numpy.float32`.
                       (type, default=numpy.double)
    :param seed:       Seed value of the OpenSimplex noise (int, default=3)
    :param verbose:    Print 'Generating noise...' to the terminal? If the
                       `numba` and `numba_progress` packages are found a
                       progress bar will also be shown.
                       (bool, default=True)
    :return: The 1D curve stack as 2D array [time, x-pixel] containing
             the OpenSimplex noise values as floating points. The output is
             garantueed to be in the range [-1, 1], but the exact extrema cannot
             be known a-priori and are probably quite smaller than [-1, 1].
    """

    perm, _ = _init(seed)  # The OpenSimplex seed table

    out = progress_bar_wrapper(
        noise_fun=_looping_animated_closed_1D_curve,
        noise_kwargs={
            "N_frames": N_frames,
            "N_pixels_x": N_pixels_x,
            "t_step": t_step,
            "x_step": x_step,
            "dtype": dtype,
            "perm": perm,
        },
        verbose=verbose,
        total=N_frames,
    )

    return out


def tileable_2D_image(
    N_pixels_x: int = 1000,
    N_pixels_y: Union[int, None] = None,
    x_step: float = 0.01,
    y_step: Union[float, None] = None,
    dtype: type = np.double,
    seed: int = DEFAULT_SEED,
    verbose: bool = True,
) -> np.ndarray:
    """Generates a seamlessly-tileable 2D image drawn from OpenSimplex noise.

    The algorithm uses OpenSimplex noise in 4 dimensions. The first two
    dimensions are used to describe a circle in space, which gets projected onto
    the x-axis of the 2D image. The last two dimensions are used to describe
    another circle in space, which gets projected onto the y-axis of the 2D
    image.

    :param N_pixels_x: Number of pixels on the x-axis (int, default=1000)
    :param N_pixels_y: Number of pixels on the y-axis. When set to None
                       `N_pixels_y` will be set equal to `N_pixels_x`.
                       (int | None, default=None)
    :param x_step:     Spatial step in the x-direction (float, default=0.01)
    :param y_step:     Spatial step in the y-direction. When set to None
                       `y_step` will be set equal to `x_step`.
                       (float | None, default=None)
    :param dtype:      Return type of the noise array elements. To reduce the
                       memory footprint one can change from the default
                       `numpy.double` to e.g. `numpy.float32`.
                       (type, default=numpy.double)
    :param seed:       Seed value of the OpenSimplex noise (int, default=3)
    :param verbose:    Print 'Generating noise...' to the terminal? If the
                       `numba` and `numba_progress` packages are found a
                       progress bar will also be shown.
                       (bool, default=True)
    :return: The 2D image stack as 3D array [time, y-pixel, x-pixel] containing
             the OpenSimplex noise values as floating points. The output is
             garantueed to be in the range [-1, 1], but the exact extrema cannot
             be known a-priori and are probably quite smaller than [-1, 1].
    """

    perm, _ = _init(seed)

    out = progress_bar_wrapper(
        noise_fun=_tileable_2D_image,
        noise_kwargs={
            "N_pixels_x": N_pixels_x,
            "N_pixels_y": N_pixels_y if N_pixels_y is not None else N_pixels_x,
            "x_step": x_step,
            "y_step": y_step if y_step is not None else x_step,
            "dtype": dtype,
            "perm": perm,
        },
        verbose=verbose,
        total=N_pixels_y,
    )

    return out
