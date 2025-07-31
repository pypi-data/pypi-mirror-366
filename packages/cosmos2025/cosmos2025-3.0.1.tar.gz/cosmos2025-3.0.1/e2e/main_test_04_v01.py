# Essentials
#%%
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import time 

from dsp import *

# Pluto Library
# import adi # local
from remoteRF.drivers.adalm_pluto import * # remoteRF

# Directory for saving plots
dir_plots = 'plots/'

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
tx_carrier_freq_Hz = 905e6      # transmit carrier frequency, between 325 MHz to 3.8 GHz
rx_carrier_freq_Hz = 905e6      # receive carrier frequency, between 325 MHz to 3.8 GHz
tx_rf_bw_Hz = sample_rate * 1   # transmitter's RF bandwidth, between 200 kHz and 56 MHz
rx_rf_bw_Hz = sample_rate * 1   # receiver's RF bandwidth, between 200 kHz and 56 MHz
tx_gain_dB = -10                # transmit gain (in dB), beteween -89.75 to 0 dB with a resolution of 0.25 dB
rx_gain_dB = 30                 # receive gain (in dB), beteween 0 to 74.5 dB (only set if AGC is 'manual')
rx_agc_mode = 'manual'          # receiver's AGC mode: 'manual', 'slow_attack', or 'fast_attack'
rx_buffer_size = 500e3          # receiver's buffer size (in samples), length of data returned by sdr.rx()
tx_cyclic_buffer = True         # cyclic nature of transmitter's buffer (True -> continuously repeat transmission)

# ---------------------------------------------------------------
# Initialize Pluto object using issued token.
# ---------------------------------------------------------------
sdr_tx = adi.Pluto(token='82fn-uewolE') # create Pluto object
sdr_tx.sample_rate = int(sample_rate)   # set baseband sampling rate of Pluto

sdr_rx = adi.Pluto(token='TcrjJbxUotU') # create Pluto object
sdr_rx.sample_rate = int(sample_rate)   # set baseband sampling rate of Pluto

# 2: 82fn-uewolE
# 3: TcrjJbxUotU
# 4: 

# ---------------------------------------------------------------
# Setup Pluto's transmitter.
# ---------------------------------------------------------------
sdr_tx.tx_destroy_buffer()                   # reset transmit data buffer to be safe
sdr_tx.rx_destroy_buffer()                   # reset receive data buffer to be safe
sdr_tx.tx_rf_bandwidth = int(tx_rf_bw_Hz)    # set transmitter RF bandwidth
sdr_tx.tx_lo = int(tx_carrier_freq_Hz)       # set carrier frequency for transmission
sdr_tx.tx_hardwaregain_chan0 = tx_gain_dB    # set the transmit gain
sdr_tx.tx_cyclic_buffer = tx_cyclic_buffer   # set the cyclic nature of the transmit buffer

# ---------------------------------------------------------------
# Setup Pluto's receiver.
# ---------------------------------------------------------------
sdr_rx.tx_destroy_buffer()                   # reset transmit data buffer to be safe
sdr_rx.rx_destroy_buffer()                   # reset receive data buffer to be safe
sdr_rx.rx_lo = int(rx_carrier_freq_Hz)       # set carrier frequency for reception
sdr_rx.rx_rf_bandwidth = int(sample_rate)    # set receiver RF bandwidth
sdr_rx.rx_buffer_size = int(rx_buffer_size)  # set buffer size of receiver
sdr_rx.gain_control_mode_chan0 = rx_agc_mode # set gain control mode
sdr_rx.rx_hardwaregain_chan0 = rx_gain_dB    # set gain of receiver

# ---------------------------------------------------------------
# Generate random sequence of MQAM symbols.
# ---------------------------------------------------------------
modulation_order = 16 # 4, 16, 64, 256, etc.
num_qam_symbols = 20000 # number of random data symbols to generate
qam_symbols_unshuffled, constellation = gen_rand_qam_symbols(num_qam_symbols,M=modulation_order)

# Shuffle the QAM symbols if desired (not very relevant here)
if False:
    shuffler = np.random.permutation(num_qam_symbols) # returns indices to shuffle the list
else:
    shuffler = np.arange(num_qam_symbols) # don't shuffle

undo_shuffler = np.argsort(shuffler) # returns indices to undo the shuffle

# Shuffle the symbols if desired
qam_symbols = [qam_symbols_unshuffled[j] for j in shuffler]

num_qam_symbols = len(qam_symbols)
print('Number of QAM symbols: ', num_qam_symbols) # just to confirm

if True:
    plt.figure(figsize=(6, 6))
    plt.scatter(np.real(qam_symbols),np.imag(qam_symbols), color='blue', label='Transmit Symbols')
    plt.title('Transmit QAM Symbols')
    plt.xlabel('Real Component')
    plt.ylabel('Imaginary Component')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_00' + '.pdf'
    plt.savefig(filename)
    plt.show()

# ---------------------------------------------------------------
# Create Zadoff-Chu sequence for synchronization.
# ---------------------------------------------------------------
# num_zc_symbols = 79 # 137
# zc_root = 11
# zc_symbols = zadoff_chu_sequence(num_zc_symbols,zc_root)

# Repeat
# zc_symbols = np.concatenate((zc_symbols,zc_symbols))
# num_zc_symbols = num_zc_symbols * 2

# ---------------------------------------------------------------
# Create STF training sequence for frequency synchronization.
# ---------------------------------------------------------------
num_stf_repeat = 16
num_stf_symbols_per_sequence = 31 # 137
stf_root = 13
stf_sequence = zadoff_chu_sequence(num_stf_symbols_per_sequence,stf_root)
stf_symbols = np.tile(stf_sequence,num_stf_repeat)
num_stf_symbols = num_stf_repeat * num_stf_symbols_per_sequence

# ---------------------------------------------------------------
# Create LTF training sequence for frequency synchronization.
# ---------------------------------------------------------------
num_ltf_repeat = 2
num_ltf_symbols_per_sequence = 937 # 137, 937
ltf_root = 13
ltf_sequence = zadoff_chu_sequence(num_ltf_symbols_per_sequence,ltf_root)
ltf_symbols = np.tile(ltf_sequence,num_ltf_repeat)
num_ltf_symbols = num_ltf_repeat * num_ltf_symbols_per_sequence

# ---------------------------------------------------------------
# Combine STF and LTF training sequences.
# ---------------------------------------------------------------
num_stf_ltf_zero_symbols = 200
stf_ltf_zero_symbols = np.zeros((num_stf_ltf_zero_symbols,))
stf_ltf_symbols = np.concatenate((stf_symbols,stf_ltf_zero_symbols,ltf_symbols))
num_stf_ltf_symbols = num_stf_symbols + num_ltf_symbols + num_stf_ltf_zero_symbols

# ---------------------------------------------------------------
# Create zero pad to insert between training sequence and QAM symbols.
# ---------------------------------------------------------------
num_zero_symbols = 100
zero_symbols = np.zeros((num_zero_symbols,))

# ---------------------------------------------------------------
# Create pilots.
# ---------------------------------------------------------------
num_pilot_symbols = 300 # number of random data symbols to generate
pilot_symbols,_ = gen_rand_qam_symbols(num_pilot_symbols,M=modulation_order)

# ---------------------------------------------------------------
# Prepend ZC and zero pad to QAM symbols.
# ---------------------------------------------------------------
symbols = np.concatenate((stf_ltf_symbols,zero_symbols,pilot_symbols,qam_symbols))
num_symbols = num_stf_ltf_symbols + num_zero_symbols + num_pilot_symbols + num_qam_symbols
tx_symbols = symbols

# ---------------------------------------------------------------
# Create pulse train of symbols.
# ---------------------------------------------------------------
pulse_train = create_pulse_train(symbols,sps)

if True:
    plt.figure(figsize=(12, 6))
    plt.subplot(2,1,1)
    plt.plot(np.real(pulse_train), color='blue', label='Pulse Train')
    plt.scatter(np.arange(0,num_symbols*sps,sps),np.real(symbols), color='blue', label='Original Symbols')
    plt.title('Pulse Train of Symbols (Real)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.subplot(2,1,2)
    plt.plot(np.imag(pulse_train), color='red', label='Pulse Train')
    plt.scatter(np.arange(0,num_symbols*sps,sps),np.imag(symbols), color='red', label='Original Symbols')
    plt.title('Pulse Train of Symbols (Imaginary)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_01' + '.pdf'
    plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_01' + '.svg'
    plt.savefig(filename)
    plt.show()

# ---------------------------------------------------------------
# Generate RRC pulse shape.
# ---------------------------------------------------------------
beta = 1 # rolloff factor
symbol_span_rrc = int(23) # number of symbols spanned by filter
sps = int(10) # samples per symbol
rrc = get_rrc_pulse(beta,symbol_span_rrc,sps)

if True:
    plt.figure(figsize=(6, 6))
    plt.plot(rrc, color='blue', label='Root Raised Cosine')
    plt.title('Root Raised Cosine Transmit Pulse Shape')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_02' + '.pdf'
    plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_02' + '.svg'
    plt.savefig(filename)
    plt.show()

# ---------------------------------------------------------------
# Raised cosine pulse shape.
# ---------------------------------------------------------------
rc = np.convolve(rrc,rrc) 

if True:
    plt.figure(figsize=(6, 6))
    plt.plot(rc, color='blue', label='Raised Cosine')
    plt.title('Raised Cosine Effective Pulse Shape')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_03' + '.pdf'
    plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_03' + '.svg'
    plt.savefig(filename)
    plt.show()

# ---------------------------------------------------------------
# Perform pulse shaping with a root raised cosine pulse shape.
# ---------------------------------------------------------------
pulse_shape = rrc
tx_signal = np.convolve(pulse_train,pulse_shape)
lag_pulse_shape = int(np.floor(len(pulse_shape)/2)) # lag associated with root raised cosine
sample_indices = lag_pulse_shape + np.arange(0,sps*num_symbols,sps) # tx_signal[sample_indices]

if True:
    plt.figure(figsize=(12, 6))
    plt.subplot(2,1,1)
    plt.plot(np.real(tx_signal), color='blue', label='Real')
    plt.scatter(lag_pulse_shape+np.arange(0,num_symbols*sps,sps),np.real(symbols), color='blue', label='Original Symbols')
    plt.title('Baseband Transmit Signal (Real)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    plt.subplot(2,1,2)
    plt.plot(np.imag(tx_signal), color='red', label='Imaginary')
    plt.scatter(lag_pulse_shape+np.arange(0,num_symbols*sps,sps),np.imag(symbols), color='red', label='Original Symbols')
    plt.title('Baseband Transmit Signal (Imaginary)')
    plt.xlabel('Time Samples')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()
    filename = dir_plots + 'main_test_04_v01_04' + '.pdf'
    plt.savefig(filename)
    filename = dir_plots + 'main_test_04_v01_04' + '.svg'
    plt.savefig(filename)
    plt.show()

# ---------------------------------------------------------------
# Transmit from Pluto!
# ---------------------------------------------------------------
tx_signal_scaled = tx_signal / np.max(np.abs(tx_signal)) * 2**14 # Pluto expects TX samples to be between -2^14 and 2^14 
sdr_tx.tx(tx_signal_scaled) # will continuously transmit when cyclic buffer set to True

# ---------------------------------------------------------------
# Receive with Pluto!
# ---------------------------------------------------------------
sdr_rx.rx_destroy_buffer() # reset receive data buffer to be safe
for i in range(1): # clear buffer to be safe
    rx_data_ = sdr_rx.rx()
    
rx_signal = sdr_rx.rx() # capture raw samples from Pluto
# rx_signal -= np.mean(rx_signal) # remove DC component from RX signal

# Synthesize receive signal
if False: 
    zeros = np.zeros((1000,))
    rx_signal = np.concatenate((zeros,tx_signal,tx_signal,tx_signal,tx_signal,zeros,zeros,zeros)) 
    # rx_signal += cgauss_rv(0,0.01,np.size(rx_signal))
    t = np.arange(len(rx_signal)) / sample_rate # time vector
    rx_signal = rx_signal * np.exp(2.0j*np.pi*100*t)

# ---------------------------------------------------------------
# Clear buffers to stop transmitting.
# ---------------------------------------------------------------
sdr_tx.tx_destroy_buffer()                   # reset transmit data buffer to be safe
sdr_tx.rx_destroy_buffer()                   # reset receive data buffer to be safe
sdr_rx.tx_destroy_buffer()                   # reset transmit data buffer to be safe
sdr_rx.rx_destroy_buffer()                   # reset receive data buffer to be safe

# ---------------------------------------------------------------
# Apply matched filter (another root raised cosine pulse shape).
# ---------------------------------------------------------------
matched_filter = pulse_shape
rx_signal = np.convolve(rx_signal,matched_filter)

# ---------------------------------------------------------------
# Take FFT of received signal.
# ---------------------------------------------------------------
if True:
    nfft = 2 ** (np.ceil(np.log2(len(rx_signal)))+0).astype(int)
    rx_fft = np.abs(np.fft.fftshift(np.fft.fft(rx_signal,n=nfft)))
    f = np.linspace(sample_rate/-2, sample_rate/2, len(rx_fft))

    plt.figure()
    plt.plot(f/1e3,rx_fft,color="black")
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Magnitude")
    plt.title('FFT of Received Signal')
    plt.grid(True)
    plt.show()

# ---------------------------------------------------------------
# Symbol synchronization (MOE).
# ---------------------------------------------------------------
rx_symbols_, offset = max_output_energy_sync(rx_signal,sps,interpolation_factor=8,plot=False)

corrs, idx_peak = custom_corr(rx_symbols_,num_ltf_symbols_per_sequence,plot=False)

print(idx_peak)

num_samples_pre = num_stf_symbols + num_stf_ltf_zero_symbols
num_samples_post = num_symbols - num_samples_pre
idx_start = idx_peak - num_samples_pre
idx_stop = idx_peak + num_samples_post
rx_symbols = rx_symbols_[idx_start:idx_stop]

# ---------------------------------------------------------------
# Timing synchronization and coarse channel estimation using Zadoff-Chu signal.
# ---------------------------------------------------------------
# rx_symbols, ch_est_coarse = synchronize(rx_symbols_,zc_symbols,num_symbols)
# num_samples_pre = num_stf_symbols + num_stf_ltf_zero_symbols
# num_samples_post = num_symbols - num_samples_pre
# rx_symbols, ch_est_coarse = frame_synch_stf_ltf(rx_symbols_,ltf_symbols,num_samples_post=num_samples_post,num_samples_pre=num_samples_pre)

plt.figure()
plt.plot(np.real(symbols),color='blue',label='Transmitted Symbols')
plt.plot(np.real(rx_symbols),color='red',label='Received Symbols')
plt.grid(True)
plt.legend()
filename = dir_plots + 'main_test_04_v01_05' + '.pdf'
plt.savefig(filename)
filename = dir_plots + 'main_test_04_v01_05' + '.svg'
plt.savefig(filename)
plt.show()

# ---------------------------------------------------------------
# Sample received signal every T seconds (every sps samples).
# ---------------------------------------------------------------
received_symbols = rx_symbols

# plt.figure(figsize=(6, 6))
# plt.scatter(np.real(symbols),np.imag(symbols), color='blue', label='Transmitted Symbols')
# plt.scatter(np.real(received_symbols),np.imag(received_symbols), color='red', label='Received Symbols')
# plt.title('Transmitted and Received Symbols')
# plt.xlabel('Real Component')
# plt.ylabel('Imaginary Component')
# plt.grid(True)
# plt.axis('square')
# plt.legend()
# filename = dir_plots + 'main_test_04_v01_06' + '.pdf'
# plt.savefig(filename)
# filename = dir_plots + 'main_test_04_v01_06' + '.svg'
# plt.savefig(filename)
# plt.show()

# ---------------------------------------------------------------
# Coarse channel equalization.
# ---------------------------------------------------------------
# received_symbols = received_symbols / ch_est_coarse

plt.figure(figsize=(6, 6))
plt.scatter(np.real(symbols),np.imag(symbols), color='blue', label='Transmitted Symbols')
plt.scatter(np.real(received_symbols),np.imag(received_symbols), color='red', label='Received Symbols')
plt.title('Transmitted and Received Symbols')
plt.xlabel('Real Component')
plt.ylabel('Imaginary Component')
plt.grid(True)
plt.axis('square')
plt.legend()
filename = dir_plots + 'main_test_04_v01_07' + '.pdf'
plt.savefig(filename)
filename = dir_plots + 'main_test_04_v01_07' + '.svg'
plt.savefig(filename)
plt.show()

# ---------------------------------------------------------------
# Extract ZC training sequence and do CFO estimation, correction.
# ---------------------------------------------------------------
idx_start = 0
idx_stop = idx_start + num_stf_ltf_symbols
received_stf_ltf_symbols = received_symbols[idx_start:idx_stop:]

stf = received_stf_ltf_symbols[0:num_stf_symbols]

idx_start = num_stf_symbols + num_stf_ltf_zero_symbols
idx_stop = idx_start + num_ltf_symbols
ltf = received_stf_ltf_symbols[idx_start:idx_stop]

# print(len(stf))

cfo_max_coarse = 1 / (2 * np.pi * num_stf_symbols_per_sequence * T)
cfo_max_fine = 1 / (2 * np.pi * num_ltf_symbols_per_sequence * T)

print(f"Max Unambiguous CFO (coarse): {cfo_max_coarse:.2f} Hz")
print(f"Max Unambiguous CFO (fine): {cfo_max_fine:.2f} Hz")

cfo_est_coarse = estimate_cfo(stf,K=num_stf_repeat,N=num_stf_symbols_per_sequence,Ts=T)
print(f"Estimated CFO (coarse): {cfo_est_coarse:.2f} Hz")

t = np.arange(len(ltf)) / sample_rate # time vector
ltf = ltf * np.exp(-2.0j*np.pi*cfo_est_coarse*t*sps)

cfo_est_fine = estimate_cfo(ltf,K=num_ltf_repeat,N=num_ltf_symbols_per_sequence,Ts=T)
print(f"Estimated CFO (fine): {cfo_est_fine:.2f} Hz")

t = np.arange(len(received_symbols)) / sample_rate # time vector
received_symbols = received_symbols * np.exp(-2.0j*np.pi*cfo_est_coarse*t*sps) * np.exp(-2.0j*np.pi*cfo_est_fine*t*sps)

# print(len(received_zc_symbols))
# cfo_est = estimate_cfo(received_zc_symbols,num_zc_symbols/2,sps/sample_rate)
# print(cfo_est)
# cfo_est = -100 + 0.28
# print(cfo_est)
# t = np.arange(len(received_symbols)) / sample_rate # time vector
# received_symbols = received_symbols * np.exp(-2.0j*np.pi*cfo_est*t*sps)

# ---------------------------------------------------------------
# Extract pilots + QAM symbols (throw away Zadoff-Chu and zero pad).
# ---------------------------------------------------------------
# idx_start = num_zc_symbols + num_zero_symbols + int(symbol_span_rrc)
idx_start = num_stf_ltf_symbols + num_zero_symbols
idx_stop = idx_start + num_pilot_symbols + num_qam_symbols
received_pilots_qam_symbols = received_symbols[idx_start:idx_stop:]

# ---------------------------------------------------------------
# Extract pilot symbols only.
# ---------------------------------------------------------------
received_pilot_symbols = received_pilots_qam_symbols[0:num_pilot_symbols]

plt.figure(figsize=(6, 6))
plt.scatter(np.real(received_pilot_symbols),np.imag(received_pilot_symbols), color='red', label='Received Pilot Symbols')
plt.scatter(np.real(pilot_symbols),np.imag(pilot_symbols), color='blue', label='Transmitted Pilot Symbols')
plt.title('Transmitted and Received Pilot Symbols')
plt.xlabel('Real Component')
plt.ylabel('Imaginary Component')
plt.grid(True)
plt.axis('square')
plt.legend()
filename = dir_plots + 'main_test_04_v01_08' + '.pdf'
plt.savefig(filename)
filename = dir_plots + 'main_test_04_v01_08' + '.svg'
plt.savefig(filename)
plt.show()

# ---------------------------------------------------------------
# Extract QAM symbols only.
# ---------------------------------------------------------------
idx_start = num_pilot_symbols
idx_stop = idx_start + num_qam_symbols
received_qam_symbols = received_pilots_qam_symbols[idx_start:idx_stop]

print(received_qam_symbols.shape)

plt.figure(figsize=(6, 6))
plt.scatter(np.real(received_qam_symbols),np.imag(received_qam_symbols), color='red', label='Received QAM Symbols')
plt.scatter(np.real(qam_symbols),np.imag(qam_symbols), color='blue', label='Transmitted QAM Symbols')
plt.title('Transmitted and Received QAM Symbols')
plt.xlabel('Real Component')
plt.ylabel('Imaginary Component')
plt.grid(True)
plt.axis('square')
plt.legend()
filename = dir_plots + 'main_test_04_v01_09' + '.pdf'
plt.savefig(filename)
filename = dir_plots + 'main_test_04_v01_09' + '.svg'
plt.savefig(filename)
plt.show()

# ---------------------------------------------------------------
# Fine channel estimation and equalization.
# ---------------------------------------------------------------
ch_est_fine = np.mean(received_pilot_symbols / pilot_symbols)
received_qam_symbols /= ch_est_fine

plt.figure(figsize=(6, 6))
plt.scatter(np.real(received_qam_symbols),np.imag(received_qam_symbols), color='red', label='Received QAM Symbols')
plt.scatter(np.real(qam_symbols),np.imag(qam_symbols), color='blue', label='Transmitted QAM Symbols')
plt.title('Transmitted and Received QAM Symbols (After Equalization)')
plt.xlabel('Real Component')
plt.ylabel('Imaginary Component')
plt.grid(True)
plt.legend()
filename = dir_plots + 'main_test_04_v01_10' + '.pdf'
plt.savefig(filename)
filename = dir_plots + 'main_test_04_v01_10' + '.svg'
plt.savefig(filename)
plt.show()

# ---------------------------------------------------------------
# Digital demodulation to nearest constellation points.
# ---------------------------------------------------------------
constellation = get_qam_constellation(modulation_order,Es=1)
qam_symbols_est = demod_nearest(received_qam_symbols,constellation)

print(qam_symbols_est.shape)
print(undo_shuffler.shape)

# Undo any shuffling that was done before
qam_symbols_est_unshuffled = [qam_symbols_est[j] for j in undo_shuffler]

# ---------------------------------------------------------------
# Calculate symbol error rate and plot.
# ---------------------------------------------------------------
ser = calc_symbol_error_rate(qam_symbols_unshuffled,qam_symbols_est_unshuffled)
print("Symbol error rate: ", ser)

plt.figure(figsize=(6, 6))
plt.scatter(np.real(qam_symbols_est),np.imag(qam_symbols_est), color='red', label='Estimated QAM Symbols')
plt.title('Estimated QAM Symbols (SER: ' + str(ser) + ')')
plt.xlabel('Real Component')
plt.ylabel('Imaginary Component')
plt.grid(True)
plt.legend()
filename = dir_plots + 'main_test_04_v01_11' + '.pdf'
plt.savefig(filename)
filename = dir_plots + 'main_test_04_v01_11' + '.svg'
plt.savefig(filename)
plt.show()


# %%
