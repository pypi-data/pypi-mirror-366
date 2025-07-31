import warnings

import adi
import numpy as np


class Pluto(adi.Pluto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # hardware properties
        self.tx_rf_bandwidth = int(1e6)
        self.rx_rf_bandwidth = int(1e6)
        self.sample_rate = 1e6
        self.tx_cyclic_buffer = True
        self.rx_cyclic_buffer = True
        self.rx_buffer_size = 100000
        self.tx_destroy_buffer()
        self.rx_destroy_buffer()
        self.gain_control_mode_chan0 = "manual"

        # wrapped properties
        self.carrier_frequency = 815e6
        self.tx_gain = 100.0
        self.rx_gain = 100.0


    def __repr__(self):
        str = f"""Pluto SDR at {self.uri}

tx_gain:            {self.tx_gain}        Transmit Gain
rx_gain:            {self.rx_gain}        Receive Gain
carrier_frequency:  {self.carrier_frequency / 1e6:.2f}     MHz, Carrier Frequency
sample_rate:        {self.sample_rate / 1e6:.2f}       MHz, Baseband Sample Rate
        """
        return str

    def info(self):
        """
        Parent class __repr__ method.
        """
        print(super().__repr__())

    @property
    def tx_gain(self):
        """
        Simplified gain from 0 (-70 dB) - 100 (-30 dB).
        """
        return int((self.tx_hardwaregain_chan0 + 70) / 60 * 100)

    @tx_gain.setter
    def tx_gain(self, value):
        """
        Set the transmit gain as a percentage.
        """
        if not (0 <= value <= 100):
            raise ValueError("Transmit gain must be between 0 and 100.")
        self.tx_hardwaregain_chan0 = -70 + (value / 100) * 60

    @property
    def rx_gain(self):
        """
        Simplified gain from 0 (0 dB) - 100 (40 dB).
        """
        return int((self.rx_hardwaregain_chan0) / 60 * 100)

    @rx_gain.setter
    def rx_gain(self, value):
        """
        Set the receive gain as a percentage.
        """
        if not (0 <= value <= 100):
            raise ValueError("Receive gain must be between 0 and 100.")
        self.rx_hardwaregain_chan0 = (value / 100) * 60

    @adi.Pluto.tx_hardwaregain_chan0.setter
    def tx_hardwaregain_chan0(self, value):
        if value > -10.0:
            warnings.warn("Transmit gain is too high, clipping to -30 dB")
            value = -10.0
        adi.Pluto.tx_hardwaregain_chan0.fset(self, value)

    @adi.Pluto.rx_hardwaregain_chan0.setter
    def rx_hardwaregain_chan0(self, value):
        if value > 60.0:
            warnings.warn("Receive gain is too high, clipping to 40 dB")
            value = 60.0
        adi.Pluto.rx_hardwaregain_chan0.fset(self, value)

    @property
    def carrier_frequency(self):
        return self.tx_lo

    @carrier_frequency.setter
    def carrier_frequency(self, value):
        """
        Set the carrier frequency for transmission and reception.
        """
        self.tx_lo = int(value)
        self.rx_lo = int(value)

    def _set_transmitter(
        self,
        carrier_freq: int = int(815e6),
        bandwidth: int = int(1e6),
        gain: float = 100.0,
        tx_cyclic_buffer: bool = True,
    ):
        """
        Transmit data using the Pluto SDR.

        Parameters:
            carrier_freq (float): Carrier frequency for transmission.
            bandwidth (float): Transmitter RF bandwidth.
            gain (float): Transmit gain in dB.
            tx_cyclic_buffer (bool): Cyclic nature of the transmit buffer.
        """
        self.tx_destroy_buffer()  # reset transmit data buffer to be safe
        self.tx_rf_bandwidth = int(bandwidth)  # set transmitter RF bandwidth
        self.tx_lo = int(carrier_freq)  # set carrier frequency for transmission
        self.tx_gain = gain
        # set the cyclic nature of the transmit buffer
        self.tx_cyclic_buffer = tx_cyclic_buffer

    def _set_receiver(
        self,
        carrier_freq: int = int(815e6),
        bandwidth: int = int(1e6),
        gain=100.0,
        buffer_size: int = 100000,
        agc_mode: str = "manual",
    ):
        """
        Set up the receiver parameters for Pluto SDR.

        Parameters:
            carrier_freq (float): Carrier frequency for reception in Hz.
            bandwidth (float): Receiver RF bandwidth in Hz.
            gain (float): Receive gain in dB (only set if AGC is 'manual').
            buffer_size (int): Size of the receive buffer in samples.
            agc_mode (str): AGC mode for the receiver.
                Options are 'manual', 'slow_attack', or 'fast_attack'.
        """
        self.rx_destroy_buffer()
        self.rx_rf_bandwidth = int(bandwidth)  # set receiver RF bandwidth
        self.rx_lo = int(carrier_freq)  # set carrier frequency for reception
        self.rx_buffer_size = buffer_size  # set buffer size of receiver
        self.gain_control_mode_chan0 = agc_mode
        if agc_mode == "manual":
            self.rx_gain = gain

    def tx(self, data_np: np.ndarray) -> None:
        """
        Transmit data using the Pluto SDR.

        Parameters:
            data (np.ndarray): Data to be transmitted. Should be scaled between -2^14 and 2^14.
        """
        self.tx_destroy_buffer()  # reset transmit data buffer
        data = np.asarray(data_np, dtype=np.complex128)
        data_scaled = data / np.max(np.abs(data)) * 2**14
        return super().tx(data_scaled)

    def rx(self) -> np.ndarray:
        """
        Receive data using the Pluto SDR.

        Returns:
            np.ndarray: Received data.
        """

        self.rx_destroy_buffer()
        return super().rx()
