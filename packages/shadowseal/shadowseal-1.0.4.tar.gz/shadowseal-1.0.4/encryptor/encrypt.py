import os
import sys
import time
import struct
import hashlib
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from utils.cross_platform import CrossPlatformManager

VERSION = 3  # Updated version for cross-platform compatibility
BLOCK_SIZE = 16

def generate_key_from_password(password: bytes, salt: bytes) -> bytes:
    """Generate a secure key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

def generate_fixed_key() -> bytes:
    """Generate a fixed key for passwordless encryption"""
    # Fernet requires 32-byte key, base64 encoded to 44 characters
    # Use a deterministic 32-byte key for passwordless mode
    key_bytes = b"12345678901234567890123456789012"  # Exactly 32 bytes
    return base64.urlsafe_b64encode(key_bytes)

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypt data using Fernet (AES 128)"""
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypt data using Fernet (AES 128)"""
    f = Fernet(key)
    return f.decrypt(encrypted_data)

def simple_checksum(data: bytes) -> int:
    """Calculate checksum for integrity verification"""
    return int.from_bytes(hashlib.sha256(data).digest()[:4], 'big')

def pack_shc(encrypted_data: bytes, salt: bytes, version: int = VERSION, has_password: bool = True) -> bytes:
    """Pack encrypted data with metadata for cross-platform compatibility"""
    checksum = simple_checksum(encrypted_data)
    timestamp = int(time.time())
    
    # Add platform compatibility flags
    platform_manager = CrossPlatformManager()
    platform_id = platform_manager.generate_cross_platform_id()
    platform_hash = hashlib.sha256(platform_id.encode()).digest()[:4]
    
    # Combine flags: password flag + platform compatibility flag
    flags = (1 if has_password else 0) | (1 << 1)  # Bit 0 = password, Bit 1 = cross-platform
    
    # New header format with platform compatibility
    header = struct.pack('>I I Q B 4s', checksum, version, timestamp, flags, platform_hash)
    
    if has_password:
        return header + salt + encrypted_data
    else:
        return header + encrypted_data

def unpack_shc(packed_data: bytes):
    """Unpack encrypted data from .shc format with cross-platform support"""
    # Handle both old (v2) and new (v3+) formats
    if len(packed_data) < 17:
        raise ValueError("Invalid file format")
    
    # Check if this is the new format (v3+)
    if len(packed_data) >= 21:  # New format has 21-byte header
        try:
            header = packed_data[:21]
            checksum, version, timestamp, flags, platform_hash = struct.unpack('>I I Q B 4s', header)
            
            # Check version compatibility
            if version >= 3:
                # New format with cross-platform support
                has_password = bool(flags & 1)
                
                if has_password:
                    if len(packed_data) < 29:  # 21 + 8 (salt)
                        raise ValueError("Invalid file format")
                    salt = packed_data[21:29]
                    encrypted_data = packed_data[29:]
                else:
                    salt = b''
                    encrypted_data = packed_data[21:]
                
                computed_checksum = simple_checksum(encrypted_data)
                if computed_checksum != checksum:
                    raise ValueError("Checksum mismatch. File corrupted or tampered.")
                
                return encrypted_data, salt, version, has_password
            
        except struct.error:
            pass
    
    # Fallback to old format (v2)
    header = packed_data[:17]
    checksum, version, timestamp, flags = struct.unpack('>I I Q B', packed_data[:17])
    has_password = bool(flags & 1)
    
    if has_password:
        if len(packed_data) < 25:
            raise ValueError("Invalid file format")
        salt = packed_data[17:25]
        encrypted_data = packed_data[25:]
    else:
        salt = b''
        encrypted_data = packed_data[17:]
    
    computed_checksum = simple_checksum(encrypted_data)
    if computed_checksum != checksum:
        raise ValueError("Checksum mismatch. File corrupted or tampered.")
    
    return encrypted_data, salt, version, has_password

def encrypt_file(input_path: str, output_path: str, password: str = None):
    """Encrypt a Python file with optional password"""
    if not input_path.endswith('.py'):
        raise ValueError("Input file must be a .py file")
    
    # Read and encode the Python file
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Compress and encode
    data = base64.b64encode(data)
    
    if password is None:
        # Passwordless mode - use fixed key
        key = generate_fixed_key()
        salt = b''
        encrypted = encrypt_data(data, key)
        packed = pack_shc(encrypted, salt, has_password=False)
        print(f"Encrypted {input_path} -> {output_path} (passwordless)")
    else:
        # Password mode - use PBKDF2
        salt = secrets.token_bytes(8)
        key = generate_key_from_password(password.encode(), salt)
        encrypted = encrypt_data(data, key)
        packed = pack_shc(encrypted, salt, has_password=True)
        print(f"Encrypted {input_path} -> {output_path}")
        print(f"Password: {password}")
    
    # Write output
    with open(output_path, 'wb') as f:
        f.write(packed)
    
    return password

def decrypt_file(input_path: str, output_path: str, password: str = None):
    """Decrypt a .shc file back to Python"""
    with open(input_path, 'rb') as f:
        packed_data = f.read()
    
    encrypted_data, salt, version, has_password = unpack_shc(packed_data)
    
    if has_password:
        if password is None:
            raise ValueError("Password required for encrypted file")
        key = generate_key_from_password(password.encode(), salt)
    else:
        # Passwordless mode - use fixed key
        key = generate_fixed_key()
    
    decrypted = decrypt_data(encrypted_data, key)
    
    # Decode from base64
    data = base64.b64decode(decrypted)
    
    with open(output_path, 'wb') as f:
        f.write(data)
    
    print(f"Decrypted {input_path} -> {output_path}")

def run_encrypted_file(filepath: str, password: str = None):
    """Run an encrypted .shc file"""
    with open(filepath, 'rb') as f:
        packed_data = f.read()
    
    encrypted_data, salt, version, has_password = unpack_shc(packed_data)
    
    if has_password:
        if password is None:
            raise ValueError("Password required for encrypted file")
        key = generate_key_from_password(password.encode(), salt)
    else:
        # Passwordless mode - use fixed key
        key = generate_fixed_key()
    
    decrypted = decrypt_data(encrypted_data, key)
    
    # Decode from base64
    data = base64.b64decode(decrypted)
    code_str = data.decode('utf-8')
    
    # Execute in restricted globals
    exec_globals = {
        '__builtins__': __builtins__,
        '__name__': '__main__',
        '__file__': filepath,
    }
    
    code_obj = compile(code_str, filepath, 'exec')
    exec(code_obj, exec_globals)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Secure Python file encryption')
    subparsers = parser.add_subparsers(dest='command')
    
    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a Python file')
    encrypt_parser.add_argument('input', help='Input .py file')
    encrypt_parser.add_argument('-o', '--output', help='Output .shc file', required=True)
    encrypt_parser.add_argument('-p', '--password', help='Encryption password (optional - passwordless if not provided)')
    
    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt a .shc file back to Python')
    decrypt_parser.add_argument('input', help='Input .shc file')
    decrypt_parser.add_argument('-o', '--output', help='Output .py file', required=True)
    decrypt_parser.add_argument('-p', '--password', help='Decryption password (optional for passwordless files)')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run an encrypted .shc file')
    run_parser.add_argument('file', help='Encrypted .shc file to run')
    run_parser.add_argument('-p', '--password', help='Decryption password (optional for passwordless files)')
    
    args = parser.parse_args()
    
    if args.command == 'encrypt':
        encrypt_file(args.input, args.output, args.password)
    elif args.command == 'decrypt':
        decrypt_file(args.input, args.output, args.password)
    elif args.command == 'run':
        run_encrypted_file(args.file, args.password)

if __name__ == '__main__':
    main()
