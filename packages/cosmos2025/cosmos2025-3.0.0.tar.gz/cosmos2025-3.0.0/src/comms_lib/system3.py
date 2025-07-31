import json

import numpy as np
import yaml

from comms_lib.dsp import (
    create_pulse_train,
    custom_corr,
    estimate_cfo,
    gen_rand_qam_symbols,
    get_rrc_pulse,
    max_output_energy_sync,
    zadoff_chu_sequence,
)
from comms_lib.pluto import Pluto


class SystemConfiguration:
    """Configuration object shared between transmitter and receiver."""

    def __init__(self, **kwargs):
        # System parameters
        self.modulation_order = 4
        self.sample_rate = 10e6
        self.seed = None  # Random seed for reproducibility

        # Preamble parameters
        self.n_stf_repeat = 32
        self.n_stf_syms_per_seq = 31
        self.stf_root = 11

        self.n_ltf_repeat = 2
        self.n_ltf_syms_per_seq = 631
        self.ltf_root = 11
        self.n_pilot_syms = 1000

        # Pulse shaping parameters
        self.sps = 10
        self.pulse_shape_beta = 1
        self.pulse_shape_span = 23

        # Hardware parameters
        self.carrier_frequency = 815e6
        self.tx_gain = 70
        self.rx_gain = 30
        self.rx_buffer_size = int(2e6)

        # Internal calculated parameters
        self.n_stf_ltf_zero_pad = 300
        self.n_tx_zero_pad = 300

        # Additional transmitter parameters, updated when a signal is transmitted
        self.tx_sym_len = None
        self.tx_sym_is_real = None

        for key, value in kwargs.items():
            setattr(self, key, value)

        # Generate preamble symbols once for the configuration
        self._generate_preamble_symbols(seed=self.seed)

    def __repr__(self):
        return self.to_dict().__repr__()

    def to_dict(self):
        """Return a dictionary representation of the configuration."""
        return {
            "modulation_order": self.modulation_order,
            "sample_rate": self.sample_rate,
            "seed": self.seed,
            "n_stf_repeat": self.n_stf_repeat,
            "n_stf_syms_per_seq": self.n_stf_syms_per_seq,
            "stf_root": self.stf_root,
            "n_ltf_repeat": self.n_ltf_repeat,
            "n_ltf_syms_per_seq": self.n_ltf_syms_per_seq,
            "ltf_root": self.ltf_root,
            "n_pilot_syms": self.n_pilot_syms,
            "sps": self.sps,
            "pulse_shape_beta": self.pulse_shape_beta,
            "pulse_shape_span": self.pulse_shape_span,
            "carrier_frequency": self.carrier_frequency,
            "tx_gain": self.tx_gain,
            "rx_gain": self.rx_gain,
            "rx_buffer_size": self.rx_buffer_size,
            "n_stf_ptf_zero_syms": self.n_stf_ltf_zero_pad,
            "tx_zero_pad_len": self.n_tx_zero_pad,
            "tx_sym_len": self.tx_sym_len,
            "tx_sym_is_real": self.tx_sym_is_real,
        }

    def save_to_file(self, filename, format="json"):
        """Save the configuration to a file.

        Args:
            filename: The name of the file to save the configuration.
            format: The format to save the configuration, default is 'json'. Options are 'json', 'yaml'"""

        config_dict = self.to_dict()

        with open(filename, "w") as f:
            if format.lower() == "json":
                json.dump(config_dict, f, indent=4)
            elif format.lower() == "yaml":
                yaml.dump(config_dict, f, default_flow_style=False, indent=4)
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'json' or 'yaml'.")

    @classmethod
    def from_file(cls, filename, format="json"):
        """Load the configuration from a file.

        Args:
            filename: The name of the file to load the configuration from.
            format: The format of the file, default is 'json'. Options are 'json', 'yaml'"""

        with open(filename, "r") as f:
            if format.lower() == "json":
                config_dict = json.load(f)
            elif format.lower() == "yaml":
                config_dict = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'json' or 'yaml'.")

        return cls(**config_dict)

    @property
    def num_stf_symbols(self):
        """Number of STF symbols (repeat * symbols per sequence)"""
        return self.n_stf_repeat * self.n_stf_syms_per_seq

    @property
    def num_ltf_symbols(self):
        """Number of LTF symbols (repeat * symbols per sequence)"""
        return self.n_ltf_repeat * self.n_ltf_syms_per_seq

    @property
    def num_stf_ltf_symbols(self):
        """Total number of STF + zero padding + LTF symbols"""
        return self.num_stf_symbols + self.num_ltf_symbols + self.n_stf_ltf_zero_pad

    @property
    def num_preamble_symbols(self):
        """Total number of preamble symbols (STF + LTF + pilots)"""
        return self.num_stf_ltf_symbols + self.n_pilot_syms

    def num_transmit_symbols(self, tx_sym_len):
        """Total number of transmit symbols including payload"""
        return self.num_preamble_symbols + self.n_tx_zero_pad + tx_sym_len

    def _generate_preamble_symbols(self, seed=None):
        """Generate preamble symbols for the configuration."""

        # Short Training Field
        self.stf_sequence = zadoff_chu_sequence(self.n_stf_syms_per_seq, self.stf_root)
        self.stf_symbols = np.tile(self.stf_sequence, self.n_stf_repeat)

        # Long Training Field
        self.ltf_sequence = zadoff_chu_sequence(self.n_ltf_syms_per_seq, self.ltf_root)
        self.ltf_symbols = np.tile(self.ltf_sequence, self.n_ltf_repeat)

        # Zeros between STF and LTF
        stf_ltf_zero_symbols = np.zeros((self.n_stf_ltf_zero_pad,))

        # STF + Zeros + LTF
        stf_ltf_symbols = np.concatenate(
            (self.stf_symbols, stf_ltf_zero_symbols, self.ltf_symbols)
        )
        self.stf_ltf_symbols = stf_ltf_symbols

        # Pilots
        self.pilot_symbols, _ = gen_rand_qam_symbols(
            self.n_pilot_syms, M=self.modulation_order, seed=seed
        )

        # Create full preamble
        self.preamble_symbols = np.concatenate((stf_ltf_symbols, self.pilot_symbols))


class DigitalTransmitter:
    """Digital communication system transmitter."""

    def __init__(self, config: SystemConfiguration = None, sdr: Pluto = None):
        """Initialize transmitter with configuration and SDR.

        Args:
            config: SystemConfiguration object. If None, creates default config.
            sdr: Pluto SDR object. If None, must be set later.
        """
        self.config = config if config is not None else SystemConfiguration()
        self.sdr = None

        # Transmit state
        self.tx_sym_len = 0
        self.tx_sym_is_real = False
        self.desired_transmit_signal = None
        self.transmit_symbols = None

        if sdr is not None:
            self.set_sdr(sdr)

    def set_sdr(self, sdr: Pluto):
        """Configure the transmitter SDR with system parameters."""
        sdr.tx_destroy_buffer()
        sdr.rx_destroy_buffer()
        sdr.sample_rate = int(self.config.sample_rate)

        sdr.tx_lo = int(self.config.carrier_frequency)
        sdr.tx_cyclic_buffer = True
        sdr.tx_gain = self.config.tx_gain
        sdr.tx_rf_bandwidth = int(sdr.sample_rate / self.config.sps) * 2
        self.sdr = sdr

    def set_gain(self, gain):
        """Set transmitter gain."""
        if self.sdr is not None:
            self.sdr.tx_gain = gain
        self.config.tx_gain = gain

    def pulse_shape_symbols(self, symbols):
        """Apply pulse shaping to symbols."""
        pulse_shape = get_rrc_pulse(
            beta=self.config.pulse_shape_beta,
            span=self.config.pulse_shape_span,
            sps=self.config.sps,
        )
        pulse_train = create_pulse_train(symbols, self.config.sps)
        signal = np.convolve(pulse_train, pulse_shape)
        return signal

    def transmit_signal(self, signal):
        """Transmit a signal with preamble and pulse shaping."""
        if self.sdr is None:
            raise RuntimeError("No SDR configured for transmitter")

        # Store signal properties
        self.desired_transmit_signal = signal
        self.tx_sym_len = len(signal)
        self.tx_sym_is_real = not np.iscomplexobj(signal)

        # Convert real signals to complex
        if self.tx_sym_is_real:
            signal = signal + 1j * signal

        # Create zero padding
        zero_pad = np.zeros((self.config.n_tx_zero_pad,))

        # Combine preamble, zero padding, and signal
        transmit_symbols = np.concatenate(
            (self.config.preamble_symbols, zero_pad, signal)
        )

        # Apply pulse shaping
        transmit_signal = self.pulse_shape_symbols(transmit_symbols)

        # Store for debugging
        self.transmit_symbols = transmit_symbols

        # update configuration with transmit parameters
        self.config.tx_sym_len = self.tx_sym_len
        self.config.tx_sym_is_real = self.tx_sym_is_real

        # Transmit
        self.sdr.tx(transmit_signal)


class DigitalReceiver:
    """Digital communication system receiver."""

    def __init__(self, config: SystemConfiguration = None, sdr: Pluto = None):
        """Initialize receiver with configuration and SDR.

        Args:
            config: SystemConfiguration object. If None, creates default config.
            sdr: Pluto SDR object. If None, must be set later.
        """
        self.config = config if config is not None else SystemConfiguration()
        self.sdr = None

        # Receive state
        self.receive_signal_full = None

        if sdr is not None:
            self.set_sdr(sdr)

        self.tx_sym_len = self.config.tx_sym_len
        if self.tx_sym_len is None:
            Warning(
                "tx_sym_len is not set. Make sure to manually set `tx_sym_len` after transmitting a signal."
            )

        self.tx_sym_is_real = self.config.tx_sym_is_real
        if self.tx_sym_is_real is None:
            Warning(
                "tx_sym_is_real is not set. Make sure to manually set `tx_sym_is_real` after transmitting a signal."
            )

    def set_sdr(self, sdr: Pluto):
        """Configure the receiver SDR with system parameters."""
        sdr.tx_destroy_buffer()
        sdr.rx_destroy_buffer()
        sdr.rx_lo = int(self.config.carrier_frequency)
        sdr.rx_rf_bandwidth = int(sdr.sample_rate / self.config.sps) * 2
        sdr.rx_buffer_size = self.config.rx_buffer_size
        sdr.gain_control_mode_chan0 = "manual"
        sdr.rx_gain = self.config.rx_gain
        sdr.sample_rate = int(self.config.sample_rate)
        self.sdr = sdr

    def set_gain(self, gain):
        """Set receiver gain."""
        if self.sdr is not None:
            self.sdr.rx_gain = gain
        self.config.rx_gain = gain

    # def set_tx_params(self, tx_sym_len, tx_sym_is_real):
    #     """Set parameters from transmitter for proper synchronization."""
    #     self.tx_sym_len = tx_sym_len
    #     self.tx_sym_is_real = tx_sym_is_real

    def receive_signal(self):
        """Receive and process a signal."""
        if self.sdr is None:
            raise RuntimeError("No SDR configured for receiver")

        # Clear buffers and receive
        self.sdr.rx_destroy_buffer()
        _ = self.sdr.rx()  # Dummy read
        rx_signal = self.sdr.rx()

        # Clean up buffers
        # self.sdr.tx_destroy_buffer()
        # self.sdr.rx_destroy_buffer()
        
        # remove DC offset
        rx_signal -= np.mean(rx_signal)

        # Apply matched filter
        pulse_shape = get_rrc_pulse(
            beta=self.config.pulse_shape_beta,
            span=self.config.pulse_shape_span,
            sps=self.config.sps,
        )
        rx_signal = np.convolve(rx_signal, pulse_shape)
        self.receive_signal_full = rx_signal

        # Synchronization and equalization
        rx_symbols = self.timing_synchronization(rx_signal)
        rx_symbols_cfo_corrected = self.frequency_synchronization(rx_symbols)
        rx_symbols_equalized = self.channel_equalization(rx_symbols_cfo_corrected)

        # Return real or complex based on transmit signal
        if self.tx_sym_is_real:
            return np.real(rx_symbols_equalized)
        else:
            return rx_symbols_equalized

    def timing_synchronization(self, rx_signal: np.ndarray) -> np.ndarray:
        """Perform timing synchronization on the received signal."""
        # Symbol synchronization
        rx_symbols, offset = max_output_energy_sync(
            rx_signal, self.config.sps, interpolation_factor=1, plot=False
        )

        # Frame synchronization
        num_samples_pre = self.config.num_stf_symbols + self.config.n_stf_ltf_zero_pad
        num_samples_post = (
            self.config.num_ltf_symbols + self.config.n_tx_zero_pad + self.tx_sym_len
        )
        L = len(rx_symbols)

        corrs, idx_peak = custom_corr(
            rx_symbols,
            self.config.n_ltf_syms_per_seq,
            L,
            num_samples_pre,
            num_samples_post,
            plot=False,
        )

        # Extract synchronized symbols
        num_samples_post = (
            self.config.num_transmit_symbols(self.tx_sym_len) - num_samples_pre
        )
        idx_start = idx_peak - num_samples_pre
        idx_stop = idx_peak + num_samples_post

        return rx_symbols[idx_start:idx_stop]

    def frequency_synchronization(self, rx_symbols: np.ndarray) -> np.ndarray:
        """Perform frequency synchronization on the received symbols."""
        # Calculate CFO estimation limits
        T = self.config.sps / self.config.sample_rate
        cfo_max_coarse = 1 / (2 * self.config.n_stf_syms_per_seq * T)
        cfo_max_fine = 1 / (2 * self.config.n_ltf_syms_per_seq * T)

        # Extract STF for coarse CFO estimation
        idx_start = 0
        idx_stop = idx_start + self.config.num_stf_symbols
        stf = rx_symbols[idx_start:idx_stop]

        # Coarse CFO estimation
        cfo_est_coarse = estimate_cfo(
            stf,
            K=self.config.n_stf_repeat,
            N=self.config.n_stf_syms_per_seq,
            Ts=T,
        )

        # Apply coarse CFO correction
        t = np.arange(len(rx_symbols)) * self.config.sps / self.config.sample_rate
        rx_symbols = rx_symbols * np.exp(-2.0j * np.pi * cfo_est_coarse * t)

        # Extract LTF for fine CFO estimation
        idx_start = self.config.num_stf_symbols + self.config.n_stf_ltf_zero_pad
        idx_stop = idx_start + self.config.num_ltf_symbols
        ltf = rx_symbols[idx_start:idx_stop]

        # Fine CFO estimation
        cfo_est_fine = estimate_cfo(
            ltf,
            K=self.config.n_ltf_repeat,
            N=self.config.n_ltf_syms_per_seq,
            Ts=T,
        )

        # Apply fine CFO correction
        rx_symbols_cfo_corrected = rx_symbols * np.exp(-2.0j * np.pi * cfo_est_fine * t)

        # Update full signal for debugging
        if self.receive_signal_full is not None:
            t_full = np.arange(len(self.receive_signal_full)) / self.config.sample_rate
            self.receive_signal_full = self.receive_signal_full * np.exp(
                -2.0j * np.pi * (cfo_est_coarse + cfo_est_fine) * t_full
            )

        # Print CFO information
        print(
            f"Max Unambiguous CFO: coarse: {cfo_max_coarse:.2f} Hz, "
            f"fine: {cfo_max_fine:.2f} Hz"
        )
        print(
            f"Estimated CFO: coarse: {cfo_est_coarse:.2f} Hz, "
            f"fine: {cfo_est_fine:.2f} Hz"
        )

        return rx_symbols_cfo_corrected

    def channel_equalization(self, rx_symbols_cfo_corrected: np.ndarray) -> np.ndarray:
        """Perform channel equalization on CFO-corrected symbols."""
        # Extract received pilots
        idx_start = (
            self.config.num_stf_symbols
            + self.config.n_stf_ltf_zero_pad
            + self.config.num_ltf_symbols
        )
        idx_stop = idx_start + self.config.n_pilot_syms
        rx_preamble = rx_symbols_cfo_corrected[idx_start:idx_stop]

        # Get transmitted pilots
        tx_preamble = self.config.pilot_symbols

        # Debug: Check pilot alignment with correlation
        pilot_correlation = np.correlate(
            rx_symbols_cfo_corrected, self.config.pilot_symbols[::-1], "valid"
        )
        max_corr_idx = np.argmax(np.abs(pilot_correlation))
        max_corr_value = pilot_correlation[max_corr_idx]
        print(
            f"Pilot correlation peak at index {max_corr_idx}, value: {max_corr_value:.3f}"
        )

        # Channel estimation (transmitted_preamble contains zeros)
        mask = tx_preamble != 0
        if np.sum(mask) == 0:
            raise RuntimeError("No non-zero pilot symbols found for channel estimation")

        tmp = rx_preamble[mask] / tx_preamble[mask]
        channel_estimate = np.mean(tmp)

        # Sanity check on channel estimate
        if np.abs(channel_estimate) < 1e-6:
            print(f"Warning: Very small channel estimate detected: {channel_estimate}")
            channel_estimate = 1.0  # Fallback to no equalization

        print(f"Channel Estimate: {channel_estimate:.3f}")

        # Apply equalization
        rx_symbols_equalized = rx_symbols_cfo_corrected / channel_estimate

        # Extract desired portion
        return rx_symbols_equalized[-self.tx_sym_len :]

    def estimate_iq_imbalance(self, pilot_tx, pilot_rx):
        """Estimate IQ imbalance parameters."""
        if pilot_tx.shape != pilot_rx.shape:
            raise ValueError("pilot_tx and pilot_rx must have the same shape")

        # Set up linear system: r = alpha * s + beta * s*
        A = np.column_stack([pilot_tx, np.conj(pilot_tx)])
        x, _, _, _ = np.linalg.lstsq(A, pilot_rx, rcond=None)
        alpha, beta = x
        return alpha, beta

    def iq_imbalance_correction(
        self, rx_symbols_cfo_corrected: np.ndarray
    ) -> np.ndarray:
        """Perform IQ imbalance correction on CFO-corrected symbols."""
        received_preamble = rx_symbols_cfo_corrected[
            0 : self.config.num_preamble_symbols
        ]
        transmitted_preamble = self.config.preamble_symbols

        alpha, beta = self.estimate_iq_imbalance(
            transmitted_preamble, received_preamble
        )

        denominator = np.abs(alpha) ** 2 - np.abs(beta) ** 2
        corrected = (
            np.conj(alpha) * rx_symbols_cfo_corrected
            - beta * np.conj(rx_symbols_cfo_corrected)
        ) / denominator

        return corrected


# Backwards compatibility class
class DigitalCommSystem:
    """Backwards compatible wrapper for the separated transmitter/receiver system."""

    def __init__(self, config: SystemConfiguration = None):
        """Initialize with optional shared configuration."""
        self.config = config if config is not None else SystemConfiguration()
        self.transmitter_obj = DigitalTransmitter(self.config)
        self.receiver_obj = DigitalReceiver(self.config)

        # Legacy properties
        self.transmitter = None
        self.receiver = None

    @property
    def sample_rate(self):
        return self.config.sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self.config.sample_rate = value

    @property
    def sps(self):
        return self.config.sps

    @sps.setter
    def sps(self, value):
        self.config.sps = value

    def set_transmitter(self, sdr: Pluto):
        """Set transmitter SDR (legacy compatibility)."""
        self.transmitter = sdr
        self.transmitter_obj.set_sdr(sdr)

    def set_receiver(self, sdr: Pluto):
        """Set receiver SDR (legacy compatibility)."""
        self.receiver = sdr
        self.receiver_obj.set_sdr(sdr)

    def transmit_signal(self, signal):
        """Transmit signal (legacy compatibility)."""
        self.transmitter_obj.transmit_signal(signal)
        # Update receiver with transmit parameters
        self.receiver_obj.set_tx_params(
            self.transmitter_obj.tx_sym_len, self.transmitter_obj.tx_sym_is_real
        )

    def receive_signal(self):
        """Receive signal (legacy compatibility)."""
        return self.receiver_obj.receive_signal()
