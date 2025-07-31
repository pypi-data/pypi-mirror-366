class HyperRepoError(Exception):
    """Base exception for HyperRepo operations."""
    pass


class SymlinkError(HyperRepoError):
    """Exception raised when symlink operations fail."""
    pass


class ConfigError(HyperRepoError):
    """Exception raised for configuration-related issues."""
    pass


class ValidationError(HyperRepoError):
    """Exception raised when repository validation fails."""
    pass