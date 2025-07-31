import numpy as np
from numpy.typing import ArrayLike


def pulse_shape(
    symbols: ArrayLike, pulse: ArrayLike, sps: int, conv: bool = False
) -> np.ndarray:
    """Pulse shape a sequence of symbols using a specified pulse type.

    Args:
        symbols (np.ndarray): Array of symbols.
        pulse (np.ndarray): Pulse shape to use for shaping the symbols.
            The pulses are assumed to be symmetric and centered around zero.
            The length of the pulse should be odd.
        sps (int): Samples per symbol: the number of discrete-time samples from one symbol to the next,
            should match that of the pulse shape.
        conv (bool): If True, use convolution method instead of direct addition.

    Returns:
        np.ndarray: Pulse-shaped signal with zeros inserted between symbols.
    """
    if len(pulse) % 2 == 0:
        raise ValueError("Pulse length must be odd for proper centering.")

    if conv:
        return _pulse_shape_convolution(symbols, pulse, sps)
    else:
        return _pulse_shape_add(symbols, pulse, sps)


def _pulse_shape_add(symbols: ArrayLike, pulse: ArrayLike, sps: int) -> np.ndarray:
    """Pulse shape a sequence of symbols using a specified pulse type by direct addition.
    This method scales better with higher sps.

    Args:
        symbols (np.ndarray): Array of symbols.
        pulse (np.ndarray): Pulse shape to use for shaping the symbols.
            The pulses are assumed to be symmetric and centered around zero.
            The length of the pulse should be odd.
        sps (int): Samples per symbol: the number of discrete-time samples from one symbol to the next,
            should match that of the pulse shape.

    Returns:
        np.ndarray: Pulse-shaped signal with zeros inserted between symbols.
    """

    # Calculate the pulses for each symbol
    pulses = np.outer(symbols, pulse)

    # initialize output signal to match convolution size: len(symbols) * sps + len(pulse) - 1
    signal = np.zeros(len(symbols) * sps + pulse.shape[0] - 1, dtype=complex)

    # Calculate the indices at which the pulses should be added
    inds = np.arange(len(symbols))[:, None] * sps + np.arange(pulse.shape[0])

    np.add.at(signal, inds.flatten(), pulses.flatten())
    return signal


def _pulse_shape_convolution(symbols, pulse, sps: int) -> np.ndarray:
    """Alternative implementation using create_pulse_train + convolution."""
    # Create pulse train (impulse train from symbols)
    upsampled_symbols = np.zeros(len(symbols) * sps, dtype=complex)
    upsampled_symbols[::sps] = symbols
    return np.convolve(upsampled_symbols, pulse, mode="full")


def get_rc_pulse(beta: float, span: int, sps: int) -> np.ndarray:
    """Generates raised cosine pulse.

    Args:
        beta (float): Roll-off factor in [0, 1].
        span (int): Number of symbol durations spanned by the pulse,
            not including the symbol at t=0.
        sps (int): Samples per symbol

    Returns:
        np.ndarray: Raised cosine pulse normalized to unit energy at peak.
            The number of zero crossings is equal to `span`.
    """

    T = 1  # Symbol duration = 1
    t = np.arange(-span * sps / 2, span * sps / 2 + 1) / sps

    if len(t) % 2 == 0:
        raise ValueError("Time vector length must be odd for proper centering.")

    # if beta is 0, return sinc pulse
    if beta == 0:
        return np.sinc(t / T)

    # check for t = +- T / (2 * beta)
    mask = np.abs(t) != (T / (2 * beta))

    # Calculate the raised cosine pulse
    rc_pulse = np.zeros_like(t)
    rc_pulse[~mask] = np.pi / (4 * T) * np.sinc(1 / (2 * beta))

    rc_pulse[mask] = (
        np.sinc(t[mask] / T)
        * np.cos(np.pi * beta * t[mask] / T)
        / (1 - (2 * beta * t[mask] / T) ** 2)
    ) / T

    return rc_pulse


def get_rrc_pulse(beta: float, span: int, sps: int) -> np.ndarray:
    """Generates root raised cosine pulse.

    Args:
        beta (float): Roll-off factor in [0, 1].
        span (int): Number of symbol durations spanned by the pulse,
            not including the symbol at t=0.
        sps (int): Samples per symbol

    Returns:
        np.ndarray: Root raised cosine pulse normalized to unit energy at peak.
            The number of zero crossings is equal to `span`.
    """

    T = 1  # Symbol duration = 1
    t = np.arange(-span * sps / 2, span * sps / 2 + 1) / sps

    if len(t) % 2 == 0:
        raise ValueError("Time vector length must be odd for proper centering.")

    # Special case: beta = 0 (root Nyquist pulse)
    if beta == 0:
        return np.sinc(t / T)

    pulse = np.zeros_like(t)

    # t = 0
    pulse[t == 0] = 1 / T * (1 + beta * (4 / np.pi - 1))

    # t = +- T / (4 * beta)
    mask = np.abs(t) == (T / (4 * beta))
    pulse[mask] = (beta / (np.sqrt(2) * T)) * (
        (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
        + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta))
    )

    # General case: t != 0 and t != +- T / (4 * beta)
    mask = (t != 0) & (np.abs(t) != (T / (4 * beta)))
    tT = t[mask] / T
    pulse[mask] = (
        np.sin(np.pi * tT * (1 - beta))
        + 4 * beta * tT * np.cos(np.pi * tT * (1 + beta))
    ) / (T * np.pi * tT * (1 - (4 * beta * tT) ** 2))

    return pulse
