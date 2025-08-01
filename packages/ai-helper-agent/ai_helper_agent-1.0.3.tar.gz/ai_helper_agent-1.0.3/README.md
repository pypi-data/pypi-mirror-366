# AI Helper Agent

[![PyPI version](https://badge.fury.io/py/ai-helper-agent.svg)](https://badge.fury.io/py/ai-helper-agent)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive AI-powered programming assistant with advanced code generation, analysis, debugging, and optimization capabilities using multiple LLM providers including Groq, OpenAI, Anthropic, Google, and Ollama.

## Features

### 🚀 Core Capabilities
- **Code Generation**: Create code from natural language descriptions
- **Intelligent Analysis**: Advanced code review and optimization suggestions
- **Multi-Language Support**: Python, JavaScript, TypeScript, and more
- **Cross-Language Translation**: Convert code between programming languages
- **Advanced Debugging**: Identify and fix bugs with AI assistance
- **File Operations**: Secure file reading, writing, and modification

### 🔧 Advanced Features
- **Multi-Provider Support**: Choose from Groq, OpenAI, Anthropic, Google, or Ollama
- **Interactive CLI**: User-friendly command-line interface with conversation history
- **Search Functionality**: Advanced codebase search and analysis
- **Security Controls**: Built-in security manager with access controls
- **Custom Models**: Support for custom model selection per provider
- **Streaming Responses**: Real-time response streaming for better UX

### 🤖 Latest AI Models
- **Groq**: Llama 3.1, Llama 3.3, Gemma 2, Mixtral
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku
- **Google**: Gemini Pro, Gemini Pro Vision
- **Ollama**: Local model support

## Installation

```bash
pip install ai-helper-agent
```

## Quick Start

### Basic Usage

```bash
# Start the multi-provider CLI (default)
ai-helper

# Use specific provider CLI
ai-helper-single  # Groq only
```

### Python API

```python
from ai_helper_agent import create_agent

# Create an agent instance
agent = create_agent()

# Ask for help
response = agent.process_request("How do I implement a binary search in Python?")
print(response)
```

## CLI Commands

The package provides several CLI entry points:

- `ai-helper` - Multi-provider CLI (default, recommended)
- `ai-helper-multi` - Multi-provider CLI (alias)
- `ai-helper-single` - Single provider CLI (Groq only)
- `ai-helper-groq` - Groq-specific CLI (alias)

## Configuration

### API Keys Setup

The agent supports multiple LLM providers. Configure your API keys:

```bash
# For Groq (recommended for free tier)
export GROQ_API_KEY="your-groq-api-key"

# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For Google
export GOOGLE_API_KEY="your-google-api-key"
```

### Provider Selection

In the multi-provider CLI, you can:
- Choose your preferred provider at startup
- Switch between providers during conversation
- Use custom models for each provider
- Configure default settings

## Examples

### Code Generation
```
> Create a Python function to calculate fibonacci numbers

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Optimized version with memoization
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]
```

### Code Analysis
```
> Analyze this code for potential issues: [paste your code]

Analysis Results:
- Performance: Consider using list comprehension instead of for loop
- Security: Input validation needed for user data
- Best Practices: Add type hints and docstrings
```

### Bug Fixing
```
> Fix the bug in this function: [paste problematic code]

Issue Identified: Index out of range error
Fixed Code: [corrected version with explanation]
Explanation: The loop was accessing array[i+1] without checking bounds
```

## Advanced Usage

### Custom Configuration

```python
from ai_helper_agent import InteractiveAgent
from ai_helper_agent.config import config

# Customize configuration
config.update({
    'temperature': 0.7,
    'max_tokens': 2048,
    'provider': 'groq'
})

# Create agent with custom settings
agent = InteractiveAgent()
```

### File Operations

```python
from ai_helper_agent import InteractiveAgent

agent = InteractiveAgent()

# Analyze a file
response = agent.process_request("Analyze the code in myfile.py")

# Get optimization suggestions
response = agent.process_request("Optimize the performance of myfile.py")
```

## Development

### Requirements

- Python 3.8+
- Internet connection for API access
- API keys for chosen providers

### Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [GitHub Repository](https://github.com/AIMLDev726/ai-helper-agent)
- **Issues**: [Bug Tracker](https://github.com/AIMLDev726/ai-helper-agent/issues)
- **Changelog**: [CHANGELOG.md](https://github.com/AIMLDev726/ai-helper-agent/blob/main/CHANGELOG.md)

## Acknowledgments

- Built with [LangChain](https://langchain.com/) framework
- Powered by multiple LLM providers
- Inspired by GitHub Copilot and similar AI coding assistants

---

**Made with ❤️ by AIMLDev726**
