"""Obfuscation package for ShadowSeal - advanced Python obfuscation."""

from .ast_obfuscator import obfuscate_ast
from .cryptic_inserter import weave_confusion

__all__ = ['obfuscate_ast', 'weave_confusion']