"""Integration tests for application functionality."""

import pytest

from gemma_3n import __version__


class TestApplication:
    """Test application integration."""
    
    def test_version_command(self, app, capsys):
        """Test version command output."""
        with pytest.raises(SystemExit) as exc_info:
            app.run(["--version"])
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out
    
    def test_help_command(self, app, capsys):
        """Test help command output."""
        exit_code = app.run(["--help"])
        
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "gemma-3n" in captured.out
        assert "Available commands" in captured.out
    
    def test_info_command(self, app):
        """Test info command execution."""
        exit_code = app.run(["info"])
        assert exit_code == 0
    
    def test_run_command(self, app):
        """Test run command with custom arguments."""
        exit_code = app.run(["run", "--host", "127.0.0.1", "--port", "8080"])
        assert exit_code == 0
    
    def test_debug_flag(self, app):
        """Test debug flag propagation."""
        assert app.settings.debug is True  # From fixture
        
        # Run with debug flag
        app.run(["--debug", "info"])
        assert app.settings.debug is True
    
    def test_invalid_command(self, app, capsys):
        """Test invalid command handling."""
        exit_code = app.run(["invalid"])
        
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out