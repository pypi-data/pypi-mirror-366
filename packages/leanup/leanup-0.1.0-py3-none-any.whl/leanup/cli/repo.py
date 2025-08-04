import click
import shutil
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from leanup.repo.manager import RepoManager, LeanRepo
from leanup.cli.config import ConfigManager
from leanup.utils.custom_logger import setup_logger

logger = setup_logger("repo_cli")


@click.group()
def repo():
    """Repository management commands"""
    pass


@repo.command()
@click.argument('repository', required=True)
@click.option('--source', '-s', help='Repository source (default: from config)')
@click.option('--url', '-u', help='Complete repository URL')
@click.option('--branch', '-b', help='Branch or tag to clone')
@click.option('--force', '-f', is_flag=True, help='Replace existing directory')
@click.option('--dest-dir', '-d', help='Destination directory (default: cache dir)')
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration')
@click.pass_context
def install(ctx, repository: str, source: Optional[str], url: Optional[str], 
           branch: Optional[str], force: bool, dest_dir: Optional[str], interactive: bool):
    """Install a repository (format: owner/repo)"""
    
    config_manager = ctx.parent.obj['config']
    
    if interactive:
        # Interactive configuration
        click.echo("=== Interactive Repository Installation ===")
        
        config = config_manager.load_config()
        if not config:
            config = {
                'repo': {},
                'elan': {'auto_install': True}
            }
        
        # Repository prefix
        current_prefix = config.get('repo', {}).get('prefix', '')
        if current_prefix:
            click.echo(f"Current repository prefix: {current_prefix}")
        prefix = click.prompt('Repository prefix (user/name)', default=current_prefix or '', show_default=True)
        
        # Base URL
        current_base_url = config.get('repo', {}).get('base_url', 'https://github.com')
        base_url = click.prompt('Base URL', default=current_base_url, show_default=True)
        
        # Directory
        current_cache_dir = config.get('repo', {}).get('cache_dir', str(config_manager.get_cache_dir()))
        cache_dir = click.prompt('Cache directory', default=current_cache_dir, show_default=True)
        
        # Lake update
        current_lake_update = config.get('repo', {}).get('lake_update', True)
        lake_update = click.confirm('Execute `lake update` after clone?', default=current_lake_update)
        
        # Lake build
        current_lake_build = config.get('repo', {}).get('lake_build', True)
        lake_build = click.confirm('Execute `lake build` after clone?', default=current_lake_build)
        
        # Build packages
        build_packages = []
        if lake_build:
            current_packages = config.get('repo', {}).get('build_packages', [])
            packages_str = click.prompt(
                'Build specific packages (comma-separated, empty for all)', 
                default=','.join(current_packages) if current_packages else '',
                show_default=True
            )
            if packages_str.strip():
                build_packages = [pkg.strip() for pkg in packages_str.split(',') if pkg.strip()]
        
        # Update config
        config['repo'].update({
            'prefix': prefix,
            'base_url': base_url,
            'cache_dir': cache_dir,
            'lake_update': lake_update,
            'lake_build': lake_build,
            'build_packages': build_packages
        })
        
        if config_manager.save_config(config):
            click.echo("✓ Configuration saved")
        else:
            click.echo("✗ Failed to save configuration", err=True)
            sys.exit(1)
        
        # Update variables for installation
        if not source:
            source = base_url
        if not dest_dir:
            dest_dir = cache_dir
    
    # Validate repository format
    if '/' not in repository or repository.count('/') != 1:
        click.echo("Error: Repository must be in format 'owner/repo'", err=True)
        sys.exit(1)
    
    owner, repo_name = repository.split('/')
    
    # Determine URL
    if url:
        repo_url = url
    else:
        if not source:
            source = config_manager.get_default_source()
        repo_url = f"{source.rstrip('/')}/{repository}"
    
    # Determine destination directory
    if dest_dir:
        dest_path = Path(dest_dir)
    else:
        cache_dir = config_manager.get_cache_dir()
        # Create directory name: repo_branch or repo_main
        dir_name = f"{repo_name}_{branch}" if branch else repo_name
        dest_path = cache_dir / owner / dir_name
    
    # Check if directory exists
    if dest_path.exists():
        if not force:
            click.echo(f"Directory {dest_path} already exists. Use --force to replace.", err=True)
            sys.exit(1)
        else:
            shutil.rmtree(dest_path)
            click.echo(f"Removed existing directory: {dest_path}")
    
    # Create parent directories
    dest_path.mkdir(exist_ok=True)
    
    # Clone repository
    click.echo(f"Cloning {repo_url} to {dest_path}...")
    repo_manager = RepoManager(dest_path)
    
    success = repo_manager.clone_from(
        url=repo_url,
        branch=branch,
        depth=1  # Shallow clone for faster download
    )
    
    if success:
        click.echo(f"✓ Repository cloned successfully to {dest_path}")
        
        # Check if it's a Lean project and run post-install commands
        if (dest_path / "lakefile.lean").exists() or (dest_path / "lakefile.toml").exists():
            click.echo("📦 Detected Lean project")
            
            # Show lean-toolchain if exists
            toolchain_file = dest_path / "lean-toolchain"
            if toolchain_file.exists():
                toolchain = toolchain_file.read_text().strip()
                click.echo(f"🔧 Lean toolchain: {toolchain}")
            
            # Execute post-install commands based on config
            config = config_manager.load_config()
            lean_repo = LeanRepo(dest_path)
            
            # Lake update
            if config.get('repo', {}).get('lake_update', True):
                click.echo("Executing lake update...")
                try:
                    stdout, stderr, returncode = lean_repo.lake_update()
                    if returncode == 0:
                        click.echo("✓ lake update completed")
                    else:
                        click.echo(f"⚠ lake update failed: {stderr}", err=True)
                except Exception as e:
                    click.echo(f"⚠ lake update error: {e}", err=True)
            
            # Lake build
            if config.get('repo', {}).get('lake_build', True):
                build_packages = config.get('repo', {}).get('build_packages', [])
                if build_packages:
                    click.echo(f"Building packages: {', '.join(build_packages)}...")
                    for package in build_packages:
                        try:
                            stdout, stderr, returncode = lean_repo.lake(["build", package])
                            if returncode == 0:
                                click.echo(f"✓ Built package: {package}")
                            else:
                                click.echo(f"⚠ Failed to build package {package}: {stderr}", err=True)
                        except Exception as e:
                            click.echo(f"⚠ Build error for {package}: {e}", err=True)
                else:
                    click.echo("Building project...")
                    try:
                        stdout, stderr, returncode = lean_repo.lake_build()
                        if returncode == 0:
                            click.echo("✓ Build completed")
                        else:
                            click.echo(f"⚠ Build failed: {stderr}", err=True)
                    except Exception as e:
                        click.echo(f"⚠ Build error: {e}", err=True)
    else:
        click.echo("✗ Failed to clone repository", err=True)
        sys.exit(1)


@repo.command()
@click.option('--name', '-n', help='Filter by repository name (owner/repo)')
@click.pass_context
def list(ctx, name: Optional[str]):
    """List installed repositories"""
    config_manager = ctx.parent.obj['config']
    cache_dir = config_manager.get_cache_dir()
    
    if not cache_dir.exists():
        click.echo("No repositories found. Cache directory doesn't exist.")
        return
    
    repositories = []
    
    # Walk through cache directory
    for owner_dir in cache_dir.iterdir():
        if not owner_dir.is_dir():
            continue
            
        for repo_dir in owner_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            
            # Extract repo name and branch/tag
            repo_name_parts = repo_dir.name.split('_', 1)
            repo_name = repo_name_parts[0]
            branch_tag = repo_name_parts[1] if len(repo_name_parts) > 1 else 'main'
            
            full_name = f"{owner_dir.name}/{repo_name}"
            
            # Filter by name if specified
            if name and name != full_name:
                continue
            
            # Check if it's a git repo and get info
            repo_manager = RepoManager(repo_dir)
            is_lean_project = (repo_dir / "lakefile.lean").exists() or (repo_dir / "lakefile.toml").exists()
            
            repositories.append({
                'name': full_name,
                'branch': branch_tag,
                'path': repo_dir,
                'is_git': repo_manager.is_gitrepo,
                'is_lean': is_lean_project
            })
    
    if not repositories:
        if name:
            click.echo(f"No repository found with name: {name}")
        else:
            click.echo("No repositories found.")
        return
    
    # Display repositories
    click.echo("Installed repositories:")
    click.echo()
    
    for repo in sorted(repositories, key=lambda x: x['name']):
        status_icons = []
        if repo['is_git']:
            status_icons.append('📁')
        if repo['is_lean']:
            status_icons.append('📦')
        
        status = ' '.join(status_icons) if status_icons else '📄'
        click.echo(f"{status} {repo['name']} ({repo['branch']})")
        click.echo(f"   📍 {repo['path']}")
        click.echo()