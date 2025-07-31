from pathlib import Path
from typing import Dict, Any, List
from abc import ABC, abstractmethod


class TemplateError(Exception):
    """Exception raised for template-related issues."""
    pass


class Template(ABC):
    """Base class for HyperRepo templates."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Return default hyperepo.yml configuration for this template."""
        pass
    
    @abstractmethod
    def get_meta_structure(self) -> List[str]:
        """Return list of directories/files to create in meta repository."""
        pass
    
    def apply(self, hyperepo_root: Path, meta_repo_root: Path) -> None:
        """Apply template to create structure."""
        # Create meta repository structure
        for item in self.get_meta_structure():
            path = meta_repo_root / item
            if item.endswith('/'):
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.touch()


class StandardTemplate(Template):
    """Standard HyperRepo template with common directories."""
    
    def __init__(self):
        super().__init__(
            "standard",
            "Standard template with context, prompts, and specifications"
        )
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "symlinks": [
                {"target": "context", "source": "context"},
                {"target": "prompts", "source": "prompts"},
                {"target": "specs", "source": "specifications"}
            ]
        }
    
    def get_meta_structure(self) -> List[str]:
        return [
            "context/",
            "context/README.md",
            "prompts/",
            "prompts/README.md", 
            "specifications/",
            "specifications/README.md"
        ]


class AIDevTemplate(Template):
    """Template optimized for AI-assisted development workflows."""
    
    def __init__(self):
        super().__init__(
            "ai-dev",
            "AI development template with context, prompts, and documentation"
        )
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "symlinks": [
                {"target": "context", "source": "context"},
                {"target": "prompts", "source": "prompts"},
                {"target": "docs", "source": "documentation"},
                {"target": "examples", "source": "examples"}
            ]
        }
    
    def get_meta_structure(self) -> List[str]:
        return [
            "context/",
            "context/system.md",
            "context/project.md",
            "prompts/",
            "prompts/development.md",
            "prompts/debugging.md",
            "documentation/",
            "documentation/architecture.md",
            "documentation/api.md",
            "examples/",
            "examples/usage.md"
        ]


TEMPLATES = {
    "standard": StandardTemplate(),
    "ai-dev": AIDevTemplate()
}