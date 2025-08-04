import re
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
import requests

from leanup.const import OS_TYPE
from leanup.utils.basic import execute_command, working_directory
from leanup.utils.custom_logger import setup_logger

logger = setup_logger("elan_manager")


class ElanManager:
    """Elan toolchain manager"""

    def __init__(self):
        self.elan_home = Path(os.environ.get('ELAN_HOME', Path.home() / '.elan'))
        self.elan_bin_dir = self.elan_home / 'bin'
        
    def get_elan_executable(self) -> Optional[Path]:
        """Get elan executable file path"""
        elan_exe = 'elan.exe' if OS_TYPE == 'Windows' else 'elan'
        elan_path = self.elan_bin_dir / elan_exe
        
        if elan_path.exists() and elan_path.is_file():
            return elan_path
        
        # Try to find in PATH
        elan_in_path = shutil.which('elan')
        if elan_in_path:
            return Path(elan_in_path)
            
        return None
    
    def is_elan_installed(self) -> bool:
        """Check if elan is installed"""
        return self.get_elan_executable() is not None
    
    def get_elan_version(self) -> Optional[str]:
        """Get installed elan version"""
        elan_path = self.get_elan_executable()
        if not elan_path:
            return None
            
        try:
            output, error, code = execute_command([str(elan_path), '--version'])
            if code == 0:
                # elan 4.0.0 (bb75b50d2 2025-01-30)
                elan_regex = re.compile(r'elan\s+(\d+\.\d+\.\d+)')
                match = elan_regex.search(output)
                if match:
                    return match.group(1)
                else:
                    logger.warning(f"Failed to parse elan version from output: {output}")
            return None
        except Exception as e:
            logger.error(f"Failed to get elan version: {e}")
            return None
    
    def get_download_url(self, version: Optional[str] = None) -> str:
        """Get elan installation script download URL"""
        if OS_TYPE == 'Windows':
            # Windows uses official PowerShell script
            return "https://elan.lean-lang.org/elan-init.ps1"
        else:
            # Linux and macOS use official shell script
            return "https://elan.lean-lang.org/elan-init.sh"
    
    def download_installer(self, url: str, target_path: Path) -> bool:
        """Download elan installer"""
        try:
            logger.info(f"Downloading elan installer: {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Give execution permission to installation script
            if OS_TYPE != 'Windows':
                target_path.chmod(0o755)
                
            logger.info(f"Download completed: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download elan installer: {e}")
            return False
    
    def install_elan(self, version: Optional[str] = None, force: bool = False) -> bool:
        """Install elan with optional version specification.
        
        Args:
            version: Specific version to install (default: latest)
            force: Force reinstall even if already installed
            
        Returns:
            bool: True if installation successful, False otherwise
        """
        # Check if already installed
        if self.is_elan_installed() and not force:
            current_version = self.get_elan_version()
            logger.info(f"elan is already installed (version: {current_version})")
            if version is None or current_version == version:
                return True
            logger.info(f"Installing specified version: {version}")
        try:
            download_url = self.get_download_url(version)
            # Use working_directory context manager for temporary directory
            with working_directory() as temp_dir:
                if OS_TYPE == 'Windows':
                    # Windows uses PowerShell to run script directly from network (official recommended way)
                    logger.info("Installing elan via PowerShell...")
                    # Set environment variables for non-interactive installation
                    env = os.environ.copy()
                    env['ELAN_HOME'] = str(self.elan_home)
                    
                    # Use PowerShell to download and execute as recommended by official docs
                    script_content = f"""
                    $env:ELAN_HOME = "{self.elan_home}"
                    Invoke-WebRequest -Uri "https://elan.lean-lang.org/elan-init.ps1" -OutFile "elan-init.ps1"
                    & .\\elan-init.ps1 -y
                    Remove-Item "elan-init.ps1" -ErrorAction SilentlyContinue
                    """
                    
                    cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', script_content]
                else:
                    # Linux/macOS use shell script installation
                    installer_path = temp_dir / 'elan-init.sh'
                    if not self.download_installer(download_url, installer_path):
                        return False
                    
                    logger.info("Running elan installation script...")
                    # Set environment variables for non-interactive installation
                    env = os.environ.copy()
                    env['ELAN_HOME'] = str(self.elan_home)
                    
                    cmd = ['sh', str(installer_path), '-y']
                output, error, code = execute_command(cmd, cwd=str(temp_dir))
                if code != 0:
                    logger.error(f"Installation failed: {error}")
                    return False
                
                # Verify installation
                if self.is_elan_installed():
                    installed_version = self.get_elan_version()
                    logger.info(f"elan installed successfully! Version: {installed_version}")
                    return True
                else:
                    logger.error("Installation completed, but elan executable not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Error occurred during elan installation: {e}")
            return False
    
    def proxy_elan_command(self, args: List[str]) -> int:
        """Proxy execute elan command with streaming output"""
        elan_path = self.get_elan_executable()
        
        if not elan_path:
            self.install_elan()
        
        # Build complete command
        cmd = [str(elan_path)] + args
        
        try:
            # Pass directly to subprocess to maintain interactivity and streaming
            result = subprocess.run(cmd, check=False)
            return result.returncode
        except Exception as e:
            logger.error(f"Failed to execute elan command: {e}")
            return 1
    
    def get_installed_toolchains(self) -> List[str]:
        """Get list of installed toolchains"""
        elan_path = self.get_elan_executable()
        if not elan_path:
            return []
        
        try:
            output, error, code = execute_command([str(elan_path), 'toolchain', 'list'])
            if code == 0:
                toolchains = []
                for line in output.strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Remove status markers (like (default))
                        toolchain = line.split()[0]
                        toolchains.append(toolchain)
                return toolchains
            return []
        except Exception as e:
            logger.error(f"Failed to get toolchain list: {e}")
            return []
    
    def get_status_info(self) -> Dict[str, any]:
        """Get elan status information"""
        info = {
            'installed': self.is_elan_installed(),
            'version': None,
            'elan_home': str(self.elan_home),
            'executable': None,
            'toolchains': []
        }
        
        if info['installed']:
            info['version'] = self.get_elan_version()
            info['executable'] = str(self.get_elan_executable())
            info['toolchains'] = self.get_installed_toolchains()
        
        return info
