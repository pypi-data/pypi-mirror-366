import numpy as np

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


class DigitalCommSystem:
    def __init__(self):
        self.modulation_order = 4
        self.sample_rate = 10e6

        self.num_stf_repeat = 32
        self.num_stf_symbols_per_sequence = 31
        self.stf_root = 11
        self.num_ltf_repeat = 2
        self.num_ltf_symbols_per_sequence = 631
        self.ltf_root = 11

        self.num_pilot_symbols = 1000  # number of random data symbols to generate

        self.sps = 10
        self.pulse_shape_beta = 1
        self.pulse_shape_span = 23

        self.receiver = None
        self.transmitter = None
        
        self.tx_sym_len = 0
        self.tx_zero_pad_len = 0
        self.tx_sym_is_real = True

        self.generate_preamble_symbols()

    @property
    def num_stf_symbols(self):
        """Number of STF symbols (repeat * symbols per sequence)"""
        return self.num_stf_repeat * self.num_stf_symbols_per_sequence

    @property
    def num_ltf_symbols(self):
        """Number of LTF symbols (repeat * symbols per sequence)"""
        return self.num_ltf_repeat * self.num_ltf_symbols_per_sequence

    @property
    def num_stf_ltf_symbols(self):
        """Total number of STF + zero padding + LTF symbols"""
        return self.num_stf_symbols + self.num_ltf_symbols + self.num_stf_ltf_zero_symbols

    @property
    def num_preamble_symbols(self):
        """Total number of preamble symbols (STF + LTF + pilots)"""
        return self.num_stf_ltf_symbols + self.num_pilot_symbols

    @property
    def num_transmit_symbols(self):
        """Total number of transmit symbols"""
        return self.num_preamble_symbols + self.tx_zero_pad_len + self.tx_sym_len

    def set_carrier_frequency(self, fc):
        self.transmitter.tx_lo = int(fc)
        self.receiver.rx_lo = int(fc)
        return

    def set_transmitter(self, sdr: Pluto):
        """Sets the transmitter PlutoSDR with the specified parameters.
        Args:
            sdr (Pluto): The PlutoSDR instance to set as the transmitter.
        """

        sdr.tx_destroy_buffer()  # reset transmit data buffer to be safe
        sdr.rx_destroy_buffer()  # reset receive data buffer to be safe
        sdr.tx_lo = int(815e6)  # set carrier frequency for reception
        sdr.sample_rate = int(self.sample_rate)
        sdr.tx_cyclic_buffer = True
        sdr.tx_gain = 75
        self.transmitter = sdr
        return

    def set_receiver(self, sdr: Pluto):
        """Sets the receiver PlutoSDR with the specified parameters.
        Args:
            sdr (Pluto): The PlutoSDR instance to set as the receiver.
        """

        sdr.tx_destroy_buffer()  # reset transmit data buffer to be safe
        sdr.rx_destroy_buffer()  # reset receive data buffer to be safe
        sdr.rx_lo = int(815e6)  # set carrier frequency for reception
        sdr.rx_rf_bandwidth = int(self.sample_rate)  # set receiver RF bandwidth
        sdr.rx_buffer_size = int(2e6)  # set buffer size of receiver
        sdr.gain_control_mode_chan0 = "manual"  # set gain control mode
        sdr.rx_gain = 75
        sdr.sample_rate = int(self.sample_rate)
        self.receiver = sdr
        return

    def set_transmit_gain(self, value):
        self.transmitter.gain = value
        return

    def transmit_signal(self, signal):
        # scale pilots according to size of input signal?
        pulse_shape = get_rrc_pulse(
            beta=self.pulse_shape_beta, span=self.pulse_shape_span, sps=self.sps
        )
        self.pulse_shape_length = len(pulse_shape)
        num_zeros = 100  # number of zero samples between preamble and transmit signal
        zero_pad = np.zeros((num_zeros,))

        self.tx_zero_pad_len = num_zeros
        self.desired_transmit_signal = signal
        self.tx_sym_len = len(signal)
        self.tx_sym_is_real = not np.iscomplexobj(signal)
        if self.tx_sym_is_real:
            signal = signal + 1j * signal
        transmit_symbols = np.concatenate((self.preamble_symbols, zero_pad, signal))
        transmit_signal = self.pulse_shape_symbols(transmit_symbols, pulse_shape)
        self.transmit_symbols = transmit_symbols
        self.transmit_signal_raw = transmit_signal
        self.transmit_signal_length = len(transmit_signal)
        self.transmitter.tx(transmit_signal)
        return

    def pulse_shape_symbols(self, symbols, pulse_shape):
        sps = self.sps
        pulse_train = create_pulse_train(symbols, sps)
        signal = np.convolve(pulse_train, pulse_shape)
        return signal

    def generate_preamble_symbols(self):
        # Short Training Field
        self.stf_sequence = zadoff_chu_sequence(
            self.num_stf_symbols_per_sequence, self.stf_root
        )
        self.stf_symbols = np.tile(self.stf_sequence, self.num_stf_repeat)

        # Long Training Field
        self.ltf_sequence = zadoff_chu_sequence(
            self.num_ltf_symbols_per_sequence, self.ltf_root
        )
        self.ltf_symbols = np.tile(self.ltf_sequence, self.num_ltf_repeat)

        # Zeros between STF and LTF
        self.num_stf_ltf_zero_symbols = 100
        stf_ltf_zero_symbols = np.zeros((self.num_stf_ltf_zero_symbols,))

        # STF + Zeros + LTF
        stf_ltf_symbols = np.concatenate(
            (self.stf_symbols, stf_ltf_zero_symbols, self.ltf_symbols)
        )
        self.stf_ltf_symbols = stf_ltf_symbols

        # Pilots
        self.pilot_symbols, _ = gen_rand_qam_symbols(self.num_pilot_symbols, M=4)

        # Create full preamble
        self.preamble_symbols = np.concatenate((stf_ltf_symbols, self.pilot_symbols))

    def receive_signal(self):
        self.receiver.rx_destroy_buffer()  # reset receive data buffer to be safe
        _ = self.receiver.rx()

        rx_signal = self.receiver.rx()  # capture raw samples from Pluto

        # self.transmitter.tx_destroy_buffer()  # reset transmit data buffer to be safe
        # self.transmitter.rx_destroy_buffer()  # reset receive data buffer to be safe

        self.receiver.tx_destroy_buffer()  # reset transmit data buffer to be safe
        self.receiver.rx_destroy_buffer()  # reset receive data buffer to be safe

        # remove DC component from RX signal
        # rx_signal -= np.mean(rx_signal)

        # matched filter
        pulse_shape = get_rrc_pulse(
            beta=self.pulse_shape_beta, span=self.pulse_shape_span, sps=self.sps
        )
        rx_signal = np.convolve(rx_signal, pulse_shape)
        self.receive_signal_full = rx_signal

        # synchronization and equalization
        rx_symbols = self.timing_synchronization(rx_signal)
        rx_symbols_cfo_corrected = self.frequency_synchronization(rx_symbols)
        # self.frequency_synchronization(rx_symbols)
        # self.iq_imbalance_correction(rx_symbols_cfo_corrected)
        rx_symbols_equalized = self.channel_equalization(rx_symbols_cfo_corrected)

        if self.tx_sym_is_real:
            rx_signal = np.real(rx_symbols_equalized)
        else:
            rx_signal = rx_symbols_equalized
        return rx_signal

    def timing_synchronization(self, rx_signal: np.ndarray) -> np.ndarray:
        """Performs timing synchronization on the received signal.

        Args:
            rx_signal (np.ndarray): The received signal to synchronize.

        Returns:
            np.ndarray: Synchronized symbols aligned to transmit frame.
        """
        # rx_signal = self.receive_signal_full

        # symbol synchronization
        rx_symbols, offset = max_output_energy_sync(
            rx_signal, self.sps, interpolation_factor=1, plot=False
        )

        # frame synchronization: revised method
        num_samples_pre = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        num_samples_post = (
            self.num_ltf_symbols
            + self.tx_zero_pad_len
            + self.tx_sym_len
        )
        L = len(rx_symbols)
        corrs, idx_peak = custom_corr(
            rx_symbols,
            self.num_ltf_symbols_per_sequence,
            L,
            num_samples_pre,
            num_samples_post,
            plot=False,
        )

        # print(idx_peak)

        # frame synchronization: original method
        # corrs, idx_peak_2 = custom_corr_orig(rx_symbols_,self.num_ltf_symbols_per_sequence,plot=False)
        # print(idx_peak_2)

        # extract preamble
        # num_samples_pre = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        # num_samples_post = self.num_ltf_symbols
        # idx_start = idx_peak - num_samples_pre
        # idx_stop = idx_peak + num_samples_post
        # self.rx_preamble_symbols = rx_symbols_[idx_start:idx_stop]

        # extract zeros
        # idx_start = self.num_stf_symbols
        # idx_stop = idx_start + self.num_stf_ltf_zero_symbols
        # preamble_zeros = self.rx_preamble_symbols[idx_start:idx_stop]
        # print(preamble_zeros)
        # rx_symbols_ -= np.mean(preamble_zeros)
        # self.rx_preamble_symbols -= np.mean(preamble_zeros)

        # extract
        num_samples_pre = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        num_samples_post = self.num_transmit_symbols - num_samples_pre
        idx_start = idx_peak - num_samples_pre
        idx_stop = idx_peak + num_samples_post

        rx_symbols_trunc = rx_symbols[idx_start:idx_stop]

        return rx_symbols_trunc

    def frequency_synchronization(self, rx_symbols: np.ndarray) -> np.ndarray:
        """Performs frequency synchronization on the received symbols.

        Args:
            rx_symbols (np.ndarray): Received symbols to correct for CFO.

        Returns:
            np.ndarray: CFO-corrected symbols.
        """
        # calculate limits on CFO estimation
        T = self.sps / self.sample_rate
        cfo_max_coarse = 1 / (2 * self.num_stf_symbols_per_sequence * T)
        cfo_max_fine = 1 / (2 * self.num_ltf_symbols_per_sequence * T)

        # extract STF
        idx_start = 0
        idx_stop = idx_start + self.num_stf_symbols
        stf = rx_symbols[idx_start:idx_stop]

        # coarse CFO estimation
        cfo_est_coarse = estimate_cfo(
            stf, K=self.num_stf_repeat, N=self.num_stf_symbols_per_sequence, Ts=T
        )

        # apply coarse CFO correction to all received symbols
        t = np.arange(len(rx_symbols)) * self.sps / self.sample_rate
        rx_symbols = rx_symbols * np.exp(-2.0j * np.pi * cfo_est_coarse * t)

        # extract LTF after coarse CFO correction
        idx_start = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        idx_stop = idx_start + self.num_ltf_symbols
        ltf = rx_symbols[idx_start:idx_stop]

        # fine CFO estimation using coarse-corrected LTF
        cfo_est_fine = estimate_cfo(
            ltf, K=self.num_ltf_repeat, N=self.num_ltf_symbols_per_sequence, Ts=T
        )

        # apply fine CFO correction to all received symbols (pilots and payload)
        rx_symbols_cfo_corrected = rx_symbols * np.exp(-2.0j * np.pi * cfo_est_fine * t)

        # Update full signal for debugging purposes
        t_full = np.arange(len(self.receive_signal_full)) / self.sample_rate
        self.receive_signal_full = self.receive_signal_full * np.exp(
            -2.0j * np.pi * (cfo_est_coarse + cfo_est_fine) * t_full
        )

        max_cfo_str = (
            f"Max Unambiguous CFO: "
            f"coarse: {cfo_max_coarse:.2f} Hz, "
            f"fine: {cfo_max_fine:.2f} Hz"
        )
        print(max_cfo_str)

        est_cfo_str = (
            f"Estimated CFO:       "
            f"coarse: {cfo_est_coarse:.2f} Hz, "
            f"fine: {cfo_est_fine:.2f} Hz"
        )
        print(est_cfo_str)

        return rx_symbols_cfo_corrected

    def channel_equalization(self, rx_symbols_cfo_corrected: np.ndarray) -> np.ndarray:
        """Performs channel equalization on CFO-corrected symbols.

        Args:
            rx_symbols_cfo_corrected (np.ndarray): CFO-corrected received symbols.

        Returns:
            np.ndarray: Equalized signal containing only the desired transmit data.
        """
        # fetch received pilots from CFO-corrected symbols
        idx_start = (
            self.num_stf_symbols + self.num_stf_ltf_zero_symbols + self.num_ltf_symbols
        )
        idx_stop = idx_start + self.num_pilot_symbols
        rx_preamble = rx_symbols_cfo_corrected[idx_start:idx_stop]
        # fetch transmit pilots
        tx_preamble = self.pilot_symbols

        # channel estimation using least squares (transmitted_preamble contains zeros)
        mask = np.abs(tx_preamble) > 0.1  # mask to ignore zero pilots

        # Use least squares to estimate channel coefficient
        tx_pilots = tx_preamble[mask].reshape(-1, 1)
        rx_pilots = rx_preamble[mask]

        # Solve: rx_pilots = channel * tx_pilots
        channel_coeff, _, _, _ = np.linalg.lstsq(tx_pilots, rx_pilots, rcond=None)
        channel_estimate = channel_coeff[0]

        print(f"Channel Estimate: {channel_estimate:.3f}")

        # channel equalization applied to all CFO-corrected receive symbols
        rx_symbols_equalized = rx_symbols_cfo_corrected / channel_estimate

        # fetch desired portion of receive symbols
        rx_symbol_equalized = rx_symbols_equalized[
            -self.tx_sym_len :
        ]

        return rx_symbol_equalized

    def estimate_iq_imbalance(self, pilot_tx, pilot_rx):
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
        """Performs IQ imbalance correction on CFO-corrected symbols.

        Args:
            rx_symbols_cfo_corrected (np.ndarray): CFO-corrected received symbols.

        Returns:
            np.ndarray: IQ imbalance corrected symbols.
        """
        received_preamble = rx_symbols_cfo_corrected[0 : self.num_preamble_symbols]
        transmitted_preamble = self.preamble_symbols
        alpha, beta = self.estimate_iq_imbalance(
            transmitted_preamble, received_preamble
        )
        denominator = np.abs(alpha) ** 2 - np.abs(beta) ** 2
        corrected = (
            np.conj(alpha) * rx_symbols_cfo_corrected
            - beta * np.conj(rx_symbols_cfo_corrected)
        ) / denominator
        return corrected
