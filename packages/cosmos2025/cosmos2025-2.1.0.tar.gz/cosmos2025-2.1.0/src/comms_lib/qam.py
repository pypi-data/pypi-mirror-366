import numpy as np


def detect_qam(symbols: np.ndarray, M: int) -> np.ndarray:
    constellation = qam_constellation(M)
    distances = np.abs(symbols[:, None] - constellation[None, :])
    return constellation[np.argmin(distances, axis=1)]


def qam_constellation(M: int = 4) -> np.ndarray:
    """Generates random QAM constellation symbols from a square QAM constellation normalized to unit average symbol energy.

    Args:
        M (int): Order of the QAM constellation (e.g., 4 for QPSK, 16 for 16-QAM).
            Default is 4 (QPSK).

    Returns:
        np.ndarray: Array of `M`-QAM constellation points, centered around the origin and normalized to unit average symbol energy.
    """

    # check if M is a valid QAM order
    if not np.sqrt(M).is_integer() or M < 2:
        raise ValueError("M is not a valid QAM order.")

    # Generate constellation points
    constellation = np.array(
        [x + 1j * y for x in range(int(np.sqrt(M))) for y in range(int(np.sqrt(M)))]
    )
    constellation -= constellation.mean()  # Center constellation around origin
    constellation /= np.sqrt((np.abs(constellation) ** 2).mean())
    return constellation


def gen_rand_qam_symbols(N: int, M: int = 4) -> np.ndarray:
    """Generates random QAM constellation symbols from a square QAM constellation normalized to unit average symbol energy.

    Args:
        N (int): Number of symbols to generate.
        M (int): Order of the QAM constellation (e.g., 4 for QPSK, 16 for 16-QAM).
            Default is 4 (QPSK).

    Returns:
        np.ndarray: Array of randomly selected `M`-QAM symbols.
    """
    # Generate random symbols
    return np.random.default_rng().choice(qam_constellation(M), size=N, replace=True)


def inverse_gray(g: np.ndarray) -> np.ndarray:
    """Vectorized conversion of Gray-coded integers to natural binary integers."""
    mask = g >> 1
    m = g ^ mask
    while np.any(mask != 0):
        mask >>= 1
        m ^= mask
    return m


def gray_code(n: np.ndarray) -> np.ndarray:
    """Vectorized conversion of natural binary integers to Gray-coded integers."""
    return n ^ (n >> 1)


def qam_modulator(bits: np.ndarray, M: int) -> np.ndarray:
    """
    Maps a 1D array of bits to a QAM constellation with normalized average energy.

    This function takes a sequence of bits, groups them into symbols, and maps
    each group to a complex number representing a point in a Quadrature
    Amplitude Modulation (QAM) constellation. The mapping uses Gray coding to
    minimize the bit error rate. The resulting constellation is normalized to
    have an average energy of 1.

    Args:
        bits (np.ndarray): A 1D NumPy array of bits (0s and 1s). The length
            must be a multiple of log2(M).
        M (int): The order of the QAM constellation (e.g., 4, 16, 64).
            Must be a perfect square and a power of two.

    Returns:
        np.ndarray: A 1D NumPy array of complex numbers representing the
            QAM symbols.

    Raises:
        ValueError: If M is not a perfect square and a power of two, or if
                    the length of the bit stream is not a multiple of log2(M).
    """
    # --- 1. Input Validation ---
    if np.log2(M) % 1 != 0:
        raise ValueError("M must be a power of two.")
    if np.sqrt(M) % 1 != 0:
        raise ValueError("M must be a perfect square for rectangular QAM.")

    k = int(np.log2(M))
    if len(bits) % k != 0:
        raise ValueError(
            f"Length of bit stream ({len(bits)}) must be a multiple of log2(M)={k}."
        )

    # --- 2. Setup for Gray Mapping ---
    L = int(np.sqrt(M))  # Number of levels per dimension (I or Q)
    k_pam = int(np.log2(L))  # Number of bits per dimension
    pam_levels = np.arange(-(L - 1), L, 2)

    # --- 3. Vectorized Bit-to-Symbol Mapping ---
    num_symbols = len(bits) // k
    reshaped_bits = bits.reshape(num_symbols, k)

    # Split bits for I and Q components for all symbols at once
    bits_I = reshaped_bits[:, :k_pam]
    bits_Q = reshaped_bits[:, k_pam:]

    # Create a powers-of-2 vector to convert binary arrays to integers
    # e.g., for k_pam=2, powers = [2, 1]. A bit group [1, 0] becomes 1*2 + 0*1 = 2.
    powers = 2 ** np.arange(k_pam - 1, -1, -1)

    # Convert all I and Q bit groups to Gray-coded integers via matrix multiplication
    int_I_gray = bits_I @ powers
    int_Q_gray = bits_Q @ powers

    # Convert Gray-coded integers to natural binary integers to get indices
    idx_I = inverse_gray(int_I_gray)
    idx_Q = inverse_gray(int_Q_gray)

    # Use advanced indexing to look up the corresponding PAM levels for all symbols
    levels_I = pam_levels[idx_I]
    levels_Q = pam_levels[idx_Q]

    # Construct the complex symbols from the I and Q levels
    symbols = levels_I + 1j * levels_Q

    # --- 4. Normalize to Average Energy of 1 ---
    avg_energy = 2 * (M - 1) / 3
    normalized_symbols = symbols / np.sqrt(avg_energy)

    return normalized_symbols


def qam_demodulator(symbols: np.ndarray, M: int) -> np.ndarray:
    """
    Demodulates a 1D array of QAM symbols back into a bit stream.
    This implementation is fully vectorized using NumPy.
    """
    # --- Input Validation ---
    if np.log2(M) % 1 != 0:
        raise ValueError("M must be a power of two.")
    if np.sqrt(M) % 1 != 0:
        raise ValueError("M must be a perfect square for rectangular QAM.")

    # --- Setup ---
    L = int(np.sqrt(M))
    k = int(np.log2(M))
    k_pam = int(np.log2(L))
    pam_levels = np.arange(-(L - 1), L, 2)

    # --- 1. Denormalization ---
    avg_energy = 2 * (M - 1) / 3
    denormalized_symbols = symbols * np.sqrt(avg_energy)

    # --- 2. Slicing (Decision Making) ---
    # Separate I and Q components
    levels_I_rx = np.real(denormalized_symbols)
    levels_Q_rx = np.imag(denormalized_symbols)

    # For each received level, find the index of the closest ideal PAM level.
    # A simple way for uniformly spaced levels is to scale, round, and clip.
    # The distance between levels is 2. Decision boundaries are at 0, +/-2, +/-4...
    idx_I = np.clip(np.round((levels_I_rx + L - 1) / 2), 0, L - 1).astype(int)
    idx_Q = np.clip(np.round((levels_Q_rx + L - 1) / 2), 0, L - 1).astype(int)

    # --- 3. Index to Gray Code ---
    int_I_gray = gray_code(idx_I)
    int_Q_gray = gray_code(idx_Q)

    # --- 4. Gray Integers to Bits ---
    # Create a powers-of-2 vector for bit extraction
    powers = 2 ** np.arange(k_pam - 1, -1, -1)

    # Use broadcasting to extract bits from each integer
    bits_I = (int_I_gray[:, None] & powers) // powers
    bits_Q = (int_Q_gray[:, None] & powers) // powers

    # --- 5. Combine and Reshape ---
    demodulated_bits = np.hstack((bits_I, bits_Q)).flatten()

    return demodulated_bits
