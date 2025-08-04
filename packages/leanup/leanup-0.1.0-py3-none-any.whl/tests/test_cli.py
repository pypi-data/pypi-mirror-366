import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from leanup.const import OS_TYPE
from leanup.cli import cli
from leanup.cli.config import ConfigManager


class TestCLI:
    """Test CLI commands"""
    
    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'LeanUp - Lean project management tool' in result.output
    
    @patch('leanup.cli.ConfigManager')
    @patch('leanup.cli.ElanManager')
    def test_init_command(self, mock_elan_manager, mock_config_manager):
        """Test init command"""
        # Mock config manager
        mock_config = Mock()
        mock_config.init_config.return_value = True
        mock_config_manager.return_value = mock_config
        
        # Mock elan manager
        mock_elan = Mock()
        mock_elan.is_elan_installed.return_value = False
        mock_elan.install_elan.return_value = True
        mock_elan_manager.return_value = mock_elan
        
        result = self.runner.invoke(cli, ['init'])
        
        assert result.exit_code == 0
        assert '✓ Initialized .leanup/config.yaml' in result.output
        assert '✓ elan installed successfully' in result.output
        mock_config.init_config.assert_called_once()
        mock_elan.install_elan.assert_called_once()
    
    @patch('leanup.cli.ElanManager')
    def test_install_command_latest(self, mock_elan_manager):
        """Test install command for latest version"""
        mock_elan = Mock()
        mock_elan.is_elan_installed.return_value = True
        mock_elan.proxy_elan_command.return_value = iter(['Installing...\n', 'Done\n'])
        mock_elan_manager.return_value = mock_elan
        
        result = self.runner.invoke(cli, ['install'])
        
        if result.exit_code == 0:
            assert 'Installing latest Lean toolchain...' in result.output
    
    @patch('leanup.cli.ElanManager')
    def test_install_command_specific_version(self, mock_elan_manager):
        """Test install command for specific version"""
        mock_elan = Mock()
        mock_elan.is_elan_installed.return_value = True
        mock_elan.proxy_elan_command.return_value = iter(['Installing v4.10.0...\n', 'Done\n'])
        mock_elan_manager.return_value = mock_elan
        
        result = self.runner.invoke(cli, ['install', 'v4.10.0'])
        
        if result.exit_code == 0:
            assert 'Installing Lean toolchain v4.10.0...' in result.output
            mock_elan.proxy_elan_command.assert_called_once_with(['toolchain', 'install', 'v4.10.0'])
    
    @patch('leanup.cli.ElanManager')
    def test_install_command_elan_not_installed(self, mock_elan_manager):
        """Test install command when elan is not installed"""
        mock_elan = Mock()
        mock_elan.is_elan_installed.return_value = False
        mock_elan_manager.return_value = mock_elan
        
        result = self.runner.invoke(cli, ['install'])
        
        if result.exit_code == 0:
            assert 'Installing latest Lean toolchain...' in result.output
    
    @patch('leanup.cli.ConfigManager')
    @patch('leanup.cli.ElanManager')
    @pytest.mark.skipif(OS_TYPE == 'Windows', reason="Windows path separator issue")
    def test_status_command(self, mock_elan_manager, mock_config_manager):
        """Test status command"""
        # Mock config manager
        mock_config = Mock()
        mock_config.config_exists.return_value = True
        mock_config.config_path = Path('/test/.leanup/config.yaml')
        mock_config_manager.return_value = mock_config
        
        # Mock elan manager
        mock_elan = Mock()
        mock_elan.is_elan_installed.return_value = True
        mock_elan.get_elan_version.return_value = '4.0.0'
        mock_elan.get_installed_toolchains.return_value = ['leanprover/lean4:v4.10.0', 'leanprover/lean4:v4.9.0']
        mock_elan_manager.return_value = mock_elan
        
        result = self.runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert '=== LeanUp Status ===' in result.output
        assert 'elan: ✓ installed (version: 4.0.0)' in result.output
        assert 'leanprover/lean4:v4.10.0, leanprover/lean4:v4.9.0' in result.output
        assert 'Config: ✓ /test/.leanup/config.yaml' in result.output
    
    @patch('leanup.cli.ElanManager')
    def test_elan_proxy_command(self, mock_elan_manager):
        """Test elan proxy command"""
        mock_elan = Mock()
        mock_elan.is_elan_installed.return_value = True
        mock_elan.proxy_elan_command.return_value = iter(['toolchain list output\n'])
        mock_elan_manager.return_value = mock_elan
        
        result = self.runner.invoke(cli, ['elan', 'toolchain', 'list'])
        
    
    @patch('leanup.cli.ElanManager')
    def test_elan_proxy_command_not_installed(self, mock_elan_manager):
        """Test elan proxy command when elan is not installed"""
        mock_elan = Mock()
        mock_elan.is_elan_installed.return_value = False
        mock_elan_manager.return_value = mock_elan
        
        result = self.runner.invoke(cli, ['elan', 'toolchain', 'list'])
        
