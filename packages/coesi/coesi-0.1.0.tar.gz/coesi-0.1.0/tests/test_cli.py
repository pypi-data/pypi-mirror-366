"""
Test cases for COESI CLI main interface.
"""

from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from src.cli import main


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_flag(self):
        """Test --version flag."""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "COESI CLI version" in result.output

    def test_help_output(self):
        """Test help output."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "COESI Platform CLI" in result.output

    def test_dev_command_with_ip_fails(self):
        """Test that dev command fails when IP is provided."""
        result = self.runner.invoke(main, ["dev", "192.168.1.1"])
        assert result.exit_code == 1
        assert "Development profile does not accept IP parameter" in result.output

    @patch("src.cli.validate_ip", return_value=True)
    @patch("src.cli.check_docker", return_value=True)
    @patch("src.cli.validate_env", return_value=True)
    @patch("src.cli.DockerComposeManager")
    @patch("os.path.exists", return_value=True)
    def test_dev_command_success(
        self,
        mock_exists,
        mock_manager,
        mock_validate_env,
        mock_check_docker,
        mock_validate_ip,
    ):
        """Test successful dev command execution."""
        mock_manager_instance = MagicMock()
        mock_manager.return_value = mock_manager_instance

        result = self.runner.invoke(main, ["dev"])

        # Should not exit with error
        assert result.exit_code == 0

        # Docker manager should be called
        mock_manager_instance.down.assert_called_once_with("dev")
        mock_manager_instance.up.assert_called_once_with("dev", build=True, detach=True)

    @patch("src.cli.validate_ip", return_value=True)
    @patch("src.cli.check_docker", return_value=True)
    @patch("src.cli.validate_env", return_value=True)
    @patch("src.cli.DockerComposeManager")
    @patch("src.cli.update_env_file")
    @patch("src.cli.load_dotenv")
    @patch("os.path.exists", return_value=True)
    def test_prod_command_with_ip(
        self,
        mock_exists,
        mock_load_dotenv,
        mock_update_env,
        mock_manager,
        mock_validate_env,
        mock_check_docker,
        mock_validate_ip,
    ):
        """Test prod command with custom IP."""
        mock_manager_instance = MagicMock()
        mock_manager.return_value = mock_manager_instance

        result = self.runner.invoke(main, ["prod", "192.168.1.100"])

        # Should not exit with error
        assert result.exit_code == 0

        # IP validation should be called
        mock_validate_ip.assert_called_once_with("192.168.1.100")

        # Docker manager should be called
        mock_manager_instance.down.assert_called_once_with("prod")
        mock_manager_instance.up.assert_called_once_with(
            "prod", build=True, detach=True
        )

    @patch("src.cli.validate_ip", return_value=False)
    def test_prod_command_invalid_ip(self, mock_validate_ip):
        """Test prod command with invalid IP."""
        result = self.runner.invoke(main, ["prod", "invalid.ip"])
        assert result.exit_code == 1

    def test_ip_command_missing_address(self):
        """Test ip command without address argument."""
        result = self.runner.invoke(main, ["ip"])
        assert result.exit_code == 2  # Click error for missing argument
