"""
comms - High-accuracy comment removal tool

A Python package for removing comments from programming files while preserving
important code patterns like color codes, URLs, and preprocessor directives.

Supports 20+ programming languages with state-machine based parsing.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import CommentRemover
from .cli import main

__all__ = ["CommentRemover", "main"]
