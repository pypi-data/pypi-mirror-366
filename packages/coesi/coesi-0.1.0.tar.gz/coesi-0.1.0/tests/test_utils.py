"""
Test cases for COESI CLI utility functions.
"""

from unittest.mock import patch, mock_open
from src.utils import validate_ip, update_env_file


class TestIPValidation:
    """Test IP address validation functionality."""

    def test_valid_localhost(self):
        """Test that localhost is valid."""
        assert validate_ip("localhost") is True

    def test_valid_127_0_0_1(self):
        """Test that 127.0.0.1 is valid."""
        assert validate_ip("127.0.0.1") is True

    def test_valid_ipv4(self):
        """Test valid IPv4 addresses."""
        assert validate_ip("192.168.1.1") is True
        assert validate_ip("10.0.0.1") is True
        assert validate_ip("172.16.0.1") is True

    def test_invalid_format(self):
        """Test invalid IP formats."""
        assert validate_ip("not.an.ip") is False
        assert validate_ip("256.1.1.1") is False
        assert validate_ip("1.1.1") is False
        assert validate_ip("1.1.1.1.1") is False

    def test_invalid_ranges(self):
        """Test invalid IP ranges."""
        assert validate_ip("0.0.0.1") is False  # Reserved range
        assert validate_ip("224.0.0.1") is False  # Multicast range


class TestEnvFileUpdate:
    """Test environment file update functionality."""

    @patch(
        "builtins.open", new_callable=mock_open, read_data="KEY1=value1\nKEY2=value2\n"
    )
    @patch("os.path.exists", return_value=True)
    def test_update_existing_key(self, mock_exists, mock_file):
        """Test updating an existing key in env file."""
        update_env_file(".env", "KEY1", "new_value")

        # Check that file was written with updated value
        mock_file().writelines.assert_called_once()
        written_lines = mock_file().writelines.call_args[0][0]
        assert "KEY1=new_value\n" in written_lines
        assert "KEY2=value2\n" in written_lines

    @patch("builtins.open", new_callable=mock_open, read_data="KEY1=value1\n")
    @patch("os.path.exists", return_value=True)
    def test_add_new_key(self, mock_exists, mock_file):
        """Test adding a new key to env file."""
        update_env_file(".env", "NEW_KEY", "new_value")

        # Check that file was written with new key added
        mock_file().writelines.assert_called_once()
        written_lines = mock_file().writelines.call_args[0][0]
        assert "KEY1=value1\n" in written_lines
        assert "NEW_KEY=new_value\n" in written_lines

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)
    def test_create_new_file(self, mock_exists, mock_file):
        """Test creating a new env file."""
        update_env_file(".env", "KEY", "value")

        # Check that file was created with the key-value pair
        mock_file().write.assert_called_once_with("KEY=value\n")
