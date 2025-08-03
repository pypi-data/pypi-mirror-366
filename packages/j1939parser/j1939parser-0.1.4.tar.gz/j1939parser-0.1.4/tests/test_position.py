from j1939parser.core import parse_vehicle_position

def test_parse_valid_position():
    """
    Test known good input for PGN 65267 (Vehicle Position)
    """
    data_bytes = ['0E', '23', '6A', '93', '1E', 'DE', '81', '34']
    result = parse_vehicle_position(data_bytes)
    
    assert result is not None, "Expected valid position, got None"
    
    lat, lon = result
    assert abs(lat - 37.3206542) < 1e-6, f"Latitude incorrect: {lat}"
    assert abs(lon - (-121.9073762)) < 1e-6, f"Longitude incorrect: {lon}"

def test_parse_invalid_length():
    """
    Should return None if data bytes are not exactly 8
    """
    data_bytes = ['01', '02', '03']  # too short
    assert parse_vehicle_position(data_bytes) is None

def test_parse_all_ff_bytes():
    """
    All 0xFF bytes should decode to max float values, outside valid range
    """
    data_bytes = ['FF'] * 8
    lat, lon = parse_vehicle_position(data_bytes)
    assert lat > 90 or lat < -90, "Latitude should be out of range for all 0xFF"
    assert lon > 180 or lon < -180, "Longitude should be out of range for all 0xFF"
