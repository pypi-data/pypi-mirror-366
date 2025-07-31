# HyperRepo

Monorepo pattern with symlinked meta repositories for clean documentation management.

## Overview

HyperRepo solves the nested-git problem in monorepos by providing clean separation between code projects and meta-layer documentation through symlinked repositories. This allows you to maintain version control for documentation, context files, and shared resources without the complexity of git submodules or subtrees.

## Features

- **Clean Separation**: Code projects remain independent while sharing documentation
- **Version Control**: Full git history for both code and meta documentation  
- **Zero Ceremony**: Simple YAML configuration with automatic symlink management
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Template System**: Pre-built templates for common patterns

## Installation

```bash
pip install hyperepo
```

## Quick Start

1. **Initialize a new hyperepo:**
   ```bash
   hyperepo init myproject
   ```

2. **Check symlink integrity:**
   ```bash
   hyperepo check
   ```

3. **View repository status:**
   ```bash
   hyperepo status
   ```

4. **Create configured symlinks:**
   ```bash
   hyperepo create-links
   ```

## Configuration

HyperRepo uses a simple `hyperepo.yml` configuration file:

```yaml
version: "1.0"
meta_repo: "../myproject-meta"
symlinks:
  - target: "context"
    source: "context"
  - target: "prompts"
    source: "prompts"
  - target: "specs"
    source: "specifications"
```

## Directory Structure

```
myproject/
├── hyperepo.yml                    # Configuration
├── subproject-a/                   # Git submodule
├── subproject-b/                   # Git submodule  
├── context → ../myproject-meta/context        # Symlinked directories
├── prompts → ../myproject-meta/prompts
└── specs → ../myproject-meta/specifications

myproject-meta/                     # Separate git repository
├── context/
├── prompts/
└── specifications/
```

## CLI Commands

- `hyperepo init <name>` - Initialize new hyperepo structure
- `hyperepo check` - Validate symlink integrity
- `hyperepo status` - Show repository structure status  
- `hyperepo create-links` - Create all configured symlinks

## Python API

```python
from hyperepo import HyperRepo

# Initialize
repo = HyperRepo()
repo.init("../project-meta")

# Validate
issues = repo.validate_symlinks()
if not issues:
    print("All symlinks valid!")

# Create symlinks
repo.create_symlinks()
```

## Templates

HyperRepo includes built-in templates for common patterns:

- **standard**: Basic template with context, prompts, and specifications
- **ai-dev**: AI development template optimized for AI-assisted workflows

## License

MIT License - see LICENSE file for details.

## Contributing

Issues and pull requests welcome at https://github.com/tysonzero/hyperepo