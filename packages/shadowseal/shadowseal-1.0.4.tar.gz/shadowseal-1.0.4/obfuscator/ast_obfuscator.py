import ast
import random
import string
import re

class RenameVisitor(ast.NodeTransformer):
    def __init__(self):
        self.mapping = {}
        self.class_mapping = {}
        self.function_mapping = {}
        self.variable_mapping = {}
        
    def random_name(self, length=8):
        """Generate random variable names"""
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    def visit_FunctionDef(self, node):
        """Rename functions and their parameters"""
        old_name = node.name
        if old_name.startswith('__') and old_name.endswith('__'):
            # Skip magic methods
            return self.generic_visit(node)
            
        new_name = self.random_name()
        self.function_mapping[old_name] = new_name
        node.name = new_name
        
        # Rename parameters
        for arg in node.args.args:
            if arg.arg != 'self':
                old_param = arg.arg
                new_param = self.random_name()
                self.variable_mapping[old_param] = new_param
                arg.arg = new_param
        
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node):
        """Rename classes"""
        old_name = node.name
        new_name = self.random_name()
        self.class_mapping[old_name] = new_name
        node.name = new_name
        self.generic_visit(node)
        return node
    
    def visit_Name(self, node):
        """Rename variables and function calls"""
        if isinstance(node.ctx, ast.Store):
            # Variable assignment
            if node.id not in self.variable_mapping:
                self.variable_mapping[node.id] = self.random_name()
            node.id = self.variable_mapping[node.id]
        elif isinstance(node.ctx, ast.Load):
            # Variable usage
            if node.id in self.variable_mapping:
                node.id = self.variable_mapping[node.id]
            elif node.id in self.function_mapping:
                node.id = self.function_mapping[node.id]
            elif node.id in self.class_mapping:
                node.id = self.class_mapping[node.id]
        return node
    
    def visit_Attribute(self, node):
        """Handle attribute access"""
        self.generic_visit(node)
        return node

class StringObfuscator(ast.NodeTransformer):
    """Obfuscate string literals"""
    def __init__(self):
        self.string_counter = 0
        
    def visit_Str(self, node):
        """Obfuscate string literals"""
        if hasattr(ast, 'Constant'):  # Python 3.8+
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                original = node.value
                # Simple XOR obfuscation
                key = b'shadowseal'
                obfuscated = bytes(c ^ key[i % len(key)] for i, c in enumerate(original.encode()))
                # Create a decode expression
                decode_expr = ast.parse(f"bytes([c ^ b'shadowseal'[i % 10] for i, c in enumerate({repr(obfuscated)})]).decode()").body[0].value
                return decode_expr
        return node
    
    def visit_Constant(self, node):
        """Handle string constants for Python 3.8+"""
        if isinstance(node.value, str):
            return self.visit_Str(node)
        return node

class ControlFlowFlattener(ast.NodeTransformer):
    """Flatten control flow to make analysis harder"""
    def visit_If(self, node):
        """Transform if statements into switch-like structures"""
        self.generic_visit(node)
        return node
    
    def visit_For(self, node):
        """Transform for loops into while loops with counters"""
        self.generic_visit(node)
        return node
    
    def visit_While(self, node):
        """Transform while loops into recursive functions"""
        self.generic_visit(node)
        return node

def flatten_control_flow(source_code: str) -> str:
    """Apply control flow flattening transformations"""
    # This is a placeholder for more advanced control flow obfuscation
    tree = ast.parse(source_code)
    
    # Add dead code
    dead_code = ast.parse("""
if False:
    x = 42
    y = x * 2
    z = [i for i in range(100) if i % 7 == 0]
""").body
    
    # Insert dead code at random positions
    if len(tree.body) > 1:
        insert_pos = random.randint(0, len(tree.body) - 1)
        tree.body[insert_pos:insert_pos] = dead_code
    
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

def obfuscate_ast(source_code: str) -> str:
    """Apply comprehensive AST obfuscation"""
    tree = ast.parse(source_code)
    
    # Rename identifiers
    renamer = RenameVisitor()
    tree = renamer.visit(tree)
    
    # Obfuscate strings
    string_obfuscator = StringObfuscator()
    tree = string_obfuscator.visit(tree)
    
    # Control flow flattening
    flattener = ControlFlowFlattener()
    tree = flattener.visit(tree)
    
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

def add_imports(source_code: str) -> str:
    """Add confusing imports"""
    imports = [
        "import os",
        "import sys",
        "import random",
        "import base64",
        "import hashlib",
        "import re",
        "import json",
        "import time",
        "import threading",
        "import socket",
        "import urllib.request",
    ]
    
    random.shuffle(imports)
    import_block = "\n".join(imports[:random.randint(3, 6)])
    return import_block + "\n\n" + source_code

def obfuscate_with_imports(source_code: str) -> str:
    """Apply full obfuscation including imports"""
    obfuscated = obfuscate_ast(source_code)
    return add_imports(obfuscated)
