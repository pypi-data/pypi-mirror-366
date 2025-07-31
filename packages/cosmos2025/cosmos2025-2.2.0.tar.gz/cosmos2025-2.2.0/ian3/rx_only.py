# %%
# ruff: noqa: F405
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from IPython import get_ipython
from PIL import Image

from comms_lib.dsp import (
    calc_symbol_error_rate,
    create_pulse_train,
    demod_nearest,
    get_qam_constellation,
    qam_demapper,
    qam_mapper,
)
from comms_lib.pluto import Pluto

# Directory for saving plots
# from system import DigitalCommSystem
from comms_lib.system import DigitalCommSystem

if get_ipython() is not None:
    get_ipython().run_line_magic("reload_ext", "autoreload")
    get_ipython().run_line_magic("autoreload", "2")

os.chdir(Path(__file__).parent)

# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 10e6  # baseband sampling rate (samples per second)
# ts = 1 / fs  # baseband sampling period (seconds per sample)
sps = 3
# T = ts * sps  # time between data symbols (seconds per symbol)
# ---------------------------------------------------------------
# Initialize transmitter and receiver.
# ---------------------------------------------------------------
# tx = Pluto("ip:192.168.2.1")  # change to your Pluto device
# tx.tx_gain = 70  # set the transmitter gain

# Uncomment the line below to use different Pluto devices for tx and rx
# rx = Pluto("usb:7.6.5")
rx = Pluto("ip:192.168.3.1")
rx.rx_gain = 70  # set the receiver gain


# tx.sample_rate = rx.sample_rate = 3e6  # set the receiver sample rate

dir_plots = "plots/"

# ---------------------------------------------------------------
# Initialize digital communication system and define system parameters.
# ---------------------------------------------------------------

system = DigitalCommSystem()
system.sample_rate = fs  # set the sample rate
system.sps = 10

system.set_receiver(rx)

# system.tx = tx
# system.rx = rx

rx.sample_rate = fs  # set the sample rate
# tx.carrier_frequency = rx.carrier_frequency = 2450e6
rx.rx_rf_bandwidth = int(rx.sample_rate / sps) * 2  # set RF bandwidth


# digital modulation parameters
modulation_order = 64  # 4, 16, 64, 256, etc.
constellation = get_qam_constellation(modulation_order, Es=1)

img = Image.open(Path(__file__).parent / "test.png")
img = img.resize((32, 32))
img = np.array(img)
bits = np.unpackbits(img)

transmit_symbols, padding = qam_mapper(bits, constellation)
num_transmit_symbols = len(transmit_symbols)
print("Number of transmit symbols: ", num_transmit_symbols)

# Shuffle the symbols if desired
# shuffler = np.random.permutation(num_transmit_symbols)
shuffler = np.random.default_rng().permutation(num_transmit_symbols)

# transmit_signal = transmit_symbols_shuffled

# transmit from Pluto!
# keep transmit signal below 10,000 samples if possible, roughly around +/-1

# receive from Pluto!
receive_signal = system.receive_signal()

# take every sps-th sample
receive_symbols = receive_signal[sps // 2 :: sps]
print("Number of receive symbols: ", len(receive_symbols))

# associate received symbols with nearest in the constellation
detected_receive_symbols_shuffled = demod_nearest(receive_symbols, constellation)

# unshuffle received symbols
detected_receive_symbols = detected_receive_symbols_shuffled[np.argsort(shuffler)]

# demap symbols to bits
rx_bits = qam_demapper(detected_receive_symbols, padding, constellation)

print("")

# calculate symbol error rate
ser = calc_symbol_error_rate(transmit_symbols, detected_receive_symbols)
print("Symbol error rate: ", ser)

# calculate bit errorrate
ber = calc_symbol_error_rate(bits, rx_bits)
print("Bit error rate: ", ber)


# plot transmitted and received signals and symbols
fig = plt.figure(figsize=(12, 6))

# Top subplot for real signals
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1)
# ax1.plot(np.real(transmit_signal), color="blue", marker="o", label="Real Transmit")
ax1.plot(np.real(receive_signal), color="red", label="Real Receive")
ax1.set_title("Transmit and Receive Signals (Real)")
ax1.set_xlabel("Time Samples")
ax1.set_ylabel("Amplitude")
ax1.grid(True)
ax1.legend()

# Bottom subplot for imaginary signals
ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=1)
# ax2.plot(np.imag(transmit_signal), color="blue", marker="o", label="Imaginary Transmit")
ax2.plot(np.imag(receive_signal), color="red", label="Imaginary Receive")
ax2.set_title("Transmit and Receive Signals (Imaginary)")
ax2.set_xlabel("Time Samples")
ax2.set_ylabel("Amplitude")
ax2.grid(True)
ax2.legend()

# Right side square subplot for symbols
ax3 = plt.subplot2grid((2, 2), (0, 1), rowspan=2, aspect="equal")
ax3.scatter(
    np.real(receive_symbols),
    np.imag(receive_symbols),
    color="red",
    label="Received Symbols",
)
ax3.scatter(
    np.real(transmit_symbols),
    np.imag(transmit_symbols),
    color="blue",
    label="Transmitted Symbols",
)
ax3.set_title("Transmitted and Received Symbols")
ax3.set_xlabel("Real Component")
ax3.set_ylabel("Imaginary Component")
ax3.grid(True)
ax3.legend()
plt.tight_layout()

# filename = dir_plots + "main_test_04_v01_01" + ".pdf"
# plt.savefig(filename)
# filename = dir_plots + "main_test_04_v01_01" + ".svg"
# plt.savefig(filename)
plt.show()

# plot the received image
rx_img = np.packbits(rx_bits[: rx_bits.shape[0] - padding]).reshape(img.shape)
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(img)
ax[0].set_title("Original Image")
ax[0].axis("off")
ax[1].imshow(rx_img)
ax[1].set_title("Received Image")
ax[1].axis("off")
plt.tight_layout()
plt.show()

# %%

# %%
plt.tight_layout()
plt.show()

# %%
