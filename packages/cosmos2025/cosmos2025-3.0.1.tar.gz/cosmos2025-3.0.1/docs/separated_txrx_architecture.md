# Separated TX/RX Digital Communication System

This document describes the refactored digital communication system that separates transmitter and receiver functionality into distinct classes with shared configuration.

## Architecture Overview

The new architecture consists of three main components:

1. **SystemConfiguration**: Contains all system parameters shared between TX and RX
2. **DigitalTransmitter**: Handles signal transmission and pulse shaping
3. **DigitalReceiver**: Handles signal reception, synchronization, and equalization

## Key Features

### Shared Configuration
- All system parameters (sample rate, SPS, preamble settings, etc.) are centralized
- Ensures TX and RX always use compatible parameters
- Can be shared between multiple TX/RX instances or used independently

### Separate TX/RX Classes
- Independent transmitter and receiver operation
- Clean separation of concerns
- Easier testing and debugging
- Supports different deployment scenarios

### Backwards Compatibility
- `DigitalCommSystem` class provides compatibility with existing code
- Legacy interface automatically manages shared configuration

## Usage Examples

### Basic Usage with Shared Configuration

```python
from comms_lib.system3 import SystemConfiguration, DigitalTransmitter, DigitalReceiver
from comms_lib.pluto import Pluto

# Create shared configuration
config = SystemConfiguration()
config.sample_rate = 10e6
config.sps = 8

# Create TX and RX with shared config
tx_sdr = Pluto("ip:192.168.2.1")
rx_sdr = Pluto("ip:192.168.3.1")

transmitter = DigitalTransmitter(config, tx_sdr)
receiver = DigitalReceiver(config, rx_sdr)

# Transmit signal
transmitter.transmit_signal(my_signal)

# Configure receiver with TX parameters
receiver.set_transmit_parameters(
    transmitter.tx_sym_len,
    transmitter.tx_sym_is_real
)

# Receive signal
received_signal = receiver.receive_signal()
```

### Transmit-Only Application

```python
# Create transmitter for broadcast application
config = SystemConfiguration()
config.tx_gain = 80

transmitter = DigitalTransmitter(config, tx_sdr)
transmitter.transmit_signal(broadcast_data)
```

### Receive-Only Application

```python
# Create receiver for monitoring application
config = SystemConfiguration()
config.rx_gain = 60

receiver = DigitalReceiver(config, rx_sdr)
receiver.set_transmit_parameters(expected_length, is_real=False)
received_data = receiver.receive_signal()
```

### Legacy Compatibility

```python
from comms_lib.system3 import DigitalCommSystem

# Use existing interface
system = DigitalCommSystem()
system.set_transmitter(tx_sdr)
system.set_receiver(rx_sdr)
system.transmit_signal(data)
received = system.receive_signal()
```

## Configuration Parameters

### System Parameters
- `sample_rate`: Baseband sampling rate (Hz)
- `sps`: Samples per symbol
- `modulation_order`: QAM modulation order

### Preamble Parameters
- `num_stf_repeat`: STF repetitions
- `num_stf_symbols_per_sequence`: STF symbols per sequence
- `stf_root`: STF Zadoff-Chu root
- `num_ltf_repeat`: LTF repetitions
- `num_ltf_symbols_per_sequence`: LTF symbols per sequence
- `ltf_root`: LTF Zadoff-Chu root
- `num_pilot_symbols`: Number of pilot symbols

### Pulse Shaping Parameters
- `pulse_shape_beta`: RRC filter roll-off
- `pulse_shape_span`: RRC filter span
- `pulse_shape_length`: Filter length (calculated)

### Hardware Parameters
- `carrier_frequency`: RF carrier frequency (Hz)
- `tx_gain`: Transmitter gain (dB)
- `rx_gain`: Receiver gain (dB)
- `rx_buffer_size`: Receiver buffer size (samples)

## Files

- **src/comms_lib/system3.py**: New separated architecture
- **ian3/main_ian_v04_separate_txrx.py**: Updated test based on main_ian_v03.py
- **ian3/example_separate_txrx.py**: Comprehensive examples demonstrating all usage scenarios

## Benefits

1. **Modularity**: TX and RX can be developed and tested independently
2. **Flexibility**: Supports TX-only, RX-only, and combined applications
3. **Configuration Management**: Centralized parameter management prevents mismatches
4. **Scalability**: Easy to extend for multiple TX/RX pairs
5. **Maintainability**: Clear separation of concerns improves code organization
6. **Backwards Compatibility**: Existing code continues to work unchanged
