"""
File System Abstraction Interface
Provides an abstraction layer for file system operations to enable testing
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any
import json


class FileSystemInterface(ABC):
    """Abstract interface for file system operations"""
    
    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if a path exists"""
        pass
    
    @abstractmethod
    def read_text(self, path: Path, encoding: str = 'utf-8') -> str:
        """Read text content from a file"""
        pass
    
    @abstractmethod
    def write_text(self, path: Path, content: str, encoding: str = 'utf-8') -> None:
        """Write text content to a file"""
        pass
    
    @abstractmethod
    def mkdir(self, path: Path, parents: bool = False, exist_ok: bool = False) -> None:
        """Create a directory"""
        pass
    
    @abstractmethod
    def glob(self, path: Path, pattern: str) -> List[Path]:
        """Find files matching a pattern"""
        pass
    
    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """Check if path is a file"""
        pass
    
    @abstractmethod
    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory"""
        pass


class RealFileSystem(FileSystemInterface):
    """Real file system implementation"""
    
    def exists(self, path: Path) -> bool:
        return path.exists()
    
    def read_text(self, path: Path, encoding: str = 'utf-8') -> str:
        return path.read_text(encoding=encoding)
    
    def write_text(self, path: Path, content: str, encoding: str = 'utf-8') -> None:
        path.write_text(content, encoding=encoding)
    
    def mkdir(self, path: Path, parents: bool = False, exist_ok: bool = False) -> None:
        path.mkdir(parents=parents, exist_ok=exist_ok)
    
    def glob(self, path: Path, pattern: str) -> List[Path]:
        return list(path.glob(pattern))
    
    def is_file(self, path: Path) -> bool:
        return path.is_file()
    
    def is_dir(self, path: Path) -> bool:
        return path.is_dir()


class MockFileSystem(FileSystemInterface):
    """Mock file system for testing"""
    
    def __init__(self):
        self.files: Dict[str, str] = {}  # path -> content
        self.directories: set = set()
    
    def _normalize_path(self, path: Path) -> str:
        """Normalize path for consistent storage"""
        return str(path).replace('\\', '/')
        
    def exists(self, path: Path) -> bool:
        path_str = self._normalize_path(path)
        return path_str in self.files or path_str in self.directories
    
    def read_text(self, path: Path, encoding: str = 'utf-8') -> str:
        path_str = self._normalize_path(path)
        if path_str not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        return self.files[path_str]
    
    def write_text(self, path: Path, content: str, encoding: str = 'utf-8') -> None:
        # Ensure parent directories exist
        parent_path = self._normalize_path(path.parent)
        if parent_path != self._normalize_path(path):  # Not root
            self.directories.add(parent_path)
        self.files[self._normalize_path(path)] = content
    
    def mkdir(self, path: Path, parents: bool = False, exist_ok: bool = False) -> None:
        path_str = self._normalize_path(path)
        if path_str in self.directories:
            if not exist_ok:
                raise FileExistsError(f"Directory already exists: {path}")
            return  # Directory exists and exist_ok=True
        
        if parents:
            # Create parent directories
            current = path
            while current != current.parent:
                self.directories.add(self._normalize_path(current))
                current = current.parent
        else:
            # Check if parent exists
            parent_str = self._normalize_path(path.parent)
            if parent_str != path_str and parent_str not in self.directories:
                raise FileNotFoundError(f"Parent directory does not exist: {path.parent}")
            self.directories.add(path_str)
    
    def glob(self, path: Path, pattern: str) -> List[Path]:
        # Simple pattern matching for testing
        import fnmatch
        path_str = self._normalize_path(path)
        
        matches = []
        for file_path_key in self.files.keys():
            # Check if the file is in the specified directory
            file_path_parts = file_path_key.split('/')
            path_parts = path_str.split('/')
            
            # File must be in the directory (or subdirectory for **)
            if len(file_path_parts) > len(path_parts):
                # Check if file path starts with directory path
                if file_path_parts[:len(path_parts)] == path_parts:
                    # Get the filename relative to the search directory
                    relative_parts = file_path_parts[len(path_parts):]
                    filename = relative_parts[-1]  # Just the filename
                    
                    # Match against pattern
                    if fnmatch.fnmatch(filename, pattern):
                        matches.append(Path(file_path_key))  # Keep POSIX style for tests
        
        return matches
    
    def is_file(self, path: Path) -> bool:
        return self._normalize_path(path) in self.files
    
    def is_dir(self, path: Path) -> bool:
        return self._normalize_path(path) in self.directories
    
    def add_file(self, path: str, content: str) -> None:
        """Helper method to add files for testing"""
        path_obj = Path(path)
        normalized_path = self._normalize_path(path_obj)
        self.files[normalized_path] = content
        # Ensure parent directories exist
        current = path_obj.parent
        while current != current.parent:  # Stop at root
            self.directories.add(self._normalize_path(current))
            current = current.parent
    
    def add_directory(self, path: str) -> None:
        """Helper method to add directories for testing"""
        self.directories.add(Path(path).as_posix())