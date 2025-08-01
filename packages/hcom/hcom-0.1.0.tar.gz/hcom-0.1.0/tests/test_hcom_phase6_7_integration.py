#!/usr/bin/env python3
"""
Integration tests for hcom Phase 6 & 7: Clear and Cleanup Commands

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


class TestClearCommand:
    """Integration tests for clear command"""
    
    def setup_method(self):
        """Set up test environment"""
        # Note: temp_home will be accessed via test method parameters
        pass
    def test_clear_archives_conversation(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Clear archives existing conversation"""
        # Create test messages
        test_messages = [
            f"{datetime.now().isoformat()}|alice|Message before clear\n",
            f"{datetime.now().isoformat()}|bob|Another message\n"
        ]
        log_file.write_text(''.join(test_messages))
        
        # Create position data
        positions = {'alice': {'pos': 50}, 'bob': {'pos': 100}}
        pos_file.write_text(json.dumps(positions))
        
        # Run clear
        result = run_hcom(['clear'])
        assert result.returncode == 0
        
        # Should indicate archiving
        assert 'Archived' in result.stdout or 'archived' in result.stdout.lower()
        assert 'hcom' in result.stdout
        
        # Check archive files exist
        archive_files = list(hcom_dir.glob('hcom-*.log'))
        assert len(archive_files) == 1
        
        # Verify archive contains original data
        archive_content = archive_files[0].read_text()
        assert 'Message before clear' in archive_content
        assert 'Another message' in archive_content
    
    def test_clear_creates_fresh_files(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Clear creates fresh empty files"""
        # Create some data
        log_file.write_text(f"{datetime.now().isoformat()}|user|Old data\n")
        pos_file.write_text('{"user": {"pos": 10}}')
        
        # Run clear
        result = run_hcom(['clear'])
        assert result.returncode == 0
        
        # Check fresh files created
        assert log_file.exists()
        assert log_file.stat().st_size == 0  # Empty
        
        assert pos_file.exists()
        pos_data = json.loads(pos_file.read_text())
        assert pos_data == {}  # Empty positions
        
        # Should indicate fresh start
        assert 'fresh' in result.stdout.lower()
    
    def test_clear_no_conversation(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Clear handles no existing conversation"""
        # Ensure no files exist
        if log_file.exists():
            log_file.unlink()
        if pos_file.exists():
            pos_file.unlink()
        
        result = run_hcom(['clear'])
        assert result.returncode == 0
        
        # Should indicate no conversation
        assert 'No' in result.stdout or 'no' in result.stdout
        assert 'conversation' in result.stdout.lower()
    
    def test_clear_archive_naming(self, temp_home):
        # Set up test environment
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        log_file = hcom_dir / 'hcom.log'
        pos_file = hcom_dir / 'hcom.json'
        log_file.touch()
        
        """Test: Archive files have timestamp format"""
        # Create data
        log_file.write_text(f"{datetime.now().isoformat()}|user|Data\n")
        
        # Clear
        result = run_hcom(['clear'])
        assert result.returncode == 0
        
        # Check archive naming
        archives = list(hcom_dir.glob('hcom-*.log'))
        assert len(archives) == 1
        
        # Parse archive name
        archive_name = archives[0].name
        # Should be: global-YYYYMMDD-HHMMSS.log
        parts = archive_name.split('-')
        assert len(parts) == 3  # global, date, time.log
        assert parts[0] == 'hcom'
        
        # Verify date format (8 digits)
        assert len(parts[1]) == 8
        assert parts[1].isdigit()
        
        # Verify time format (6 digits + .log)
        time_part = parts[2].replace('.log', '')
        assert len(time_part) == 6
        assert time_part.isdigit()


class TestCleanupCommand:
    """Integration tests for cleanup command"""
    
    def test_cleanup_removes_hooks(self, temp_home):
        """Test: Cleanup removes hcom hooks"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Create test directory
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # First set up hooks
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # Verify hooks exist
        settings_file = test_dir / '.claude/settings.local.json'
        assert settings_file.exists()
        settings = json.loads(settings_file.read_text())
        assert 'hooks' in settings
        assert 'PostToolUse' in settings['hooks']
        
        # Now cleanup
        result = run_hcom(['cleanup'])
        assert result.returncode == 0
        assert 'Removed' in result.stdout or 'removed' in result.stdout.lower()
        
        # Verify hooks removed
        if settings_file.exists():
            settings = json.loads(settings_file.read_text())
            hooks = settings.get('hooks', {})
            
            # Check PostToolUse hooks
            if 'PostToolUse' in hooks:
                for matcher in hooks['PostToolUse']:
                    for hook in matcher.get('hooks', []):
                        assert 'hcom' not in hook.get('command', '')
            
            # Same for Stop and Notification
            if 'Stop' in hooks:
                for matcher in hooks['Stop']:
                    for hook in matcher.get('hooks', []):
                        assert 'hcom' not in hook.get('command', '')
    
    def test_cleanup_removes_permissions(self, temp_home):
        """Test: Cleanup removes HCOM_SEND permission"""
        # Set up test directory
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # Create settings with permissions
        settings_dir = test_dir / '.claude'
        settings_dir.mkdir()
        settings = {
            'hooks': {
                'PostToolUse': [{
                    'matcher': '.*',
                    'hooks': [{
                        'type': 'command',
                        'command': 'hcom post'
                    }]
                }],
                'Stop': [{
                    'matcher': '',
                    'hooks': [{
                        'type': 'command',
                        'command': 'hcom stop'
                    }]
                }]
            },
            'permissions': {
                'allow': [
                    'Bash echo "HCOM_SEND:*"',
                    'Read *',
                    'Write *'
                ]
            }
        }
        (settings_dir / 'settings.local.json').write_text(json.dumps(settings))
        
        # Cleanup
        result = run_hcom(['cleanup'])
        assert result.returncode == 0
        
        # Check permissions
        if (settings_dir / 'settings.local.json').exists():
            settings = json.loads((settings_dir / 'settings.local.json').read_text())
            perms = settings.get('permissions', {}).get('allow', [])
            
            # HCOM_SEND should be removed
            assert not any('HCOM_SEND' in p for p in perms)
            # Other permissions preserved
            assert any('Read' in p for p in perms)
            assert any('Write' in p for p in perms)
    
    def test_cleanup_no_hooks_to_remove(self, temp_home):
        """Test: Cleanup handles no hooks gracefully"""
        # Create empty directory
        test_dir = temp_home / 'empty_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        result = run_hcom(['cleanup'])
        assert result.returncode == 0
        
        # Should indicate no hooks found or no settings
        assert 'No' in result.stdout or 'no' in result.stdout
        assert ('hooks' in result.stdout.lower() or 'settings' in result.stdout.lower())
    
    def test_cleanup_preserves_other_settings(self, temp_home):
        """Test: Cleanup preserves non-hcom settings"""
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # Create mixed settings
        settings_dir = test_dir / '.claude'
        settings_dir.mkdir()
        settings = {
            'hooks': {
                'PostToolUse': [{
                    'id': 'hcom-post',
                    'hooks': [{
                        'command': '"python" "hcom.py" post'
                    }]
                }],
                'CustomHook': [{  # Should be preserved
                    'id': 'custom',
                    'hooks': [{'command': 'custom command'}]
                }]
            },
            'other_setting': 'preserve_this'
        }
        (settings_dir / 'settings.local.json').write_text(json.dumps(settings))
        
        # Cleanup
        result = run_hcom(['cleanup'])
        assert result.returncode == 0
        
        # Check preservation
        settings_file = settings_dir / 'settings.local.json'
        if settings_file.exists():
            new_settings = json.loads(settings_file.read_text())
            
            # Note: HCOM_ACTIVE is never in settings - it's passed as env var
            # This test was checking for something that should never exist
            
            # Custom hook preserved
            assert 'CustomHook' in new_settings.get('hooks', {})
            
            # Other setting preserved
            assert new_settings.get('other_setting') == 'preserve_this'
    
    def test_cleanup_deletes_empty_settings(self, temp_home):
        """Test: Cleanup deletes settings file if empty after cleanup"""
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # Create settings with only hcom content
        settings_dir = test_dir / '.claude'
        settings_dir.mkdir()
        settings = {
            'hooks': {
                'PostToolUse': [{
                    'id': 'hcom-post',
                    'hooks': [{'command': '"python" "hcom.py" post'}]
                }]
            },
            'permissions': {
                'allow': ['Bash echo "HCOM_SEND:*"']
            }
        }
        (settings_dir / 'settings.local.json').write_text(json.dumps(settings))
        
        # Cleanup
        result = run_hcom(['cleanup'])
        assert result.returncode == 0
        
        # File should be deleted if empty
        settings_file = settings_dir / 'settings.local.json'
        if settings_file.exists():
            # If it exists, it should have minimal content
            settings = json.loads(settings_file.read_text())
            # Check that hcom content is gone
            hooks = settings.get('hooks', {})
            if 'PostToolUse' in hooks:
                for matcher in hooks['PostToolUse']:
                    for hook in matcher.get('hooks', []):
                        assert 'hcom' not in hook.get('command', '')


class TestClearCleanupIntegration:
    """Integration tests combining clear and cleanup"""
    
    def test_clear_then_cleanup_workflow(self, temp_home):
        """Test: Typical workflow of clear then cleanup"""
        # Set up project with hcom
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # Set up hcom
        run_hcom(['open'])
        
        # Send some messages
        run_hcom(['send', 'Test message 1'])
        run_hcom(['send', 'Test message 2'])
        
        # Clear conversation
        result = run_hcom(['clear'])
        assert result.returncode == 0
        assert 'Archived' in result.stdout
        
        # Cleanup hooks
        result = run_hcom(['cleanup'])
        assert result.returncode == 0
        assert 'Removed' in result.stdout
        
        # Verify clean state
        settings_file = test_dir / '.claude/settings.local.json'
        if settings_file.exists():
            settings = json.loads(settings_file.read_text())
            # No hcom hooks
            hooks = settings.get('hooks', {})
            for hook_type in hooks:
                for matcher in hooks[hook_type]:
                    for hook in matcher.get('hooks', []):
                        assert 'hcom' not in hook.get('command', '')


class TestErrorHandling:
    """Integration tests for error conditions"""
    
    def test_clear_permission_error(self, temp_home):
        """Test: Clear handles permission errors gracefully"""
        # Create read-only directory
        hcom_dir = temp_home / '.hcom'
        hcom_dir.mkdir(exist_ok=True)
        (hcom_dir / 'hcom.log').write_text('data')
        
        # Make directory read-only
        os.chmod(hcom_dir, 0o444)
        
        try:
            result = run_hcom(['clear'])
            # Should fail gracefully
            assert result.returncode == 1
            assert 'error' in result.stderr.lower() or 'permission' in result.stderr.lower()
        finally:
            # Restore permissions
            os.chmod(hcom_dir, 0o755)
    
    def test_cleanup_malformed_settings(self, temp_home):
        """Test: Cleanup handles malformed settings file"""
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # Create malformed settings
        settings_dir = test_dir / '.claude'
        settings_dir.mkdir()
        (settings_dir / 'settings.local.json').write_text('{"invalid": json}')
        
        result = run_hcom(['cleanup'])
        # Should handle gracefully
        assert result.returncode in [0, 1]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])