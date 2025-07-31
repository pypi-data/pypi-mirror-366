"""
Commit-Gen - AI-Powered Git Commit Message Generator

A command-line tool that automatically generates conventional commit messages using AI.
Supports multiple AI providers including OpenRouter, Ollama, and custom providers.
"""

__version__ = "0.1.0"
__author__ = "Mobio Team"
__email__ = "dev@mobio.vn"

from .core import generate_commit_message, generate_changelog
from .cli import main

__all__ = ["generate_commit_message", "generate_changelog", "main"] 