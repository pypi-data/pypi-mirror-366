import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

def estimate_cfo(received_signal, K, N, Ts):
    """
    Estimate coarse CFO from the STF portion of a received signal.

    Parameters:
    - received_signal : np.ndarray
        The received complex baseband samples containing the STF
        (should contain at least K * N samples)
    - K : int
        Total number of repeated short symbols in STF 
    - N : int
        Length of each repeated sequence in samples
    - Ts : float
        Sampling period in seconds 

    Returns:
    - f_cfo : float
        Estimated coarse carrier frequency offset (Hz)
    """
    if K < 2:
        raise ValueError("Need at least 2 repetitions to form 1 pair for CFO estimation")
    
    # Need K repeated segments → (K - 1) pairs
    assert len(received_signal) >= K * N, "Signal too short for given K and N"

    acc = 0.0 + 0.0j
    for k in range(K - 1):  # Now we form (K - 1) pairs
        r1 = received_signal[k * N : (k + 1) * N]
        r2 = received_signal[(k + 1) * N : (k + 2) * N]
        acc += np.vdot(r1, r2)

    angle = np.angle(acc)
    f_cfo = angle / (2 * np.pi * N * Ts)

    return f_cfo

def max_output_energy_sync(received_signal, samples_per_symbol_input, interpolation_factor, plot=False):
    """
    Performs maximum output energy symbol synchronization on a received signal.

    This method finds the optimal sampling instant within a symbol period
    by upsampling the signal and then searching for the phase that maximizes
    the energy of the sampled symbols. It assumes the input signal is
    already passed through a matched filter (or equivalent processing)
    such that maximizing output energy directly relates to optimal sampling.

    Args:
        received_signal (np.ndarray): The input received signal (1D array),
                                      typically after matched filtering. Can be complex.
        samples_per_symbol_input (int): The number of samples per symbol in the
                                        `received_signal`.
        interpolation_factor (int): The factor by which to upsample the signal
                                    to allow for finer phase resolution in the search.
                                    Must be a positive integer. If 1, no upsampling
                                    is performed, and synchronization occurs on existing samples.

    Returns:
        tuple: A tuple containing:
            - synchronized_symbols (np.ndarray): The signal sampled at the
                                                  optimal symbol synchronization phase.
            - optimal_phase_offset (int): The index of the optimal phase offset
                                           within the interpolated symbol period (0 to new_samples_per_symbol - 1).
    Raises:
        ValueError: If interpolation_factor is not a positive integer,
                    or if samples_per_symbol_input is not positive,
                    or if the signal is too short for processing.
    """
    # Input validation
    if not isinstance(samples_per_symbol_input, int) or samples_per_symbol_input <= 0:
        raise ValueError("samples_per_symbol_input must be a positive integer.")
    
    # Allow interpolation_factor to be 1
    if not isinstance(interpolation_factor, int) or interpolation_factor < 1:
        raise ValueError("interpolation_factor must be a positive integer (>= 1).")
    
    received_signal = np.array(received_signal)
    if len(received_signal) < samples_per_symbol_input:
        raise ValueError(f"Received signal length ({len(received_signal)}) is too short "
                         f"to contain even one symbol based on samples_per_symbol_input ({samples_per_symbol_input}).")

    # 1. Upsample the received signal (or use as is if interpolation_factor is 1)
    # This creates a higher resolution version of the signal, allowing for more precise
    # determination of the optimal sampling point.
    upsampled_signal = upsample_signal(received_signal, interpolation_factor)

    # Calculate the new number of samples per symbol in the upsampled signal.
    # This is the interval between consecutive symbol samples in the upsampled domain.
    new_samples_per_symbol = samples_per_symbol_input * interpolation_factor

    # Ensure the upsampled signal is long enough to find at least one full symbol
    if len(upsampled_signal) < new_samples_per_symbol:
        raise ValueError("Upsampled signal is too short to extract even one symbol after interpolation.")

    max_energy = -1.0  # Initialize with a very small energy value
    optimal_phase_offset = 0 # Initialize optimal phase
    
    # List to store energies for plotting
    energy_vs_offset = []

    # 2. Search for the optimal phase offset by maximizing output energy
    # We iterate through all possible starting phase offsets within one full upsampled symbol period.
    # This covers all possible fine timing shifts.
    for phase_offset in range(new_samples_per_symbol):
        # Extract potential symbol samples for the current phase offset.
        # We start at `phase_offset` and then take every `new_samples_per_symbol`-th sample.
        current_sampled_symbols = upsampled_signal[phase_offset::new_samples_per_symbol]

        # Calculate the energy of these sampled symbols.
        # Energy is the sum of the squared magnitudes of the complex samples.
        current_energy = np.sum(np.abs(current_sampled_symbols)**2)
        
        # Store the energy for plotting
        energy_vs_offset.append(current_energy)

        # If the current energy is greater than the maximum found so far, update the optimum.
        if current_energy > max_energy:
            max_energy = current_energy
            optimal_phase_offset = phase_offset

    # 3. Extract the synchronized symbols using the determined optimal phase offset
    # These are the actual symbol estimates that will be passed on for further decoding.
    synchronized_symbols = upsampled_signal[optimal_phase_offset::new_samples_per_symbol]

    # print(f"Symbol Synchronization Report:")
    # print(f"  Input samples per symbol: {samples_per_symbol_input}")
    # print(f"  Interpolation factor: {interpolation_factor}")
    # print(f"  Optimal phase offset found (index in upsampled signal): {optimal_phase_offset}")
    # print(f"  Number of synchronized symbols extracted: {len(synchronized_symbols)}")

    # 4. Plotting the energy vs. phase offset
    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(range(new_samples_per_symbol), energy_vs_offset, marker='o', linestyle='-')
        plt.axvline(optimal_phase_offset, color='r', linestyle='--', label=f'Optimal Phase Offset: {optimal_phase_offset}')
        plt.title('Energy of Sampled Symbols vs. Phase Offset')
        plt.xlabel('Phase Offset (index in interpolated samples within one symbol period)')
        plt.ylabel('Total Energy')
        plt.grid(True)
        plt.legend()
        plt.show()

    return synchronized_symbols, optimal_phase_offset

def estimate_cfo_old(z, Ntr, Ts):
    """
    Estimates the Carrier Frequency Offset (CFO) based on a given 1D signal.

    Args:
        z (np.ndarray): The 1D input signal, expected to contain complex samples.
        Ntr (int): The number of samples for the correlation. This also defines
                   the offset between the correlated segments.
        Ts (float): The sampling period in seconds.

    Returns:
        float: The estimated CFO (Delta_hat) in Hz.
    """

    # Ensure Ntr is an integer
    Ntr = int(Ntr)

    # Ensure z is a 1D NumPy array
    z = np.array(z).flatten()

    # Validate input length
    if len(z) < Ntr * 2:
        raise ValueError(f"Input 'z' (length {len(z)}) is too short for the given Ntr ({Ntr}). "
                         f"Requires at least {Ntr * 2} samples.")

    tmp = 0.0 + 0.0j  # Initialize as complex to handle complex products

    # The loop runs Ntr times, correlating z[mm] with z[mm+Ntr]
    for mm in range(Ntr):
        # np.vdot(a, b) computes the dot product of a and b, where a is conjugated.
        # This directly translates z(mm)' * z(mm+Ntr) for complex vectors/scalars.
        tmp += np.vdot(z[mm], z[mm + Ntr])

    # CFO estimate
    # np.angle returns the phase angle in radians
    eps_hat = np.angle(tmp) / (2 * np.pi * Ntr)
    Delta_hat = eps_hat / Ts

    # print(f'Estimated CFO: {Delta_hat / 1e3:.3f} kHz')

    return Delta_hat

def block_correlation(x, N):
    """
    Computes the correlation between N-sample segments and their immediate next
    N-sample segments in sequence x.

    Inputs:
        x - input signal (numpy array or list) of length M
        N - segment length to correlate

    Output:
        correlations - numpy array of correlation values between each N-pair segment
    """

    x = np.array(x).flatten()  # Ensure x is a flat NumPy array
    M = len(x)

    # Ensure we have enough samples to compare at least one full pair
    if 2 * N > M:
        raise ValueError('Input sequence is too short for even one N-to-N comparison.')

    # Number of full N-to-N segment comparisons possible
    num_segments = (M - N) // N

    correlations = np.zeros(num_segments)  # Preallocate

    for k in range(num_segments):
        idx1 = k * N
        idx2 = idx1 + N

        segment1 = x[idx1 : idx1 + N]
        segment2 = x[idx2 : idx2 + N]

        # Compute normalized correlation (cosine similarity)
        # Handle cases where norm might be zero to avoid division by zero
        norm_segment1 = np.linalg.norm(segment1)
        norm_segment2 = np.linalg.norm(segment2)

        if norm_segment1 == 0 or norm_segment2 == 0:
            correlations[k] = 0  # Or handle as appropriate for your application
        else:
            correlations[k] = np.dot(segment1, segment2) / (norm_segment1 * norm_segment2)

    return correlations

def gen_rand_bits(N):
    bits = np.random.randint(0, 2, size=(N, 1))
    return bits

def get_qam_constellation(M, Es=1):
    """
    Generate an M-QAM constellation with Gray coding.
    
    Parameters:
    M (int): Modulation order (must be a perfect square).
    Es (float): Symbol energy normalization factor (default is 1).
    
    Returns:
    np.ndarray: Array of M-QAM constellation points following Gray coding.
    """
    m = int(np.sqrt(M))
    if m ** 2 != M:
        raise ValueError("M must be a perfect square.")

    # Function to convert binary to Gray code
    def binary_to_gray(n):
        return n ^ (n >> 1)

    # Generate Gray-coded indices for both axes
    gray_indices = np.array([binary_to_gray(i) for i in range(m)])

    # Normalize Gray-coded indices to constellation points
    re_gray = 2 * gray_indices - (m - 1)  # Shift and scale
    im_gray = 2 * gray_indices - (m - 1)

    # Create the constellation using Gray-coded indices
    const = np.array([complex(re, -im) for im in im_gray for re in re_gray])  # Flip imag for correct quadrant

    # Normalize to unit average energy Es
    const = const / np.sqrt(np.mean(np.abs(const) ** 2)) * np.sqrt(Es)

    return const

def get_qam_constellation_old(M,Es=1):
    """
    Generate M-QAM constellation points.
    
    Parameters:
    M (int): Modulation order (must be a perfect square).
    
    Returns:
    np.ndarray: Array of M-QAM constellation points.
    """
    m = int(np.sqrt(M))
    if m ** 2 != M:
        raise ValueError("M must be a perfect square.")
    re = np.arange(-m + 1, m, 2)
    im = np.arange(-m + 1, m, 2)
    const = np.array([x + 1j * y for x in re for y in im])
    const = const / np.sqrt(np.mean(np.power(np.abs(const),2))) * np.sqrt(Es)
    return const

def gen_rand_qam_symbols(N,M=4):
    if not (M and (M & (M - 1)) == 0):
        raise ValueError("M must be a power of 2")
    
    m = int(np.sqrt(M))
    if m ** 2 != M:
        raise ValueError("M must be a square number for square QAM constellations")
    
    # random symbols
    # real_part = np.random.randint(0, m, N) * 2 - (m - 1)
    # imag_part = np.random.randint(0, m, N) * 2 - (m - 1)
    # symbols = real_part + 1j * imag_part
    # symbols /= np.sqrt((2 / 3) * (M - 1))  # Normalize average power to 1

    # get constellation
    const = get_qam_constellation(M,Es=1)

    # draw random symbols from constellation
    idx = np.random.randint(0,M,N)
    symbols = const[idx]

    return symbols, const

def get_rrc_pulse(beta, span, sps):
    """
    Generate a Root Raised Cosine (RRC) pulse shape.
    
    Parameters:
        beta (float): Roll-off factor (0 to 1).
        span (int): Number of symbol durations the filter spans.
        sps (int): Samples per symbol.
    
    Returns:
        np.ndarray: RRC pulse shape.
    """
    t = np.arange(-span * sps // 2, span * sps // 2 + 1) / sps
    pulse = np.zeros_like(t, dtype=float)
    
    for i in range(len(t)):
        if t[i] == 0:
            pulse[i] = 1 - beta + (4 * beta / np.pi)
        elif abs(t[i]) == 1 / (4 * beta):
            pulse[i] = (beta / np.sqrt(2)) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            pulse[i] = (np.sin(np.pi * t[i] * (1 - beta)) + 4 * beta * t[i] * np.cos(np.pi * t[i] * (1 + beta))) / (np.pi * t[i] * (1 - (4 * beta * t[i]) ** 2))
    
    pulse /= np.sqrt(np.sum(np.abs(pulse)**2)) # unit energy pulse
    return pulse

def get_rc_pulse(beta, span, sps):
    """
    Generate a Raised Cosine (RC) pulse shape.
    
    Parameters:
        beta (float): Roll-off factor (0 to 1).
        span (int): Number of symbol durations the filter spans.
        sps (int): Samples per symbol.
    
    Returns:
        np.ndarray: RC pulse shape.
    """
    T = 1  # Symbol duration
    t = np.arange(-span * T / 2, span * T / 2 + 1 / sps, 1 / sps)
    pulse = np.zeros_like(t)

    for i, ti in enumerate(t):
        if np.isclose(ti, 0.0):
            pulse[i] = 1.0
        elif beta != 0 and np.isclose(abs(ti), T / (2 * beta)):
            # L'Hôpital's rule at t = ±T/(2β)
            pulse[i] = (np.pi / 4) * np.sinc(1 / (2 * beta))
        else:
            numerator = np.sin(np.pi * ti / T)
            sinc_part = numerator / (np.pi * ti / T)
            cos_part = np.cos(np.pi * beta * ti / T)
            denom = 1 - (2 * beta * ti / T) ** 2
            pulse[i] = sinc_part * cos_part / denom

    # Normalize to unit energy
    # pulse /= np.sqrt(np.sum(pulse**2))
    return pulse

def create_pulse_train(symbols,sps):
    symbols = np.array(symbols)
    pulse_train = np.zeros((sps*len(symbols)),dtype=symbols.dtype)
    pulse_train[::sps] = symbols
    return pulse_train

def frame_sync_stf_ltf(received_signal, training_seq, num_samples_post=0, num_samples_pre=0):
    """
    Perform frame synchronization via correlation.

    Parameters:
    - received_signal : np.ndarray
        Complex baseband received signal (1D array).
    - training_seq : np.ndarray
        Known complex training sequence used for correlation.
    - num_samples_post : int
        Number of samples to include after the detected sequence start.
    - num_samples_pre : int
        Number of samples to include before the detected sequence start.
    
    Returns:
    - synced_segment : np.ndarray
        Portion of the received signal from (start - K) to (start + N)
    - start_index : int
        Estimated start index of the training sequence within received_signal
    """
    if num_samples_post <= 0:
        num_samples_post = len(training_seq)

    # Cross-correlation (complex baseband)
    corr = signal.correlate(received_signal, training_seq.conj(), mode='valid')

    # Find peak of the magnitude of the correlation
    peak_index = np.argmax(np.abs(corr))

    # Determine the start of the training sequence in the received signal
    start = peak_index

    # Compute start and end indices for slicing
    start_idx = max(0, start - num_samples_pre)
    end_idx = start + num_samples_post

    # Guard against out-of-bounds access
    if end_idx > len(received_signal):
        raise ValueError("Requested slice exceeds received signal length.")

    # Extract the desired segment
    synced_segment = received_signal[start_idx:end_idx]

    # Channel estimate
    h = corr[peak_index]

    plt.figure()
    plt.plot(np.abs(corr))
    plt.show()

    return synced_segment, h

def frame_synch_stf_ltf(y,training_sequence,num_samples_post=0,num_samples_pre=0):
    if num_samples_post <= 0:
        num_samples_post = len(training_sequence)
    L = np.max((len(y),len(training_sequence)))
    zz = np.correlate(training_sequence,y,mode='full') / len(training_sequence)
    zz[:L-len(y)-1+num_samples_post:] = 0
    # zz[0:num_samples_pre:] = 0
    z = np.abs(zz)
    idx_max = np.argmax(z)
    idx = L - idx_max - 1
    xx = y[idx:idx+num_samples_post]
    xx = y[idx-num_samples_pre:idx+num_samples_post]
    h = zz[idx_max]
    if len(xx) < num_samples_post:
        print('!!! len(xx) LESS THAN N')
        print('len(xx): ', len(xx))
        print('len(x): ', len(training_sequence))
        print('len(y): ', len(y))
        print('N: ', num_samples_post)
        print('L: ', L)
        print('idx_max: ',idx_max)
        print('synch index: ',idx)
    plt.figure()
    plt.plot(z)
    # plt.show()
    return xx, h

def custom_corr(x, N, plot=False):
    """
    Computes sliding-window normalized correlations between every
    N-sample segment and the next N-sample segment.

    Parameters:
    - x : np.ndarray
        Input signal (1D array, real or complex)
    - N : int
        Segment length for correlation
    - plot : bool
        Whether to plot correlation values

    Returns:
    - correlations : np.ndarray (complex)
        Array of scalar correlation values (one per sliding window)
    - peak_index : int
        Index (starting sample) where the maximum correlation magnitude occurs
    """
    x = np.asarray(x).flatten()
    M = len(x)
    num_windows = M - 2 * N + 1

    if num_windows < 1:
        raise ValueError("Signal too short for even one sliding N-to-N comparison.")

    correlations = np.zeros(num_windows, dtype=np.complex128)

    for k in range(num_windows):
        seg1 = x[k : k + N]
        seg2 = x[k + N : k + 2 * N]
        correlations[k] = np.vdot(seg1, seg2) / np.sqrt(N) 

    peak_index = np.argmax(np.abs(correlations))  # sample index where max magnitude occurs

    if plot:
        plt.figure(figsize=(8, 4))
        plt.plot(np.abs(correlations), label='|correlation|')
        plt.plot(peak_index, np.abs(correlations[peak_index]), 'ro', label='Peak')
        plt.title('Sliding N-to-N Correlation')
        plt.xlabel('Sliding Window Start Index')
        plt.ylabel('Correlation Magnitude')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return correlations, peak_index

def synchronize(y,x,N=0):
    if N <= 0:
        N = len(x)
    L = np.max((len(y),len(x)))
    zz = np.correlate(x,y,mode='full') / len(x)
    zz[:L-len(y)-1+N:] = 0
    idx_max = np.argmax(np.abs(zz))
    idx = L - idx_max - 1
    xx = y[idx:idx+N]
    # h = zz[idx_max]
    # print(h)
    return xx

def zadoff_chu_sequence(N, root):
    """
    Generate a length-N Zadoff-Chu sequence.
    
    Parameters:
        N (int): Length of the sequence (must be prime relative to root).
        root (int): Root index of the sequence.
    
    Returns:
        np.ndarray: Zadoff-Chu sequence.
    """
    n = np.arange(N)
    return np.exp(-1j * np.pi * root * n * (n + 1) / N)

def cgauss_rv(mu,sigmasq,N):
    """
    Generate realizations of a complex Gaussian random variable.
    
    Parameters:
    mu (complex): Mean of the complex Gaussian random variable.
    sigmasq (float): Variance of the complex Gaussian random variable.
    N (int): Number of samples to generate.
    
    Returns:
    np.ndarray: An array of realizations of the complex Gaussian random variable.
    """
    real_part = np.random.normal(mu.real, np.sqrt(sigmasq / 2), N)
    imag_part = np.random.normal(mu.imag, np.sqrt(sigmasq / 2), N)
    return real_part + 1j * imag_part

def demod_nearest(y,S):
    """
    Snap each point in y to the nearest point in S.
    
    Parameters:
    y (np.ndarray): Array of complex numbers to be demodulated.
    S (np.ndarray): Array of possible constellation points.
    
    Returns:
    np.ndarray: Array of demodulated points.
    """
    return np.array([S[np.argmin(np.abs(s - S))] for s in y])

def calc_symbol_error_rate(s1,s2):
    return np.mean(s1 != s2)

def unpack_jpg_bits(image_path):
    try:
        with open(image_path, 'rb') as file:
            image_data = file.read()
            bits = ''.join(format(byte, '08b') for byte in image_data)
            return bits
    except FileNotFoundError:
        return "Error: File not found."
    
def bits_to_qam_symbols(bits, M):
    """
    Convert a bit sequence to a sequence of M-QAM symbols.
    
    Parameters:
    bits (np.ndarray): Input bit sequence.
    M (int): Modulation order (must be a perfect square).
    
    Returns:
    np.ndarray: Sequence of M-QAM symbols.
    """
    k = int(np.log2(M))
    bits = np.asarray(bits).flatten()  # Ensure it's a 1D array
    remainder = len(bits) % k

    # Pad bits with zeros if necessary
    if remainder != 0:
        bits = np.pad(bits, (0, k - remainder), mode='constant')

    constellation = get_qam_constellation(M,Es=1)
    bit_groups = bits.reshape(-1, k)
    decimal_values = int(np.array([int("".join(map(str, group)), 2) for group in bit_groups]))
    return constellation[decimal_values], remainder

def qam_mapper(bit_string, M):
    """
    Maps a string of N bits to symbols in an M-QAM constellation.
    Zero-pads N as needed to fit log2(M) bits per symbol.
    
    :param bit_string: String of bits (e.g., "110101")
    :param M: QAM modulation order (e.g., 16 for 16-QAM)
    :return: List of complex symbols representing QAM modulation
    """
    k = int(np.log2(M))  # Bits per symbol
    
    # Zero-padding to make length a multiple of k
    padding_length = (k - len(bit_string) % k) % k
    bit_string = bit_string.zfill(len(bit_string) + padding_length)
    
    # Define constellation points
    # constellation_size = int(np.sqrt(M))
    # real_vals = np.arange(-constellation_size + 1, constellation_size, 2)
    # imag_vals = np.arange(-constellation_size + 1, constellation_size, 2)
    # qam_constellation = [complex(i, j) for j in reversed(imag_vals) for i in real_vals]
    qam_constellation = get_qam_constellation(M,Es=1)

    # Mapping bits to symbols
    symbols = []
    for i in range(0, len(bit_string), k):
        bit_group = bit_string[i:i+k]
        index = int(bit_group, 2)  # Convert bit group to integer
        symbols.append(qam_constellation[index])
    
    symbols = np.array(symbols)

    return symbols, padding_length

def qam_demapper(symbols, padding_length, M=16):
    """
    Converts QAM symbols back to a bit string and removes zero-padding.
    
    :param symbols: List of complex symbols representing QAM modulation
    :param M: QAM modulation order (e.g., 16 for 16-QAM)
    :param padding_length: Number of zero-padding bits added during mapping
    :return: String of bits corresponding to the symbols
    """
    k = int(np.log2(M))  # Bits per symbol
    
    # Define constellation points
    # constellation_size = int(np.sqrt(M))
    # real_vals = np.arange(-constellation_size + 1, constellation_size, 2)
    # imag_vals = np.arange(-constellation_size + 1, constellation_size, 2)
    # qam_constellation = [complex(i, j) for j in reversed(imag_vals) for i in real_vals]
    qam_constellation = get_qam_constellation(M,Es=1)

    # Mapping symbols to bits
    bit_string = ""
    for symbol in symbols:
        index = min(range(len(qam_constellation)), key=lambda i: abs(qam_constellation[i] - symbol))
        bit_string += format(index, f'0{k}b')
    
    # Remove zero-padding
    if padding_length > 0:
        bit_string = bit_string[padding_length:]
    
    return bit_string

def jpg_to_bits(file_path):
    with open(file_path, 'rb') as f:
        # Read the file as binary
        binary_data = f.read()
    
    # Convert binary data to a bit sequence (a string of '0's and '1's)
    bit_sequence = ''.join(format(byte, '08b') for byte in binary_data)
    return bit_sequence


def bits_to_jpg(bit_sequence, output_path):
    # Convert the bit sequence back into bytes
    byte_data = bytes(int(bit_sequence[i:i+8], 2) for i in range(0, len(bit_sequence), 8))
    
    # Write the byte data to a new file
    with open(output_path, 'wb') as f:
        f.write(byte_data)

def psd_from_autocorr(signal, fs):
    """
    Estimate the two-sided Power Spectral Density (PSD) from a (possibly complex) signal
    using the Wiener-Khinchin theorem: PSD = FFT of the autocorrelation.
    
    Parameters:
        signal: 1D array-like, real or complex time-domain signal
        fs: Sampling frequency in Hz

    Returns:
        freqs: Frequency bins (Hz), spanning from -fs/2 to fs/2
        psd: Two-sided Power Spectral Density (V^2/Hz or similar)
    """
    signal = np.asarray(signal, dtype=np.complex128)

    N = len(signal)

    # Remove DC (mean)
    signal -= np.mean(signal)

    # Full autocorrelation, using complex conjugate
    full_corr = np.correlate(signal, signal.conj(), mode='full')

    # Keep only non-negative lags
    autocorr = full_corr[N-1:]

    # Normalize using unbiased estimator
    lags = np.arange(N, 0, -1)
    autocorr = autocorr / lags

    # Compute FFT and frequency bins (two-sided)
    psd = np.fft.fft(autocorr) / fs

    # Generate frequency bins spanning from -fs/2 to fs/2
    freqs = np.fft.fftfreq(N, d=1/fs)

    # Normalize to have equal positive and negative frequencies
    psd = np.fft.fftshift(np.abs(psd))  # Two-sided PSD

    # Shift frequency axis from -fs/2 to fs/2
    freqs = np.fft.fftshift(freqs)

    return freqs, psd

def downsample_signal(x, M):
    """
    Downsamples a signal by an integer factor M using an antialiasing filter
    followed by decimation.

    This function effectively reduces the sampling rate of the input signal
    by a factor of M.

    Args:
        x (np.ndarray): The input signal (1D array). Can be real or complex.
        M (int): The downsampling factor. Must be a positive integer.

    Returns:
        np.ndarray: The downsampled signal.

    Raises:
        ValueError: If M is not a positive integer.
    """

    if not isinstance(M, int) or M <= 0:
        raise ValueError("Downsampling factor M must be a positive integer.")

    if M == 1:
        # No downsampling needed
        return np.array(x)

    # 1. Antialiasing Low-Pass Filter
    # Design a low-pass FIR filter.
    # The cutoff frequency should be 1/M of the original Nyquist frequency.
    # Since firwin's cutoff is normalized to 0.5 (Nyquist), the cutoff is 0.5 / M.

    # Number of taps for the FIR filter. A common choice is 6*M for reasonable performance.
    # More taps mean a sharper cutoff but also longer delay and higher computational cost.
    num_taps = 6 * M  # Can be adjusted based on desired filter performance
    cutoff_freq = 0.5 / M  # Normalized cutoff frequency (Nyquist = 0.5 of original Fs)

    # Create the filter coefficients
    b = signal.firwin(num_taps, cutoff_freq, pass_zero=True)

    # Apply the filter to the signal
    # lfilter handles complex inputs correctly.
    filtered_x = signal.lfilter(b, 1.0, x)

    # Account for filter delay by trimming the beginning
    # This helps align the downsampled output with the original signal's features,
    # though for decimation, it's primarily about getting correct samples,
    # and the absolute timing might be adjusted externally.
    delay = (num_taps - 1) // 2
    
    # Ensure we don't try to access out of bounds if the signal is very short
    if len(filtered_x) <= delay:
        return np.array([]) # Return empty array if no valid samples after delay and decimation

    # 2. Decimation (Select every M-th sample)
    # Start decimation from 'delay' index to account for filter group delay.
    downsampled_x = filtered_x[delay::M]

    return downsampled_x

def upsample_signal(x, M):
    """
    Upsamples a signal by an integer factor M using zero-insertion followed by
    an antialiasing low-pass filter.

    This function effectively increases the sampling rate of the input signal
    by a factor of M.

    Args:
        x (np.ndarray): The input signal (1D array). Can be real or complex.
        M (int): The upsampling factor. Must be a positive integer.

    Returns:
        np.ndarray: The upsampled and filtered signal.

    Raises:
        ValueError: If M is not a positive integer.
    """

    if not isinstance(M, int) or M <= 0:
        raise ValueError("Upsampling factor M must be a positive integer.")

    if M == 1:
        # No upsampling needed
        return np.array(x)

    # 1. Zero-insertion (Upsampling by M)
    # Create an array of zeros with the new length (len(x) * M)
    # and insert the original signal samples at every M-th position.
    upsampled_zeros = np.zeros(len(x) * M, dtype=x.dtype)
    upsampled_zeros[::M] = x

    # 2. Antialiasing Low-Pass Filter
    # Design a low-pass FIR filter.
    # The cutoff frequency should be 1/M of the new Nyquist frequency
    # (which is 0.5 when normalized to the new sampling rate).
    # So, the normalized cutoff is 1/M * 0.5 = 0.5 / M.

    # Number of taps for the FIR filter. A common choice is 6*M for reasonable performance.
    # More taps mean a sharper cutoff but also longer delay and higher computational cost.
    num_taps = 6 * M  # Can be adjusted based on desired filter performance
    cutoff_freq = 0.5 / M  # Normalized cutoff frequency (Nyquist = 0.5)

    # If the signal is complex, we need to handle the filter design carefully.
    # For a real-valued FIR filter, `firwin` is suitable for both real and complex signals
    # as `lfilter` handles complex inputs correctly.
    b = signal.firwin(num_taps, cutoff_freq, pass_zero=True)

    # Apply the filter to the upsampled signal.
    # lfilter performs forward and reverse filtering for zero-phase, but for upsampling
    # a simple forward filter is usually sufficient as phase distortion might be acceptable
    # or compensated later. For strict linear phase, one might consider filtfilt, but it
    # would make the signal real.
    filtered_x = signal.lfilter(b, 1.0, upsampled_zeros)

    # Due to filter delay, the start of the signal might be distorted.
    # We can trim the initial samples corresponding to half the filter order.
    # This assumes a symmetric FIR filter and aims for roughly zero phase distortion.
    # For non-causal applications, scipy.signal.filtfilt could be used, but it requires real signals.
    delay = (num_taps - 1) // 2
    # Ensure we don't return an empty array if x is too short or M is too large
    if len(filtered_x) > delay:
        return filtered_x[delay:]
    else:
        # Fallback for very short signals or very long filters
        return filtered_x
    

def cgauss_rv(mu, sigmasq, size):
    """
    Generate complex Gaussian (AWGN) random variables.

    Parameters:
    - mu : complex
        Mean of the complex Gaussian noise
    - sigmasq : float
        Total variance (real + imag) of the complex noise
    - size : int or tuple of ints
        Output shape (e.g., (N, M) for a matrix)

    Returns:
    - noise : np.ndarray
        Complex-valued random variables of given shape
    """
    std = np.sqrt(sigmasq / 2)
    real = np.random.normal(loc=np.real(mu), scale=std, size=size)
    imag = np.random.normal(loc=np.imag(mu), scale=std, size=size)
    return real + 1j * imag

def qam_pad_bits(bits: np.ndarray, M: int = 4) -> np.ndarray:
    """
    Pad bits before QAM modulation to ensure the number of bits is a multiple of the bits per symbol.
    """

    bits = bits.flatten()  # Ensure bits is a 1D array
    n_bits_per_symbol = int(np.log2(M))

    # Pad bits if necessary
    padding = (n_bits_per_symbol - len(bits) % n_bits_per_symbol) % n_bits_per_symbol
    if padding > 0:
        bits = np.concatenate([bits, np.zeros(padding, dtype=int)])

    return bits, padding