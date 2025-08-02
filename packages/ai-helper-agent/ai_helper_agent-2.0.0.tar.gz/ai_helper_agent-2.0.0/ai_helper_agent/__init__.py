"""
AI Helper Agent - Interactive AI Assistant for Programming

A comprehensive AI-powered programming assistant with advanced code generation,
analysis, debugging, and optimization capabilities using Groq's latest models.

Features:
- Code generation from natural language descriptions
- Intelligent code completion and suggestions
- Cross-language code translation
- Advanced debugging and optimization
- File operations with security controls
- Search functionality across codebases
- Interactive CLI with conversation history
- Support for multiple programming languages

Latest enhancements:
- Updated to latest Groq models (Llama 3.1, Llama 3.3, Gemma 2, etc.)
- Enhanced file creation with proper permissions handling
- Advanced search functionality for files and content
- Codex-like capabilities for professional development
- Improved security manager with better file access controls
"""

from .core import InteractiveAgent, create_agent
from .utils import validate_python_code, run_python_code, format_code_output
from .config import config
from .cli import AIHelperCLI, main
from .security import security_manager

__version__ = "2.0.0"
__author__ = "AIMLDev726"
__email__ = "aistudentlearn4@gmail.com"

__all__ = [
    "InteractiveAgent",
    "create_agent",
    "validate_python_code", 
    "run_python_code",
    "format_code_output",
    "config",
    "AIHelperCLI",
    "main",
    "security_manager"
]

# Package metadata
__title__ = "ai-helper-agent"
__description__ = "Interactive AI Helper Agent for code assistance, analysis, and bug fixing with Codex-like capabilities"
__url__ = "https://github.com/AIMLDev726/ai-helper-agent"
__license__ = "MIT"