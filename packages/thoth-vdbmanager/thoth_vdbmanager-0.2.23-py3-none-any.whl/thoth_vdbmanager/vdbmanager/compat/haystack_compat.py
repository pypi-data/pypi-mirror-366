"""
Haystack compatibility layer for smooth migration between versions.
"""

import sys
import importlib

# Ensure haystack module is imported
import haystack

# Import functions from their new locations in haystack-ai
try:
    from haystack.core.serialization import default_from_dict, default_to_dict
    from haystack.dataclasses import Document
    from haystack.core.component import component
    from haystack.core.pipeline import Pipeline
    
    # Inject into haystack module namespace for backward compatibility
    haystack.default_from_dict = default_from_dict
    haystack.default_to_dict = default_to_dict
    haystack.Document = Document
    haystack.component = component
    haystack.Pipeline = Pipeline
    
    # Also update sys.modules to handle direct imports
    if 'haystack' in sys.modules:
        sys.modules['haystack'].default_from_dict = default_from_dict
        sys.modules['haystack'].default_to_dict = default_to_dict
        sys.modules['haystack'].Document = Document
        sys.modules['haystack'].component = component
        sys.modules['haystack'].Pipeline = Pipeline
        
except ImportError:
    # Fallback for older haystack versions
    pass

def apply_compatibility_patches():
    """Apply compatibility patches for haystack imports."""
    # This function can be called explicitly if needed
    pass