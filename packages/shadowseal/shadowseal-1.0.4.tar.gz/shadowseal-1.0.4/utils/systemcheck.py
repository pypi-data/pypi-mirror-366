"""
Advanced system check utilities for ShadowSeal package.

Provides platform detection, hardware binding, expiry lock, and environment checks.
"""

import platform
import hashlib
import uuid
import time
import os
import subprocess
import sys
import socket
import psutil

# Check if running on Android (Termux or similar)
def is_android():
    """Check if running on Android (Termux or similar environment)"""
    try:
        # Check for Android-specific files
        if os.path.exists("/system/build.prop") or os.path.exists("/system/bin/getprop"):
            return True
        # Check for Termux environment
        if "TERMUX" in os.environ.get("PREFIX", ""):
            return True
        # Check for Android in platform
        if "android" in platform.platform().lower():
            return True
        return False
    except Exception:
        return False

def get_android_device_id():
    """Get Android device ID for hardware binding"""
    try:
        # Try to get Android ID from system properties
        result = subprocess.run(['getprop', 'ro.serialno'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        # Try alternative Android ID
        result = subprocess.run(['getprop', 'ro.boot.serialno'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
            
        # Fallback to Android Secure ID
        android_data_dir = "/data/data"
        if os.path.exists(android_data_dir):
            # Use directory listing as unique identifier
            dirs = os.listdir(android_data_dir)
            combined = ''.join(sorted(dirs[:10]))  # Take first 10 directories
            return hashlib.sha256(combined.encode()).hexdigest()[:32]
            
    except Exception:
        pass
    return None

def get_platform() -> str:
    """Get the current platform name."""
    return platform.system()

def get_machine_id() -> str:
    """Generate a cross-platform hardware binding ID."""
    try:
        # Use a consistent approach across all platforms
        # This ensures encrypted files work on any platform
        
        # Get basic system info that's consistent across platforms
        uname = platform.uname()
        system_info = f"{uname.system}-{uname.machine}"
        
        # Use Python executable path as a stable identifier
        python_path = sys.executable
        
        # Use home directory path as another stable identifier
        home_dir = os.path.expanduser("~")
        
        # Combine system info with Python installation info
        combined_info = f"{system_info}|{python_path}|{home_dir}"
        
        # Generate consistent hash across platforms
        return hashlib.sha256(combined_info.encode()).hexdigest()
        
    except Exception:
        # Ultimate fallback - use a deterministic approach
        fallback = f"shadowseal-{platform.system()}-{platform.machine()}"
        return hashlib.sha256(fallback.encode()).hexdigest()

def check_expiry(expiry_timestamp: int) -> bool:
    """Check if the current time is before the expiry timestamp."""
    current = int(time.time())
    return current <= expiry_timestamp

def check_root() -> bool:
    """Check if running as root/administrator."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows fallback
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

def check_virtual_env() -> bool:
    """Check if running inside a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

def check_debugger_processes() -> bool:
    """Check for common debugger processes running."""
    debuggers = [
        'gdb', 'lldb', 'strace', 'ltrace', 'ida', 'ollydbg',
        'x64dbg', 'windbg', 'radare2', 'hopper', 'binaryninja',
        'frida', 'mitmproxy', 'burpsuite', 'wireshark', 'pycharm',
        'vscode', 'code', 'atom', 'sublime_text'
    ]
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                for dbg in debuggers:
                    if dbg.lower() in proc_name or dbg.lower() in cmdline:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return False

def check_network_connection() -> bool:
    """Check if network connection is available."""
    try:
        # Try to connect to Google's DNS
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def check_system_resources() -> dict:
    """Check system resources."""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime': time.time() - psutil.boot_time(),
    }

def check_python_version() -> str:
    """Check Python version."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def check_system_architecture() -> str:
    """Check system architecture."""
    return platform.machine()

def check_environment_safety() -> dict:
    """Check if environment is safe for execution."""
    return {
        'is_root': check_root(),
        'is_virtual_env': check_virtual_env(),
        'has_debugger': check_debugger_processes(),
        'has_network': check_network_connection(),
        'platform': get_platform(),
        'python_version': check_python_version(),
        'architecture': check_system_architecture(),
    }

def generate_system_fingerprint() -> str:
    """Generate a unique system fingerprint."""
    try:
        # Get system information
        system_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': sys.version,
            'hostname': socket.gethostname(),
            'username': os.getlogin(),
        }
        
        # Convert to string and hash
        info_str = str(sorted(system_info.items()))
        return hashlib.sha256(info_str.encode()).hexdigest()
    except Exception:
        return "unknown"

def check_system_compatibility() -> bool:
    """Check if system is compatible with ShadowSeal."""
    min_python_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < min_python_version:
        return False
    
    # Check for required modules
    required_modules = ['cryptography', 'psutil']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            return False
    
    return True

def get_system_info() -> dict:
    """Get comprehensive system information."""
    return {
        'platform': get_platform(),
        'machine_id': get_machine_id(),
        'python_version': check_python_version(),
        'architecture': check_system_architecture(),
        'is_root': check_root(),
        'is_virtual_env': check_virtual_env(),
        'has_network': check_network_connection(),
        'resources': check_system_resources(),
        'fingerprint': generate_system_fingerprint(),
        'compatible': check_system_compatibility(),
    }

# Example usage
if __name__ == "__main__":
    info = get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
