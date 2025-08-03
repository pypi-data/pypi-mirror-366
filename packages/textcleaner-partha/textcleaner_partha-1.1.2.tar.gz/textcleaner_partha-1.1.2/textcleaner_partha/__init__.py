# textcleaner_partha/__init__.py

from . import preprocess  # Import the module as a namespace
from .preprocess import get_tokens, preprocess_file, get_tokens_from_file  # Import specific functions

__all__ = [
    "preprocess",            # Module namespace
    "get_tokens",            # Function
    "preprocess_file",       # Function
    "get_tokens_from_file"   # Function
]