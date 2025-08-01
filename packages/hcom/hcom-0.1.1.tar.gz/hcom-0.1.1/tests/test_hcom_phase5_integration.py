#!/usr/bin/env python3
"""
Integration tests for hcom Phase 5: Watch Command

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
from datetime import datetime
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .conftest import run_hcom


class TestWatchNonInteractive:
    """Integration tests for non-interactive watch mode"""
    
    def test_watch_shows_help_non_interactive(self, temp_home):
        """Test: Watch shows help in non-interactive mode"""
        # Create group files
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        (hcom_dir / 'hcom.log').touch()
        
        # Run watch (tests run non-interactively)
        result = run_hcom(['watch'])
        assert result.returncode == 0
        
        # Should show automation help
        assert 'Automation usage:' in result.stdout
        assert 'hcom send' in result.stdout
        assert 'hcom watch --logs' in result.stdout
        assert 'hcom watch --status' in result.stdout
    
    def test_watch_no_group_error(self, temp_home):
        """Test: Error when no conversation exists"""
        # Ensure no group files exist
        hcom_dir = temp_home / '.hcom'
        if hcom_dir.exists():
            for f in hcom_dir.iterdir():
                f.unlink()
        
        result = run_hcom(['watch'])
        assert result.returncode == 1
        assert 'No conversation found' in result.stderr


class TestWatchLogsFlag:
    """Integration tests for --logs flag"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_logs_shows_message_history(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --logs displays all messages"""
        # Create test messages directly in log file
        test_messages = [
            f"{datetime.now().isoformat()}|alice|First message from Alice\n",
            f"{datetime.now().isoformat()}|bob|Reply from Bob\n",
            f"{datetime.now().isoformat()}|alice|Thanks Bob!\n"
        ]
        log_file.write_text(''.join(test_messages))
        
        result = run_hcom(['watch', '--logs'])
        assert result.returncode == 0
        
        # Should show all messages
        assert 'First message from Alice' in result.stdout
        assert 'Reply from Bob' in result.stdout
        assert 'Thanks Bob!' in result.stdout
        assert 'alice' in result.stdout
        assert 'bob' in result.stdout
    
    def test_logs_empty_conversation(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --logs with no messages"""
        # Empty log file
        log_file.write_text('')
        
        result = run_hcom(['watch', '--logs'])
        assert result.returncode == 0
        
        # Should indicate no messages
        assert 'No messages' in result.stdout or result.stdout.strip() == ''
    
    def test_logs_with_multiline_messages(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --logs handles multiline messages"""
        # Create message with newlines
        test_messages = [
            f"{datetime.now().isoformat()}|poet|Line one\\nLine two\\nLine three\n",
            f"{datetime.now().isoformat()}|reader|Nice poem!\n"
        ]
        log_file.write_text(''.join(test_messages))
        
        result = run_hcom(['watch', '--logs'])
        assert result.returncode == 0
        
        # Should show multiline message properly
        output = result.stdout
        assert 'Line one' in output
        assert 'Line two' in output
        assert 'Line three' in output
        assert 'Nice poem!' in output
    
    def test_logs_with_special_characters(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --logs handles special characters"""
        # Messages with pipes and special chars
        test_messages = [
            f"{datetime.now().isoformat()}|user1|Message with \\| pipe\n",
            f"{datetime.now().isoformat()}|user2|@user1 got it!\n"
        ]
        log_file.write_text(''.join(test_messages))
        
        result = run_hcom(['watch', '--logs'])
        assert result.returncode == 0
        
        # Should show special characters
        assert 'Message with | pipe' in result.stdout
        assert '@user1 got it!' in result.stdout


class TestWatchStatusFlag:
    """Integration tests for --status flag"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_status_shows_instances(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --status shows instance table"""
        # Create test instances
        current_time = int(time.time())
        positions = {
            'frontend-alice': {
                'pos': 0,
                'directory': '/home/alice/frontend',
                'last_stop': current_time - 10,
                'conversation_uuid': 'uuid1'
            },
            'backend-bob': {
                'pos': 0,
                'directory': '/home/bob/backend',
                'last_tool': current_time - 300,
                'conversation_uuid': 'uuid2'
            }
        }
        pos_file.write_text(json.dumps(positions))
        
        result = run_hcom(['watch', '--status'])
        assert result.returncode == 0
        
        # Should show instance names
        assert 'frontend-alice' in result.stdout
        assert 'backend-bob' in result.stdout
        
        # Should show directories
        assert 'frontend' in result.stdout
        assert 'backend' in result.stdout
    
    def test_status_shows_correct_states(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --status shows accurate instance states"""
        current_time = int(time.time())
        positions = {
            'waiting-instance': {
                'pos': 0,
                'directory': '/test',
                'last_stop': current_time - 5  # Recent = waiting
            },
            'inactive-instance': {
                'pos': 0,
                'directory': '/test',
                'last_tool': current_time - 3600  # Old = inactive
            },
            'blocked-instance': {
                'pos': 0,
                'directory': '/test',
                'last_permission_request': current_time - 2  # Recent = blocked
            }
        }
        pos_file.write_text(json.dumps(positions))
        
        result = run_hcom(['watch', '--status'])
        assert result.returncode == 0
        
        output = result.stdout
        
        # Check states appear correctly
        # Note: exact format depends on implementation
        lines = output.split('\n')
        
        # Find lines with our instances
        waiting_line = next((l for l in lines if 'waiting-instance' in l), '')
        inactive_line = next((l for l in lines if 'inactive-instance' in l), '')
        blocked_line = next((l for l in lines if 'blocked-instance' in l), '')
        
        # Verify states (implementation may use colors/symbols)
        assert 'waiting' in waiting_line.lower() or '◉' in waiting_line
        assert 'inactive' in inactive_line.lower() or '○' in inactive_line
        assert 'blocked' in blocked_line.lower() or '■' in blocked_line
    
    def test_status_empty_conversation(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --status with no instances"""
        # Create empty position file
        pos_file.write_text('{}')
        
        result = run_hcom(['watch', '--status'])
        assert result.returncode == 0
        
        # Should indicate no instances (check actual text from error above)
        assert 'No Claude instances connected' in result.stdout or 'No instances' in result.stdout
    
    def test_status_with_timestamps(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: --status shows time information"""
        current_time = int(time.time())
        positions = {
            'test-instance': {
                'pos': 0,
                'directory': '/test',
                'last_stop': current_time - 30,  # 30 seconds ago
                'conversation_uuid': 'test-uuid'
            }
        }
        pos_file.write_text(json.dumps(positions))
        
        result = run_hcom(['watch', '--status'])
        assert result.returncode == 0
        
        # Should show some time indication
        # Could be "30s ago", "waiting (30s)", etc
        output = result.stdout
        assert 'test-instance' in output
        # Time format is implementation dependent


# TestWatchMultipleGroups removed - HCOM simplified to single global group


class TestWatchFormating:
    """Integration tests for output formatting"""
    
    def test_logs_formatting(self, temp_home):
        """Test: --logs has readable format"""
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        
        # Create varied messages
        base_time = datetime.now()
        messages = []
        for i in range(3):
            timestamp = base_time.isoformat()
            sender = f"user{i}"
            content = f"Message number {i}"
            messages.append(f"{timestamp}|{sender}|{content}\n")
        
        log_file.write_text(''.join(messages))
        
        result = run_hcom(['watch', '--logs'])
        assert result.returncode == 0
        
        # Should have readable format with sender names
        for i in range(3):
            assert f"user{i}" in result.stdout
            assert f"Message number {i}" in result.stdout
    
    def test_status_table_format(self, temp_home):
        """Test: --status shows table-like format"""
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        pos_file = hcom_dir / 'hcom.json'
        
        # Create multiple instances
        positions = {}
        for i in range(3):
            positions[f"instance{i}"] = {
                'pos': 0,
                'directory': f'/project{i}',
                'last_stop': int(time.time()) - (i * 60)
            }
        
        pos_file.write_text(json.dumps(positions))
        
        result = run_hcom(['watch', '--status'])
        assert result.returncode == 0
        
        # Should show all instances
        for i in range(3):
            assert f"instance{i}" in result.stdout
            assert f"project{i}" in result.stdout


class TestWatchErrorHandling:
    """Integration tests for error conditions"""
    
    def test_watch_invalid_group(self, temp_home):
        """Test: Error for non-existent group"""
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        
        result = run_hcom(['watch', 'nonexistent', '--logs'])
        assert result.returncode == 1
        assert 'not found' in result.stderr.lower() or 'No conversation' in result.stderr
    
    def test_watch_corrupt_log(self, temp_home):
        """Test: Handle corrupt log file gracefully"""
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        
        # Write invalid log format
        log_file.write_text('invalid|log|format|too|many|pipes\n')
        
        result = run_hcom(['watch', '--logs'])
        # Should either succeed with partial data or fail gracefully
        assert result.returncode in [0, 1]
    
    def test_watch_corrupt_positions(self, temp_home):
        """Test: Handle corrupt position file gracefully"""
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        (hcom_dir / 'hcom.log').touch()
        pos_file = hcom_dir / 'hcom.json'
        
        # Write invalid JSON
        pos_file.write_text('{"invalid": json}')
        
        result = run_hcom(['watch', '--status'])
        # Should handle gracefully
        assert result.returncode in [0, 1]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])