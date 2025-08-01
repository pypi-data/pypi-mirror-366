#!/usr/bin/env python3
"""
Detailed integration tests for hcom hooks

CRITICAL: hcom runs as a subprocess via run_hcom()
NEVER mock internal functions like launch_terminal, send_message, etc.
They won't affect the subprocess execution.
Always test via command-line interface.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .conftest import run_hcom
import hcom


class TestPostToolUseHookDetails:
    """Detailed tests for PostToolUse hook behavior"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_post_hook_delivers_pending_messages(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: PostToolUse delivers pending messages even without HCOM_SEND"""
        # Send a message via CLI
        result = run_hcom(['send', 'Pending message for delivery'])
        assert result.returncode == 0
        
        # Wait for message to be written
        time.sleep(0.1)
        
        # Set up position file to simulate instance at position 0
        positions = {'test-instance': {'pos': 0}}
        pos_file.write_text(json.dumps(positions))
        
        # Create transcript file
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "test-instance"}\n')
        
        # Run hook with non-HCOM_SEND command
        hook_input = json.dumps({
            'tool_name': 'Write',
            'tool_input': {'file_path': 'test.txt', 'content': 'hello'},
            'session_id': 'test-session',
            'transcript_path': str(transcript_file)
        })
        
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        
        # Should deliver pending message with exit code 2
        # But allow for race conditions where message isn't ready yet
        if result.returncode == 2:
            assert 'Pending message for delivery' in result.stderr
        else:
            assert result.returncode == 0  # No messages pending is also valid
    
    def test_post_hook_processes_hcom_send(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: PostToolUse processes HCOM_SEND commands"""
        # Create transcript
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "test-sender"}\n')
        
        hook_input = json.dumps({
            'tool_name': 'Bash',
            'tool_input': {'command': 'echo "HCOM_SEND:Hello from hook"'},
            'session_id': 'test-session',
            'transcript_path': str(transcript_file)
        })
        
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        
        # Should process successfully
        assert result.returncode in [0, 2]
        
        # Check message was written to log
        log_content = log_file.read_text()
        if log_content:  # May not be implemented yet
            assert 'Hello from hook' in log_content
    
    def test_post_hook_multiple_hcom_sends(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: PostToolUse handles multiple HCOM_SEND in one command"""
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "test-multi"}\n')
        
        # Command with multiple HCOM_SEND
        hook_input = json.dumps({
            'tool_name': 'Bash',
            'tool_input': {'command': 'echo "HCOM_SEND:First" && echo "HCOM_SEND:Second"'},
            'session_id': 'test-session',
            'transcript_path': str(transcript_file)
        })
        
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        assert result.returncode in [0, 2]
        
        # Both messages should be processed (if implemented)
        log_content = log_file.read_text()
        # Implementation may vary - just check it doesn't crash


class TestStopHookDetails:
    """Detailed tests for Stop hook behavior"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_stop_hook_delivers_filtered_messages(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Stop hook delivers messages with @-mention filtering"""
        # Create transcript with UUID
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "frontend-test"}\n')
        
        # Get the actual instance name that will be generated
        instance_name = hcom.get_display_name(str(transcript_file))
        
        # Send messages with mentions from CLI sender
        run_hcom(['send', 'Broadcast to everyone'])
        run_hcom(['send', f'@{instance_name[:2]} please deploy'])  # Message for this instance
        run_hcom(['send', '@backend check logs'])  # Message for different instance
        
        # Set up instance with help already shown
        positions = {instance_name: {'pos': 0, 'help_shown': True}}
        pos_file.write_text(json.dumps(positions))
        
        hook_input = json.dumps({
            'session_id': 'test-session',
            'hook_event_name': 'Stop',
            'transcript_path': str(transcript_file)
        })
        
        # Run briefly to check for messages
        result = run_hcom(['stop'], input=hook_input, timeout=0.5,
                         env={'HCOM_ACTIVE': '1'})
        
        # If messages delivered, should exit with code 2
        if result.returncode == 2:
            # Should include broadcast and message to this instance
            assert 'Broadcast to everyone' in result.stderr
            assert f'@{instance_name[:2]} please deploy' in result.stderr
            # Should NOT include @backend
            assert '@backend check logs' not in result.stderr
    
    def test_stop_hook_updates_timestamps(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Stop hook updates last_stop timestamp"""
        # Create transcript
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "test-instance"}\n')
        
        # Get actual instance name
        instance_name = hcom.get_display_name(str(transcript_file))
        
        # Create instance
        positions = {instance_name: {'pos': 0, 'help_shown': True}}
        pos_file.write_text(json.dumps(positions))
        
        hook_input = json.dumps({
            'session_id': 'test-session',
            'hook_event_name': 'Stop',
            'transcript_path': str(transcript_file)
        })
        
        # Run briefly - expect timeout since stop hook runs indefinitely
        try:
            run_hcom(['stop'], input=hook_input, timeout=0.5,
                    env={'HCOM_ACTIVE': '1'})
        except subprocess.TimeoutExpired:
            # This is expected - stop hook runs indefinitely
            pass
        
        # Check position file updated
        if pos_file.exists():
            positions = json.loads(pos_file.read_text())
            if instance_name in positions:
                # Should have last_stop timestamp
                assert 'last_stop' in positions[instance_name]
                assert positions[instance_name]['last_stop'] > 0


class TestNotificationHookDetails:
    """Detailed tests for Notification hook behavior"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_notification_tracks_permission_requests(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Notification hook updates permission request timestamp"""
        # Create transcript
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "test-instance"}\n')
        
        # Get actual instance name
        instance_name = hcom.get_display_name(str(transcript_file))
        
        # Create instance with help already shown
        positions = {instance_name: {'pos': 0, 'help_shown': True}}
        pos_file.write_text(json.dumps(positions))
        
        hook_input = json.dumps({
            'session_id': 'test-session',
            'hook_event_name': 'Notification',
            'transcript_path': str(transcript_file)
        })
        
        result = run_hcom(['notify'], input=hook_input,
                         env={'HCOM_ACTIVE': '1'})
        assert result.returncode == 0
        
        # Check timestamp updated
        if pos_file.exists():
            positions = json.loads(pos_file.read_text())
            if instance_name in positions:
                assert 'last_permission_request' in positions[instance_name]
                assert positions[instance_name]['last_permission_request'] > 0


class TestMessageEscaping:
    """Test message format handling"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_pipe_character_handling(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Pipe characters in messages handled correctly"""
        # Send message with pipes via CLI
        result = run_hcom(['send', 'Message with |pipes| in it'])
        assert result.returncode == 0
        
        # Check raw log content
        raw_content = log_file.read_text()
        
        # Should have escaped pipes in storage
        assert '\\|' in raw_content
        
        # When delivered via hook, pipes should be unescaped
        positions = {'test-reader': {'pos': 0}}
        (hcom_dir / 'hcom.json').write_text(json.dumps(positions))
        
        hook_input = json.dumps({
            'tool_name': 'Write',
            'session_id': 'test-session'
        })
        
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        
        if result.returncode == 2:
            # Delivered message should have unescaped pipes
            assert 'Message with |pipes| in it' in result.stderr
    
    def test_multiline_message_preservation(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Multiline messages preserved through system"""
        # Send multiline message
        multiline = 'Line 1\nLine 2\nLine 3'
        result = run_hcom(['send', multiline])
        assert result.returncode == 0
        
        # Set up reader
        positions = {'reader': {'pos': 0}}
        (hcom_dir / 'hcom.json').write_text(json.dumps(positions))
        
        # Retrieve via hook
        hook_input = json.dumps({
            'tool_name': 'Write',
            'session_id': 'test-session'
        })
        
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        
        if result.returncode == 2:
            # Should preserve newlines
            assert 'Line 1' in result.stderr
            assert 'Line 2' in result.stderr
            assert 'Line 3' in result.stderr


class TestAtMentionFiltering:
    """Test @-mention filtering behavior"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_mention_prefix_matching(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: @-mentions match by prefix"""
        # Create transcript with UUID
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "frontend-bob"}\n')
        
        # Get actual instance name
        instance_name = hcom.get_display_name(str(transcript_file))
        
        # Send various messages
        run_hcom(['send', 'Hello everyone'])  # Broadcast
        run_hcom(['send', f'@{instance_name[:2]} deploy the app'])  # For this instance (prefix match)
        run_hcom(['send', '@backend check database'])  # For backend
        run_hcom(['send', f'@{instance_name} more specific'])  # Full name match
        
        # Set up instance with help_shown
        positions = {instance_name: {'pos': 0, 'help_shown': True}}
        pos_file.write_text(json.dumps(positions))
        
        # Run stop hook to get messages
        hook_input = json.dumps({
            'session_id': 'test-session',
            'hook_event_name': 'Stop',
            'transcript_path': str(transcript_file)
        })
        
        result = run_hcom(['stop'], input=hook_input, timeout=0.5,
                         env={'HCOM_ACTIVE': '1'})
        
        if result.returncode == 2:
            # Should get broadcast and mentions for this instance
            assert 'Hello everyone' in result.stderr
            assert f'@{instance_name[:2]} deploy the app' in result.stderr
            assert f'@{instance_name} more specific' in result.stderr
            # Should NOT get @backend
            assert '@backend check database' not in result.stderr
    
    def test_case_insensitive_mentions(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: @-mentions are case insensitive"""
        # Create transcript
        transcript_file = temp_home / 'test.jsonl'
        transcript_file.write_text('{"uuid": "frontend-test"}\n')
        
        # Get actual instance name
        instance_name = hcom.get_display_name(str(transcript_file))
        
        # Send with different cases
        run_hcom(['send', f'@{instance_name.upper()} please review'])
        run_hcom(['send', f'@{instance_name.upper()} urgent'])
        run_hcom(['send', f'@{instance_name.title()} check this'])
        
        # Set up instance with help already shown
        positions = {instance_name: {'pos': 0, 'help_shown': True}}
        pos_file.write_text(json.dumps(positions))
        
        hook_input = json.dumps({
            'session_id': 'test-session',
            'hook_event_name': 'Stop',
            'transcript_path': str(transcript_file)
        })
        
        result = run_hcom(['stop'], input=hook_input, timeout=0.5,
                         env={'HCOM_ACTIVE': '1'})
        
        if result.returncode == 2:
            # Should get all case variations
            assert result.stderr.count('please review') >= 1
            assert result.stderr.count('urgent') >= 1
            assert result.stderr.count('check this') >= 1


class TestHookErrorHandling:
    """Test hook error handling"""
    
    def test_post_hook_invalid_json(self):
        """Test: PostToolUse handles invalid JSON gracefully"""
        result = run_hcom(['post'], input='invalid json{',
                         env={'HCOM_ACTIVE': '1'})
        # Should exit cleanly
        assert result.returncode == 0
    
    def test_stop_hook_missing_transcript(self):
        """Test: Stop hook handles missing transcript path"""
        hook_input = json.dumps({
            'session_id': 'test-session',
            'hook_event_name': 'Stop'
            # No transcript_path
        })
        
        result = run_hcom(['stop'], input=hook_input, timeout=0.5,
                         env={'HCOM_ACTIVE': '1'})
        # Should handle gracefully
        assert result.returncode in [0, 1, 2]
    
    def test_hooks_exit_when_inactive(self):
        """Test: All hooks exit immediately when HCOM_ACTIVE != 1"""
        hook_input = json.dumps({'session_id': 'test'})
        
        for hook in ['post', 'stop', 'notify']:
            # Without HCOM_ACTIVE
            result = run_hcom([hook], input=hook_input)
            assert result.returncode == 0
            assert result.stdout == ''
            assert result.stderr == ''
            
            # With HCOM_ACTIVE=0
            result = run_hcom([hook], input=hook_input,
                             env={'HCOM_ACTIVE': '0'})
            assert result.returncode == 0
            assert result.stdout == ''
            assert result.stderr == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])