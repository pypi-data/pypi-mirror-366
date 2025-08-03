import pytest
from unittest.mock import patch, mock_open
from j1939parser.core import is_raspberry_pi


def test_is_raspberry_pi_true():
    """Test detection of Raspberry Pi when cpuinfo contains 'Raspberry Pi'."""
    mock_content = "processor\t: 0\nmodel name\t: ARMv7 Processor rev 4 (v7l)\nBogoMIPS\t: 38.40\nFeatures\t: half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae evtstrm crc32\nCPU implementer\t: 0x41\nCPU architecture: 7\nCPU variant\t: 0x0\nCPU part\t: 0xd08\nCPU revision\t: 3\n\nHardware\t: BCM2835\nRevision\t: a020d3\nSerial\t\t: 00000000b827eb8e\nModel\t\t: Raspberry Pi 3 Model B Plus Rev 1.3\n"
    
    with patch("builtins.open", mock_open(read_data=mock_content)):
        assert is_raspberry_pi() == True


def test_is_raspberry_pi_false():
    """Test detection when cpuinfo doesn't contain 'Raspberry Pi'."""
    mock_content = "processor\t: 0\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 142\nmodel name\t: Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz\n"
    
    with patch("builtins.open", mock_open(read_data=mock_content)):
        assert is_raspberry_pi() == False


def test_is_raspberry_pi_file_not_found():
    """Test behavior when /proc/cpuinfo doesn't exist (e.g., on macOS/Windows)."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert is_raspberry_pi() == False


def test_is_raspberry_pi_permission_error():
    """Test behavior when /proc/cpuinfo can't be read due to permissions."""
    with patch("builtins.open", side_effect=PermissionError):
        assert is_raspberry_pi() == False


def test_is_raspberry_pi_other_exception():
    """Test behavior when other exceptions occur."""
    with patch("builtins.open", side_effect=IOError("Unexpected error")):
        assert is_raspberry_pi() == False
