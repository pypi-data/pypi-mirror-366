import numpy as np

from comms_lib.dsp import (
    cgauss_rv,
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

        self.sps = 10
        self.pulse_shape_beta = 1
        self.pulse_shape_span = 23

        self.receiver = None
        self.transmitter = None

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
        preamble_symbols = self.generate_preamble_symbols()
        # scale pilots according to size of input signal?
        pulse_shape = get_rrc_pulse(
            beta=self.pulse_shape_beta, span=self.pulse_shape_span, sps=self.sps
        )
        self.pulse_shape_length = len(pulse_shape)
        num_zeros = 100  # number of zero samples between preamble and transmit signal
        zero_pad = np.zeros((num_zeros,))
        self.transmit_signal_zero_pad_length = num_zeros
        self.desired_transmit_signal = signal
        self.desired_transmit_signal_length = len(signal)
        self.desired_transmit_signal_is_real = not np.iscomplexobj(signal)
        if self.desired_transmit_signal_is_real:
            signal = signal + 1j * signal
        transmit_symbols = np.concatenate((preamble_symbols, zero_pad, signal))
        transmit_signal = self.pulse_shape_symbols(transmit_symbols, pulse_shape)
        self.transmit_symbols = transmit_symbols
        self.num_transmit_symbols = len(transmit_symbols)
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
        # self.stf_sequence = np.concatenate((zadoff_chu_sequence(self.num_stf_symbols_per_sequence,self.stf_root),np.zeros((5,))))
        self.stf_symbols = np.tile(self.stf_sequence, self.num_stf_repeat)
        # self.num_stf_symbols_per_sequence += 5
        self.num_stf_symbols = self.num_stf_repeat * self.num_stf_symbols_per_sequence

        # Long Training Field
        self.ltf_sequence = zadoff_chu_sequence(
            self.num_ltf_symbols_per_sequence, self.ltf_root
        )
        self.ltf_symbols = np.tile(self.ltf_sequence, self.num_ltf_repeat)
        self.num_ltf_symbols = self.num_ltf_repeat * self.num_ltf_symbols_per_sequence

        # Zeros between STF and LTF
        self.num_stf_ltf_zero_symbols = 100
        stf_ltf_zero_symbols = np.zeros((self.num_stf_ltf_zero_symbols,))

        # STF + Zeros + LTF
        stf_ltf_symbols = np.concatenate(
            (self.stf_symbols, stf_ltf_zero_symbols, self.ltf_symbols)
        )
        self.num_stf_ltf_symbols = (
            self.num_stf_symbols + self.num_ltf_symbols + self.num_stf_ltf_zero_symbols
        )

        # Pilots
        self.num_pilot_symbols = 1000  # number of random data symbols to generate
        self.pilot_symbols, _ = gen_rand_qam_symbols(self.num_pilot_symbols, M=4)

        # Create full preamble
        self.preamble_symbols = np.concatenate((stf_ltf_symbols, self.pilot_symbols))
        self.num_preamble_symbols = self.num_stf_ltf_symbols + self.num_pilot_symbols
        self.stf_ltf_symbols = stf_ltf_symbols
        # self.preamble_symbols = stf_ltf_symbols
        # self.num_preamble_symbols = self.num_stf_ltf_symbols
        return self.preamble_symbols

    def receive_signal(self):
        self.receiver.rx_destroy_buffer()  # reset receive data buffer to be safe
        for i in range(1):  # clear buffer to be safe
            rx_data_ = self.receiver.rx()

        if False:  # synthesize receive signal
            tx_signal = self.transmit_signal_raw
            zeros = np.zeros((123,))
            rx_signal = np.concatenate(
                (zeros, tx_signal, tx_signal, tx_signal, tx_signal, zeros, zeros, zeros)
            )
            h = cgauss_rv(0, 1, 1)
            print(h)
            # h = [0.02311763+0.05290167j]
            rx_signal *= h
            rx_signal += cgauss_rv(0, 0.01, np.size(rx_signal))
            t = np.arange(len(rx_signal)) / self.sample_rate  # time vector
            rx_signal = rx_signal * np.exp(-2.0j * np.pi * 7e3 * t)
        else:  # actually receive from Pluto
            rx_signal = self.receiver.rx()  # capture raw samples from Pluto
            self.transmitter.tx_destroy_buffer()  # reset transmit data buffer to be safe
            self.transmitter.rx_destroy_buffer()  # reset receive data buffer to be safe
            self.receiver.tx_destroy_buffer()  # reset transmit data buffer to be safe
            self.receiver.rx_destroy_buffer()  # reset receive data buffer to be safe

        # remove DC component from RX signal
        rx_signal -= np.mean(rx_signal)

        # matched filter
        pulse_shape = get_rrc_pulse(
            beta=self.pulse_shape_beta, span=self.pulse_shape_span, sps=self.sps
        )
        rx_signal = np.convolve(rx_signal, pulse_shape)
        self.receive_signal_full = rx_signal

        # synchronization and equalization
        self.timing_synchronization()
        self.frequency_synchronization()
        # self.timing_synchronization()
        # self.frequency_synchronization()
        # self.iq_imbalance_correction()
        self.channel_equalization()

        rx_signal = self.desired_receive_signal_equalized
        if self.desired_transmit_signal_is_real:
            rx_signal = np.real(rx_signal)
        return rx_signal

    def timing_synchronization(self):
        rx_signal = self.receive_signal_full

        # symbol synchronization
        rx_symbols_, offset = max_output_energy_sync(
            rx_signal, self.sps, interpolation_factor=1, plot=False
        )

        # frame synchronization: revised method
        num_samples_pre = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        num_samples_post = (
            self.num_ltf_symbols
            + self.transmit_signal_zero_pad_length
            + self.desired_transmit_signal_length
        )
        L = len(rx_symbols_)
        corrs, idx_peak = custom_corr(
            rx_symbols_,
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
        rx_symbols = rx_symbols_[idx_start:idx_stop]
        self.receive_symbols = rx_symbols
        return

    def frequency_synchronization(self):
        sps = self.sps
        rx_symbols = self.receive_symbols

        # calculate limits on CFO estimation
        T = sps / self.sample_rate
        cfo_max_coarse = 1 / (2 * self.num_stf_symbols_per_sequence * T)
        cfo_max_fine = 1 / (2 * self.num_ltf_symbols_per_sequence * T)
        print(f"Max Unambiguous CFO (coarse): {cfo_max_coarse:.2f} Hz")
        print(f"Max Unambiguous CFO (fine): {cfo_max_fine:.2f} Hz")

        # extract STF and LTF chunk (separated by zeros)
        # idx_start = 0
        # idx_stop = idx_start + self.num_stf_ltf_symbols
        # received_stf_ltf_symbols = self.rx_preamble_symbols[idx_start:idx_stop:]

        # extract STF
        idx_start = 0
        idx_stop = idx_start + self.num_stf_symbols
        stf = rx_symbols[idx_start:idx_stop]

        # coarse CFO estimation
        cfo_est_coarse = estimate_cfo(
            stf, K=self.num_stf_repeat, N=self.num_stf_symbols_per_sequence, Ts=T
        )
        print(f"Estimated CFO (coarse): {cfo_est_coarse:.2f} Hz")
        # cfo_est_coarse = -7e3

        # apply coarse CFO correction to all received symbols
        t = np.arange(len(rx_symbols)) * sps / self.sample_rate
        rx_symbols = rx_symbols * np.exp(-2.0j * np.pi * cfo_est_coarse * t)

        # extract LTF after coarse CFO correction
        idx_start = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        idx_stop = idx_start + self.num_ltf_symbols
        ltf = rx_symbols[idx_start:idx_stop]

        # fine CFO estimation using coarse-corrected LTF
        cfo_est_fine = estimate_cfo(
            ltf, K=self.num_ltf_repeat, N=self.num_ltf_symbols_per_sequence, Ts=T
        )
        print(f"Estimated CFO (fine): {cfo_est_fine:.2f} Hz")

        # apply fine CFO correction to all received symbols (pilots and payload)
        # t = np.arange(len(rx_symbols)) * sps / self.sample_rate
        self.receive_symbols_cfo_corrected = rx_symbols * np.exp(
            -2.0j * np.pi * cfo_est_fine * t
        )

        t = np.arange(len(self.receive_signal_full)) / self.sample_rate
        self.receive_signal_full = self.receive_signal_full * np.exp(
            -2.0j * np.pi * (cfo_est_coarse + cfo_est_fine) * t
        )
        return

    def channel_equalization(self):
        # fetch received pilots from CFO-corrected symbols
        idx_start = (
            self.num_stf_symbols + self.num_stf_ltf_zero_symbols + self.num_ltf_symbols
        )
        idx_stop = idx_start + self.num_pilot_symbols
        received_preamble = self.receive_symbols_cfo_corrected[idx_start:idx_stop]

        # fetch transmit pilots
        transmitted_preamble = self.pilot_symbols

        # Debug: plot the correlation to see if pilots are aligned
        pilot_correlation = np.correlate(
            self.receive_symbols_cfo_corrected, self.pilot_symbols[::-1], "valid"
        )

        # channel estimation (transmitted_preamble contains zeros)
        mask = transmitted_preamble != 0
        tmp = received_preamble[mask] / transmitted_preamble[mask]
        self.channel_estimate = np.mean(tmp)
        print("Channel estimate: ", self.channel_estimate)

        # channel equalization applied to all CFO-corrected receive symbols
        self.receive_symbols_equalized = (
            self.receive_symbols_cfo_corrected / self.channel_estimate
        )

        # fetch desired portion of receive symbols
        self.desired_receive_signal_equalized = self.receive_symbols_equalized[
            -self.desired_transmit_signal_length :
        ]
        return

    def estimate_iq_imbalance(self, pilot_tx, pilot_rx):
        if pilot_tx.shape != pilot_rx.shape:
            raise ValueError("pilot_tx and pilot_rx must have the same shape")

        # Set up linear system: r = alpha * s + beta * s*
        A = np.column_stack([pilot_tx, np.conj(pilot_tx)])
        x, _, _, _ = np.linalg.lstsq(A, pilot_rx, rcond=None)
        alpha, beta = x
        return alpha, beta

    def iq_imbalance_correction(self):
        rx_signal = self.receive_symbols_cfo_corrected
        received_preamble = self.receive_symbols_cfo_corrected[
            0 : self.num_preamble_symbols
        ]
        transmitted_preamble = self.preamble_symbols
        alpha, beta = self.estimate_iq_imbalance(
            transmitted_preamble, received_preamble
        )
        denominator = np.abs(alpha) ** 2 - np.abs(beta) ** 2
        corrected = (
            np.conj(alpha) * rx_signal - beta * np.conj(rx_signal)
        ) / denominator
        self.receive_symbols_cfo_corrected = corrected
        return
