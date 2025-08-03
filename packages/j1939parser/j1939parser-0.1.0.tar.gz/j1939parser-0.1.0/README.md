# j1939parser

**Extract GPS position and vehicle speed from SAE J1939 CAN logs or live CAN interfaces**

---

## Overview

`j1939parser` is a Python library for decoding vehicle position (latitude and longitude) from J1939 CAN bus data, specifically PGN 65267 (0xFEF3) Vehicle Position, as well as support for live reading from CAN hardware or parsing log files.

It supports two modes of operation:

- **Case A:** Tail and parse a CAN log file (e.g., output from `candump can0 > output.log`)
- **Case B:** Read directly from a live CAN interface like `can0` on a Raspberry Pi with MCP2515 CAN module

---

## Features

- Extract latitude and longitude from J1939 PGN 65267 frames
- Support real-time streaming from live CAN interface or log files
- Auto-detects source type (file or CAN interface)
- Graceful fallback if `python-can` library is missing
- Includes platform check with warning for non-Raspberry Pi environments
- Lightweight and easy to integrate into existing Python projects

---

## Installation

```bash
# Basic install (file parsing only)
pip install j1939parser

# For live CAN interface support (requires python-can)
pip install j1939parser[can]

```
## Usage

### Parsing from a CAN Log file (output.log)
```python
from j1939parser import stream_vehicle_positions

source = "output.log"  # Path to your CAN log file

for lat, lon in stream_vehicle_positions(source):
    print(f"Live GPS → Latitude: {lat:.7f}, Longitude: {lon:.7f}")

```
This will tail the log file and print new positions as they appear.

### Reading from live CAN interface (e.g., Raspberry Pi can0)
```python
from j1939parser import stream_vehicle_positions

source = "can0"  # Your CAN interface name

for lat, lon in stream_vehicle_positions(source):
    print(f"Live GPS → Latitude: {lat:.7f}, Longitude: {lon:.7f}")
```
## Hardware Setup
Raspberry Pi with Linux-based OS

Waveshare MCP2515 CAN module (SPI-based)

CAN interface enabled and configured (e.g., can0)

Bitrate typically set to 250000:

```bash
sudo ip link set can0 up type can bitrate 250000
```
Use candump to log CAN traffic:
```bash
candump can0 > output.log
```

### How Input LOg Lines Should Look

Typical CAN log lines compatible with the parser have this format:
```scss
(1737413716.432751)  can1  18FEF34A   [8]  0E 23 6A 93 1E DE 81 34
```
18FEF34A contains the PGN (18FEF3 = PGN 65267 + source)

Data bytes follow in hex, exactly 8 bytes for PGN 65267 vehicle position


### Development & Contribution
Contributions are welcome! Please open issues or pull requests.

