#!/usr/bin/env python3
"""
Unit tests for hcom (Hook Communications)
These tests directly call hcom functions for testing internal logic.
DO NOT mix these with subprocess/integration tests.
"""

import os
import sys
import json
import tempfile
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime
import pytest

# Add parent directory to path to import hcom
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hcom


class TestFileSystemUtils:
    """Unit tests for file system utilities"""
    
    def test_get_hcom_dir(self):
        """Test: get_hcom_dir returns correct path"""
        assert hcom.get_hcom_dir() == Path.home() / '.hcom'
    
    def test_atomic_write(self, temp_home):
        """Test: atomic_write creates file safely"""
        hcom.ensure_hcom_dir()
        test_file = hcom.get_hcom_dir() / 'test.txt'
        
        hcom.atomic_write(test_file, 'test content')
        assert test_file.exists()
        assert test_file.read_text() == 'test content'
    
    def test_atomic_write_concurrent(self, temp_home):
        """Test: atomic_write prevents corruption under concurrent access"""
        hcom.ensure_hcom_dir()
        test_file = hcom.get_hcom_dir() / 'concurrent_test.txt'
        
        # Use longer content to increase chance of detecting corruption
        def write_pattern(n):
            # Write a pattern that would show corruption if interleaved
            pattern = f"{n}" * 1000
            hcom.atomic_write(test_file, pattern)
        
        # Start multiple threads writing different patterns
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_pattern, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # File should contain exactly one pattern (no interleaving)
        content = test_file.read_text()
        assert len(content) == 1000
        # All characters should be the same digit
        first_char = content[0]
        assert all(c == first_char for c in content)
        assert first_char.isdigit()


class TestMessageValidation:
    """Unit tests for message validation"""
    
    def test_valid_messages(self):
        """Test: Valid messages pass validation"""
        assert hcom.validate_message("Hello") is None
        assert hcom.validate_message("Multi\nline\nmessage") is None
        assert hcom.validate_message("With |pipes| and special chars!") is None
        assert hcom.validate_message("x" * 4096) is None  # Max size
    
    def test_message_too_large(self):
        """Test: Size limit enforced"""
        assert hcom.validate_message("x" * 4097) == "Error: Message too large (max 4096 chars)"
    
    def test_empty_message(self):
        """Test: Empty message rejected"""
        assert hcom.validate_message("") == "Error: Message required"
        assert hcom.validate_message("   ") == "Error: Message required"  # Whitespace only


class TestMessageParsing:
    """Unit tests for message parsing and delivery logic"""
    
    def test_should_deliver_broadcast(self):
        """Test: No @ = broadcast to all"""
        msg = {'message': 'Hello everyone'}
        assert hcom.should_deliver_message(msg, 'hovoa7') is True
        assert hcom.should_deliver_message(msg, 'mivob8') is True
        assert hcom.should_deliver_message(msg, 'anyone') is True
    
    def test_should_deliver_mention(self):
        """Test: @mention matches prefix"""
        msg = {'message': '@hov please check this'}
        assert hcom.should_deliver_message(msg, 'hovoa7') is True
        assert hcom.should_deliver_message(msg, 'hovoa8') is True
        assert hcom.should_deliver_message(msg, 'mivob8') is False
    
    def test_should_deliver_multiple_mentions(self):
        """Test: Multiple mentions"""
        msg = {'message': '@hov @miv meeting in 5 minutes'}
        assert hcom.should_deliver_message(msg, 'hovoa7') is True
        assert hcom.should_deliver_message(msg, 'mivob8') is True
        assert hcom.should_deliver_message(msg, 'other') is False


class TestConfiguration:
    """Unit tests for configuration loading"""
    
    def test_default_config_structure(self):
        """Test: Default config has expected structure"""
        # Force reload
        hcom._config = None
        config = hcom.get_cached_config()
        
        # Verify config has expected structure
        assert isinstance(config, dict)
        assert 'terminal_command' in config
        assert 'initial_prompt' in config
        assert 'env_overrides' in config
        assert isinstance(config['env_overrides'], dict)
        
        # Verify defaults are sensible (not testing exact values)
        assert config.get('wait_timeout', 0) > 0
        assert config.get('max_message_size', 0) > 0
        assert len(config.get('sender_name', '')) > 0


class TestDirectMessageOperations:
    """Unit tests for message send/receive functions"""
    
    def setup_method(self):
        """Clean up before each test"""
        hcom.ensure_hcom_dir()
        log_file = hcom.get_hcom_dir() / 'hcom.log'
        pos_file = hcom.get_hcom_dir() / 'hcom.json'
        if log_file.exists():
            log_file.unlink()
        if pos_file.exists():
            pos_file.unlink()
    
    def test_send_and_parse_messages(self, temp_home):
        """Test: Can send and parse messages correctly"""
        # Send a message
        hcom.send_message('sender1', 'Test message')
        
        # Parse it back
        messages = hcom.parse_log_messages(hcom.get_hcom_dir() / 'hcom.log')
        assert len(messages) > 0
        
        # Check the actual message content
        sent_message = messages[-1]
        assert sent_message['from'] == 'sender1'
        assert sent_message['message'] == 'Test message'
        assert 'timestamp' in sent_message
    
    def test_message_position_tracking(self, temp_home):
        """Test: Position tracking for message retrieval"""
        # Send a message
        hcom.send_message('sender', 'Test message')
        
        # First retrieval should get the message
        messages1 = hcom.get_new_messages('receiver')
        assert len(messages1) == 1
        assert messages1[0]['message'] == 'Test message'
        
        # Second retrieval should get nothing (position advanced)
        messages2 = hcom.get_new_messages('receiver')
        assert len(messages2) == 0
    
    def test_own_messages_filtered(self, temp_home):
        """Test: Instances don't receive their own messages"""
        # Send message from 'sender'
        hcom.send_message('sender', 'My message')
        
        # Sender shouldn't get own message
        messages = hcom.get_new_messages('sender')
        assert len(messages) == 0
        
        # Others should get it
        messages = hcom.get_new_messages('receiver')
        assert len(messages) == 1
        assert messages[0]['message'] == 'My message'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])