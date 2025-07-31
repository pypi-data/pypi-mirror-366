"""
HyperRepo: Monorepo pattern with symlinked meta repositories.

Provides clean separation between code projects and meta-layer documentation
through symlinked repositories, solving the nested-git problem in complex
development environments.
"""

__version__ = "0.0.1"
__author__ = "Tyson"

from .core import HyperRepo, MetaRepo
from .exceptions import HyperRepoError, SymlinkError

__all__ = ["HyperRepo", "MetaRepo", "HyperRepoError", "SymlinkError"]