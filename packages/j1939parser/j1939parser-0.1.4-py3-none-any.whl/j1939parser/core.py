import time
import re
import os
import platform
import importlib

# Try importing python-can only if needed
try:
    can = importlib.import_module("can")
except ImportError:
    can = None


def hex_to_int(hex_str_list):
    raw_bytes = bytes(int(b, 16) for b in hex_str_list)
    return int.from_bytes(raw_bytes, byteorder='little', signed=False)


def follow(file):
    """Tail a file like `tail -f`."""
    #file.seek(0, 2)  # Move to end of file
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


def parse_vehicle_position(data_bytes):
    """Convert 8-byte hex list to (lat, lon)."""
    if len(data_bytes) != 8:
        return None
    lat_int = hex_to_int(data_bytes[0:4])
    lon_int = hex_to_int(data_bytes[4:8])
    lat = lat_int * 1e-7 - 210
    lon = lon_int * 1e-7 - 210
    return lat, lon


def is_raspberry_pi():
    """Basic check for Raspberry Pi."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            return "Raspberry Pi" in f.read()
    except:
        return False


def stream_vehicle_positions(source):
    """
    Real-time stream of vehicle positions from either:
    - a CAN log file (Case A)
    - a live CAN interface like 'can0' (Case B)

    Args:
        source (str): File path or CAN interface name

    Yields:
        Tuple: (latitude, longitude) in real-time
    """
    pgn_pattern = re.compile(
        r'can\d+\s+18FEF3[\da-fA-F]{2}\s+\[8\]\s+((?:[\da-fA-F]{2}\s+){7}[\da-fA-F]{2})'
    )

    if os.path.isfile(source):
        # 🟢 Case A: Read from log file
        with open(source, 'r') as file:
            for line in follow(file):
                match = pgn_pattern.search(line)
                if match:
                    data_bytes = match.group(1).strip().split()
                    result = parse_vehicle_position(data_bytes)
                    if result:
                        yield result

    else:
        # 🔵 Case B: Read from live CAN interface
        if not is_raspberry_pi():
            print("⚠️  Warning: Live CAN access is typically supported on Raspberry Pi or similar Linux systems.")

        if can is None:
            raise ImportError("Live CAN interface requires 'python-can'. Install with: pip install j1939parser[can]")

        try:
            bus = can.interface.Bus(channel=source, bustype="socketcan")
        except Exception as e:
            raise RuntimeError(f"Could not open CAN interface '{source}': {e}")

        while True:
            msg = bus.recv()
            if msg is None or msg.dlc != 8:
                continue

            pgn = (msg.arbitration_id >> 8) & 0xFFFF
            if pgn != 0xFEF3:
                continue

            data = [f"{b:02X}" for b in msg.data]
            result = parse_vehicle_position(data)
            if result:
                yield result
