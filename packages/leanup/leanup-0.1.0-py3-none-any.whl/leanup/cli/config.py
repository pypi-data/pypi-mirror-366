import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from leanup.utils.custom_logger import setup_logger
from leanup.const import LEANUP_CACHE_DIR, LEANUP_CONFIG_DIR

logger = setup_logger("config_manager")


class ConfigManager:
    """Manage leanup configuration"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config manager
        
        Args:
            config_dir: Custom config directory (default: LEANUP_CONFIG_DIR)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = LEANUP_CONFIG_DIR
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_path = self.config_dir / "config.yaml"
        self._config = None
    
    def config_exists(self) -> bool:
        """Check if config file exists"""
        return self.config_path.exists()
    
    def init_config(self) -> bool:
        """Initialize config file with default settings"""
        try:
            # Create config directory
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Default config
            default_config = {
                'repo': {
                    'default_source': 'https://github.com',
                    'cache_dir': str(LEANUP_CACHE_DIR / 'repos'),
                    'prefix': '',
                    'base_url': 'https://github.com',
                    'lake_update': True,
                    'lake_build': True,
                    'build_packages': []
                },
                'elan': {
                    'auto_install': True
                }
            }
            
            # Write config file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            logger.info(f"Config initialized at {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize config: {e}")
            return False
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save config to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            self._config = config
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Load config from file"""
        if self._config is not None:
            return self._config
        
        if not self.config_exists():
            logger.warning("Config file not found, using defaults")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            return self._config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key (supports dot notation)"""
        config = self.load_config()
        keys = key.split('.')
        
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_cache_dir(self) -> Path:
        """Get repository cache directory"""
        cache_dir = self.get('repo.cache_dir', str(LEANUP_CACHE_DIR / 'repos'))
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    def get_default_source(self) -> str:
        """Get default repository source"""
        return self.get('repo.default_source', 'https://github.com')