"""
Interfaces package for dependency injection and abstraction.
"""

from .file_system import FileSystemInterface, RealFileSystem, MockFileSystem

__all__ = [
    'FileSystemInterface',
    'RealFileSystem', 
    'MockFileSystem'
]