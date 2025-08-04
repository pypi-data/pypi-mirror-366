import pytest
from unittest.mock import patch, Mock, mock_open
from pathlib import Path
import tempfile
import os

from leanup.repo.manager import LeanRepo


class TestLeanRepo:
    """Test cases for LeanRepo class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.lean_repo = LeanRepo(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_lean_toolchain_exists(self):
        """Test reading lean-toolchain file when it exists"""
        toolchain_content = "leanprover/lean4:v4.3.0"
        toolchain_file = Path(self.temp_dir) / "lean-toolchain"
        toolchain_file.write_text(toolchain_content)
        
        result = self.lean_repo.get_lean_toolchain()
        assert result == toolchain_content
    
    def test_parse_dependencies_lean(self):
        """Test parsing dependencies from lakefile.lean"""
        lakefile_content = '''
require mathlib from git "https://github.com/leanprover-community/mathlib4" @ "main"
require std from git "https://github.com/leanprover/std4" @ "v4.3.0"
'''
        lakefile = Path(self.temp_dir) / "lakefile.lean"
        lakefile.write_text(lakefile_content)
        
        result = self.lean_repo.parse_dependencies()
        
        assert 'mathlib' in result
        assert 'std' in result
        assert result['mathlib']['git'] == 'https://github.com/leanprover-community/mathlib4'
        assert result['mathlib']['rev'] == 'main'
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_command(self, mock_execute):
        """Test basic lake command execution"""
        mock_execute.return_value = ('output', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake(['build'])
        
        mock_execute.assert_called_once_with(['lake', 'build'], cwd=self.temp_dir)
        assert stdout == 'output'
        assert returncode == 0
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_build(self, mock_execute):
        """Test lake build command"""
        mock_execute.return_value = ('build successful', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake_build()
        
        mock_execute.assert_called_once_with(['lake', 'build'], cwd=self.temp_dir)
        assert returncode == 0
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_build_with_target(self, mock_execute):
        """Test lake build command with target"""
        mock_execute.return_value = ('build successful', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake_build('MyLib')
        
        mock_execute.assert_called_once_with(['lake', 'build', 'MyLib'], cwd=self.temp_dir)
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_update(self, mock_execute):
        """Test lake update command"""
        mock_execute.return_value = ('update successful', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake_update()
        
        mock_execute.assert_called_once_with(['lake', 'update'], cwd=self.temp_dir)
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_env_lean_with_js(self, mock_execute):
        """Test lake env lean command with JS backend"""
        mock_execute.return_value = ('lean output', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake_env_lean('Main.lean', json=True)
        
        mock_execute.assert_called_once_with(['lake', 'env', 'lean', '--json', 'Main.lean'], cwd=self.temp_dir)
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_env_lean_without_js(self, mock_execute):
        """Test lake env lean command without JS backend"""
        mock_execute.return_value = ('lean output', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake_env_lean('Main.lean', json=False)
        
        mock_execute.assert_called_once_with(['lake', 'env', 'lean', 'Main.lean'], cwd=self.temp_dir)
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_clean(self, mock_execute):
        """Test lake clean command"""
        mock_execute.return_value = ('clean successful', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake_clean()
        
        mock_execute.assert_called_once_with(['lake', 'clean'], cwd=self.temp_dir)
    
    @patch('leanup.repo.manager.execute_command')
    def test_lake_test(self, mock_execute):
        """Test lake test command"""
        mock_execute.return_value = ('tests passed', '', 0)
        
        stdout, stderr, returncode = self.lean_repo.lake_test()
        
        mock_execute.assert_called_once_with(['lake', 'test'], cwd=self.temp_dir)
    
    def test_get_project_info(self):
        """Test getting project information"""
        # Create some files
        (Path(self.temp_dir) / "lean-toolchain").write_text("leanprover/lean4:v4.3.0")
        (Path(self.temp_dir) / "lakefile.toml").write_text("[package]\nname = 'test'")
        (Path(self.temp_dir) / ".lake").mkdir()
        
        info = self.lean_repo.get_project_info()
        
        assert info['lean_version'] == "leanprover/lean4:v4.3.0"
        assert info['has_lakefile_toml'] is True
        assert info['has_lakefile_lean'] is False
        assert info['build_dir_exists'] is True