"""
Advanced file utilities for ShadowSeal package.

Provides robust file handling, checksum calculation, and safe file operations.
"""

import os
import hashlib
import shutil
import tempfile
import json
from typing import Optional, Dict, Any

def read_file_bytes(path: str) -> bytes:
    """Read the entire file content as bytes."""
    with open(path, 'rb') as f:
        return f.read()

def write_file_bytes(path: str, data: bytes) -> None:
    """Write bytes data to a file safely."""
    temp_path = path + '.tmp'
    with open(temp_path, 'wb') as f:
        f.write(data)
    os.replace(temp_path, path)

def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)

def get_file_size(path: str) -> int:
    """Get the size of a file in bytes."""
    return os.path.getsize(path)

def compute_sha256(path: str) -> str:
    """Compute SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA256 checksum of bytes."""
    return hashlib.sha256(data).hexdigest()

def safe_delete(path: str) -> None:
    """Safely delete a file if it exists."""
    try:
        if file_exists(path):
            os.remove(path)
    except Exception:
        pass

def copy_file(src: str, dst: str) -> None:
    """Copy a file from src to dst."""
    shutil.copy2(src, dst)

def create_temp_file(suffix: str = '.tmp') -> str:
    """Create a temporary file."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path

def atomic_write(path: str, data: bytes) -> None:
    """Atomically write data to a file."""
    temp_path = create_temp_file()
    try:
        with open(temp_path, 'wb') as f:
            f.write(data)
        shutil.move(temp_path, path)
    except Exception:
        safe_delete(temp_path)
        raise

def read_json_file(path: str) -> Dict[str, Any]:
    """Read JSON file."""
    with open(path, 'r') as f:
        return json.load(f)

def write_json_file(path: str, data: Dict[str, Any]) -> None:
    """Write JSON file."""
    atomic_write(path, json.dumps(data, indent=2).encode('utf-8'))

def get_file_info(path: str) -> Dict[str, Any]:
    """Get comprehensive file information."""
    stat = os.stat(path)
    return {
        'size': stat.st_size,
        'mtime': stat.st_mtime,
        'ctime': stat.st_ctime,
        'sha256': compute_sha256(path),
    }

def secure_delete(path: str, passes: int = 3) -> None:
    """Securely delete a file by overwriting it multiple times."""
    if not file_exists(path):
        return
    
    try:
        with open(path, 'r+b') as f:
            size = os.path.getsize(path)
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
    except Exception:
        pass
    finally:
        safe_delete(path)

def list_python_files(directory: str) -> list:
    """List all Python files in a directory."""
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py'):
                files.append(os.path.join(root, filename))
    return files

def create_backup(path: str) -> str:
    """Create a backup of a file."""
    backup_path = path + '.backup'
    copy_file(path, backup_path)
    return backup_path

def restore_backup(backup_path: str, original_path: str) -> None:
    """Restore from backup."""
    if file_exists(backup_path):
        copy_file(backup_path, original_path)
        safe_delete(backup_path)

def validate_file_integrity(path: str, expected_hash: str) -> bool:
    """Validate file integrity using SHA256."""
    actual_hash = compute_sha256(path)
    return actual_hash == expected_hash

def get_file_extension(path: str) -> str:
    """Get file extension."""
    return os.path.splitext(path)[1].lower()

def is_python_file(path: str) -> bool:
    """Check if file is a Python file."""
    return get_file_extension(path) == '.py'

def is_encrypted_file(path: str) -> bool:
    """Check if file is an encrypted .shc file."""
    return get_file_extension(path) == '.shc'
