#!/usr/bin/env python3
"""
Integration tests for hcom (Hook Communications)
These tests use ONLY subprocess calls via run_hcom().
DO NOT import hcom or call its functions directly.

CRITICAL: hcom runs as a subprocess via run_hcom()
NEVER mock internal functions like launch_terminal, send_message, etc.
They won't affect the subprocess execution.
Always test via command-line interface.
"""

import os
import sys
import json
import time
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .conftest import run_hcom
import hcom


class TestCommandRouting:
    """Integration tests for command routing"""
    
    def test_help_command_succeeds(self):
        """Test: help command returns 0"""
        result = run_hcom(['help'])
        assert result.returncode == 0
        assert 'hcom - Hook Communications' in result.stdout
    
    def test_no_args_shows_help(self):
        """Test: No arguments shows help"""
        result = run_hcom([])
        assert result.returncode == 0
        assert 'hcom - Hook Communications' in result.stdout
    
    def test_invalid_command_fails(self):
        """Test: Invalid command returns error"""
        result = run_hcom(['invalid'])
        assert result.returncode == 1
        assert 'Error' in result.stderr


class TestSendCommand:
    """Integration tests for send command"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_send_basic_message(self, temp_home):
        """Test: Can send a basic message"""
        # Create conversation first
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        log_file.touch()
        
        result = run_hcom(['send', 'Hello world'])
        assert result.returncode == 0
        assert 'Message sent' in result.stdout
        
        # Verify message is in log
        assert 'Hello world' in log_file.read_text()
    
    def test_send_requires_message(self):
        """Test: Send command requires a message"""
        result = run_hcom(['send'])
        assert result.returncode == 1
        assert 'Error: Message required' in result.stderr
    
    def test_send_no_group_error(self, temp_home):
        """Test: Error when no conversation exists"""
        # Remove the log file
        log_file = temp_home / '.hcom/hcom.log'
        if log_file.exists():
            log_file.unlink()
        
        result = run_hcom(['send', 'test'])
        assert result.returncode == 1
        assert 'No conversation found' in result.stderr
    
    def test_send_uses_cli_sender(self, temp_home):
        """Test: CLI sends use configured sender name"""
        # Create conversation first
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        log_file.touch()
        
        run_hcom(['send', 'From CLI'])
        
        content = log_file.read_text()
        # Default sender is 'bigboss'
        assert '|bigboss|From CLI' in content


class TestHookActivation:
    """Integration tests for hook activation"""
    
    def test_hooks_inactive_by_default(self):
        """Test: Hooks exit silently when HCOM_ACTIVE != '1'"""
        for hook in ['post', 'stop', 'notify']:
            # Without HCOM_ACTIVE
            result = run_hcom([hook])
            assert result.returncode == 0
            assert result.stdout == ''
            assert result.stderr == ''
            
            # With HCOM_ACTIVE=0
            result = run_hcom([hook], env={'HCOM_ACTIVE': '0'})
            assert result.returncode == 0
            assert result.stdout == ''
            assert result.stderr == ''
    
    def test_hooks_process_when_active(self):
        """Test: Hooks process input when HCOM_ACTIVE=1"""
        hook_input = json.dumps({
            'hook_event_name': 'PostToolUse',
            'tool_name': 'Write',
            'session_id': 'test-session'
        })
        
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        # Should process without error
        assert result.returncode in [0, 2]  # 0 = success, 2 = message delivery


class TestMessageRoundtrip:
    """Integration tests for complete message flow"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_send_and_retrieve_via_hook(self, temp_home):
        """Test: Messages sent via CLI can trigger hook delivery"""
        # Set up hcom files first
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        pos_file.write_text('{}')
        
        # Send a message
        result = run_hcom(['send', 'Test message for hooks'])
        assert result.returncode == 0
        
        # Create transcript file with UUID
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "test-uuid-123"}\n')
        
        # Get the actual instance name from the algorithm
        instance_name = hcom.get_display_name(str(transcript_file))
        
        # Set up position file to simulate a Claude instance
        pos_file = temp_home / '.hcom/hcom.json'
        positions = {instance_name: {'pos': 0, 'help_shown': True}}
        pos_file.write_text(json.dumps(positions))
        
        # Run post hook - should deliver the message
        hook_input = json.dumps({
            'tool_name': 'Write',
            'session_id': 'test-session',
            'transcript_path': str(transcript_file)
        })
        
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        
        # Should exit with code 2 (message delivery)
        assert result.returncode == 2
        assert 'Test message for hooks' in result.stderr


class TestOpenCommand:
    """Integration tests for open command"""
    
    def test_open_requires_setup(self, temp_home):
        """Test: Open command sets up necessary files"""
        # Configure to show commands instead of launching terminals
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open'])
        
        # Should succeed and show launch command
        assert result.returncode == 0
        assert 'claude' in result.stdout.lower()
    
    def test_open_with_count(self, temp_home):
        """Test: Can specify number of instances"""
        # Configure to show commands
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '3'])
        assert result.returncode == 0
        
        # Should show 3 commands
        assert result.stdout.count('claude') == 3


class TestWatchCommand:
    """Integration tests for watch command"""
    
    def test_watch_non_interactive(self, temp_home):
        """Test: Watch shows help in non-interactive mode"""
        # Create group
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        (hcom_dir / 'hcom.log').touch()
        
        # Run watch (non-interactive in tests)
        result = run_hcom(['watch'])
        assert result.returncode == 0
        assert 'Automation usage:' in result.stdout
    
    def test_watch_logs_flag(self, temp_home):
        """Test: --logs shows message history"""
        # Set up test messages
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        
        # Write test messages directly
        test_messages = [
            f"{time.time()}|test1|First message\n",
            f"{time.time()}|test2|Second message\n"
        ]
        log_file.write_text(''.join(test_messages))
        
        result = run_hcom(['watch', '--logs'])
        assert result.returncode == 0
        assert 'First message' in result.stdout
        assert 'Second message' in result.stdout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])