"""
AI Helper Agent Setup Configuration
==================================

Production-ready setup for AI Helper Agent v2.0.1
Author: Meet Solanki (AIML Student)
Email: aistudentlearn4@gmail.com

Features:
- 40+ CLI commands with optimized lazy loading
- Multi-provider AI support (Groq, OpenAI, Anthropic, Google)
- Internet search capabilities
- Rich terminal UI with streaming responses
- Session management with conversation history
- Secure API key management
- Cross-platform compatibility (Windows, Linux, macOS)
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure Python 3.8+ compatibility
if sys.version_info < (3, 8):
    raise RuntimeError("AI Helper Agent requires Python 3.8 or higher")

# Read README for long description
here = Path(__file__).parent.resolve()
try:
    long_description = (here / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "Advanced AI-Powered Programming Assistant with Multi-Provider Support, Internet Search, and 40+ CLI Commands"

# Core dependencies for production deployment
install_requires = [
    # Core LangChain Framework
    "langchain>=0.1.0",
    "langchain-core>=0.1.0", 
    "langchain-community>=0.1.0",
    
    # AI Provider Integrations
    "langchain-groq>=0.1.0",
    "langchain-openai>=0.1.0",
    "langchain-anthropic>=0.1.0",
    "langchain-google-genai>=0.1.0",
    "langchain-ollama>=0.1.0",
    
    # Core System Dependencies
    "rich>=13.0.0",          # Terminal UI and formatting
    "structlog>=23.0.0",     # Structured logging
    "requests>=2.25.0",      # HTTP requests
    "cryptography>=3.4.0",   # Security and encryption
    "sqlalchemy>=1.4.0",     # Database operations
    
    # Internet & Web Search
    "beautifulsoup4>=4.9.0",        # HTML parsing
    "duckduckgo-search>=3.0.0",     # Privacy-focused search
    "googlesearch-python>=1.2.0",   # Google search integration
    
    # Vector Storage & AI Processing
    "faiss-cpu>=1.7.0",      # Fast similarity search
    "chromadb>=0.4.0",       # Vector database
    
    # Python 3.3 compatibility
    "pathlib2; python_version<'3.4'",
]

# Optional development dependencies
extras_require = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
    ],
    "test": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "coverage>=7.0.0",
    ]
}

# Production CLI entry points
entry_points = {
    "console_scripts": [
        # Primary CLI Interfaces
        "ai-helper=ai_helper_agent.cli.enhanced_cli:main",
        "ai-chat=ai_helper_agent.cli.enhanced_cli:main",
        "ai-assist=ai_helper_agent.cli.enhanced_cli:main",
        "ai-selector=ai_helper_agent.cli.cli_selector:main",
        
        # Single Provider CLIs
        "ai-groq=ai_helper_agent.cli.cli_single:main",
        "ai-openai=ai_helper_agent.cli.cli_single:main",
        "ai-anthropic=ai_helper_agent.cli.cli_single:main",
        "ai-google=ai_helper_agent.cli.cli_single:main",
        "ai-ollama=ai_helper_agent.cli.cli_single:main",
        
        # Multi-Provider CLI
        "ai-multi=ai_helper_agent.cli.multi_provider_cli:main",
        "ai-providers=ai_helper_agent.cli.multi_provider_cli:main",
        
        # Internet-Enabled CLIs
        "ai-web=ai_helper_agent.cli.enhanced_internet_cli:main",
        "ai-search=ai_helper_agent.cli.enhanced_internet_cli:main",
        "ai-internet=ai_helper_agent.cli.enhanced_internet_cli:main",
        "ai-web-single=ai_helper_agent.cli.cli_internet_single:main",
        
        # Specialized Commands
        "ai-code=ai_helper_agent.cli.enhanced_cli:main",
        "ai-debug=ai_helper_agent.cli.enhanced_cli:main",
        "ai-fix=ai_helper_agent.cli.enhanced_cli:main",
        "ai-analyze=ai_helper_agent.cli.enhanced_cli:main",
        "ai-review=ai_helper_agent.cli.enhanced_cli:main",
        "ai-optimize=ai_helper_agent.cli.enhanced_cli:main",
        "ai-test=ai_helper_agent.cli.enhanced_cli:main",
        "ai-docs=ai_helper_agent.cli.enhanced_cli:main",
        "ai-explain=ai_helper_agent.cli.enhanced_cli:main",
        "ai-refactor=ai_helper_agent.cli.enhanced_cli:main",
        
        # Provider-Specific Commands
        "groq-chat=ai_helper_agent.cli.cli_single:main",
        "openai-chat=ai_helper_agent.cli.cli_single:main",
        "claude-chat=ai_helper_agent.cli.cli_single:main",
        "gemini-chat=ai_helper_agent.cli.cli_single:main",
        "ollama-chat=ai_helper_agent.cli.cli_single:main",
        
        # Utility Commands
        "ai-setup=ai_helper_agent.utilities.api_key_setup:main",
        "ai-config=ai_helper_agent.core.config:main",
        "ai-version=ai_helper_agent.cli.enhanced_cli:version",
        "ai-help=ai_helper_agent.cli.enhanced_cli:help",
        "ai-status=ai_helper_agent.cli.enhanced_cli:status",
        
        # Advanced Features
        "ai-stream=ai_helper_agent.cli.enhanced_cli:stream_mode",
        "ai-history=ai_helper_agent.cli.enhanced_cli:show_history",
        "ai-clear=ai_helper_agent.cli.enhanced_cli:clear_history",
        "ai-export=ai_helper_agent.cli.enhanced_cli:export_conversation",
        "ai-import=ai_helper_agent.cli.enhanced_cli:import_conversation",
    ]
}

setup(
    name="ai-helper-agent",
    version="2.0.1",
    author="Meet Solanki (AIML Student)",
    author_email="aistudentlearn4@gmail.com",
    description="Advanced AI-Powered Programming Assistant with Multi-Provider Support, Internet Search, and 40+ CLI Commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AIMLDev726/ai-helper-agent",
    project_urls={
        "Bug Reports": "https://github.com/AIMLDev726/ai-helper-agent/issues",
        "Source": "https://github.com/AIMLDev726/ai-helper-agent",
        "Documentation": "https://github.com/AIMLDev726/ai-helper-agent/wiki",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points=entry_points,
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "ai", "assistant", "programming", "code-analysis", "bug-fixing",
        "automation", "groq", "openai", "anthropic", "google", "langchain",
        "internet-search", "cli", "developer-tools", "ai-agent", "streaming",
        "rich-ui", "multi-provider", "conversation-history"
    ],
    platforms=["any"],
    license="MIT",
)
