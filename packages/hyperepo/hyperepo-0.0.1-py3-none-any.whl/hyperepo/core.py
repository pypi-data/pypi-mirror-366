import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from .exceptions import HyperRepoError, SymlinkError, ConfigError, ValidationError


class MetaRepo:
    """Represents a meta repository containing documentation and context."""
    
    def __init__(self, path: Path):
        self.path = Path(path).resolve()
        
    def exists(self) -> bool:
        """Check if the meta repository exists."""
        return self.path.exists() and self.path.is_dir()
    
    def validate(self) -> bool:
        """Validate that the meta repository is properly structured."""
        if not self.exists():
            return False
        
        git_dir = self.path / ".git"
        return git_dir.exists()


class HyperRepo:
    """Main class for managing hyperepo structure with symlinked meta repositories."""
    
    CONFIG_FILE = "hyperepo.yml"
    
    def __init__(self, root_path: Optional[Path] = None):
        self.root = Path(root_path or Path.cwd()).resolve()
        self.config_path = self.root / self.CONFIG_FILE
        self._config: Optional[Dict[str, Any]] = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Load and return configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from hyperepo.yml."""
        if not self.config_path.exists():
            raise ConfigError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                raise ConfigError("Configuration must be a YAML dictionary")
            
            return config
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in configuration: {e}")
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to hyperepo.yml."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            self._config = config
        except (IOError, yaml.YAMLError) as e:
            raise ConfigError(f"Failed to save configuration: {e}")
    
    def init(self, meta_repo_path: str, symlinks: Optional[List[Dict[str, str]]] = None) -> None:
        """Initialize a new hyperepo structure."""
        if self.config_path.exists():
            raise ConfigError(f"HyperRepo already initialized at {self.root}")
        
        config = {
            "version": "1.0",
            "meta_repo": meta_repo_path,
            "symlinks": symlinks or [
                {"target": "context", "source": "context"},
                {"target": "prompts", "source": "prompts"},
                {"target": "specs", "source": "specifications"}
            ]
        }
        
        self._save_config(config)
    
    def get_meta_repo(self) -> MetaRepo:
        """Get the meta repository instance."""
        meta_path = Path(self.config["meta_repo"])
        if not meta_path.is_absolute():
            meta_path = self.root / meta_path
        return MetaRepo(meta_path)
    
    def create_symlinks(self) -> None:
        """Create all configured symlinks."""
        meta_repo = self.get_meta_repo()
        
        if not meta_repo.exists():
            raise SymlinkError(f"Meta repository not found: {meta_repo.path}")
        
        for link_config in self.config.get("symlinks", []):
            target = link_config["target"]
            source = link_config["source"]
            
            self._create_symlink(target, meta_repo.path / source)
    
    def _create_symlink(self, target_name: str, source_path: Path) -> None:
        """Create a single symlink."""
        target_path = self.root / target_name
        
        if target_path.exists():
            if target_path.is_symlink():
                if target_path.resolve() == source_path.resolve():
                    return  # Already correctly linked
                target_path.unlink()
            else:
                raise SymlinkError(f"Target exists and is not a symlink: {target_path}")
        
        if not source_path.exists():
            raise SymlinkError(f"Source path does not exist: {source_path}")
        
        try:
            target_path.symlink_to(source_path)
        except OSError as e:
            raise SymlinkError(f"Failed to create symlink {target_path} -> {source_path}: {e}")
    
    def validate_symlinks(self) -> List[str]:
        """Validate all symlinks and return list of issues."""
        issues = []
        meta_repo = self.get_meta_repo()
        
        if not meta_repo.exists():
            issues.append(f"Meta repository not found: {meta_repo.path}")
            return issues
        
        for link_config in self.config.get("symlinks", []):
            target = link_config["target"]
            source = link_config["source"]
            
            target_path = self.root / target
            source_path = meta_repo.path / source
            
            if not target_path.exists():
                issues.append(f"Symlink missing: {target}")
            elif not target_path.is_symlink():
                issues.append(f"Target is not a symlink: {target}")
            elif target_path.resolve() != source_path.resolve():
                issues.append(f"Symlink points to wrong location: {target}")
            elif not source_path.exists():
                issues.append(f"Source path missing: {source_path}")
        
        return issues
    
    def status(self) -> Dict[str, Any]:
        """Get repository status information."""
        meta_repo = self.get_meta_repo()
        
        return {
            "root": str(self.root),
            "config_exists": self.config_path.exists(),
            "meta_repo": {
                "path": str(meta_repo.path),
                "exists": meta_repo.exists(),
                "valid": meta_repo.validate()
            },
            "symlinks": {
                "configured": len(self.config.get("symlinks", [])),
                "issues": self.validate_symlinks()
            }
        }