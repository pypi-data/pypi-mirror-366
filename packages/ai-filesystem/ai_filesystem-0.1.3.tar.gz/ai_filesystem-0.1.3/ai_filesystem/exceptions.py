class FilesystemError(Exception):
    """Base exception for filesystem operations."""
    pass

class PathNotFoundError(FilesystemError):
    """Raised when a path is not found."""
    pass

class FileNotFoundInFilesystemError(FilesystemError):
    """Raised when a file is not found."""
    pass

class FileAlreadyExistsError(FilesystemError):
    """Raised when trying to create a file that already exists."""
    pass

class AuthenticationError(FilesystemError):
    """Raised when authentication fails."""
    pass