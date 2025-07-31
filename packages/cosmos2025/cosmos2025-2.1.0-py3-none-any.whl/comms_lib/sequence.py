import numpy as np


def zadoff_chu_sequence(N: int, q: int) -> np.ndarray:
    """
    Generate a Zadoff-Chu sequence of length N with root index q.
    Args:
        N (int): Length of the sequence (should be a prime number).
        q (int): Root index (should be co-prime to N).

    Returns:
        np.ndarray: Zadoff-Chu sequence of length N.
    """

    if np.gcd(N, q) != 1:
        raise ValueError("Root index q must be co-prime to length N.")

    n = np.arange(N)
    zc_sequence = np.exp(-1j * np.pi * q * n * (n + 1) / N)
    return zc_sequence
