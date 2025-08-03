import pytest
from j1939parser.core import hex_to_int


def test_hex_to_int_basic():
    """Test basic hex string list conversion to integer."""
    hex_list = ['0E', '23', '6A', '93']
    result = hex_to_int(hex_list)
    expected = int.from_bytes(bytes([0x0E, 0x23, 0x6A, 0x93]), byteorder='little')
    assert result == expected


def test_hex_to_int_single_byte():
    """Test single byte conversion."""
    hex_list = ['FF']
    result = hex_to_int(hex_list)
    assert result == 255


def test_hex_to_int_zero():
    """Test zero byte conversion."""
    hex_list = ['00']
    result = hex_to_int(hex_list)
    assert result == 0


def test_hex_to_int_lowercase():
    """Test lowercase hex strings."""
    hex_list = ['0e', '23', '6a', '93']
    result = hex_to_int(hex_list)
    expected = int.from_bytes(bytes([0x0E, 0x23, 0x6A, 0x93]), byteorder='little')
    assert result == expected


def test_hex_to_int_empty_list():
    """Test empty hex list."""
    hex_list = []
    result = hex_to_int(hex_list)
    assert result == 0


def test_hex_to_int_eight_bytes():
    """Test full 8-byte conversion (common for CAN messages)."""
    hex_list = ['0E', '23', '6A', '93', '1E', 'DE', '81', '34']
    result = hex_to_int(hex_list)
    expected = int.from_bytes(bytes([0x0E, 0x23, 0x6A, 0x93, 0x1E, 0xDE, 0x81, 0x34]), byteorder='little')
    assert result == expected
