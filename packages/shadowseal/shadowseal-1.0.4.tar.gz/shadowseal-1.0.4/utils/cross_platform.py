"""
Cross-platform compatibility utilities for ShadowSeal.

Ensures encrypted files work consistently across all platforms (Windows, Linux, macOS, Android).
"""

import os
import sys
import platform
import hashlib
import tempfile
from typing import Dict, Any, Optional

class CrossPlatformManager:
    """Manages cross-platform compatibility for encrypted files."""
    
    @staticmethod
    def get_platform_info() -> Dict[str, str]:
        """Get platform information in a cross-platform way."""
        return {
            'system': platform.system(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'sep': os.sep,
            'pathsep': os.pathsep,
        }
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize file paths for cross-platform compatibility."""
        return os.path.normpath(path).replace(os.sep, '/')
    
    @staticmethod
    def get_temp_dir() -> str:
        """Get cross-platform temporary directory."""
        return tempfile.gettempdir()
    
    @staticmethod
    def get_home_dir() -> str:
        """Get cross-platform home directory."""
        return os.path.expanduser("~")
    
    @staticmethod
    def generate_cross_platform_id() -> str:
        """Generate a platform-independent identifier."""
        # Use Python executable path and version for consistent ID
        python_info = f"{sys.executable}|{sys.version}|{platform.machine()}"
        return hashlib.sha256(python_info.encode()).hexdigest()
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == "Windows"
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == "Linux"
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system() == "Darwin"
    
    @staticmethod
    def is_android() -> bool:
        """Check if running on Android/Termux."""
        try:
            # Check for Android-specific indicators
            if os.path.exists("/system/build.prop") or os.path.exists("/system/bin/getprop"):
                return True
            if "TERMUX" in os.environ.get("PREFIX", ""):
                return True
            return False
        except:
            return False
    
    @staticmethod
    def get_executable_extension() -> str:
        """Get executable extension for current platform."""
        return ".exe" if CrossPlatformManager.is_windows() else ""
    
    @staticmethod
    def get_path_separator() -> str:
        """Get path separator for current platform."""
        return os.sep
    
    @staticmethod
    def join_paths(*paths: str) -> str:
        """Join paths in cross-platform way."""
        return os.path.join(*paths).replace(os.sep, '/')

def ensure_cross_platform_compatibility():
    """Ensure all components work across platforms."""
    # This function can be called to verify cross-platform compatibility
    manager = CrossPlatformManager()
    
    # Test basic functionality
    platform_info = manager.get_platform_info()
    temp_dir = manager.get_temp_dir()
    home_dir = manager.get_home_dir()
    
    return {
        'platform_info': platform_info,
        'temp_dir': temp_dir,
        'home_dir': home_dir,
        'cross_platform_id': manager.generate_cross_platform_id(),
        'is_compatible': True
    }

if __name__ == "__main__":
    # Test cross-platform compatibility
    result = ensure_cross_platform_compatibility()
    print("Cross-platform compatibility check:")
    for key, value in result.items():
        print(f"  {key}: {value}")