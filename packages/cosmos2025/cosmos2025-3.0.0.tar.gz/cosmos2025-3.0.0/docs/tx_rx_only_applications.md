# TX-Only and RX-Only Applications

This document describes the standalone transmitter and receiver applications created using the separated TX/RX architecture.

## Files Created

### `tx_only.py` - Transmitter-Only Application

A standalone transmitter application that demonstrates:
- **Independent transmitter operation** using `DigitalTransmitter`
- **Flexible data input** (loads test image or generates random data)
- **Complete signal processing** including QAM mapping and pulse shaping
- **Continuous transmission** with cyclic buffer
- **Simulation mode** when no hardware is available
- **Signal analysis** and statistics

**Key Features:**
- Configurable system parameters
- Error handling for missing hardware
- Signal quality analysis (PAPR, power statistics)
- Continuous transmission mode
- Clean shutdown handling

### `rx_only.py` - Receiver-Only Application

A standalone receiver application that demonstrates:
- **Independent receiver operation** using `DigitalReceiver`
- **Continuous reception loop** with error handling
- **Signal demodulation** and symbol detection
- **Image reconstruction** from received data
- **Real-time plotting** of constellation and received images
- **Performance analysis** with signal statistics

**Key Features:**
- Configurable expected signal parameters
- Multiple reception attempts
- Automatic image saving
- Constellation plotting
- Reception timing analysis
- Clean shutdown handling

## Usage

### Running the Transmitter

```bash
cd ian3
python tx_only.py
```

**Configuration:**
- Modify IP address: Change `"ip:192.168.2.1"` to your Pluto SDR IP
- Adjust parameters in the `SystemConfiguration()` setup
- Change modulation order, image size, or signal parameters as needed

**Output:**
- Continuous transmission status
- Signal analysis and statistics
- Hardware connection status
- Transmission timing information

### Running the Receiver

```bash
cd ian3
python rx_only.py
```

**Configuration:**
- Modify IP address: Change `"ip:192.168.3.1"` to your Pluto SDR IP
- Ensure expected signal parameters match the transmitter
- Adjust reception timing and analysis settings

**Output:**
- Received signal analysis
- Constellation plots
- Reconstructed images saved as PNG files
- Reception timing and error statistics

## System Architecture Benefits

### Independent Operation
- **TX-only applications**: Broadcasting, beacon transmission, test signal generation
- **RX-only applications**: Monitoring, spectrum analysis, signal detection
- **Separate development**: TX and RX can be developed and tested independently

### Shared Configuration
- **Parameter consistency**: Both applications use `SystemConfiguration`
- **Protocol compliance**: Ensures transmitter and receiver use compatible settings
- **Easy synchronization**: Same preamble, timing, and signal structure

### Hardware Flexibility
- **Different SDR devices**: TX and RX can use different Pluto SDRs
- **Simulation support**: Applications work without hardware for testing
- **Error resilience**: Graceful handling of hardware connection issues

## Example Workflow

1. **Start Receiver First:**
   ```bash
   python rx_only.py
   ```
   - Receiver begins listening for signals
   - Shows configuration and expected parameters

2. **Start Transmitter:**
   ```bash
   python tx_only.py
   ```
   - Transmitter begins sending signals
   - Uses compatible configuration

3. **Monitor Reception:**
   - Receiver displays signal analysis
   - Images are reconstructed and saved
   - Constellation plots show signal quality

4. **Stop Applications:**
   - Use Ctrl+C to cleanly stop both applications
   - Hardware buffers are properly cleaned up

## Customization

### Signal Parameters
- Modify `modulation_order` for different QAM schemes
- Adjust `expected_image_size` for different data types
- Change `sps_external` for different oversampling

### Hardware Settings
- Update IP addresses for your Pluto SDR devices
- Modify gain settings (`tx_gain`, `rx_gain`)
- Adjust RF bandwidth and carrier frequency

### Data Processing
- Replace image loading with other data sources
- Modify signal analysis and plotting functions
- Add custom error correction or protocol features

## Benefits Over Combined System

1. **Modularity**: Clear separation of TX and RX functionality
2. **Testing**: Independent validation of each component
3. **Deployment**: Flexible deployment in TX-only or RX-only scenarios
4. **Development**: Parallel development of transmitter and receiver features
5. **Debugging**: Easier to isolate and fix issues in specific components
