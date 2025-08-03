"""
AI Helper Agent - Interactive AI Assistant for Programming

A comprehensive AI-powered programming assistant with advanced code generation,
analysis, debugging, and optimization capabilities using multiple LLM providers.

Features:
- Code generation from natural language descriptions
- Intelligent code completion and suggestions
- Cross-language code translation
- Advanced debugging and optimization
- File operations with security controls
- Search functionality across codebases
- Interactive CLI with conversation history
- Support for multiple programming languages
- Multi-provider support (Groq, OpenAI, Anthropic, Google, Ollama)
- Internet-enabled AI with web search capabilities

Latest enhancements:
- Organized project structure for better maintainability
- Updated to latest Groq models (Llama 3.1, Llama 3.3, Gemma 2, etc.)
- Enhanced file creation with proper permissions handling
- Advanced search functionality for files and content
- Codex-like capabilities for professional development
- Improved security manager with better file access controls
"""

# Package metadata
__version__ = "2.0.1"
__author__ = "AIMLDev726"
__email__ = "aistudentlearn4@gmail.com"
__title__ = "ai-helper-agent"
__description__ = "Interactive AI Helper Agent for code assistance, analysis, and bug fixing with multi-provider support"
__url__ = "https://github.com/AIMLDev726/ai-helper-agent"
__license__ = "MIT"

# Lazy loading globals - these imports are what's causing the 5 second delay!
InteractiveAgent = None
create_agent = None
config = None
security_manager = None
validate_python_code = None
run_python_code = None
format_code_output = None
AIHelperCLI = None
main = None

def _lazy_load_core():
    """Lazy load core functionality when needed"""
    global InteractiveAgent, create_agent, config, security_manager
    
    if InteractiveAgent is None:
        try:
            from .core.core import InteractiveAgent, create_agent
            from .core.config import config
            from .core.security import security_manager
        except ImportError:
            # Final fallback
            InteractiveAgent = None
            create_agent = None
            config = None
            security_manager = None

def _lazy_load_utils():
    """Lazy load utilities when needed"""
    global validate_python_code, run_python_code, format_code_output
    
    if validate_python_code is None:
        try:
            from .utils.utils import validate_python_code, run_python_code, format_code_output
        except ImportError:
            try:
                from .utils import validate_python_code, run_python_code, format_code_output
            except ImportError:
                validate_python_code = None
                run_python_code = None
                format_code_output = None

def _lazy_load_cli():
    """Lazy load CLI functionality when needed"""
    global AIHelperCLI, main
    
    if AIHelperCLI is None:
        try:
            from .cli.multi_provider_cli import EnhancedMultiProviderCLI as AIHelperCLI
            from .cli.multi_provider_cli import main
        except ImportError:
            try:
                from .cli.cli import AIHelperCLI, main
            except ImportError:
                AIHelperCLI = None
                main = None

# Lazy property access - load modules only when accessed
def __getattr__(name):
    """Lazy loading of package attributes"""
    if name in ('InteractiveAgent', 'create_agent', 'config', 'security_manager'):
        _lazy_load_core()
        return globals()[name]
    elif name in ('validate_python_code', 'run_python_code', 'format_code_output'):
        _lazy_load_utils()
        return globals()[name]
    elif name in ('AIHelperCLI', 'main'):
        _lazy_load_cli()
        return globals()[name]
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Define what's available for import
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
__description__ = "Interactive AI Helper Agent for code assistance, analysis, and bug fixing with multi-provider support"
__url__ = "https://github.com/AIMLDev726/ai-helper-agent"
__license__ = "MIT"