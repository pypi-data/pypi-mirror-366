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
tx = Pluto("ip:192.168.2.1")  # change to your Pluto device
tx.tx_gain = 70  # set the transmitter gain

# tx.sample_rate = rx.sample_rate = 3e6  # set the receiver sample rate

dir_plots = "plots/"

# ---------------------------------------------------------------
# Initialize digital communication system and define system parameters.
# ---------------------------------------------------------------

system = DigitalCommSystem()
system.sample_rate = fs  # set the sample rate
system.sps = 10

system.set_transmitter(tx)


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

transmit_symbols_shuffled = transmit_symbols[shuffler]
# transmit_symbols_shuffled = transmit_symbols

# create transmit signal
pulse_train = create_pulse_train(transmit_symbols_shuffled, sps)
pulse_shape = np.ones((sps,))
transmit_signal = np.convolve(pulse_train, pulse_shape, "full")
transmit_signal = transmit_signal[:-sps]

# transmit_signal = transmit_symbols_shuffled