# %%
"""
Example demonstrating separate transmitter and receiver operation.
This shows how to use the new separated architecture for different scenarios.
"""
import numpy as np

from comms_lib.dsp import get_qam_constellation, qam_mapper
from comms_lib.system3 import (
    DigitalCommSystem,
    DigitalReceiver,
    DigitalTransmitter,
    SystemConfiguration,
)

# ---------------------------------------------------------------
# Scenario 1: Shared configuration for synchronized TX/RX
# ---------------------------------------------------------------
print("="*60)
print("SCENARIO 1: Shared Configuration")
print("="*60)

# Create shared configuration
config = SystemConfiguration()
config.sample_rate = 5e6
config.sps = 8
config.carrier_frequency = 915e6

print(f"Configuration: {config.sample_rate/1e6:.1f} MHz, {config.sps} SPS, {config.carrier_frequency/1e6:.0f} MHz")

# Create TX and RX with shared config
tx = DigitalTransmitter(config)
rx = DigitalReceiver(config)

# Verify they share the same configuration
print(f"TX config sample rate: {tx.config.sample_rate/1e6:.1f} MHz")
print(f"RX config sample rate: {rx.config.sample_rate/1e6:.1f} MHz")
print(f"Configs are same object: {tx.config is rx.config}")

# ---------------------------------------------------------------
# Scenario 2: Separate configurations (for testing mismatched systems)
# ---------------------------------------------------------------
print("\n" + "="*60)
print("SCENARIO 2: Separate Configurations")
print("="*60)

# Create separate configurations
tx_config = SystemConfiguration()
tx_config.sample_rate = 10e6
tx_config.sps = 10

rx_config = SystemConfiguration()
rx_config.sample_rate = 10e6
rx_config.sps = 10

tx_separate = DigitalTransmitter(tx_config)
rx_separate = DigitalReceiver(rx_config)

print(f"TX separate config: {tx_separate.config.sample_rate/1e6:.1f} MHz")
print(f"RX separate config: {rx_separate.config.sample_rate/1e6:.1f} MHz")
print(f"Configs are same object: {tx_separate.config is rx_separate.config}")

# ---------------------------------------------------------------
# Scenario 3: Transmit-only operation
# ---------------------------------------------------------------
print("\n" + "="*60)
print("SCENARIO 3: Transmit-Only Operation")
print("="*60)

# Create transmitter-only system
tx_only_config = SystemConfiguration()
tx_only_config.sample_rate = 8e6
tx_only_config.sps = 4
tx_only_config.tx_gain = 60

# Create transmitter (no SDR for this example)
tx_only = DigitalTransmitter(tx_only_config)

# Generate test data
test_data = np.random.randint(0, 2, 1000)  # Random bits
constellation = get_qam_constellation(16)
symbols, padding = qam_mapper(test_data, constellation)

print(f"Generated {len(test_data)} bits -> {len(symbols)} symbols")
print(f"Using {len(constellation)}-QAM constellation")
print(f"Preamble has {len(tx_only.config.preamble_symbols)} symbols")

# Simulate transmit signal generation (without actual SDR)
tx_only.desired_transmit_signal = symbols
tx_only.tx_sym_len = len(symbols)
tx_only.tx_sym_is_real = False

# ---------------------------------------------------------------
# Scenario 4: Receive-only operation
# ---------------------------------------------------------------
print("\n" + "="*60)
print("SCENARIO 4: Receive-Only Operation")
print("="*60)

# Create receiver-only system
rx_only_config = SystemConfiguration()
rx_only_config.sample_rate = 8e6
rx_only_config.sps = 4
rx_only_config.rx_gain = 50

# Create receiver (no SDR for this example)
rx_only = DigitalReceiver(rx_only_config)

# Set expected transmit parameters (would come from protocol knowledge)
rx_only.set_tx_params(tx_sym_len=len(symbols), tx_sym_is_real=False)

print(f"Receiver configured for {rx_only.config.tx_sym_len} symbols")
print(f"Expected signal type: {'real' if rx_only.config.tx_sym_is_real else 'complex'}")

# ---------------------------------------------------------------
# Scenario 5: Configuration parameter access and modification
# ---------------------------------------------------------------
print("\n" + "="*60)
print("SCENARIO 5: Configuration Management")
print("="*60)

# Create new configuration
mgmt_config = SystemConfiguration()

print("Original parameters:")
print(f"  Sample rate: {mgmt_config.sample_rate/1e6:.1f} MHz")
print(f"  SPS: {mgmt_config.sps}")
print(f"  STF symbols: {mgmt_config.num_stf_symbols}")
print(f"  LTF symbols: {mgmt_config.num_ltf_symbols}")
print(f"  Pilot symbols: {mgmt_config.n_pilot_syms}")

# Modify parameters
mgmt_config.sample_rate = 20e6
mgmt_config.sps = 16
mgmt_config.n_pilot_syms = 2000

print("\nModified parameters:")
print(f"  Sample rate: {mgmt_config.sample_rate/1e6:.1f} MHz")
print(f"  SPS: {mgmt_config.sps}")
print(f"  Pilot symbols: {mgmt_config.n_pilot_syms}")

# Create new TX/RX with modified config
mgmt_tx = DigitalTransmitter(mgmt_config)
mgmt_rx = DigitalReceiver(mgmt_config)

print(f"\nNew preamble length: {len(mgmt_config.preamble_symbols)} symbols")

# ---------------------------------------------------------------
# Scenario 6: Backwards compatibility
# ---------------------------------------------------------------
print("\n" + "="*60)
print("SCENARIO 6: Backwards Compatibility")
print("="*60)

# Use old interface
legacy_system = DigitalCommSystem()
legacy_system.sample_rate = 12e6
legacy_system.sps = 6

print(f"Legacy system sample rate: {legacy_system.sample_rate/1e6:.1f} MHz")
print(f"Legacy system SPS: {legacy_system.sps}")
print(f"Internal TX config: {legacy_system.transmitter_obj.config.sample_rate/1e6:.1f} MHz")
print(f"Internal RX config: {legacy_system.receiver_obj.config.sample_rate/1e6:.1f} MHz")

# Demonstrate that configuration is shared
print(f"TX and RX share config: {legacy_system.transmitter_obj.config is legacy_system.receiver_obj.config}")

print("\n" + "="*60)
print("ALL SCENARIOS COMPLETED")
print("="*60)

# %%
