import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch

from leanup.cli.config import ConfigManager
from leanup.const import LEANUP_CACHE_DIR, LEANUP_CONFIG_DIR


class TestConfigManager:
    """Test ConfigManager class"""
    
    def test_init_default_config_dir(self):
        """Test ConfigManager initialization with default config directory"""
        config_manager = ConfigManager()
        assert config_manager.config_dir == LEANUP_CONFIG_DIR
        assert config_manager.config_path == config_manager.config_dir / 'config.yaml'
    
    def test_init_custom_config_dir(self):
        """Test ConfigManager initialization with custom config directory"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir) / 'custom_config'
            config_manager = ConfigManager(config_dir=custom_dir)
            assert config_manager.config_dir == custom_dir
            assert config_manager.config_path == custom_dir / 'config.yaml'
    
    def test_config_exists_false(self):
        """Test config_exists when config file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_manager = ConfigManager(config_dir=Path(tmp_dir))
            assert not config_manager.config_exists()
    
    def test_config_exists_true(self):
        """Test config_exists when config file exists"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir)
            config_file = config_dir / 'config.yaml'
            config_file.touch()
            
            config_manager = ConfigManager(config_dir=config_dir)
            assert config_manager.config_exists()
    
    def test_init_config(self):
        """Test config initialization"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_manager = ConfigManager(config_dir=Path(tmp_dir))
            
            result = config_manager.init_config()
            
            assert result is True
            assert config_manager.config_exists()
            
            # Check config content
            with open(config_manager.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            assert 'repo' in config
            assert 'elan' in config
            assert config['repo']['default_source'] == 'https://github.com'
            assert config['elan']['auto_install'] is True
    
    def test_load_config_nonexistent(self):
        """Test loading config when file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_manager = ConfigManager(config_dir=Path(tmp_dir))
            config = config_manager.load_config()
            assert config == {}
    
    def test_load_config_existing(self):
        """Test loading existing config"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir)
            config_file = config_dir / 'config.yaml'
            
            test_config = {
                'repo': {'default_source': 'https://example.com'},
                'elan': {'auto_install': False}
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(test_config, f)
            
            config_manager = ConfigManager(config_dir=config_dir)
            config = config_manager.load_config()
            
            assert config == test_config
    
    def test_save_config(self):
        """Test saving config"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_manager = ConfigManager(config_dir=Path(tmp_dir))
            
            test_config = {
                'repo': {'prefix': 'test'},
                'elan': {'auto_install': True}
            }
            
            result = config_manager.save_config(test_config)
            
            assert result is True
            assert config_manager.config_exists()
            
            # Verify saved content
            with open(config_manager.config_path, 'r') as f:
                saved_config = yaml.safe_load(f)
            
            assert saved_config == test_config
    
    def test_get_config_value(self):
        """Test getting config values"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir)
            config_file = config_dir / 'config.yaml'
            
            test_config = {
                'repo': {
                    'default_source': 'https://example.com',
                    'cache_dir': str(Path(tmp_dir) / 'cache')
                },
                'elan': {'auto_install': False}
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(test_config, f)
            
            config_manager = ConfigManager(config_dir=config_dir)
            
            assert config_manager.get('repo.default_source') == 'https://example.com'
            assert config_manager.get('repo.cache_dir') == str(Path(tmp_dir) / 'cache')
            assert config_manager.get('elan.auto_install') is False
            assert config_manager.get('nonexistent.key', 'default') == 'default'
    
    def test_get_cache_dir_default(self):
        """Test getting cache directory with default value"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('leanup.cli.config.LEANUP_CACHE_DIR', Path(tmp_dir) / 'test_cache'):
                config_manager = ConfigManager(config_dir=Path(tmp_dir))
                cache_dir = config_manager.get_cache_dir()
                
                # Should return default cache dir with repos subdirectory
                expected = Path(tmp_dir) / 'test_cache' / 'repos'
                assert cache_dir == expected
    
    def test_get_cache_dir_from_config(self):
        """Test getting cache directory from config"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir)
            config_file = config_dir / 'config.yaml'
            custom_cache = Path(tmp_dir) / 'custom_cache'
            
            test_config = {
                'repo': {'cache_dir': str(custom_cache)}
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(test_config, f)
            
            config_manager = ConfigManager(config_dir=config_dir)
            cache_dir = config_manager.get_cache_dir()
            
            assert cache_dir == custom_cache
    
    def test_get_default_source(self):
        """Test getting default source"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_manager = ConfigManager(config_dir=Path(tmp_dir))
            source = config_manager.get_default_source()
            
            # Should return default GitHub URL
            assert source == 'https://github.com'