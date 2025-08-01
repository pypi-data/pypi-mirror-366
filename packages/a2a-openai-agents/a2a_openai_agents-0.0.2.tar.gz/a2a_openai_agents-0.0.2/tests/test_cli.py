"""Tests for CLI functionality."""

import pytest
from unittest.mock import patch, Mock
import sys
from io import StringIO

from a2a_openai_agents.cli import main


class TestCLI:
    """Test CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        with patch('sys.argv', ['a2a-agents', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_cli_version(self):
        """Test CLI version output."""
        with patch('sys.argv', ['a2a-agents', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_cli_no_command(self):
        """Test CLI with no command shows help."""
        with patch('sys.argv', ['a2a-agents']):
            with patch('argparse.ArgumentParser.print_help') as mock_help:
                main()
                mock_help.assert_called_once()

    @patch('a2a_openai_agents.cli.run_weather_agent')
    def test_weather_command(self, mock_run_weather):
        """Test weather command execution."""
        with patch('sys.argv', ['a2a-agents', 'weather', '--port', '8888']):
            with patch('builtins.print'):  # Suppress output
                main()

        # Verify weather agent was called with correct port
        mock_run_weather.assert_called_once_with(8888)

    @patch('a2a_openai_agents.cli.run_math_agent')
    def test_math_command(self, mock_run_math):
        """Test math command execution."""
        with patch('sys.argv', ['a2a-agents', 'math', '--port', '8999']):
            with patch('builtins.print'):  # Suppress output
                main()

        # Verify math agent was called with correct port
        mock_run_math.assert_called_once_with(8999)

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_multi_agent_command(self, mock_exists, mock_subprocess):
        """Test multi-agent command execution."""
        # Mock that the script exists
        mock_exists.return_value = True

        with patch('sys.argv', ['a2a-agents', 'multi-agent']):
            with patch('builtins.print'):  # Suppress output
                main()

        # Verify subprocess was called
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == sys.executable
        assert 'working_multi_agent.py' in call_args[1]

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_multi_agent_command_file_not_found(self, mock_exists, mock_subprocess):
        """Test multi-agent command when file doesn't exist."""
        # Mock that the script doesn't exist
        mock_exists.return_value = False

        with patch('sys.argv', ['a2a-agents', 'multi-agent']):
            with patch('builtins.print'):  # Suppress output
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 1
        mock_subprocess.assert_not_called()

    def test_keyboard_interrupt_handling(self):
        """Test keyboard interrupt handling."""
        with patch('sys.argv', ['a2a-agents', 'weather']):
            with patch('a2a_openai_agents.cli.run_weather_agent') as mock_run:
                mock_run.side_effect = KeyboardInterrupt()
                with patch('builtins.print') as mock_print:
                    main()
                
                # Check that the interrupt was handled gracefully
                mock_print.assert_called_with("\nweather agent stopped")

    @patch('a2a_openai_agents.cli.run_weather_agent')
    def test_import_error_handling_weather(self, mock_run_weather):
        """Test import error handling in weather command."""
        mock_run_weather.side_effect = ImportError("Test import error")
        
        with patch('sys.argv', ['a2a-agents', 'weather']):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1
                # Check that error message was printed
                mock_print.assert_any_call("Error: Required dependencies not installed: Test import error")

    @patch('a2a_openai_agents.cli.run_math_agent')
    def test_import_error_handling_math(self, mock_run_math):
        """Test import error handling in math command."""
        mock_run_math.side_effect = ImportError("Test import error")
        
        with patch('sys.argv', ['a2a-agents', 'math']):
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1
                # Check that error message was printed
                mock_print.assert_any_call("Error: Required dependencies not installed: Test import error")