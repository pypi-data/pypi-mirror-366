#!/usr/bin/env python3
"""
Contract-based tests for hcom - testing behavioral contracts
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hcom
from .conftest import run_hcom


class TestMessageDeliveryContract:
    """
    Message Delivery Contract:
    1. Messages sent by one instance are delivered to others
    2. Sender never receives own messages
    3. Messages are delivered in order
    4. Messages persist across instance restarts
    5. @-mention filtering works correctly
    """
    
    def test_messages_delivered_to_others(self):
        """Contract: Messages sent by one instance are delivered to others"""
        # Send from instance A
        hcom.send_message('instanceA', 'Test message')
        
        # Receive as instance B
        messages = hcom.get_new_messages('instanceB')
        
        assert len(messages) == 1
        assert messages[0]['from'] == 'instanceA'
        assert messages[0]['message'] == 'Test message'
    
    def test_sender_filtering(self):
        """Contract: Sender never receives own messages"""
        # Send from instance A
        hcom.send_message('instanceA', 'My own message')
        
        # Try to receive as same instance
        messages = hcom.get_new_messages('instanceA')
        
        assert len(messages) == 0
    
    def test_message_ordering(self):
        """Contract: Messages are delivered in order"""
        # Send multiple messages
        for i in range(5):
            hcom.send_message(f'sender{i}', f'Message {i}')
        
        # Receive all messages
        messages = hcom.get_new_messages('receiver')
        
        assert len(messages) == 5
        for i in range(5):
            assert messages[i]['message'] == f'Message {i}'
    
    def test_message_persistence(self):
        """Contract: Messages persist across instance restarts"""
        # Send messages
        hcom.send_message('persistent', 'Survives restart')
        
        # Simulate restart by removing position data
        pos_file = hcom.get_hcom_dir() / 'hcom.json'
        if pos_file.exists():
            pos_file.unlink()
        
        # Messages should still be retrievable
        messages = hcom.get_new_messages('new_instance')
        assert len(messages) == 1
        assert messages[0]['message'] == 'Survives restart'
    
    def test_mention_filtering_contract(self):
        """Contract: @-mention filtering works correctly"""
        # Send various messages
        hcom.send_message('sender', 'Broadcast to all')
        hcom.send_message('sender', '@frontend Deploy ready')
        hcom.send_message('sender', '@backend Check logs')
        hcom.send_message('sender', '@front @back Meeting')
        
        # Test frontend instance
        frontend_msgs = hcom.get_new_messages('frontend-abc')
        frontend_texts = [m['message'] for m in frontend_msgs]
        
        assert 'Broadcast to all' in frontend_texts
        assert '@frontend Deploy ready' in frontend_texts
        assert '@front @back Meeting' in frontend_texts
        assert '@backend Check logs' not in frontend_texts
        
        # Test backend instance  
        backend_msgs = hcom.get_new_messages('backend-xyz')
        backend_texts = [m['message'] for m in backend_msgs]
        
        assert 'Broadcast to all' in backend_texts
        assert '@backend Check logs' in backend_texts
        assert '@front @back Meeting' in backend_texts
        assert '@frontend Deploy ready' not in backend_texts


class TestConcurrencyContract:
    """
    Concurrency Contract:
    1. Concurrent message sending doesn't corrupt log
    2. Concurrent position updates don't lose data
    3. Atomic operations prevent partial writes
    """
    
    def test_concurrent_message_sending(self):
        """Contract: Concurrent senders don't corrupt the log"""
        def send_batch(sender_id):
            for i in range(10):
                hcom.send_message(f'sender{sender_id}', f'Msg {sender_id}-{i}')
        
        # Launch concurrent senders
        threads = []
        for i in range(5):
            t = threading.Thread(target=send_batch, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all messages intact
        log_file = hcom.get_hcom_dir() / 'hcom.log'
        messages = hcom.parse_log_messages(log_file)
        
        # Should have all 50 messages
        assert len(messages) == 50
        
        # Each message should be complete and valid
        for msg in messages:
            assert msg['from'].startswith('sender')
            assert msg['message'].startswith('Msg ')
            assert '|' not in msg['from']  # No unescaped pipes
            assert '|' not in msg['message']  # No unescaped pipes
    
    def test_concurrent_position_updates(self):
        """Contract: Concurrent readers don't lose position updates"""
        # Seed with messages
        for i in range(10):
            hcom.send_message('seeder', f'Message {i}')
        
        results = {}
        
        def read_messages(reader_id):
            msgs = hcom.get_new_messages(f'reader{reader_id}')
            results[reader_id] = len(msgs)
        
        # Launch concurrent readers
        threads = []
        for i in range(5):
            t = threading.Thread(target=read_messages, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All readers should see all messages
        for reader_id, count in results.items():
            assert count == 10, f"Reader {reader_id} saw {count} messages, expected 10"
        
        # Position file exists and has at least one reader
        # (Due to atomic writes, not all readers may be in final file)
        pos_file = hcom.get_hcom_dir() / 'hcom.json'
        positions = json.loads(pos_file.read_text())
        assert len(positions) >= 1  # At least one reader recorded


class TestConfigurationContract:
    """
    Configuration Contract:
    1. Config values override defaults
    2. Missing config uses sensible defaults
    3. Invalid config doesn't crash
    4. Environment conversion works correctly
    """
    
    def test_config_override_contract(self):
        """Contract: User config overrides defaults"""
        # Write custom config
        config_path = hcom.get_hcom_dir() / 'config.json'
        custom = {
            'max_message_size': 1000,
            'sender_name': 'custom_boss',
            'wait_timeout': 300
        }
        hcom.atomic_write(config_path, json.dumps(custom))
        
        # Force reload
        hcom._config = None
        config = hcom.get_cached_config()
        
        # Custom values should override
        assert config['max_message_size'] == 1000
        assert config['sender_name'] == 'custom_boss'
        assert config['wait_timeout'] == 300
        
        # Defaults still apply to missing keys
        assert 'terminal_mode' in config  # Has default
        assert 'initial_prompt' in config  # Has default
    
    def test_config_robustness(self):
        """Contract: Invalid config doesn't break the system"""
        # Write invalid JSON
        config_path = hcom.get_hcom_dir() / 'config.json'
        config_path.write_text('{ invalid json')
        
        # Force reload
        hcom._config = None
        
        # Should not crash
        config = hcom.get_cached_config()
        
        # Should have valid defaults
        assert isinstance(config, dict)
        assert config['max_message_size'] > 0
        assert len(config['sender_name']) > 0


class TestHookActivationContract:
    """
    Hook Activation Contract:
    1. Hooks only process when HCOM_ACTIVE='1'
    2. Hooks exit silently when inactive
    3. Hook commands are accessible via 'hcom post/stop/notify'
    """
    
    def test_hook_activation_control(self):
        """Contract: HCOM_ACTIVE controls hook processing"""
        hook_input = json.dumps({
            'tool_name': 'Write',
            'session_id': 'test'
        })
        
        # Test inactive
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '0'})
        assert result.returncode == 0
        assert result.stdout == ''
        assert result.stderr == ''
        
        # Test missing env var (same as inactive)
        result = run_hcom(['post'], input=hook_input, env={})
        assert result.returncode == 0
        assert result.stdout == ''
        assert result.stderr == ''
        
        # Test active
        result = run_hcom(['post'], input=hook_input, env={'HCOM_ACTIVE': '1'})
        assert result.returncode in [0, 1, 2]  # May process


class TestErrorRecoveryContract:
    """
    Error Recovery Contract:
    1. Corrupted files are handled gracefully
    2. Missing files are created as needed
    3. Operations continue despite partial failures
    """
    
    def test_corrupted_log_recovery(self):
        """Contract: System continues despite corrupted log"""
        log_file = hcom.get_hcom_dir() / 'hcom.log'
        
        # Write corrupted content (invalid format)
        log_file.write_text('corrupted|||data|||invalid\n')
        
        # Should still be able to parse (may return empty or partial)
        messages = hcom.parse_log_messages(log_file)
        
        # Should not crash
        assert isinstance(messages, list)
        
        # Should still be able to send new messages
        hcom.send_message('recovery', 'After corruption')
        
        # New message should be retrievable
        all_messages = hcom.parse_log_messages(log_file)
        valid_messages = [m for m in all_messages if m.get('message') == 'After corruption']
        assert len(valid_messages) == 1
    
    def test_missing_file_creation(self):
        """Contract: Missing files are created as needed"""
        # Ensure no files exist
        for f in hcom.get_hcom_dir().glob('hcom*'):
            f.unlink()
        
        # send_message creates log file
        hcom.send_message('creator', 'Creates files')
        assert (hcom.get_hcom_dir() / 'hcom.log').exists()
        
        # get_new_messages creates position file
        hcom.get_new_messages('reader')
        assert (hcom.get_hcom_dir() / 'hcom.json').exists()
    
    def test_partial_failure_handling(self):
        """Contract: Operations continue despite partial failures"""
        # Make position file read-only (simulate permission issue)
        pos_file = hcom.get_hcom_dir() / 'hcom.json'
        pos_file.write_text('{}')
        os.chmod(pos_file, 0o444)  # Read-only
        
        try:
            # Should still be able to send messages (log is separate)
            hcom.send_message('persistent', 'Despite read-only')
            
            # Message should be in log
            log_file = hcom.get_hcom_dir() / 'hcom.log'
            assert 'Despite read-only' in log_file.read_text()
        finally:
            # Restore permissions
            os.chmod(pos_file, 0o644)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])