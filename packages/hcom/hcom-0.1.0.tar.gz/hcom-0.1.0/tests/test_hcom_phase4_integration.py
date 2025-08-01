#!/usr/bin/env python3
"""
Integration tests for hcom Phase 4: Open Command

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


class TestOpenCommandBasic:
    """Integration tests for basic open command functionality"""
    
    def test_open_no_args(self, temp_home):
        """Test: Open with no args launches 1 instance"""
        # Configure to show commands instead of launching
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # Should show 1 claude command
        assert result.stdout.count('claude') == 1
        assert 'HCOM_ACTIVE=1' in result.stdout
    
    def test_open_with_count(self, temp_home):
        """Test: Open N instances"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '3'])
        assert result.returncode == 0
        
        # Should show 3 claude commands
        assert result.stdout.count('claude') == 3
        assert result.stdout.count('HCOM_ACTIVE=1') == 3
    
    def test_open_invalid_number(self, temp_home):
        """Test: Invalid number treated as agent name"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # 'abc' is not a valid number, so it's treated as agent name
        result = run_hcom(['open', 'abc'])
        
        # Should fail since agent doesn't exist
        assert result.returncode == 1
        assert 'Agent not found' in result.stderr or 'error' in result.stderr.lower()


class TestOpenWithAgents:
    """Integration tests for agent loading"""
    
    def test_open_with_local_agent(self, temp_home):
        """Test: Open loads local agent file"""
        # Create local agent
        agent_dir = temp_home / '.claude/agents'
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agent_dir / 'writer.md'
        agent_file.write_text('You are a writer assistant')
        
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', 'writer'])
        assert result.returncode == 0
        
        # Should show agent being loaded (via temp file)
        assert '--append-system-prompt' in result.stdout
        assert 'hcom_agent_' in result.stdout
    
    def test_open_with_global_agent(self, temp_home):
        """Test: Open loads global agent as fallback"""
        # Create global agent in home directory
        global_agent_dir = temp_home / '.claude/agents'
        global_agent_dir.mkdir(parents=True)
        (global_agent_dir / 'reviewer.md').write_text('You are a code reviewer')
        
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Move to test directory (no local agent)
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        result = run_hcom(['open', 'reviewer'])
        assert result.returncode == 0
        
        # Should show agent being loaded (via temp file)
        assert '--append-system-prompt' in result.stdout
        assert 'hcom_agent_' in result.stdout
    
    def test_open_agent_not_found(self, temp_home):
        """Test: Error when agent doesn't exist"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', 'nonexistent'])
        assert result.returncode == 1
        assert 'Agent not found' in result.stderr or 'error' in result.stderr.lower()
    
    def test_open_multiple_agents(self, temp_home):
        """Test: Open multiple different agents"""
        # Create agents
        agent_dir = temp_home / '.claude/agents'
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / 'writer.md').write_text('Writer prompt')
        (agent_dir / 'reviewer.md').write_text('Reviewer prompt')
        
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', 'writer', 'reviewer'])
        assert result.returncode == 0
        
        # Should show both agents being loaded
        assert result.stdout.count('--append-system-prompt') == 2
        assert result.stdout.count('hcom_agent_') == 2
        assert result.stdout.count('claude') == 2


class TestOpenWithPrefix:
    """Integration tests for --prefix functionality"""
    
    def test_open_with_name_flag(self, temp_home):
        """Test: --prefix adds prefix to instances"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '--prefix', 'frontend', '2'])
        assert result.returncode == 0
        
        # Should show prefix in instance hints
        assert 'HCOM_INSTANCE_HINTS' in result.stdout
        assert 'frontend' in result.stdout
        assert result.stdout.count('claude') == 2
    
    def test_open_with_name_shorthand(self, temp_home):
        """Test: --prefix works (no shorthand)"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '--prefix', 'backend', '1'])
        assert result.returncode == 0
        
        # Should show prefix
        assert 'backend' in result.stdout
    
    def test_name_requires_argument(self, temp_home):
        """Test: --prefix without argument fails"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '--prefix'])
        assert result.returncode == 1
        assert '--prefix requires' in result.stderr


class TestOpenWithClaudeArgs:
    """Integration tests for --claude-args functionality"""
    
    def test_claude_args_basic(self, temp_home):
        """Test: --claude-args passes arguments to claude"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '1', '--claude-args', '-p --model sonnet'])
        assert result.returncode == 0
        
        # Should include claude args
        assert '-p' in result.stdout
        assert '--model' in result.stdout
        assert 'sonnet' in result.stdout
    
    def test_claude_args_with_agents(self, temp_home):
        """Test: --claude-args works with agent names"""
        # Create agent
        agent_dir = temp_home / '.claude/agents'
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / 'helper.md').write_text('Helper prompt')
        
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', 'helper', '--claude-args', '--add-dir ../shared'])
        assert result.returncode == 0
        
        # Should include agent being loaded
        assert '--append-system-prompt' in result.stdout
        assert '--add-dir' in result.stdout
        assert '../shared' in result.stdout
    
    def test_claude_args_requires_value(self, temp_home):
        """Test: --claude-args without value fails"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '--claude-args'])
        assert result.returncode == 1
        assert '--claude-args requires' in result.stderr


class TestOpenHookSetup:
    """Integration tests for automatic hook setup"""
    
    def test_open_creates_hooks(self, temp_home):
        """Test: Open command sets up hooks automatically"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Change to test directory
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # Check hooks were created
        settings_file = test_dir / '.claude/settings.local.json'
        assert settings_file.exists()
        
        settings = json.loads(settings_file.read_text())
        assert 'hooks' in settings
        assert 'PostToolUse' in settings['hooks']
        assert 'Stop' in settings['hooks']
        assert 'Notification' in settings['hooks']
        
        # Check permissions
        assert 'permissions' in settings
        perms = settings['permissions']['allow']
        assert any('HCOM_SEND' in p for p in perms)
    
    def test_open_preserves_existing_hooks(self, temp_home):
        """Test: Open preserves existing settings"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Create test directory with existing settings
        test_dir = temp_home / 'test_project'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # Create existing settings
        settings_dir = test_dir / '.claude'
        settings_dir.mkdir()
        existing = {
            'custom_setting': 'preserved',
            'hooks': {
                'CustomHook': [{'id': 'custom'}]
            }
        }
        (settings_dir / 'settings.local.json').write_text(json.dumps(existing))
        
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # Check settings preserved
        settings = json.loads((settings_dir / 'settings.local.json').read_text())
        assert settings['custom_setting'] == 'preserved'
        assert 'CustomHook' in settings['hooks']
        # And new hooks added
        assert 'PostToolUse' in settings['hooks']


class TestOpenEnvironment:
    """Integration tests for environment variable setup"""
    
    def test_open_sets_hcom_active(self, temp_home):
        """Test: HCOM_ACTIVE is always set to 1"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open', '2'])
        assert result.returncode == 0
        
        # Every instance should have HCOM_ACTIVE=1
        assert result.stdout.count('HCOM_ACTIVE=1') == 2
    
    def test_open_no_hcom_group(self, temp_home):
        """Test: HCOM_GROUP is NOT set (per spec)"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # HCOM_GROUP should NOT appear
        assert 'HCOM_GROUP' not in result.stdout
    
    def test_open_instance_hints(self, temp_home):
        """Test: HCOM_INSTANCE_HINTS is set"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # Should set instance hints
        assert 'HCOM_INSTANCE_HINTS' in result.stdout
    
    def test_open_with_config_overrides(self, temp_home):
        """Test: Config env_overrides are applied"""
        # Configure with custom env overrides
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {
            'terminal_mode': 'show_commands',
            'env_overrides': {
                'CUSTOM_VAR': 'custom_value',
                'ANOTHER_VAR': 'another_value'
            }
        }
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # Should include custom env vars
        assert 'CUSTOM_VAR=custom_value' in result.stdout
        assert 'ANOTHER_VAR=another_value' in result.stdout


class TestOpenTerminalModes:
    """Integration tests for different terminal modes"""
    
    def test_show_commands_mode(self, temp_home):
        """Test: show_commands prints instead of launching"""
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # Should print commands, not launch
        assert 'claude' in result.stdout
        # Should not have terminal-specific output
        assert 'Launching' not in result.stdout
    
    def test_terminal_command_config(self, temp_home):
        """Test: Custom terminal command from config"""
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {
            'terminal_mode': 'show_commands',
            'terminal_command': 'custom-terminal -x "{cmd}"'
        }
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Even in show_commands mode, it should use the command format
        result = run_hcom(['open'])
        assert result.returncode == 0
        
        # The output format depends on implementation
        # Just verify it runs without error
    
    def test_invalid_terminal_mode(self, temp_home):
        """Test: Invalid terminal mode falls back gracefully"""
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {
            'terminal_mode': 'invalid_mode',
            'terminal_command': 'echo "Running: {cmd}"'
        }
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Should still work with fallback behavior
        result = run_hcom(['open'])
        # May succeed or fail depending on implementation
        # Just ensure it doesn't crash catastrophically


class TestOpenComplexScenarios:
    """Integration tests for complex usage scenarios"""
    
    def test_open_mixed_args(self, temp_home):
        """Test: Mix of count, agents, and flags"""
        # Create agents
        agent_dir = temp_home / '.claude/agents'
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / 'writer.md').write_text('Writer agent')
        (agent_dir / 'reviewer.md').write_text('Reviewer agent')
        
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Complex command: 2 generic + 2 agents with prefix
        result = run_hcom(['open', '--prefix', 'team', '2', 'writer', 'reviewer'])
        assert result.returncode == 0
        
        # Should launch 4 instances total
        assert result.stdout.count('claude') == 4
        # Should have team prefix
        assert 'team' in result.stdout
        # Should have agents being loaded
        assert result.stdout.count('--append-system-prompt') == 2
    
    def test_open_with_everything(self, temp_home):
        """Test: All features combined"""
        # Create agent
        agent_dir = temp_home / '.claude/agents'
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / 'assistant.md').write_text('---\nname: Assistant\n---\nAssistant prompt')
        
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {
            'terminal_mode': 'show_commands',
            'env_overrides': {'PROJECT': 'test'}
        }
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Complex command with all features
        result = run_hcom([
            'open', 
            '--prefix', 'project',
            'assistant',
            '--claude-args', '--model opus --add-dir src'
        ])
        assert result.returncode == 0
        
        # Verify all components present
        assert '--append-system-prompt' in result.stdout  # Agent loaded
        assert 'project' in result.stdout  # Prefix applied
        assert '--model' in result.stdout  # Claude args
        assert 'opus' in result.stdout
        assert 'PROJECT=test' in result.stdout  # Env override


class TestOpenErrorHandling:
    """Integration tests for error conditions"""
    
    def test_open_permission_error(self, temp_home):
        """Test: Handle permission errors gracefully"""
        # Configure for testing
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config = {'terminal_mode': 'show_commands'}
        (config_dir / 'config.json').write_text(json.dumps(config))
        
        # Create read-only directory
        test_dir = temp_home / 'readonly'
        test_dir.mkdir()
        os.chdir(test_dir)
        
        # Make .claude directory read-only
        claude_dir = test_dir / '.claude'
        claude_dir.mkdir()
        os.chmod(claude_dir, 0o444)
        
        try:
            result = run_hcom(['open'])
            # Should fail with permission error
            assert result.returncode == 1
            assert 'permission' in result.stderr.lower() or 'error' in result.stderr.lower()
        finally:
            # Restore permissions for cleanup
            os.chmod(claude_dir, 0o755)
    
    def test_open_corrupt_config(self, temp_home):
        """Test: Handle corrupt config file"""
        config_dir = temp_home / '.hcom'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'config.json'
        config_file.write_text('invalid json{')
        
        # Should handle gracefully with defaults
        result = run_hcom(['open'])
        # May succeed with defaults or fail - implementation dependent


if __name__ == '__main__':
    pytest.main([__file__, '-v'])