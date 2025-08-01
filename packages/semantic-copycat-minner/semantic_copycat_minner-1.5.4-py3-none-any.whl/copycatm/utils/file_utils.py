"""
File handling utilities for CopycatM.
"""

import os
from pathlib import Path
from typing import Set


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


def is_supported_language(language: str) -> bool:
    """Check if language is supported by CopycatM."""
    supported_languages = {
        "python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"
    }
    return language in supported_languages


def is_supported_file(filename: str) -> bool:
    """Check if file extension is supported."""
    supported_extensions = {
        # Python
        ".py", ".pyx", ".pyi",
        
        # JavaScript/TypeScript
        ".js", ".ts", ".jsx", ".tsx",
        
        # Java
        ".java",
        
        # C/C++
        ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp",
        
        # Go
        ".go",
        
        # Rust
        ".rs",
    }
    
    extension = get_file_extension(filename)
    return extension in supported_extensions


def get_supported_files(directory: str, recursive: bool = True) -> Set[str]:
    """Get all supported files in directory."""
    supported_files = set()
    directory_path = Path(directory)
    
    if recursive:
        files = directory_path.rglob("*")
    else:
        files = directory_path.glob("*")
    
    for file_path in files:
        if file_path.is_file() and is_supported_file(file_path.name):
            supported_files.add(str(file_path))
    
    return supported_files


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def get_file_mime_type(file_path: str) -> str:
    """Get MIME type of file."""
    import magic
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)


def is_text_file(file_path: str) -> bool:
    """Check if file is a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Read first 1KB
        return True
    except (UnicodeDecodeError, IOError):
        return False 