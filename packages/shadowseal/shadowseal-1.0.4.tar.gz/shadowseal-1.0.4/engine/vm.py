import types
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureVM:
    """Secure Virtual Machine for executing encrypted Python code"""
    
    def __init__(self, password: str = None):
        self.password = password or secrets.token_urlsafe(32)
        self.restricted_globals = {
            '__builtins__': __builtins__,
            '__name__': '__main__',
            '__file__': '<encrypted>',
        }
    
    def generate_key(self, salt: bytes) -> bytes:
        """Generate encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
    
    def encrypt_code(self, code: str) -> tuple:
        """Encrypt Python code"""
        salt = secrets.token_bytes(16)
        key = self.generate_key(salt)
        f = Fernet(key)
        
        # Compress and encode
        encoded = base64.b64encode(code.encode('utf-8'))
        encrypted = f.encrypt(encoded)
        
        return encrypted, salt
    
    def decrypt_code(self, encrypted: bytes, salt: bytes) -> str:
        """Decrypt Python code"""
        key = self.generate_key(salt)
        f = Fernet(key)
        
        decrypted = f.decrypt(encrypted)
        decoded = base64.b64decode(decrypted)
        return decoded.decode('utf-8')
    
    def create_sandbox(self):
        """Create a restricted execution environment"""
        sandbox_globals = {
            '__builtins__': {
                'abs': abs,
                'all': all,
                'any': any,
                'bin': bin,
                'bool': bool,
                'bytearray': bytearray,
                'bytes': bytes,
                'chr': chr,
                'dict': dict,
                'enumerate': enumerate,
                'filter': filter,
                'float': float,
                'format': format,
                'frozenset': frozenset,
                'hasattr': hasattr,
                'hash': hash,
                'hex': hex,
                'id': id,
                'int': int,
                'isinstance': isinstance,
                'issubclass': issubclass,
                'iter': iter,
                'len': len,
                'list': list,
                'map': map,
                'max': max,
                'memoryview': memoryview,
                'min': min,
                'next': next,
                'oct': oct,
                'ord': ord,
                'pow': pow,
                'print': print,
                'range': range,
                'repr': repr,
                'reversed': reversed,
                'round': round,
                'set': set,
                'slice': slice,
                'sorted': sorted,
                'str': str,
                'sum': sum,
                'tuple': tuple,
                'type': type,
                'zip': zip,
            },
            '__name__': '__main__',
            '__file__': '<encrypted>',
        }
        return sandbox_globals
    
    def execute_encrypted(self, encrypted_code: bytes, salt: bytes, filename='<encrypted>'):
        """Execute encrypted code in a secure environment"""
        try:
            # Decrypt code
            code_str = self.decrypt_code(encrypted_code, salt)
            
            # Create sandbox
            sandbox = self.create_sandbox()
            
            # Compile and execute
            code_obj = compile(code_str, filename, 'exec')
            exec(code_obj, sandbox)
            
        except Exception as e:
            print(f"VM execution error: {e}")
            return False
        return True
    
    def execute_file(self, filepath: str):
        """Execute encrypted file"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # Parse file format: salt + encrypted_code
            if len(data) < 16:
                raise ValueError("Invalid file format")
            
            salt = data[:16]
            encrypted_code = data[16:]
            
            return self.execute_encrypted(encrypted_code, salt, filepath)
            
        except Exception as e:
            print(f"File execution error: {e}")
            return False

class EncryptedVM(SecureVM):
    """Legacy compatibility class"""
    pass

# Example usage
if __name__ == "__main__":
    # Example code
    sample_code = """
print("Hello from encrypted code!")
x = 42
print(f"The answer is {x}")
"""
    
    vm = SecureVM("test_password")
    encrypted, salt = vm.encrypt_code(sample_code)
    vm.execute_encrypted(encrypted, salt)
