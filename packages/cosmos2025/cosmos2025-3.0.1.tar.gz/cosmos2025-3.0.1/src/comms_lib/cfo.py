import numpy as np


def estimate_cfo(rx_signal: np.ndarray, seq_num: int, seq_len: int, Ts: float):
    """Estimate coarse CFO from the STF/LTF portion of a received signal.

    Args:
        received_signal (np.ndarray): The received complex baseband samples
            containing the entire STF or LTF (should contain at least K * N samples).
        seq_num (int): Total number of sequence repetitions in STF or LTF.
        seq_len (int): Length of each repeated sequence in samples.
        Ts (float): Sampling period in seconds.

    Returns:
        float: Estimated coarse carrier frequency offset (Hz).

    Raises:
        ValueError: If seq_num < 2 (need at least 2 repetitions to form 1 pair for CFO estimation).
        AssertionError: If signal is too short for given seq_num and seq_len.
    """
    if seq_num < 2:
        raise ValueError(
            "Need at least 2 repetitions to form 1 pair for CFO estimation"
        )

    # Need K repeated segments → (K - 1) pairs
    assert len(rx_signal) >= seq_num * seq_len, (
        "Signal too short for given seq_num and seq_len"
    )

    acc = 0.0 + 0.0j
    for k in range(seq_num - 1):  # Now we form (K - 1) pairs
        r1 = rx_signal[k * seq_len : (k + 1) * seq_len]
        r2 = rx_signal[(k + 1) * seq_len : (k + 2) * seq_len]
        acc += np.vdot(r1, r2)

    angle = np.angle(acc)
    f_cfo = angle / (2 * np.pi * seq_len * Ts)

    return f_cfo


def correct_cfo(rx_signal: np.ndarray, f_cfo: float, Ts: float) -> np.ndarray:
    """Correct the coarse CFO in the received signal.

    Args:
        received_signal (np.ndarray): The received complex baseband samples.
        f_cfo (float): Estimated coarse carrier frequency offset (Hz).
        Ts (float): Sampling period in seconds.

    Returns:
        np.ndarray: Received signal with CFO corrected.
    """
    num_samples = len(rx_signal)
    correction_factor = np.exp(-1j * 2 * np.pi * f_cfo * Ts * np.arange(num_samples))
    corrected_signal = rx_signal * correction_factor

    return corrected_signal
