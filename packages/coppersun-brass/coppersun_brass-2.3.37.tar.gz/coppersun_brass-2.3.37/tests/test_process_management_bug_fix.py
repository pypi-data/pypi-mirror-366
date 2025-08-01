#!/usr/bin/env python3
"""
Test Plan for Process Management Bug Fix
Test validation for brass uninstall --all daemon termination feature
"""

import unittest
import os
import sys
import subprocess
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from coppersun_brass.cli.brass_cli import BrassCLI
    from coppersun_brass.cli.background_process_manager import BackgroundProcessManager
except ImportError as e:
    print(f"Warning: Could not import Copper Sun Brass modules: {e}")
    print("This test requires the full Copper Sun Brass installation")


class TestProcessManagementBugFix(unittest.TestCase):
    """Test suite for Process Management Bug Fix validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.brass_dir = self.test_dir / '.brass'
        self.brass_dir.mkdir(exist_ok=True)
        
        # Create mock PID file
        self.pid_file = self.brass_dir / 'monitoring.pid'
        
        # Change to test directory
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        
        # Clean up test directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_uninstall_system_wide_process_termination(self):
        """Test that uninstall --all includes system-wide process termination."""
        cli = BrassCLI()
        
        # Create mock .brass directories in different locations
        mock_projects = [
            self.test_dir / "project1" / ".brass",
            self.test_dir / "project2" / ".brass", 
            self.test_dir / "project3" / ".brass"
        ]
        
        for brass_dir in mock_projects:
            brass_dir.mkdir(parents=True, exist_ok=True)
            # Create mock PID files
            (brass_dir / "monitoring.pid").write_text("12345")
        
        # Mock the BackgroundProcessManager to avoid actual process manipulation
        with patch('coppersun_brass.cli.brass_cli.BackgroundProcessManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.stop_background_process.return_value = (True, "Process 12345 stopped")
            
            # Mock the path search to find our test directories
            with patch('pathlib.Path.rglob') as mock_rglob:
                mock_rglob.return_value = mock_projects
                
                # Mock user input to confirm uninstall
                with patch('builtins.input', return_value='yes'):
                    # Capture stdout to verify process termination message
                    from io import StringIO
                    import sys
                    captured_output = StringIO()
                    
                    with patch('sys.stdout', captured_output):
                        try:
                            cli.uninstall(remove_all=True, dry_run=False)
                        except SystemExit:
                            pass  # Expected when no files are found
                    
                    output = captured_output.getvalue()
                    
                    # Verify that process termination was attempted for multiple projects
                    self.assertIn("Stopping background monitoring processes", output)
                    # Should be called once per project with PID files
                    self.assertEqual(mock_manager.stop_background_process.call_count, 3)
                
    def test_uninstall_without_all_flag_no_process_termination(self):
        """Test that uninstall without --all does NOT terminate processes."""
        cli = BrassCLI()
        
        # Mock the BackgroundProcessManager
        with patch('coppersun_brass.cli.brass_cli.BackgroundProcessManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            # Mock user input to confirm uninstall
            with patch('builtins.input', return_value='yes'):
                from io import StringIO
                import sys
                captured_output = StringIO()
                
                with patch('sys.stdout', captured_output):
                    try:
                        cli.uninstall(remove_all=False, dry_run=False)
                    except SystemExit:
                        pass  # Expected when no files are found
                
                output = captured_output.getvalue()
                
                # Verify that process termination was NOT attempted
                self.assertNotIn("Stopping background monitoring processes", output)
                mock_manager.stop_background_process.assert_not_called()
                
    def test_uninstall_process_termination_error_handling(self):
        """Test error handling when process termination fails."""
        cli = BrassCLI()
        
        # Mock the BackgroundProcessManager to simulate failure
        with patch('coppersun_brass.cli.brass_cli.BackgroundProcessManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.stop_background_process.return_value = (False, "Failed to stop process 12345")
            
            # Mock user input to confirm uninstall
            with patch('builtins.input', return_value='yes'):
                from io import StringIO
                import sys
                captured_output = StringIO()
                
                with patch('sys.stdout', captured_output):
                    try:
                        cli.uninstall(remove_all=True, dry_run=False)
                    except SystemExit:
                        pass  # Expected when no files are found
                
                output = captured_output.getvalue()
                
                # Verify that error is handled gracefully with detailed guidance
                self.assertIn("Stopping background monitoring processes", output)
                self.assertIn("Failed to stop process 12345", output)
                self.assertIn("could not be stopped automatically", output)
                self.assertIn("Manual cleanup options", output)
                self.assertIn("pkill -f coppersun_brass", output)
                mock_manager.stop_background_process.assert_called_once()
                
    def test_uninstall_import_error_handling(self):
        """Test error handling when BackgroundProcessManager import fails."""
        cli = BrassCLI()
        
        # Mock import failure
        with patch('coppersun_brass.cli.brass_cli.BackgroundProcessManager', side_effect=ImportError("Module not found")):
            # Mock user input to confirm uninstall
            with patch('builtins.input', return_value='yes'):
                from io import StringIO
                import sys
                captured_output = StringIO()
                
                with patch('sys.stdout', captured_output):
                    try:
                        cli.uninstall(remove_all=True, dry_run=False)
                    except SystemExit:
                        pass  # Expected when no files are found
                
                output = captured_output.getvalue()
                
                # Verify that import error is handled gracefully
                self.assertIn("Stopping background monitoring processes", output)
                self.assertIn("Could not stop background processes", output)
                
    def test_process_termination_execution_order(self):
        """Test that process termination happens before file removal."""
        cli = BrassCLI()
        
        # Create test files to remove
        test_file = self.brass_dir / 'config.json'
        test_file.write_text('{"test": "data"}')
        
        call_order = []
        
        # Mock the BackgroundProcessManager
        with patch('coppersun_brass.cli.brass_cli.BackgroundProcessManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            def mock_stop_process():
                call_order.append('stop_process')
                return (True, "Process stopped")
            mock_manager.stop_background_process.side_effect = mock_stop_process
            
            # Mock file operations to track order
            original_unlink = Path.unlink
            def mock_unlink(self, missing_ok=False):
                call_order.append('file_removal')
                return original_unlink(self, missing_ok=missing_ok)
                
            with patch.object(Path, 'unlink', mock_unlink):
                # Mock user input to confirm uninstall
                with patch('builtins.input', return_value='yes'):
                    from io import StringIO
                    import sys
                    captured_output = StringIO()
                    
                    with patch('sys.stdout', captured_output):
                        cli.uninstall(remove_all=True, dry_run=False)
            
            # Verify order: process termination before file removal
            self.assertIn('stop_process', call_order)
            if 'file_removal' in call_order:
                self.assertLess(call_order.index('stop_process'), call_order.index('file_removal'))


class TestBackgroundProcessManagerIntegration(unittest.TestCase):
    """Test BackgroundProcessManager integration points."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_background_process_manager_stop_nonexistent_process(self):
        """Test BackgroundProcessManager handling of non-existent process (cross-platform)."""
        manager = BackgroundProcessManager(self.test_dir)
        
        # Create fake PID file with non-existent PID
        brass_dir = self.test_dir / '.brass'
        brass_dir.mkdir(exist_ok=True)
        pid_file = brass_dir / 'monitoring.pid'
        pid_file.write_text('999999')  # Very unlikely to exist
        
        success, message = manager.stop_background_process()
        
        # Should succeed because process doesn't exist
        self.assertTrue(success)
        self.assertIn("already stopped", message.lower())
        self.assertFalse(pid_file.exists())  # PID file should be cleaned up
        
    def test_background_process_manager_no_pid_file(self):
        """Test BackgroundProcessManager when no PID file exists."""
        manager = BackgroundProcessManager(self.test_dir)
        
        success, message = manager.stop_background_process()
        
        # Should succeed because no process is running
        self.assertTrue(success)
        self.assertIn("no background process", message.lower())


class TestEnhancedErrorHandling(unittest.TestCase):
    """Test enhanced error handling and user guidance."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_enhanced_error_guidance_for_failed_processes(self):
        """Test enhanced error guidance when processes cannot be stopped."""
        cli = BrassCLI()
        
        # Create test project with PID file
        test_project = self.test_dir / "failing_project" / ".brass"
        test_project.mkdir(parents=True)
        pid_file = test_project / "monitoring.pid"
        pid_file.write_text("99999")  # Fake PID
        
        # Mock BackgroundProcessManager to simulate failure
        with patch('coppersun_brass.cli.brass_cli.BackgroundProcessManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.stop_background_process.return_value = (False, "Permission denied")
            
            # Mock path search to find our test project
            with patch('pathlib.Path.rglob') as mock_rglob:
                mock_rglob.return_value = [test_project]
                
                # Mock user input to confirm uninstall
                with patch('builtins.input', return_value='yes'):
                    from io import StringIO
                    import sys
                    captured_output = StringIO()
                    
                    with patch('sys.stdout', captured_output):
                        try:
                            cli.uninstall(remove_all=True, dry_run=False)
                        except SystemExit:
                            pass
                    
                    output = captured_output.getvalue()
                    
                    # Verify enhanced error guidance is provided
                    self.assertIn("could not be stopped automatically", output)
                    self.assertIn("Manual cleanup options", output)
                    self.assertIn("Option 1 - Kill all Brass processes", output)
                    self.assertIn("Option 2 - Kill specific processes by project", output)
                    self.assertIn("Option 3 - Clean up PID files manually", output)
                    self.assertIn("failing_project", output)
                    self.assertIn("kill 99999", output)
                    self.assertIn("taskkill /PID 99999", output)
                    self.assertIn("ps aux | grep coppersun_brass", output)


def run_manual_integration_test():
    """Manual integration test for real system-wide process termination."""
    print("\n" + "="*60)
    print("MANUAL INTEGRATION TEST")
    print("Testing system-wide process termination during uninstall")
    print("="*60)
    
    # This test should be run manually to validate real process behavior
    print("\nTo run manual integration test:")
    print("1. Create multiple projects with background monitoring")
    print("2. Verify processes are running across projects")
    print("3. Run uninstall --all from any directory")
    print("4. Verify ALL processes are stopped system-wide")
    print("5. Expected: No coppersun_brass processes should remain anywhere")
    
    print("\nTest Commands:")
    print("# Setup multiple projects with monitoring")
    print("cd /tmp")
    print("mkdir -p test_project1 test_project2 test_project3")
    print("")
    print("# Start monitoring in each project")
    print("cd test_project1 && brass init && python -m coppersun_brass start --daemon &")
    print("cd ../test_project2 && brass init && python -m coppersun_brass start --daemon &") 
    print("cd ../test_project3 && brass init && python -m coppersun_brass start --daemon &")
    print("sleep 5")
    print("")
    print("# Verify multiple processes running")
    print("ps aux | grep coppersun_brass | grep -v grep  # Should show 3 processes")
    print("")
    print("# Test system-wide uninstall from any directory")
    print("cd /tmp  # Run from parent directory")
    print("brass uninstall --all  # Type 'yes' when prompted")
    print("")
    print("# Verify ALL processes stopped")
    print("ps aux | grep coppersun_brass | grep -v grep  # Should show NO processes")
    print("")
    print("Expected output should show:")
    print("🛑 Stopping background monitoring processes...")
    print("  ✅ test_project1: Background process XXXX stopped")
    print("  ✅ test_project2: Background process YYYY stopped") 
    print("  ✅ test_project3: Background process ZZZZ stopped")
    print("  ✅ Successfully stopped all 3 background process(es)")


if __name__ == '__main__':
    # Run unit tests
    print("Running Process Management Bug Fix Test Suite...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Print manual test instructions
    run_manual_integration_test()