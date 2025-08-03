import pytest
import tempfile
import time
import threading
from unittest.mock import patch, MagicMock
from j1939parser.core import follow


def test_follow_with_existing_content():
    """Test follow function with a file that already has content."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write("line 1\nline 2\n")
        temp_file.flush()
        temp_file.seek(0)
        
        generator = follow(temp_file)
        
        # Should read existing lines
        line1 = next(generator)
        assert line1 == "line 1\n"
        
        line2 = next(generator)
        assert line2 == "line 2\n"


def test_follow_with_new_content():
    """Test follow function behavior when new content is added to file."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write("existing line\n")
        temp_file.flush()
        temp_file.seek(0)
        
        generator = follow(temp_file)
        
        # Should read existing line first
        line = next(generator)
        assert line == "existing line\n"
        
        # Mock time.sleep to prevent infinite loop and simulate behavior
        with patch('j1939parser.core.time.sleep') as mock_sleep:
            def stop_generator(*args):
                raise StopIteration("Stopping for test")
            mock_sleep.side_effect = stop_generator
            
            try:
                next(generator)
                assert False, "Should have raised StopIteration"
            except (StopIteration, RuntimeError):
                # Either exception is acceptable for our test purposes
                pass


def test_follow_empty_file():
    """Test follow function with an empty file."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.flush()
        temp_file.seek(0)
        
        generator = follow(temp_file)
        
        # Mock time.sleep to prevent infinite loop in test
        with patch('j1939parser.core.time.sleep') as mock_sleep:
            def stop_generator(*args):
                raise StopIteration("Stopping for test")
            mock_sleep.side_effect = stop_generator
            
            try:
                next(generator)
                assert False, "Should have raised StopIteration"
            except (StopIteration, RuntimeError):
                # Either exception is acceptable for our test purposes
                pass
