#!/usr/bin/env python3
"""
Basic iTerm test for hcom open command
Actually launches hcom and verifies it works by observing terminal behavior
"""

import os
import sys
import json
import time
import tempfile
import shutil
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestHcomIterm:
    """Basic iTerm test that actually launches hcom and observes behavior"""
        
    async def setup(self):
        """Setup test environment and iTerm connection"""
        # Initialize instance variables
        self.test_dir = None
        self.connection = None
        self.app = None
        self.control_session = None
        self.claude_sessions = {}
        # Calculate hcom.py path once
        self.hcom_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'hcom.py'
        )
        
        # Create test directory
        self.test_dir = tempfile.mkdtemp(prefix="hcom-test-")
        print(f"Test directory: {self.test_dir}")
        
        # Connect to iTerm2
        import iterm2
        self.connection = await iterm2.Connection.async_create()
        self.app = await iterm2.async_get_app(self.connection)
        
        # Create control session
        window = self.app.current_terminal_window
        if not window:
            window = await iterm2.Window.async_create(self.connection)
        
        tab = await window.async_create_tab()
        self.control_session = tab.current_session
        
        # Change to test directory
        await self.control_session.async_send_text(f"cd {self.test_dir}\n")
        await asyncio.sleep(1)
        
        # Configure hcom to use iTerm for launching
        await self.setup_hcom_config()
        
    async def setup_hcom_config(self):
        """Configure hcom to launch Claude instances for real testing"""
        # Create real hcom directory at expected location (~/.hcom)
        real_hcom_dir = Path.home() / '.hcom'
        real_hcom_dir.mkdir(exist_ok=True)
        
        # Backup existing config if it exists
        config_file = real_hcom_dir / 'config.json'
        backup_file = real_hcom_dir / 'config.json.test_backup'
        
        if config_file.exists():
            config_file.rename(backup_file)
            print(f"Backed up existing config to {backup_file}")
        
        # Create test config for real launches but with short timeout
        config = {
            "terminal_mode": "new_window",  # Actually launch in new windows
            "initial_prompt": "You are testing hcom. Say 'HCOM TEST READY' then wait for instructions.",
            "wait_timeout": 30,  # Short timeout for testing
            "max_message_size": 4096,
            "max_messages_per_delivery": 20,
            "sender_name": "testuser",
            "sender_emoji": "🧪"
        }
        
        config_file.write_text(json.dumps(config, indent=2))
        
        # Verify config was created in correct location
        await self.control_session.async_send_text(f"cat {config_file}\n")
        await asyncio.sleep(1)
        
        # Store backup info for cleanup
        self.config_backup = backup_file if backup_file.exists() else None
        
    async def capture_terminal_output(self, session=None, lines=20):
        """Capture output from terminal session"""
        if session is None:
            session = self.control_session
            
        screen = await session.async_get_screen_contents()
        output_lines = []
        
        # Get the last 'lines' lines
        for i in range(max(0, screen.number_of_lines - lines), screen.number_of_lines):
            line = screen.line(i)
            output_lines.append(line.string)
        
        return "\n".join(output_lines)
    
    async def wait_for_text_in_session(self, session, expected_texts, timeout=10):
        """Wait for expected text to appear in session"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            output = await self.capture_terminal_output(session, lines=30)
            
            for text in expected_texts:
                if text.lower() in output.lower():
                    return True
            
            await asyncio.sleep(0.5)
        
        return False
    
    async def test_hcom_open_launches_claude(self):
        """Test that hcom open actually launches Claude"""
        print("🧪 Testing hcom open actually launches Claude...")
        
        # Count initial windows/tabs
        initial_tab_count = sum(len(window.tabs) for window in self.app.terminal_windows)
        print(f"Initial tab count: {initial_tab_count}")
        
        # Run hcom open 1 using full path to hcom.py
        await self.control_session.async_send_text(f"python {self.hcom_path} open 1\n")
        
        # Wait for launch to complete
        await asyncio.sleep(5)
        
        # Capture what happened in control terminal
        output = await self.capture_terminal_output(lines=30)
        print(f"Control terminal output:\n{output}")
        
        # Check for successful launch message
        if "Launched 1 Claude instance" not in output:
            print("❌ FAIL: No success message from hcom open")
            return False
        
        # Wait a bit more for new window to appear
        await asyncio.sleep(3)
        
        # Count tabs after - should have increased
        final_tab_count = sum(len(window.tabs) for window in self.app.terminal_windows)
        print(f"Final tab count: {final_tab_count}")
        
        if final_tab_count <= initial_tab_count:
            print("❌ FAIL: No new tabs created by hcom open")
            return False
        
        # Find the new Claude session
        new_sessions = []
        for window in self.app.terminal_windows:
            for tab in window.tabs:
                session = tab.current_session
                if session != self.control_session and session not in self.claude_sessions.values():
                    new_sessions.append(session)
        
        if not new_sessions:
            print("❌ FAIL: No new Claude sessions found")
            return False
        
        # Take the first new session as our Claude instance
        claude_session = new_sessions[0]
        
        # Wait for Claude to be ready
        claude_ready = await self.wait_for_text_in_session(
            claude_session, 
            ["HCOM TEST READY", "Welcome to Claude", "> "], 
            timeout=30
        )
        
        if not claude_ready:
            print("❌ FAIL: Claude didn't become ready")
            claude_output = await self.capture_terminal_output(claude_session, lines=30)
            print(f"Claude session output:\n{claude_output}")
            return False
        
        print("✅ PASS: hcom open successfully launched Claude")
        self.claude_sessions['claude1'] = claude_session
        return True
    
    async def test_hcom_hooks_setup(self):
        """Test that hcom open set up hooks correctly"""
        print("🧪 Testing hook setup...")
        
        # Check if settings file was created
        settings_file = Path(self.test_dir) / '.claude/settings.local.json'
        if not settings_file.exists():
            print("❌ FAIL: No settings file created")
            return False
        
        # Verify settings content
        try:
            settings = json.loads(settings_file.read_text())
            
            # Check for required hooks
            required_hooks = ['PostToolUse', 'Stop', 'Notification']
            for hook_type in required_hooks:
                if hook_type not in settings.get('hooks', {}):
                    print(f"❌ FAIL: Missing {hook_type} hook")
                    return False
                
                # Verify hook command references hcom.py
                hooks_list = settings['hooks'][hook_type]
                if not hooks_list:
                    print(f"❌ FAIL: Empty {hook_type} hooks list")
                    return False
                
                command = hooks_list[0]['hooks'][0]['command']
                if 'hcom.py' not in command:
                    print(f"❌ FAIL: {hook_type} doesn't reference hcom.py")
                    return False
            
            # Check permissions
            if 'permissions' not in settings:
                print("❌ FAIL: No permissions in settings")
                return False
            
            perms = settings['permissions']['allow']
            has_hcom_send = any('HCOM_SEND' in p for p in perms)
            if not has_hcom_send:
                print("❌ FAIL: No HCOM_SEND permission")
                return False
            
            print("✅ PASS: Hooks configured correctly")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: Error reading settings: {e}")
            return False
    
    async def test_claude_hook_integration(self):
        """Test that Claude can send messages through hooks"""
        print("🧪 Testing Claude hook integration...")
        
        claude_session = self.claude_sessions.get('claude1')
        if not claude_session:
            print("❌ FAIL: No Claude session available")
            return False
        
        # Send command to Claude to trigger HCOM_SEND
        await claude_session.async_send_text('Use the Bash tool to run: echo "HCOM_SEND:Test from Claude"\n')
        
        # Wait for command to execute
        await asyncio.sleep(5)
        
        # Check if message appeared in real hcom log
        log_file = Path.home() / '.hcom/hcom.log'
        if not log_file.exists():
            print("❌ FAIL: No hcom log file created")
            return False
        
        log_content = log_file.read_text()
        if 'Test from Claude' not in log_content:
            print("❌ FAIL: Message not found in log")
            print(f"Log content: {log_content}")
            return False
        
        print("✅ PASS: Claude hook integration working")
        return True
    
    async def test_hcom_send_cli(self):
        """Test hcom send command"""
        print("🧪 Testing hcom send CLI...")
        
        # Send message via CLI using full path
        await self.control_session.async_send_text(f'python {self.hcom_path} send "CLI test message"\n')
        await asyncio.sleep(2)
        
        # Check if message appeared in log
        log_file = Path.home() / '.hcom/hcom.log'
        if not log_file.exists():
            print("❌ FAIL: No log file for CLI message")
            return False
        
        log_content = log_file.read_text()
        if 'CLI test message' not in log_content:
            print("❌ FAIL: CLI message not in log")
            print(f"Log content: {log_content}")
            return False
        
        print("✅ PASS: hcom send CLI working")
        return True
    
    async def test_hcom_open_agent(self):
        """Test that hcom open works with agents"""
        print("🧪 Testing hcom open with agent...")
        
        # First create a simple test agent
        agents_dir = Path(self.test_dir) / '.claude/agents'
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        agent_content = """---
name: test-agent
---
You are a test agent. When asked, respond with "TEST AGENT ACTIVE"."""
        
        agent_file = agents_dir / 'test-agent.md'
        agent_file.write_text(agent_content)
        
        # Count initial tabs
        initial_tab_count = sum(len(window.tabs) for window in self.app.terminal_windows)
        print(f"Initial tab count: {initial_tab_count}")
        
        # Launch agent
        await self.control_session.async_send_text(f"python {self.hcom_path} open test-agent\n")
        
        # Wait for launch
        await asyncio.sleep(5)
        
        # Capture control terminal output
        output = await self.capture_terminal_output()
        print(f"Control terminal output:\n{output}")
        
        # Check for successful launch message
        if "Launched 1 Claude instance" not in output:
            print("❌ FAIL: No success message from hcom open")
            return False
        
        # Wait for new window to appear
        await asyncio.sleep(3)
        
        # Count tabs after - should have increased
        final_tab_count = sum(len(window.tabs) for window in self.app.terminal_windows)
        print(f"Final tab count: {final_tab_count}")
        
        if final_tab_count <= initial_tab_count:
            print("❌ FAIL: No new tabs created for agent")
            return False
        
        # Find the newest session (agent session)
        agent_session = None
        for window in self.app.terminal_windows:
            for tab in window.tabs:
                session = tab.current_session
                if session != self.control_session and session not in self.claude_sessions.values():
                    agent_session = session
                    break
        
        if not agent_session:
            print("❌ FAIL: No new agent session found")
            return False
        
        print("Found agent session, checking if Claude is ready...")
        
        # Wait for Claude to be ready with agent content
        agent_ready = await self.wait_for_text_in_session(
            agent_session, 
            ["Welcome to Claude", "test agent", "> ", "cwd:"], 
            timeout=30
        )
        
        if not agent_ready:
            print("❌ FAIL: Agent didn't become ready")
            agent_output = await self.capture_terminal_output(agent_session, lines=50)
            print(f"Agent session output:\n{agent_output}")
            return False
        
        print("✅ PASS: hcom open successfully launched agent in new iTerm tab")
        self.claude_sessions['test-agent'] = agent_session
        return True
    
    async def cleanup(self):
        """Clean up test environment"""
        print("🧹 Cleaning up...")
        
        # Close all Claude sessions
        for session in self.claude_sessions.values():
            try:
                await session.async_send_text("\x03")  # Ctrl-C
                await asyncio.sleep(0.5)
                await session.async_close()
            except:
                pass
        
        # Restore original hcom config if we backed it up
        if hasattr(self, 'config_backup') and self.config_backup:
            config_file = Path.home() / '.hcom/config.json'
            try:
                if self.config_backup.exists():
                    self.config_backup.rename(config_file)
                    print(f"Restored original config from backup")
                elif config_file.exists():
                    config_file.unlink()
                    print("Removed test config file")
            except Exception as e:
                print(f"Warning: Could not restore config: {e}")
        else:
            # Just remove our test config
            config_file = Path.home() / '.hcom/config.json'
            try:
                if config_file.exists():
                    config_file.unlink()
                    print("Removed test config file")
            except Exception as e:
                print(f"Warning: Could not remove test config: {e}")
        
        if self.connection:
            self.connection.close()
        
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting hcom iTerm integration tests...")
        
        try:
            await self.setup()
            
            # Run tests in sequence
            tests = [
                self.test_hcom_open_launches_claude,
                self.test_hcom_hooks_setup,
                self.test_claude_hook_integration,
                self.test_hcom_send_cli,
                self.test_hcom_open_agent,
            ]
            
            results = []
            for test in tests:
                try:
                    result = await test()
                    results.append(result)
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed with error: {e}")
                    results.append(False)
            
            # Summary
            passed = sum(results)
            total = len(results)
            
            if passed == total:
                print(f"🎉 All {total} tests passed!")
                return True
            else:
                print(f"💥 {passed}/{total} tests passed")
                return False
                
        except Exception as e:
            print(f"❌ Test setup error: {e}")
            return False
        finally:
            await self.cleanup()

async def main():
    """Main test runner"""
    try:
        import iterm2
    except ImportError:
        print("❌ Error: iterm2 module not found. Install with: pip install iterm2")
        return 1
    
    test = TestHcomIterm()
    success = await test.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))