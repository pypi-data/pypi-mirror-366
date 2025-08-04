from numpy.typing import NDArray
from typing import Optional
from numpy import ndarray
from numba import njit
import numpy as np
import math


@njit
def iterate(a: float, b: float, n: int) -> tuple[ndarray, ndarray]:
    """calculates the simon attractor

    Args:
        a (float): _description_
        b (float): _description_
        n (int): _description_

    Returns:
        tuple[ndarray, ndarray]: arr_x, arr_y
        # arr_x[i], arr_y[i] => x, y at iteration i
    """
    x, y = a, b

    arr_x = np.zeros(shape=(n,), dtype=np.float64)
    arr_y = np.zeros(shape=(n,), dtype=np.float64)
    for i in range(n):
        x_new = math.sin(x**2 - y**2 + a)
        y_new = math.cos(2 * x * y + b)

        x, y = x_new, y_new
        arr_x[i] = x
        arr_y[i] = y

    return arr_x, arr_y


def render_frame(
    resolution: int,
    a: float,
    b: float,
    n: int,
    percentile: float,
    colors: Optional[NDArray[np.float32]] = None,
    raw: bool = True
) -> NDArray:
    """
    Computes the Simon Attractor and returns either a normalized histogram or a color-mapped image.

    Args:
        resolution (int): Resolution of the output grid (res x res). Runtime ~ O(n^2).
        a (float): Parameter 'a' for the Simon Attractor.
        b (float): Parameter 'b' for the Simon Attractor.
        n (int): Number of iterations. Higher values yield smoother output; usually n > 1_000_000.
        percentile (float): Clipping percentile for histogram normalization (e.g., 95-99.9).
        colors (NDArray[np.float32] | None): Colormap values in range [0, 1]. Required if raw is False.
        raw (bool): If True, returns raw normalized histogram. If False, returns color-mapped image.

    Returns:
        NDArray[np.float32] if raw=True, otherwise NDArray[np.uint8] (RGB image).
    """
    x_raw, y_raw = iterate(a, b, n)
    histogram, _, _ = np.histogram2d(x_raw, y_raw, bins=resolution)

    clip_max = np.percentile(histogram, percentile)
    if clip_max == 0 or np.isnan(clip_max):
        clip_max = 1.0

    h_normalized = np.clip(histogram / clip_max, 0, 1).astype(np.float32)

    if raw:
        return h_normalized

    if colors is None:
        raise ValueError("`colors` must be provided when raw=False.")

    values = (h_normalized * 255).astype(int)
    img = (colors[values] * 255).astype(np.uint8)
    return img
