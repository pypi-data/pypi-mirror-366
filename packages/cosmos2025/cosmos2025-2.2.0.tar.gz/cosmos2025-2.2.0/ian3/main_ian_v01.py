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
# import adi
from comms_lib.qam import qam_modulator, qam_demodulator
from comms_lib.utils import plot_signal, plot_symbols

# Directory for saving plots
dir_plots = 'plots/'

from dsp import *

class DigitalCommSystem:
    def __init__(self):
        self.modulation_order = 4
        self.sample_rate = 10e6
        self.fs = self.sample_rate
        self.ts = 1 / self.sample_rate
        self.Ts = 1 / self.sample_rate
        self.num_stf_repeat = 16*4
        self.num_stf_symbols_per_sequence = 37
        self.stf_root = 1
        self.num_ltf_repeat = 2
        self.num_ltf_symbols_per_sequence = 637
        self.ltf_root = 11
        self.sps = 10
        self.pulse_shape_beta = 1
        self.pulse_shape_span = 17

    def set_carrier_frequency(self,fc):
        self.transmitter.tx_lo = int(fc)
        self.receiver.rx_lo = int(fc)
        return

    def set_transmitter(self,sdr):
        sdr.tx_destroy_buffer() # reset transmit data buffer to be safe
        sdr.rx_destroy_buffer() # reset receive data buffer to be safe
        sdr.tx_lo = int(915e6) # set carrier frequency for reception
        sdr.sample_rate = self.sample_rate
        sdr.tx_cyclic_buffer = True
        sdr.tx_gain = 80
        self.transmitter = sdr
        return

    def set_receiver(self,sdr):
        sdr.tx_destroy_buffer() # reset transmit data buffer to be safe
        sdr.rx_destroy_buffer() # reset receive data buffer to be safe
        sdr.rx_lo = int(915e6) # set carrier frequency for reception
        sdr.rx_rf_bandwidth = int(self.sample_rate) # set receiver RF bandwidth
        sdr.rx_buffer_size = int(600e3) # set buffer size of receiver
        sdr.gain_control_mode_chan0 = 'manual' # set gain control mode
        sdr.rx_gain = 80
        sdr.sample_rate = self.sample_rate
        self.receiver = sdr
        return

    def set_transmit_gain(self,value):
        self.transmitter.gain = value
        return

    def transmit_signal(self,signal):
        preamble_symbols = self.generate_preamble_symbols()
        # scale pilots according to size of input signal?
        pulse_shape = get_rrc_pulse(beta=self.pulse_shape_beta,span=self.pulse_shape_span,sps=self.sps)
        self.pulse_shape_length = len(pulse_shape)
        num_zeros = 10 # number of zero samples between preamble and transmit signal
        zero_pad = np.zeros((num_zeros,))
        self.transmit_signal_zero_pad_length = num_zeros
        self.desired_transmit_signal = signal
        self.desired_transmit_signal_length = len(signal)
        transmit_symbols = np.concatenate((preamble_symbols,zero_pad,signal))
        transmit_signal = self.pulse_shape_symbols(transmit_symbols,pulse_shape)
        self.transmit_symbols = transmit_symbols
        self.num_transmit_symbols = len(transmit_symbols)
        # transmit_signal = np.concatenate((preamble_signal,zero_pad,signal))
        self.transmit_signal_raw = transmit_signal
        self.transmit_signal_length = len(transmit_signal)
        # print("Length of TX signal: ", self.transmit_signal_length)
        # transmit_signal = np.asarray(transmit_signal, dtype=np.complex128)
        # transmit_signal = transmit_signal / np.max(np.abs(transmit_signal)) * 2**14
        self.transmitter.tx(transmit_signal)
        return
    
    def pulse_shape_symbols(self,symbols,pulse_shape):
        sps = self.sps
        pulse_train = create_pulse_train(symbols,sps)
        signal = np.convolve(pulse_train,pulse_shape)
        return signal
    
    def generate_preamble_symbols(self):
        # Short Training Field
        self.stf_sequence = zadoff_chu_sequence(self.num_stf_symbols_per_sequence,self.stf_root)
        # self.stf_sequence = np.concatenate((zadoff_chu_sequence(self.num_stf_symbols_per_sequence,self.stf_root),np.zeros((5,))))
        self.stf_symbols = np.tile(self.stf_sequence,self.num_stf_repeat)
        # self.num_stf_symbols_per_sequence += 5
        self.num_stf_symbols = self.num_stf_repeat * self.num_stf_symbols_per_sequence

        # Long Training Field
        self.ltf_sequence = zadoff_chu_sequence(self.num_ltf_symbols_per_sequence,self.ltf_root)
        self.ltf_symbols = np.tile(self.ltf_sequence,self.num_ltf_repeat)
        self.num_ltf_symbols = self.num_ltf_repeat * self.num_ltf_symbols_per_sequence

        # Zeros between STF and LTF
        self.num_stf_ltf_zero_symbols = 30
        stf_ltf_zero_symbols = np.zeros((self.num_stf_ltf_zero_symbols,))

        # STF + Zeros + LTF
        stf_ltf_symbols = np.concatenate((self.stf_symbols,stf_ltf_zero_symbols,self.ltf_symbols))
        self.num_stf_ltf_symbols = self.num_stf_symbols + self.num_ltf_symbols + self.num_stf_ltf_zero_symbols
        
        # Pilots
        self.num_pilot_symbols = 300 # number of random data symbols to generate
        self.pilot_symbols, _ = gen_rand_qam_symbols(self.num_pilot_symbols,M=4)

        # Create full preamble
        self.preamble_symbols = np.concatenate((stf_ltf_symbols,self.pilot_symbols))
        self.num_preamble_symbols = self.num_stf_ltf_symbols + self.num_pilot_symbols
        self.stf_ltf_symbols = stf_ltf_symbols
        # self.preamble_symbols = stf_ltf_symbols
        # self.num_preamble_symbols = self.num_stf_ltf_symbols
        return self.preamble_symbols
    
    def receive_signal(self):
        self.receiver.rx_destroy_buffer() # reset receive data buffer to be safe
        for i in range(1): # clear buffer to be safe
            rx_data_ =  self.receiver.rx()

        if False: # synthesize receive signal
            tx_signal = self.transmit_signal_raw
            zeros = np.zeros((123,))
            rx_signal = np.concatenate((zeros,tx_signal,tx_signal,tx_signal,tx_signal,zeros,zeros,zeros))
            h = cgauss_rv(0,1,1)
            print(h)
            # h = [0.02311763+0.05290167j]
            rx_signal *= h
            rx_signal += cgauss_rv(0,0.1,np.size(rx_signal))
            t = np.arange(len(rx_signal)) / self.sample_rate # time vector
            rx_signal = rx_signal * np.exp(-2.0j*np.pi*7e3*t)
        else: # actually receive from Pluto
            rx_signal =  self.receiver.rx() # capture raw samples from Pluto
            self.transmitter.tx_destroy_buffer() # reset transmit data buffer to be safe
            self.transmitter.rx_destroy_buffer() # reset receive data buffer to be safe
            self.receiver.tx_destroy_buffer() # reset transmit data buffer to be safe
            self.receiver.rx_destroy_buffer() # reset receive data buffer to be safe
        
        # remove DC component from RX signal
        rx_signal -= np.mean(rx_signal)
        
        # matched filter
        pulse_shape = get_rrc_pulse(beta=self.pulse_shape_beta,span=self.pulse_shape_span,sps=self.sps)
        rx_signal = np.convolve(rx_signal,pulse_shape)
        self.receive_signal_full = rx_signal

        # synchronization and equalization
        self.timing_synchronization()
        self.frequency_synchronization()
        # self.iq_imbalance_correction()
        self.channel_equalization()
        return self.desired_receive_signal_equalized
    
    def timing_synchronization(self):
        rx_signal = self.receive_signal_full

        # symbol synchronization
        rx_symbols_, offset = max_output_energy_sync(rx_signal,self.sps,interpolation_factor=1,plot=False)
        
        # frame synchronization: revised method
        num_samples_pre = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        num_samples_post = self.num_ltf_symbols + self.transmit_signal_zero_pad_length + self.desired_transmit_signal_length
        L = len(rx_symbols_) - 1
        corrs, idx_peak = custom_corr(rx_symbols_,self.num_ltf_symbols_per_sequence,L,num_samples_pre,num_samples_post,plot=False)
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
        # print(f"Max Unambiguous CFO (coarse): {cfo_max_coarse:.2f} Hz")
        # print(f"Max Unambiguous CFO (fine): {cfo_max_fine:.2f} Hz")

        # extract STF and LTF chunk (separated by zeros)
        # idx_start = 0
        # idx_stop = idx_start + self.num_stf_ltf_symbols
        # received_stf_ltf_symbols = self.rx_preamble_symbols[idx_start:idx_stop:]

        # extract STF
        idx_start = 0
        idx_stop = idx_start + self.num_stf_symbols
        stf = rx_symbols[idx_start:idx_stop]

        # coarse CFO estimation
        cfo_est_coarse = estimate_cfo(stf,K=self.num_stf_repeat,N=self.num_stf_symbols_per_sequence,Ts=T)
        # print(f"Estimated CFO (coarse): {cfo_est_coarse:.2f} Hz")
        # cfo_est_coarse = -7e3

        # apply coarse CFO correction to all received symbols
        t = np.arange(len(rx_symbols)) * sps / self.sample_rate
        rx_symbols = rx_symbols * np.exp(-2.0j*np.pi*cfo_est_coarse*t)

        # extract LTF after coarse CFO correction
        idx_start = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        idx_stop = idx_start + self.num_ltf_symbols
        ltf = rx_symbols[idx_start:idx_stop]

        # fine CFO estimation using coarse-corrected LTF
        cfo_est_fine = estimate_cfo(ltf,K=self.num_ltf_repeat,N=self.num_ltf_symbols_per_sequence,Ts=T)
        # print(f"Estimated CFO (fine): {cfo_est_fine:.2f} Hz")

        # apply fine CFO correction to all received symbols (pilots and payload)
        # t = np.arange(len(rx_symbols)) * sps / self.sample_rate 
        self.receive_symbols_cfo_corrected = rx_symbols * np.exp(-2.0j*np.pi*cfo_est_fine*t)
        return

    def channel_equalization(self):
        # fetch received pilots from CFO-corrected symbols
        idx_start = self.num_stf_symbols + self.num_stf_ltf_zero_symbols + self.num_ltf_symbols
        idx_stop = idx_start + self.num_pilot_symbols
        received_preamble = self.receive_symbols_cfo_corrected[idx_start:idx_stop]
        # print(len(self.receive_symbols_cfo_corrected[idx_stop:]))
        # print(self.desired_transmit_signal_length)
        # print(self.transmit_signal_zero_pad_length)
        # received_preamble = received_preamble[0:5]

        # fetch transmit pilots
        transmitted_preamble = self.pilot_symbols
        # transmitted_preamble = transmitted_preamble[0:5]

        # Debug: plot the correlation to see if pilots are aligned
        pilot_correlation = np.correlate(self.receive_symbols_cfo_corrected, 
                                    self.pilot_symbols[::-1], 'valid')

        # channel estimation (transmitted_preamble contains zeros)
        mask = transmitted_preamble != 0
        tmp = received_preamble[mask] / transmitted_preamble[mask]
        self.channel_estimate = np.mean(tmp)
        # print("Channel estimate: ", self.channel_estimate)

        # channel equalization applied to all CFO-corrected receive symbols
        self.receive_symbols_equalized = self.receive_symbols_cfo_corrected / self.channel_estimate

        # fetch desired portion of receive symbols
        self.desired_receive_signal_equalized = self.receive_symbols_equalized[-self.desired_transmit_signal_length:]

        return
    
    def estimate_iq_imbalance(self,pilot_tx,pilot_rx):        
        if pilot_tx.shape != pilot_rx.shape:
            raise ValueError("pilot_tx and pilot_rx must have the same shape")

        # Set up linear system: r = alpha * s + beta * s*
        A = np.column_stack([pilot_tx, np.conj(pilot_tx)])
        x, _, _, _ = np.linalg.lstsq(A, pilot_rx, rcond=None)
        
        alpha, beta = x
        return alpha, beta

    def iq_imbalance_correction(self):
        rx_signal = self.receive_symbols_cfo_corrected
        received_preamble = self.receive_symbols_cfo_corrected[0:self.num_preamble_symbols]
        transmitted_preamble = self.preamble_symbols
        alpha, beta = self.estimate_iq_imbalance(transmitted_preamble,received_preamble)
        denominator = np.abs(alpha)**2 - np.abs(beta)**2
        corrected = (np.conj(alpha) * rx_signal - beta * np.conj(rx_signal)) / denominator
        self.receive_symbols_cfo_corrected = corrected
        return
        
#%%
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
if False:
    # tx = Pluto("ip:192.168.2.1")
    tx = Pluto("usb:2.6.5")
    rx = tx
elif True:
    tx = Pluto("usb:2.6.5")
    rx = Pluto("usb:2.7.5")
else:
    tx = adi.Pluto("usb:2.6.5")
    rx = tx

# ---------------------------------------------------------------
# Initialize digital communication system and define system parameters.
# ---------------------------------------------------------------
system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)

modulation_order = 4 # 4, 16, 64, 256, etc.
constellation = get_qam_constellation(modulation_order,Es=1)

num_qam_symbols = 20 # number of random data symbols to generate
transmit_symbols, _ = gen_rand_qam_symbols(num_qam_symbols,M=modulation_order)

# print('Number of QAM symbols: ', num_qam_symbols)

# transmit_symbols = qam_symbols
# transmit_symbols = np.array([1,2,3,4,5]) + 1j * np.array([5,4,3,2,1])
# transmit_symbols -= np.mean(transmit_symbols)

# Load image and convert to bits
img = Image.open("test.png")
img = img.resize((32,32))
img = np.array(img)
bits = np.unpackbits(img)

# bits = np.random.randint(0, 2, len(bits))  # Generate random bits for testing
# bits_padded, padding = qam_pad_bits(bits, M=modulation_order)
transmit_symbols, padding = qam_mapper(bits, constellation)
# transmit_symbols = qam_modulator(bits_padded, M=modulation_order)  # Modulate bits to QAM symbols
# transmit_symbols = transmit_symbols[0:]
# transmit_symbols -= np.mean(transmit_symbols)
num_transmit_symbols = len(transmit_symbols)
print('Number of transmit symbols: ', len(transmit_symbols))

# Shuffle the symbols if desired 
if False:
    shuffler = np.random.permutation(num_transmit_symbols) # returns indices to shuffle the list
else:
    shuffler = np.arange(num_transmit_symbols) # don't shuffle

transmit_symbols_shuffled = transmit_symbols[shuffler]

# sps = 5
# pulse_train = create_pulse_train(transmit_symbols,sps)
# pulse_shape = np.ones((sps,))
# transmit_signal = np.convolve(pulse_train,pulse_shape,'full')
# transmit_signal = transmit_signal[:-sps]
transmit_signal = transmit_symbols_shuffled

system.transmit_signal(transmit_signal)

receive_signal = system.receive_signal()

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

# receive_symbols = receive_signal[sps//2::sps]
receive_symbols = receive_signal
print('Number of receive symbols: ', len(receive_symbols))

detected_receive_symbols_shuffled = demod_nearest(receive_symbols,constellation)

# Undo any shuffling that was done before
detected_receive_symbols = detected_receive_symbols_shuffled[np.argsort(shuffler)]

rx_bits = qam_demapper(detected_receive_symbols, padding, constellation)

ser = calc_symbol_error_rate(transmit_symbols,detected_receive_symbols)

print("Symbol error rate: ", ser)

if True:
    plt.figure(figsize=(6, 6))
    plt.scatter(np.real(receive_symbols),np.imag(receive_symbols), color='red', label='Received Preamble')
    plt.scatter(np.real(transmit_symbols),np.imag(transmit_symbols), color='blue', label='Transmitted Preamble')
    plt.scatter(np.real(constellation),np.imag(constellation), color='black', label='Transmitted Preamble')
    plt.title('Transmitted and Received Symbols')
    plt.xlabel('Real Component')
    plt.ylabel('Imaginary Component')
    plt.grid(True)
    plt.axis('square')
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_09' + '.pdf'
    # plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_09' + '.svg'
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