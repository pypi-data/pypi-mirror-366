import pytest
from unittest.mock import MagicMock, patch
from j1939parser.core import stream_vehicle_positions

class MockCANMessage:
    def __init__(self, arbitration_id, data):
        self.arbitration_id = arbitration_id
        self.data = data
        self.dlc = len(data)

def test_stream_vehicle_position_from_mock_can():
    mock_msg = MockCANMessage(
        arbitration_id=0x18FEF34A,  # PGN 0xFEF3 + source address
        data=bytes.fromhex('0E 23 6A 93 1E DE 81 34')
    )

    # Patch can.interface.Bus to return a mock bus with one message
    with patch('j1939parser.core.can.interface.Bus') as MockBus:
        mock_bus = MagicMock()
        mock_bus.recv.side_effect = [mock_msg, None]  # One message, then None
        MockBus.return_value = mock_bus

        gen = stream_vehicle_positions("can0")  # Source is mocked
        lat, lon = next(gen)

        assert abs(lat - 37.3206542) < 1e-6
        assert abs(lon - (-121.9073762)) < 1e-6
