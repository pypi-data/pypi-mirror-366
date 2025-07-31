import click
import sys
from pathlib import Path
from typing import Optional
from .core import HyperRepo
from .exceptions import HyperRepoError


@click.group()
@click.version_option(version="0.0.1")
def cli():
    """HyperRepo: Monorepo pattern with symlinked meta repositories."""
    pass


@cli.command()
@click.argument('name')
@click.option('--meta-repo', '-m', default="../{name}-meta", 
              help='Path to meta repository (default: ../{name}-meta)')
@click.option('--root', '-r', type=click.Path(exists=True, file_okay=False), 
              help='Root directory for hyperepo (default: current directory)')
def init(name: str, meta_repo: str, root: Optional[str]):
    """Initialize a new hyperepo structure."""
    try:
        root_path = Path(root) if root else Path.cwd()
        meta_repo_path = meta_repo.format(name=name)
        
        hyperepo = HyperRepo(root_path)
        hyperepo.init(meta_repo_path)
        
        click.echo(f"✅ Initialized hyperepo '{name}' at {root_path}")
        click.echo(f"📁 Meta repository: {meta_repo_path}")
        click.echo(f"📄 Configuration saved to: {hyperepo.config_path}")
        
    except HyperRepoError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--root', '-r', type=click.Path(exists=True, file_okay=False),
              help='Root directory of hyperepo (default: current directory)')
def check(root: Optional[str]):
    """Validate symlink integrity and repository structure."""
    try:
        root_path = Path(root) if root else Path.cwd()
        hyperepo = HyperRepo(root_path)
        
        issues = hyperepo.validate_symlinks()
        
        if not issues:
            click.echo("✅ All symlinks are valid")
        else:
            click.echo("❌ Issues found:")
            for issue in issues:
                click.echo(f"  - {issue}")
            sys.exit(1)
            
    except HyperRepoError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--root', '-r', type=click.Path(exists=True, file_okay=False),
              help='Root directory of hyperepo (default: current directory)')
def status(root: Optional[str]):
    """Show repository structure status."""
    try:
        root_path = Path(root) if root else Path.cwd()
        hyperepo = HyperRepo(root_path)
        
        status_info = hyperepo.status()
        
        click.echo(f"📁 Root: {status_info['root']}")
        click.echo(f"📄 Config: {'✅' if status_info['config_exists'] else '❌'}")
        
        meta = status_info['meta_repo']
        click.echo(f"🔗 Meta repo: {meta['path']}")
        click.echo(f"   Exists: {'✅' if meta['exists'] else '❌'}")
        click.echo(f"   Valid: {'✅' if meta['valid'] else '❌'}")
        
        symlinks = status_info['symlinks']
        click.echo(f"🔗 Symlinks: {symlinks['configured']} configured")
        
        if symlinks['issues']:
            click.echo("❌ Issues:")
            for issue in symlinks['issues']:
                click.echo(f"  - {issue}")
        else:
            click.echo("✅ All symlinks OK")
            
    except HyperRepoError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--root', '-r', type=click.Path(exists=True, file_okay=False),
              help='Root directory of hyperepo (default: current directory)')
def create_links(root: Optional[str]):
    """Create all configured symlinks."""
    try:
        root_path = Path(root) if root else Path.cwd()
        hyperepo = HyperRepo(root_path)
        
        hyperepo.create_symlinks()
        click.echo("✅ Symlinks created successfully")
        
    except HyperRepoError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()