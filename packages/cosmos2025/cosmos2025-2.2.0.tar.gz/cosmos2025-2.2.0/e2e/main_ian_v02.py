# %%
# ruff: noqa: F405
import matplotlib.pyplot as plt
import numpy as np

from PIL import Image

from comms_lib import (
    detect_qam,
    get_rrc_pulse,
    pulse_shape,
    zadoff_chu_sequence,
)
from comms_lib.cfo import correct_cfo, estimate_cfo
from comms_lib.pluto import Pluto
from comms_lib.qam import qam_modulator, qam_demodulator
from comms_lib.utils import plot_signal, plot_symbols

# Directory for saving plots
dir_plots = 'plots/'

from dsp import *

def digital_modulation(bits,M):
    # ...
    return symbols


class DigitalCommSystem:
    def __init__(self):
        self.modulation_order = 4
        self.sample_rate = 1e6
        self.fs = self.sample_rate
        self.ts = 1 / self.sample_rate
        self.Ts = 1 / self.sample_rate
        self.num_stf_repeat = 32
        self.num_stf_symbols_per_sequence = 31
        self.stf_root = 11
        self.num_ltf_repeat = 2
        self.num_ltf_symbols_per_sequence = 2797 # 937 1999
        self.ltf_root = 137

    def set_carrier_frequency(self,fc):
        self.transmitter.tx_lo = int(fc)
        self.receiver.rx_lo = int(fc)
        return

    def set_transmitter(self,sdr):
        sdr.tx_destroy_buffer() # reset transmit data buffer to be safe
        sdr.rx_destroy_buffer() # reset receive data buffer to be safe
        # ...
        sdr.tx_lo = int(915e6) # set carrier frequency for reception
        sdr.tx_cyclic_buffer = True
        # sdr.set_transmit_gain()
        sdr.tx_gain = 70
        self.transmitter = sdr
        return

    def set_receiver(self,sdr):
        sdr.tx_destroy_buffer() # reset transmit data buffer to be safe
        sdr.rx_destroy_buffer() # reset receive data buffer to be safe
        sdr.rx_lo = int(915e6) # set carrier frequency for reception
        sdr.rx_rf_bandwidth = int(self.sample_rate) # set receiver RF bandwidth
        sdr.rx_buffer_size = int(500e3) # set buffer size of receiver
        sdr.gain_control_mode_chan0 = 'manual' # set gain control mode
        # sdr.rx_hardwaregain_chan0 = 50 # set gain of receiver
        sdr.rx_gain = 50
        # ...
        self.receiver = sdr
        return

    def set_transmit_gain(self,value):
        # self.transmitter...
        return

    def transmit_signal(self,signal):
        preamble_symbols = self.generate_preamble_symbols()
        pulse_shape = get_rc_pulse(beta=1,span=23,sps=10)
        self.pulse_shape_length = len(pulse_shape)
        preamble_signal = self.pulse_shape_symbols(preamble_symbols,pulse_shape,sps=10)
        self.preamble_signal = preamble_signal
        num_zeros = 100 # number of zero samples between preamble and transmit signal
        zero_pad = np.zeros((num_zeros,))
        self.transmit_signal_zero_pad_length = num_zeros
        self.desired_transmit_signal = signal
        self.desired_transmit_signal_length = len(signal)
        transmit_signal = np.concatenate((preamble_signal,zero_pad,signal))
        self.transmit_signal = transmit_signal
        self.transmit_signal_length = len(transmit_signal)
        self.transmitter.tx(transmit_signal)
        return
    
    def pulse_shape_symbols(self,symbols,pulse_shape,sps):
        pulse_train = create_pulse_train(symbols,sps)
        signal = np.convolve(pulse_train,pulse_shape)
        return signal
    
    def generate_preamble_symbols(self):
        # Short Training Field
        self.stf_sequence = np.concatenate((zadoff_chu_sequence(self.num_stf_symbols_per_sequence,self.stf_root),np.zeros((5,))))
        self.stf_symbols = np.tile(self.stf_sequence,self.num_stf_repeat)
        self.num_stf_symbols_per_sequence += 5
        self.num_stf_symbols = self.num_stf_repeat * self.num_stf_symbols_per_sequence

        # Long Training Field
        self.ltf_sequence = zadoff_chu_sequence(self.num_ltf_symbols_per_sequence,self.ltf_root)
        self.ltf_symbols = np.tile(self.ltf_sequence,self.num_ltf_repeat)
        self.num_ltf_symbols = self.num_ltf_repeat * self.num_ltf_symbols_per_sequence

        # Zeros between STF and LTF
        # self.num_stf_ltf_zero_symbols = 200
        # stf_ltf_zero_symbols = np.zeros((self.num_stf_ltf_zero_symbols,))

        # STF + Zeros + LTF
        # stf_ltf_symbols = np.concatenate((self.stf_symbols,stf_ltf_zero_symbols,self.ltf_symbols))
        # self.num_stf_ltf_symbols = self.num_stf_symbols + self.num_ltf_symbols + self.num_stf_ltf_zero_symbols
        stf_ltf_symbols = np.concatenate((self.stf_symbols,self.ltf_symbols))
        self.num_stf_ltf_symbols = self.num_stf_symbols + self.num_ltf_symbols

        # Pilots
        # self.num_pilot_symbols = 300 # number of random data symbols to generate
        # self.pilot_symbols, _ = gen_rand_qam_symbols(self.num_pilot_symbols,M=4)

        # Create full preamble
        # self.preamble_symbols = np.concatenate((stf_ltf_symbols,self.pilot_symbols))
        # self.num_preamble_symbols = self.num_stf_ltf_symbols + self.num_pilot_symbols
        self.preamble_symbols = stf_ltf_symbols
        self.num_preamble_symbols = self.num_stf_ltf_symbols

        return self.preamble_symbols # return preamble symbols
    
    def receive_signal(self):
        self.receiver.rx_destroy_buffer() # reset receive data buffer to be safe
        for i in range(2): # clear buffer to be safe
            rx_data_ =  self.receiver.rx()
        # Synthesize receive signal
        if False: 
            tx_signal = self.transmit_signal
            zeros = np.zeros((1000,))
            rx_signal = np.concatenate((zeros,tx_signal,tx_signal,tx_signal,tx_signal,zeros,zeros,zeros)) 
            rx_signal += cgauss_rv(0,0.01,np.size(rx_signal))
            t = np.arange(len(rx_signal)) / self.sample_rate # time vector
            rx_signal = rx_signal * np.exp(2.0j*np.pi*123*t)
        else:
            rx_signal =  self.receiver.rx() # capture raw samples from Pluto
            self.transmitter.tx_destroy_buffer() # reset transmit data buffer to be safe
            self.transmitter.rx_destroy_buffer() # reset receive data buffer to be safe
            self.receiver.tx_destroy_buffer() # reset transmit data buffer to be safe
            self.receiver.rx_destroy_buffer() # reset receive data buffer to be safe
        # rx_signal -= np.mean(rx_signal) # remove DC component from RX signal
        self.receive_signal_full = rx_signal
        # pulse_shape = get_rrc_pulse(beta=1,span=23,sps=10)
        # rx_signal_filtered = np.convolve(rx_signal,pulse_shape)
        self.timing_synchronization(rx_signal,sps=10)
        self.frequency_synchronization(sps=10)
        self.timing_synchronization(self.rx_signal_cfo_corrected,sps=10)
        self.timing_synchronization_refinement()
        self.channel_equalization()
        return self.desired_receive_signal_equalized
    
    def timing_synchronization(self,rx_signal,sps):
        rx_symbols_, offset = max_output_energy_sync(rx_signal,sps,interpolation_factor=1,plot=False)
        corrs, idx_peak = custom_corr(rx_symbols_,self.num_ltf_symbols_per_sequence,plot=False)
        num_samples_pre = self.num_stf_symbols # + self.num_stf_ltf_zero_symbols
        num_samples_post = self.num_ltf_symbols
        idx_start = idx_peak - num_samples_pre
        idx_stop = idx_peak + num_samples_post
        self.rx_preamble_symbols = rx_symbols_[idx_start:idx_stop]
        pulse_shape_lag = int(np.floor(self.pulse_shape_length/2))
        idx_start = idx_peak * sps + offset + self.num_ltf_symbols * sps + self.transmit_signal_zero_pad_length + pulse_shape_lag
        idx_stop = idx_start + self.desired_transmit_signal_length
        self.desired_receive_signal_raw = rx_signal[idx_start:idx_stop]
        # print(idx_peak * sps + offset + self.num_ltf_symbols * sps)
        # print(idx_start)
        # self.index_start_desired_receive_signal = idx_start
        # self.index_stop_desired_receive_signal = idx_stop
        return
    
    def frequency_synchronization(self,sps):
        idx_start = 0
        idx_stop = idx_start + self.num_stf_ltf_symbols
        received_stf_ltf_symbols = self.rx_preamble_symbols

        stf = received_stf_ltf_symbols[0:self.num_stf_symbols]

        idx_start = self.num_stf_symbols # + self.num_stf_ltf_zero_symbols
        idx_stop = idx_start + self.num_ltf_symbols
        ltf = received_stf_ltf_symbols[idx_start:idx_stop]

        T = sps / self.sample_rate
        cfo_max_coarse = 1 / (2 * np.pi * self.num_stf_symbols_per_sequence * T)
        cfo_max_fine = 1 / (2 * np.pi * self.num_ltf_symbols_per_sequence * T)

        print(f"Max Unambiguous CFO (coarse): {cfo_max_coarse:.2f} Hz")
        print(f"Max Unambiguous CFO (fine): {cfo_max_fine:.2f} Hz")

        # print(len(stf))

        cfo_est_coarse = estimate_cfo(stf,K=self.num_stf_repeat,N=self.num_stf_symbols_per_sequence,Ts=T)
        print(f"Estimated CFO (coarse): {cfo_est_coarse:.2f} Hz")

        t = np.arange(len(ltf)) / self.sample_rate # time vector
        ltf = ltf * np.exp(-2.0j*np.pi*cfo_est_coarse*t*sps)

        cfo_est_fine = estimate_cfo(ltf,K=self.num_ltf_repeat,N=self.num_ltf_symbols_per_sequence,Ts=T)
        print(f"Estimated CFO (fine): {cfo_est_fine:.2f} Hz")

        # pulse_shape_lag = int(np.floor(self.pulse_shape_length/2))
        # offset = self.num_preamble_symbols * sps + self.transmit_signal_zero_pad_length + pulse_shape_lag
        # t = (np.arange(len(self.desired_receive_signal_raw)) + offset) / self.sample_rate # time vector
        # self.desired_receive_signal_cfo_corrected = self.desired_receive_signal_raw * np.exp(-2.0j*np.pi*cfo_est_coarse*t) * np.exp(-2.0j*np.pi*cfo_est_fine*t)

        # t = np.arange(len(self.rx_preamble_symbols)) / self.sample_rate # time vector
        # self.rx_preamble_symbols *= np.exp(-2.0j*np.pi*cfo_est_coarse*t*sps) * np.exp(-2.0j*np.pi*cfo_est_fine*t*sps)
        
        t = np.arange(len(self.receive_signal_full)) / self.sample_rate # time vector
        self.rx_signal_cfo_corrected = self.receive_signal_full * np.exp(-2.0j*np.pi*cfo_est_coarse*t) * np.exp(-2.0j*np.pi*cfo_est_fine*t)

        # pulse_shape_lag = int(np.floor(self.pulse_shape_length/2))
        # idx_start = idx_peak * sps + offset + self.num_ltf_symbols * sps + self.transmit_signal_zero_pad_length + pulse_shape_lag

        # print(idx_peak * sps + offset + self.num_ltf_symbols * sps)
        # print(idx_start)
        return
    
    def timing_synchronization_refinement(self):
        preamble = self.preamble_signal
        
        # Flip and conjugate the known sequence (for complex signals)
        flipped_known = np.conj(preamble[::-1])
        
        # Perform full correlation
        received_signal = self.rx_signal_cfo_corrected
        # correlation = np.correlate(received_signal, flipped_known, mode='full')

        # Find index of max correlation
        # max_index = np.argmax(np.abs(correlation))

        # Compute the corresponding lag (shift) into received_signal
        # idx_lag = max_index - (len(preamble) - 1)

        # idx_start = idx_lag + len(preamble) + self.transmit_signal_zero_pad_length
        # idx_stop = idx_start + self.desired_transmit_signal_length
        # self.desired_receive_signal_raw = received_signal[idx_start:idx_stop]
        # print(self.desired_receive_signal_raw[0:5])
        # print(self.desired_receive_signal_raw.shape)

        # print(self.desired_transmit_signal_length)
        tmp = synchronize(received_signal,preamble,N=self.transmit_signal_length)
        self.desired_receive_signal_raw = tmp[-self.desired_transmit_signal_length:]
        # print(self.desired_receive_signal_raw[0:5])
        # print(self.desired_receive_signal_raw.shape)
        return
    
    def channel_equalization(self):
        # ch_est_fine = np.mean(self.rx_preamble_symbols / self.preamble_symbols)
        # ch_est_fine = np.mean(np.divide(self.rx_preamble_symbols,self.preamble_symbols, where=self.preamble_symbols != 0))
        # valid = (self.preamble_symbols != 0) & (~np.isnan(self.rx_preamble_symbols))
        # ch_est_fine = np.mean(np.divide(self.rx_preamble_symbols, self.preamble_symbols, where=valid))
        valid = (self.preamble_symbols != 0) \
                & (~np.isnan(self.rx_preamble_symbols)) \
                & (~np.isnan(self.preamble_symbols)) \
                & (np.isfinite(self.rx_preamble_symbols)) \
                & (np.isfinite(self.preamble_symbols))

        ratio = np.empty_like(self.rx_preamble_symbols, dtype=np.complex64)
        ratio[:] = np.nan  # fill with NaN initially
        np.divide(self.rx_preamble_symbols, self.preamble_symbols, where=valid, out=ratio)

        # Compute mean only over valid entries
        if np.any(valid):
            ch_est_fine = np.nanmean(ratio)  # nanmean ignores NaNs
        else:
            ch_est_fine = 1.0  # or 0, or raise error depending on your application

        # print(ch_est_fine)

        if not np.isfinite(ch_est_fine) or ch_est_fine == 0:
            ch_est_fine = 1.0  # or fallback value, or raise an error

        self.desired_receive_signal_equalized = self.desired_receive_signal_raw / ch_est_fine
        # self.desired_receive_signal_equalized = self.desired_receive_signal_raw / ch_est_fine
        return self.desired_receive_signal_equalized

# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 1e6     # baseband sampling rate (samples per second)
ts = 1 / fs  # baseband sampling period (seconds per sample)
sps = 10     # samples per data symbol
T = ts * sps # time between data symbols (seconds per symbol)

# ---------------------------------------------------------------
# Initialize transmitter and receiver.
# ---------------------------------------------------------------
if True:
    # tx = Pluto("ip:192.168.2.1")
    tx = Pluto("usb:0.4.5")
    rx = tx
else: 
    tx = Pluto("usb:0.4.5")
    rx = Pluto("usb:2.6.5")

# ---------------------------------------------------------------
# Initialize digital communication system and define system parameters.
# ---------------------------------------------------------------
system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)

modulation_order = 16 # 4, 16, 64, 256, etc.

# Load image and convert to bits
img = Image.open("test.png")
img = img.resize((32,32))
img = np.array(img)
bits = np.unpackbits(img)

# zero-pad the bit sequence before digital modulation
bits_padded, padding = qam_pad_bits(bits, M=modulation_order)

# digital modulation
transmit_symbols = qam_modulator(bits_padded, M=modulation_order)  # Modulate bits to QAM symbols
# transmit_symbols = transmit_symbols[0:]
print('Number of transmit symbols: ', len(transmit_symbols))

# create our baseband message signal
sps = 10
pulse_train = create_pulse_train(transmit_symbols,sps)
pulse_shape = np.ones((sps,))
transmit_signal = np.convolve(pulse_train,pulse_shape,'full')
transmit_signal = transmit_signal[:-sps] # remove trailing zeros

# transmit the signal from Pluto! 
system.transmit_signal(transmit_signal)

# plot the transmit signal
if True:
    plt.figure(figsize=(12, 10))
    plt.subplot(2,1,1)
    plt.plot(np.real(transmit_signal), color='blue', label='Real')
    plt.title('Transmit Signal (Real)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.subplot(2,1,2)
    plt.plot(np.imag(transmit_signal), color='blue', label='Imaginary')
    plt.title('Transmit Signal (Imaginary)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_01' + '.pdf'
    # plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_01' + '.svg'
    # plt.savefig(filename)
    plt.show()

if False:
    plt.figure(figsize=(6, 6))
    plt.scatter(np.real(transmit_symbols),np.imag(transmit_symbols), color='blue', label='Transmit Symbols')
    plt.title('Transmit Symbols')
    plt.xlabel('Real Component')
    plt.ylabel('Imaginary Component')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_00' + '.pdf'
    # plt.savefig(filename)
    plt.show()

# receive from Pluto! 
receive_signal = system.receive_signal()

if True:
    plt.figure(figsize=(12, 10))
    plt.subplot(2,1,1)
    plt.plot(np.real(receive_signal), color='red', label='Real')
    plt.title('Receive Signal (Real)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.subplot(2,1,2)
    plt.plot(np.imag(receive_signal), color='red', label='Imaginary')
    plt.title('Receive Signal (Imaginary)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_01' + '.pdf'
    # plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_01' + '.svg'
    # plt.savefig(filename)
    plt.show()

# compare transmit and receive signals
if True:
    plt.figure(figsize=(12, 10))
    plt.subplot(2,1,1)
    plt.plot(np.real(transmit_signal), color='blue', marker='o', label='Real Transmit')
    plt.plot(np.real(receive_signal), color='red', label='Real Receive')
    plt.title('Transmit and Receive Signals (Real)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.subplot(2,1,2)
    plt.plot(np.imag(transmit_signal), color='blue', marker='o', label='Imaginary Transmit')
    plt.plot(np.imag(receive_signal), color='red', label='Imaginary Receive')
    plt.title('Transmit and Receive Signals (Imaginary)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_01' + '.pdf'
    plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_01' + '.svg'
    plt.savefig(filename)
    plt.show()

# extract symbols by sampling receive signal
receive_symbols = receive_signal[sps//2::sps]

# confirm number of received symbols matches those transmitted
print('Number of transmit symbols: ', len(transmit_symbols))
print('Number of receive symbols: ', len(receive_symbols))

# perform symbol detection (pick nearest)
detected_receive_symbols = detect_qam(receive_symbols, M=modulation_order)  # Detect the received symbols

# convert symbols back to bits
rx_bits = qam_demodulator(detected_receive_symbols, M=modulation_order)  # Demodulate the received symbols

# calculate the fraction of symbols incorrectly received
ser = calc_symbol_error_rate(transmit_symbols,detected_receive_symbols)
print("Symbol error rate: ", ser)

# calculate the fraction of bits incorrectly received
ber = calc_symbol_error_rate(bits,rx_bits)
print("Bit error rate: ", ber)

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
