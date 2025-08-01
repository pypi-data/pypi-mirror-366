"""Runner package for ShadowSeal - secure code execution."""

import platform
import os

# Platform-specific loader selection
def _select_loader():
    """Select appropriate loader based on platform"""
    try:
        # Check for Android/Termux environment
        if os.path.exists("/system/build.prop") or os.path.exists("/system/bin/getprop"):
            # Android environment - use pure Python
            from . import py_loader as loader
            return loader
        elif "TERMUX" in os.environ.get("PREFIX", ""):
            # Termux environment - use pure Python
            from . import py_loader as loader
            return loader
        else:
            # Regular Linux/Windows/macOS - try Cython first
            try:
                from . import loader as cy_loader
                return cy_loader
            except ImportError:
                # Fallback to pure Python
                from . import py_loader as loader
                return loader
    except Exception:
        # Final fallback
        from . import py_loader as loader
        return loader

# Select appropriate loader
loader = _select_loader()

__all__ = ['loader']
