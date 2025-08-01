import random
import string
import ast

def random_var_name(length=8):
    """Generate random variable names"""
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_dead_code():
    """Generate sophisticated dead code that looks real"""
    templates = [
        # Fake configuration
        lambda: f"{random_var_name()} = {{\n    'debug': {random.choice([True, False])},\n    'timeout': {random.randint(30, 300)},\n    'retries': {random.randint(1, 5)},\n    'ssl_verify': {random.choice([True, False])}\n}}",
        
        # Fake network operations
        lambda: f"try:\n    import socket\n    {random_var_name()} = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    {random_var_name()}.settimeout({random.randint(1, 10)})\n    {random_var_name()} = {random_var_name()}.connect_ex(('127.0.0.1', {random.randint(8000, 9000)}))\nexcept Exception as {random_var_name()}:\n    pass",
        
        # Fake file operations
        lambda: f"try:\n    with open('/tmp/{random_var_name()}.tmp', 'w') as {random_var_name()}:\n        {random_var_name()}.write(str({random.randint(1000, 9999)}))\nexcept:\n    pass",
        
        # Fake threading
        lambda: f"import threading\n{random_var_name()} = threading.Thread(target=lambda: time.sleep({random.uniform(0.1, 1.0)}))\n{random_var_name()}.daemon = True\n{random_var_name()}.start()",
        
        # Fake encryption
        lambda: f"import base64\n{random_var_name()} = base64.b64encode(b'{random_var_name()}')",
        
        # Fake regex
        lambda: f"import re\n{random_var_name()} = re.compile(r'[a-zA-Z0-9]{{{random.randint(5, 15)}}}')",
        
        # Fake math operations
        lambda: f"{random_var_name()} = sum([{', '.join(str(random.randint(1, 100)) for _ in range(5))}])",
        
        # Fake class definition
        lambda: f"class {random_var_name().capitalize()}:\n    def __init__(self):\n        self.{random_var_name()} = {random.randint(1, 100)}\n    def {random_var_name()}(self):\n        return self.{random_var_name()} * {random.randint(2, 10)}",
        
        # Fake lambda functions
        lambda: f"{random_var_name()} = lambda x, y: x ** {random.randint(2, 5)} + y ** {random.randint(2, 3)}",
        
        # Fake list comprehensions
        lambda: f"{random_var_name()} = [i for i in range({random.randint(10, 50)}) if i % {random.randint(2, 7)} == 0]",
    ]
    
    return random.choice(templates)()

def generate_imports():
    """Generate fake imports"""
    imports = [
        "import os",
        "import sys",
        "import json",
        "import time",
        "import random",
        "import hashlib",
        "import base64",
        "import re",
        "import threading",
        "import socket",
        "import urllib.request",
        "import urllib.parse",
        "import subprocess",
        "import tempfile",
        "import uuid",
        "import platform",
        "import datetime",
        "import collections",
        "import itertools",
        "import functools",
        "import operator",
    ]
    
    random.shuffle(imports)
    return "\n".join(imports[:random.randint(5, 12)])

def generate_string_obfuscation(code):
    """Obfuscate string literals"""
    tree = ast.parse(code)
    
    class StringObfuscator(ast.NodeTransformer):
        def visit_Str(self, node):
            if hasattr(ast, 'Constant'):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    return self.obfuscate_string(node.value)
            return node
        
        def visit_Constant(self, node):
            if isinstance(node.value, str):
                return self.obfuscate_string(node.value)
            return node
        
        def obfuscate_string(self, s):
            # Simple XOR obfuscation
            key = "shadowseal"
            obfuscated = "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(s))
            # Create a decode expression
            decode_expr = ast.parse(f"''.join(chr(ord(c) ^ ord('shadowseal'[i % 10])) for i, c in enumerate({repr(obfuscated)}))").body[0].value
            return decode_expr
    
    obfuscator = StringObfuscator()
    tree = obfuscator.visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

def weave_confusion(source_code: str) -> str:
    """Weave sophisticated confusion into the source code"""
    lines = source_code.splitlines()
    new_lines = []
    
    # Add fake imports at the top
    new_lines.append(generate_imports())
    new_lines.append("")
    
    # Process original code
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add dead code with decreasing probability
        if random.random() < max(0.05, 0.15 - (i * 0.001)):
            dead_code = generate_dead_code()
            new_lines.append("")
            new_lines.append("    " * line.count("    ") + dead_code.replace("\n", "\n" + "    " * line.count("    ")))
            new_lines.append("")
    
    # Add fake functions at the end
    if random.random() < 0.3:
        new_lines.append("")
        new_lines.append(generate_dead_code())
    
    result = "\n".join(new_lines)
    
    # Apply string obfuscation
    try:
        result = generate_string_obfuscation(result)
    except:
        pass
    
    return result

def add_noise_variables(source_code: str) -> str:
    """Add noise variables that look important"""
    noise_vars = [
        f"{random_var_name()} = os.environ.get('USER', 'unknown')",
        f"{random_var_name()} = sys.version_info[:2]",
        f"{random_var_name()} = time.time()",
        f"{random_var_name()} = random.randint(1000, 9999)",
        f"{random_var_name()} = hashlib.md5(b'{random_var_name()}').hexdigest()",
    ]
    
    lines = source_code.splitlines()
    if lines:
        insert_pos = random.randint(1, min(5, len(lines)))
        for var in random.sample(noise_vars, random.randint(1, 3)):
            lines.insert(insert_pos, "    " * lines[insert_pos].count("    ") + var)
    
    return "\n".join(lines)

def full_obfuscation(source_code: str) -> str:
    """Apply full obfuscation pipeline"""
    obfuscated = weave_confusion(source_code)
    obfuscated = add_noise_variables(obfuscated)
    return obfuscated
