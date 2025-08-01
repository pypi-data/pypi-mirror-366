"""
Monkey Coder Core - Python orchestration package

This package provides the core functionality for the Monkey Coder project,
including AI model integration, code generation, and analysis capabilities.
"""

__version__ = "1.0.0"

from .generator import CodeGenerator
from .analyzer import CodeAnalyzer
from . import quantum

__all__ = ["CodeGenerator", "CodeAnalyzer", "quantum"]
