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

class DigitalCommSystem:
    def __init__(self):
        self.modulation_order = 4
        self.sample_rate = 30e6
        self.fs = self.sample_rate
        self.ts = 1 / self.sample_rate
        self.Ts = 1 / self.sample_rate
        self.num_stf_repeat = 16*4
        self.num_stf_symbols_per_sequence = 7
        self.stf_root = 1
        self.num_ltf_repeat = 2
        self.num_ltf_symbols_per_sequence = 137
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
        # ...
        sdr.tx_lo = int(825e6) # set carrier frequency for reception
        sdr.tx_cyclic_buffer = True
        # sdr.set_transmit_gain()
        sdr.tx_gain = 100
        self.transmitter = sdr
        return

    def set_receiver(self,sdr):
        sdr.tx_destroy_buffer() # reset transmit data buffer to be safe
        sdr.rx_destroy_buffer() # reset receive data buffer to be safe
        sdr.rx_lo = int(825e6) # set carrier frequency for reception
        sdr.rx_rf_bandwidth = int(self.sample_rate) # set receiver RF bandwidth
        sdr.rx_buffer_size = int(600e3) # set buffer size of receiver
        sdr.gain_control_mode_chan0 = 'manual' # set gain control mode
        # sdr.rx_hardwaregain_chan0 = 50 # set gain of receiver
        sdr.rx_gain = 100
        # ...
        self.receiver = sdr
        return

    def set_transmit_gain(self,value):
        # self.transmitter...
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
        print("Length of TX signal: ", self.transmit_signal_length)
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
            rx_signal += cgauss_rv(0,0.0001,np.size(rx_signal))
            t = np.arange(len(rx_signal)) / self.sample_rate # time vector
            rx_signal = rx_signal * np.exp(2.0j*np.pi*1800*t)
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

        # plot
        if True:
            plt.figure(figsize=(12, 10))
            plt.subplot(2,1,1)
            plt.plot(np.real(rx_signal), color='blue', label='Real')
            plt.title('Receive Signal (Real)')
            plt.xlabel('Time Samples')
            plt.ylabel('Amplitude')
            plt.grid(True)
            plt.legend()
            plt.subplot(2,1,2)
            plt.plot(np.imag(rx_signal), color='blue', label='Imaginary')
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
        
        # synchronization and equalization
        self.timing_synchronization()
        self.frequency_synchronization()
        # self.iq_imbalance_correction()
        self.channel_equalization()
        return self.desired_receive_signal_equalized
    
    def timing_synchronization(self):
        rx_signal = self.receive_signal_full

        # symbol synchronization
        rx_symbols_, offset = max_output_energy_sync(rx_signal,self.sps,interpolation_factor=1,plot=True)
        
        # frame synchronization: revised method
        num_samples_pre = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        num_samples_post = self.num_ltf_symbols + self.transmit_signal_zero_pad_length + self.desired_transmit_signal_length
        L = len(rx_symbols_) - 1
        corrs, idx_peak = custom_corr(rx_symbols_,self.num_ltf_symbols_per_sequence,L,num_samples_pre,num_samples_post,plot=True)
        print(idx_peak)
        
        # frame synchronization: original method
        corrs, idx_peak_2 = custom_corr_orig(rx_symbols_,self.num_ltf_symbols_per_sequence,plot=True)
        print(idx_peak_2)

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
        cfo_max_coarse = 1 / (2 * np.pi * self.num_stf_symbols_per_sequence * T)
        cfo_max_fine = 1 / (2 * np.pi * self.num_ltf_symbols_per_sequence * T)
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
        cfo_est_coarse = estimate_cfo(stf,K=self.num_stf_repeat,N=self.num_stf_symbols_per_sequence,Ts=T)
        print(f"Estimated CFO (coarse): {cfo_est_coarse:.2f} Hz")

        # apply coarse CFO correction to all received symbols
        t = np.arange(len(rx_symbols)) * sps / self.sample_rate
        rx_symbols = rx_symbols * np.exp(-2.0j*np.pi*cfo_est_coarse*t)

        # extract LTF after coarse CFO correction
        idx_start = self.num_stf_symbols + self.num_stf_ltf_zero_symbols
        idx_stop = idx_start + self.num_ltf_symbols
        ltf = rx_symbols[idx_start:idx_stop]

        # fine CFO estimation using coarse-corrected LTF
        cfo_est_fine = estimate_cfo(ltf,K=self.num_ltf_repeat,N=self.num_ltf_symbols_per_sequence,Ts=T)
        print(f"Estimated CFO (fine): {cfo_est_fine:.2f} Hz")

        # apply fine CFO correction to all received symbols (pilots and payload)
        t = np.arange(len(rx_symbols)) * sps / self.sample_rate 
        self.receive_symbols_cfo_corrected = rx_symbols * np.exp(-2.0j*np.pi*cfo_est_fine*t)
        return

    def channel_equalization(self):
        # fetch received pilots from CFO-corrected symbols
        idx_start = self.num_stf_symbols + self.num_stf_ltf_zero_symbols + self.num_ltf_symbols
        idx_stop = idx_start + self.num_pilot_symbols
        received_preamble = self.receive_symbols_cfo_corrected[idx_start:idx_stop]
        print(len(self.receive_symbols_cfo_corrected[idx_stop:]))
        print(self.desired_transmit_signal_length)
        print(self.transmit_signal_zero_pad_length)
        # received_preamble = received_preamble[0:5]

        # fetch transmit pilots
        transmitted_preamble = self.pilot_symbols
        # transmitted_preamble = transmitted_preamble[0:5]

        plt.figure()
        plt.plot(np.abs(np.correlate(self.receive_symbols_cfo_corrected, self.stf_ltf_symbols[::-1], 'valid')))
        plt.show()

        # Debug: plot the correlation to see if pilots are aligned
        pilot_correlation = np.correlate(self.receive_symbols_cfo_corrected, 
                                    self.pilot_symbols[::-1], 'valid')
        
        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.plot(np.abs(pilot_correlation))
        plt.title('Pilot Correlation (should show clear peak)')
        plt.xlabel('Sample Index')
        plt.ylabel('Correlation Magnitude')
        
        plt.subplot(1, 2, 2)
        plt.plot(np.real(received_preamble[:50]), 'r-o', label='Received')
        plt.plot(np.real(transmitted_preamble[:50]), 'b-s', label='Transmitted')
        plt.title('First 50 Pilot Symbols')
        plt.legend()
        plt.show()

        # plot
        if True:
            plt.figure(figsize=(6, 6))
            plt.scatter(np.real(received_preamble),np.imag(received_preamble), color='red', label='Received Preamble')
            plt.scatter(np.real(transmitted_preamble),np.imag(transmitted_preamble), color='blue', label='Transmitted Preamble')
            plt.title('Transmitted and Received Preamble')
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

        # channel estimation #1 (transmitted_preamble contains zeros)
        tmp = np.where(transmitted_preamble != 0, received_preamble / transmitted_preamble, 0)
        print(tmp)
        self.channel_estimate = np.mean(tmp)

        # channel estimation #2 (transmitted_preamble contains zeros)
        self.channel_estimate = safely_divide(received_preamble, transmitted_preamble)
        print("Channel estimate: ", self.channel_estimate)

        # channel estimation #2 (transmitted_preamble contains zeros)
        mask = transmitted_preamble != 0
        tmp = received_preamble[mask] / transmitted_preamble[mask]
        self.channel_estimate = np.mean(tmp)
        print(tmp.shape)
        print(received_preamble.shape)
        print("Channel estimate: ", self.channel_estimate)

        # channel equalization applied to all CFO-corrected receive symbols
        self.receive_symbols_equalized = self.receive_symbols_cfo_corrected / self.channel_estimate

        # fetch desired portion of receive symbols
        self.desired_receive_signal_equalized = self.receive_symbols_equalized[-self.desired_transmit_signal_length:]
        print("After EQ: ", len(self.desired_receive_signal_equalized))

        h_estimates = received_preamble[mask] / transmitted_preamble[mask]
        plt.figure()
        plt.plot(np.angle(h_estimates))
        plt.title("Phase of individual channel estimates")
        plt.show()

        # plot
        if True:
            plt.figure(figsize=(6, 6))
            plt.scatter(np.real(tmp),np.imag(tmp), color='red', label='Received Preamble')
            plt.title('Channel Estimates')
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
    tx = Pluto("usb:1.26.5")
    rx = tx
else: 
    tx = Pluto("usb:2.7.5")
    rx = Pluto("usb:2.6.5")

# ---------------------------------------------------------------
# Initialize digital communication system and define system parameters.
# ---------------------------------------------------------------
system = DigitalCommSystem()
system.set_transmitter(tx)
system.set_receiver(rx)
system.set_carrier_frequency(915e6)

# ---------------------------------------------------------------
# Digital communication system parameters.
# ---------------------------------------------------------------
fs = 1e6     # baseband sampling rate (samples per second)
ts = 1 / fs  # baseband sampling period (seconds per sample)
sps = 10     # samples per data symbol
T = ts * sps # time between data symbols (seconds per symbol)

# ---------------------------------------------------------------
# Pluto system parameters.
# ---------------------------------------------------------------
sample_rate = fs                # sampling rate, between ~600e3 and 61e6
tx_carrier_freq_Hz = 915e6      # transmit carrier frequency, between 325 MHz to 3.8 GHz
rx_carrier_freq_Hz = 915e6      # receive carrier frequency, between 325 MHz to 3.8 GHz
tx_rf_bw_Hz = sample_rate * 1   # transmitter's RF bandwidth, between 200 kHz and 56 MHz
rx_rf_bw_Hz = sample_rate * 1   # receiver's RF bandwidth, between 200 kHz and 56 MHz
tx_gain_dB = -20                # transmit gain (in dB), beteween -89.75 to 0 dB with a resolution of 0.25 dB
rx_gain_dB = 40                 # receive gain (in dB), beteween 0 to 74.5 dB (only set if AGC is 'manual')
rx_agc_mode = 'manual'          # receiver's AGC mode: 'manual', 'slow_attack', or 'fast_attack'
rx_buffer_size = 100e3          # receiver's buffer size (in samples), length of data returned by sdr.rx()
tx_cyclic_buffer = True         # cyclic nature of transmitter's buffer (True -> continuously repeat transmission)

tx.sample_rate = int(sample_rate)   # set baseband sampling rate of Pluto
rx.sample_rate = int(sample_rate)
# ---------------------------------------------------------------
# Setup Pluto's transmitter.
# ---------------------------------------------------------------
tx.tx_destroy_buffer()                   # reset transmit data buffer to be safe
tx.tx_rf_bandwidth = int(tx_rf_bw_Hz)    # set transmitter RF bandwidth
tx.tx_lo = int(tx_carrier_freq_Hz)       # set carrier frequency for transmission
tx.tx_hardwaregain_chan0 = tx_gain_dB    # set the transmit gain
tx.tx_cyclic_buffer = tx_cyclic_buffer   # set the cyclic nature of the transmit buffer

# ---------------------------------------------------------------
# Setup Pluto's receiver.
# ---------------------------------------------------------------
rx.rx_destroy_buffer()                   # reset receive data buffer to be safe
rx.rx_lo = int(rx_carrier_freq_Hz)       # set carrier frequency for reception
rx.rx_rf_bandwidth = int(sample_rate)    # set receiver RF bandwidth
rx.rx_buffer_size = int(rx_buffer_size)  # set buffer size of receiver
rx.gain_control_mode_chan0 = rx_agc_mode # set gain control mode
rx.rx_hardwaregain_chan0 = rx_gain_dB    # set gain of receiver

# ---------------------------------------------------------------
# Create transmit signal.
# ---------------------------------------------------------------
N = 10000 # number of samples to transmit
t = np.arange(N) / sample_rate # time vector
tx_signal = 0.5*np.exp(2.0j*np.pi*100e3*t) # complex sinusoid at 100 kHz
tx_signal = np.concatenate((tx_signal,tx_signal))

# ---------------------------------------------------------------
# Transmit from Pluto!
# ---------------------------------------------------------------
tx_signal_scaled = tx_signal / np.max(np.abs(tx_signal)) * 2**14 # Pluto expects TX samples to be between -2^14 and 2^14 
tx.tx(tx_signal_scaled) # will continuously transmit when cyclic buffer set to True

# ---------------------------------------------------------------
# Receive with Pluto!
# ---------------------------------------------------------------
rx.rx_destroy_buffer() # reset receive data buffer to be safe
for i in range(1): # clear buffer to be safe
    rx_data_ = rx.rx() # toss them out
    
rx_signal = rx.rx() # capture raw samples from Pluto

# ---------------------------------------------------------------
# Take FFT of received signal.
# ---------------------------------------------------------------
rx_fft = np.abs(np.fft.fftshift(np.fft.fft(rx_signal)))
f = np.linspace(sample_rate/-2, sample_rate/2, len(rx_fft))

plt.figure()
plt.plot(f/1e3,rx_fft,color="black")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Magnitude")
plt.title('FFT of Received Signal')
plt.grid(True)
plt.show()
