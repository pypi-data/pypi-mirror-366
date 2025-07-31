# %% Import necessary libraries
import matplotlib.pyplot as plt
import numpy as np

from comms_lib.pluto import Pluto

# %% Initialize Pluto SDR
sample_rate = 1e6  # baseband sampling rate (samples per second)

sdr = Pluto("ip:192.168.2.1")
sdr.carrier_frequency = 815e6  # Set carrier frequency for transmission and reception
sdr.sample_rate = int(sample_rate)  # Set baseband sampling rate of Pluto

# %% Generate a signal to transmit
N = 10000  # number of samples to transmit
t = np.arange(N) / sample_rate  # time vector
tx_signal = 0.5 * np.exp(2.0j * np.pi * 100e3 * t)  # complex sinusoid at 100 kHz

# %% Transmit and receive signal
# sdr.tx_gain = 0
sdr.tx(tx_signal)

rx_signal = sdr.rx()  # Capture raw samples from Pluto
rx_fft = np.abs(np.fft.fftshift(np.fft.fft(rx_signal)))
f = np.linspace(sample_rate / -2, sample_rate / 2, len(rx_fft))

plt.figure()
plt.plot(f / 1e3, rx_fft, color="black")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude")
plt.title("Oversampled FFT of Received Signal")
plt.grid(True)
plt.show()

# %% Find the antenna resonance frequency by transmitting the same signal across different frequencies
frequencies = np.linspace(2000e6, 3000e6, 100)
rx_powers = []

for f in frequencies:
    sdr.carrier_frequency = f  # Set the carrier frequency
    # sdr.tx(tx_signal)  # Transmit the signal
    rx_signal = sdr.rx()  # Capture the received signal

    # calculate the power of the received signal
    power = np.mean(np.abs(rx_signal) ** 2)
    rx_powers.append(power)

rx_powers = np.array(rx_powers) / np.max(rx_powers)  # Normalize the received powers
rx_powers_db = 10 * np.log10(rx_powers)  # Convert to dB scale

# plt.semilogy(frequencies / 1e6, rx_powers, "-o")
plt.plot(frequencies / 1e6, rx_powers_db, "-o")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Relative Received Power")
plt.title("Received Power vs Frequency")
plt.grid(True)
plt.show()