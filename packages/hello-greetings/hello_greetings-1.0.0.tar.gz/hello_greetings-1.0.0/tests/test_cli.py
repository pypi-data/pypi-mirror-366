"""
Tests for the halo CLI module.
"""

import pytest
import sys
from io import StringIO
from unittest.mock import patch
from halo.cli import main


def test_main_with_argument(capsys):
    """Test main function with a command line argument."""
    with patch.object(sys, 'argv', ['halo', 'World']):
        main()
        captured = capsys.readouterr()
        assert captured.out.strip() == 'hello World'


def test_main_with_interactive_input(capsys):
    """Test main function with interactive input."""
    with patch.object(sys, 'argv', ['halo']):
        with patch('builtins.input', return_value='Universe'):
            main()
            captured = capsys.readouterr()
            assert captured.out.strip() == 'hello Universe'


def test_main_keyboard_interrupt():
    """Test main function handles keyboard interrupt gracefully."""
    with patch.object(sys, 'argv', ['halo']):
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
