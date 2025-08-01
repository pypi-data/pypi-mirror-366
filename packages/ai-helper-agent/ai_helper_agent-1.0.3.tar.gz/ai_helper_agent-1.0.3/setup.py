#!/usr/bin/env python3
"""
Setup script for AI Helper Agent
Creates executable installer and handles environment path setup
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Read version from package
def get_version():
    try:
        with open('ai_helper_agent/__init__.py', 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return "1.0.4"

# Read README
def get_long_description():
    readme_files = ['README_COMPREHENSIVE.md', 'README.md']
    for readme_file in readme_files:
        if os.path.exists(readme_file):
            with open(readme_file, 'r', encoding='utf-8') as f:
                return f.read()
    return "AI Helper Agent - Complete AI Assistant Suite"

# Environment path setup for Windows
def setup_windows_environment():
    """Setup Windows environment paths and shortcuts"""
    if sys.platform == "win32":
        try:
            import winreg
            import win32con
            
            # Get installation path
            install_path = sys.prefix
            scripts_path = os.path.join(install_path, 'Scripts')
            
            # Add to user PATH
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   "Environment", 0, 
                                   winreg.KEY_SET_VALUE | winreg.KEY_READ) as key:
                    
                    current_path = ""
                    try:
                        current_path, _ = winreg.QueryValueEx(key, "PATH")
                    except FileNotFoundError:
                        pass
                    
                    if scripts_path not in current_path:
                        new_path = f"{current_path};{scripts_path}" if current_path else scripts_path
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                        print(f"✅ Added to PATH: {scripts_path}")
                    else:
                        print(f"✅ Already in PATH: {scripts_path}")
                        
            except Exception as e:
                print(f"⚠️ Could not modify PATH: {e}")
                
        except ImportError:
            print("⚠️ Windows registry access not available")
            
    elif sys.platform in ["linux", "darwin"]:
        # Linux/Mac setup
        shell_rc = os.path.expanduser("~/.bashrc")
        if sys.platform == "darwin":
            shell_rc = os.path.expanduser("~/.zshrc")
        
        scripts_path = os.path.join(sys.prefix, 'bin')
        export_line = f'export PATH="{scripts_path}:$PATH"'
        
        try:
            if os.path.exists(shell_rc):
                with open(shell_rc, 'r') as f:
                    content = f.read()
                
                if export_line not in content:
                    with open(shell_rc, 'a') as f:
                        f.write(f'\n# AI Helper Agent\n{export_line}\n')
                    print(f"✅ Added to {shell_rc}")
                else:
                    print(f"✅ Already in {shell_rc}")
        except Exception as e:
            print(f"⚠️ Could not modify shell rc file: {e}")

# Custom install command that sets up environment
class CustomInstallCommand:
    def run(self):
        # Run normal installation
        print("📦 Installing AI Helper Agent...")
        
        # Setup environment
        print("🔧 Setting up environment...")
        setup_windows_environment()
        
        print("✅ Installation complete!")
        print("\n🚀 Quick Start:")
        print("1. Set API key: $env:GROQ_API_KEY='your_key'")
        print("2. Run: ai-helper (or ai-helper-single)")
        print("3. Type 'help' for commands")

# Package configuration
setup(
    name="ai-helper-agent",
    version=get_version(),
    description="Interactive AI Helper Agent for code assistance, analysis, and bug fixing",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="AIStudent",
    author_email="aistudentlearn4@gmail.com",
    maintainer="AIMLDev726",
    maintainer_email="aistudentlearn4@gmail.com",
    url="https://github.com/AIMLDev726/ai-helper-agent",
    project_urls={
        "Homepage": "https://github.com/AIMLDev726/ai-helper-agent",
        "Documentation": "https://github.com/AIMLDev726/ai-helper-agent#readme",
        "Repository": "https://github.com/AIMLDev726/ai-helper-agent",
        "Bug Tracker": "https://github.com/AIMLDev726/ai-helper-agent/issues",
        "Changelog": "https://github.com/AIMLDev726/ai-helper-agent/blob/main/CHANGELOG.md",
    },
    
    # Package discovery
    packages=find_packages(),
    package_data={
        'ai_helper_agent': ['*.txt', '*.md', '*.json'],
    },
    include_package_data=True,
    
    # Python requirements
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "langchain-groq>=0.1.0",
        "langchain-core>=0.1.0", 
        "langchain-community>=0.1.0",
        "langchain>=0.1.0",
        "rich>=13.0.0",
        "structlog>=23.0.0",
        "pathlib2; python_version<'3.4'",
        "faiss-cpu>=1.7.0",
        "chromadb>=0.4.0",
        "cryptography>=3.4.0",
        "sqlalchemy>=1.4.0",
    ],
    
    # Optional dependencies
    extras_require={
        "full": [
            "langchain-openai>=0.1.0",
            "langchain-anthropic>=0.1.0", 
            "langchain-google-genai>=0.1.0",
            "langchain-ollama>=0.1.0",
            "ddgs>=0.9.0",
            "googlesearch-python>=1.2.0",
            "mcp>=0.1.0",
        ],
        "search": [
            "ddgs>=0.9.0",
            "googlesearch-python>=1.2.0",
        ],
        "mcp": [
            "mcp>=0.1.0",
        ],
        "providers": [
            "langchain-openai>=0.1.0",
            "langchain-anthropic>=0.1.0",
            "langchain-google-genai>=0.1.0", 
            "langchain-ollama>=0.1.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8", 
            "mypy",
            "pre-commit"
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov"
        ]
    },
    
    # Console scripts (command-line entry points)
    entry_points={
        'console_scripts': [
            # Multi-provider CLIs (default)
            'ai-helper=ai_helper_agent.cli_multi_provider:main',
            'ai-helper-multi=ai_helper_agent.cli_multi_provider:main',
            'ai-helper-agent=ai_helper_agent.cli_multi_provider:main',
            
            # Single provider CLI (Groq only) 
            'ai-helper-single=ai_helper_agent.cli_single:main',
            'ai-helper-groq=ai_helper_agent.cli_single:main',
            
            # Search-enabled CLIs
            'ai-helper-search=multi_search_cli:main',
            'ai-helper-comprehensive=multi_search_comprehensive_cli:main',
            
            # Legacy compatibility
            'ai_helper_agent=ai_helper_agent.cli_multi_provider:main',
        ],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance", 
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    
    keywords=[
        "ai", "assistant", "code-analysis", "bug-fixing", "automation",
        "langchain", "groq", "openai", "anthropic", "google", "gemini",
        "cli", "development", "programming", "mcp", "search", "web-search"
    ],
    
    # License
    license="MIT",
    
    # Zip safety
    zip_safe=False,
    
    # Custom commands
    # cmdclass={
    #     'install': CustomInstallCommand,
    # },
)

# Post-installation message
if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI Helper Agent Installation Complete!")
    print("="*60)
    
    print("\nQuick Start:")
    print("1. Set your API key:")
    if sys.platform == "win32":
        print("   $env:GROQ_API_KEY='your_groq_api_key_here'")
    else:
        print("   export GROQ_API_KEY='your_groq_api_key_here'")
    
    print("\n2. Run from anywhere:")
    print("   ai-helper                    # Multi-provider CLI")
    print("   ai-helper-single             # Single provider (Groq)")
    print("   ai-helper-comprehensive      # Full features + MCP")
    
    print("\n3. Get API keys:")
    print("   - Groq (Free): https://console.groq.com/keys")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - Anthropic: https://console.anthropic.com/")
    print("   - Google: https://makersuite.google.com/app/apikey")
    
    print("\nDocumentation:")
    print("   - README_COMPREHENSIVE.md - Complete guide")
    print("   - GitHub: https://github.com/AIMLDev726/ai-helper-agent")
    
    print("\nSupport:")
    print("   - Issues: https://github.com/AIMLDev726/ai-helper-agent/issues")
    print("   - Email: aistudentlearn4@gmail.com")
    
    if sys.platform == "win32":
        print("\nImportant: Restart your terminal to use PATH commands!")
    
    print("="*60)
