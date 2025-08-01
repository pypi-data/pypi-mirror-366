"""Custom exceptions for DocMind."""

class DocMindError(Exception):
    """Base exception for DocMind."""
    pass

class FileNotFoundError(DocMindError):
    """File not found error."""
    pass

class UnsupportedFormatError(DocMindError):
    """Unsupported file format error."""
    pass

class FileTooLargeError(DocMindError):
    """File too large error."""
    pass

class CorruptedFileError(DocMindError):
    """Corrupted file error."""
    pass

class DependencyMissingError(DocMindError):
    """Required dependency missing error."""
    pass

class ConversionError(DocMindError):
    """General conversion error."""
    pass

class ConfigurationError(DocMindError):
    """Configuration file error."""
    pass