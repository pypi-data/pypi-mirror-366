"""
AI Helper Agent - Startup Page with Logo and Configuration
Requirement #5: Enhanced ASCII robot logo display, Model selection interface, 
API key persistent storage in .env, Configuration update capability
Updated with responsive design and multi-provider support
"""

import os
import sys
import time
import json
import getpass
from datetime import datetime
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.padding import Padding
from rich.align import Align

# Multi-provider LLM imports
from groq import Groq
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    ChatOllama = None

from langchain_groq import ChatGroq

console = Console()

def get_terminal_size():
    """Get terminal dimensions for responsive logo sizing"""
    try:
        columns, lines = os.get_terminal_size()
        return columns, lines
    except OSError:
        return 80, 24  # Default fallback

def get_responsive_logo():
    """Get logo based on terminal size"""
    columns, lines = get_terminal_size()
    
    if columns >= 120 and lines >= 30:
        return FULL_LOGO
    elif columns >= 80 and lines >= 20:
        return MEDIUM_LOGO
    elif columns >= 60 and lines >= 15:
        return COMPACT_LOGO
    else:
        return TINY_LOGO

# Full Screen Logo (120+ columns, 30+ rows)
FULL_LOGO = """
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                      🤖 AI HELPER AGENT v2.0 🤖                                                    ║
║                                   YOUR AUTONOMOUS CODING ASSISTANT                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

      ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗ 
      ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗
      ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝
      ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗
      ██║  ██║███████╗███████╗██║     ███████╗██║  ██║
      ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝

╭──────────────────────────── AI NEURAL INTERFACE ────────────────────────────╮
│                                                                              │
│     ╭─────╮               ╭─────╮               ╭─────╮               ╭─────╮ │
│     │ ◉ ◉ │               │ ◉ ◉ │               │ ◉ ◉ │               │ ◉ ◉ │ │
│     │  ⌂  │      ▓▓▓      │  ⌂  │      ▓▓▓      │  ⌂  │      ▓▓▓      │  ⌂  │ │
│     ╰─────╯   ╭─────────╮  ╰─────╯   ╭─────────╮  ╰─────╯   ╭─────────╮  ╰─────╯ │
│        ┃      │  GROQ   │     ┃      │ OPENAI  │     ┃      │ANTHROPIC│     ┃   │
│     ╭──┻──╮   │ MODELS  │  ╭──┻──╮   │  GPT-4  │  ╭──┻──╮   │ CLAUDE  │  ╭──┻──╮ │
│     │█▓▓▓█│   ╰─────────╯  │█▓▓▓█│   ╰─────────╯  │█▓▓▓█│   ╰─────────╯  │█▓▓▓█│ │
│     └─────┘                └─────┘                └─────┘                └─────┘ │
│                                                                              │
│        ╭─────╮                           ╭─────╮                              │
│        │ ◉ ◉ │                           │ ◉ ◉ │                              │
│        │  ⌂  │            ▓▓▓            │  ⌂  │                              │
│        ╰─────╯         ╭─────────╮        ╰─────╯                              │
│           ┃            │ GOOGLE  │           ┃                                │
│        ╭──┻──╮         │ GEMINI  │        ╭──┻──╮                             │
│        │█▓▓▓█│         ╰─────────╯        │█▓▓▓█│                             │
│        └─────┘                           └─────┘                             │
╰──────────────────────────────────────────────────────────────────────────────╯

⚡ CAPABILITIES: Advanced Code Generation • Real-time Analysis • Debug Assistance ⚡
🚀 POWERED BY: Groq Lightning • GPT-4 • Claude-3 • Gemini Pro • Local Models 🚀
"""

# Medium Screen Logo (80-119 columns, 20-29 rows)
MEDIUM_LOGO = """
╔═══════════════════════════════════════════════════════════════════════╗
║                        🤖 AI HELPER AGENT v2.0 🤖                      ║
║                    YOUR AUTONOMOUS CODING ASSISTANT                   ║
╚═══════════════════════════════════════════════════════════════════════╝

  ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗ 
  ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗
  ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝
  ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗
  ██║  ██║███████╗███████╗██║     ███████╗██║  ██║
  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝

╭─────────────────── AI NEURAL INTERFACE ──────────────────╮
│     ╭─────╮               ╭─────╮               ╭─────╮     │
│     │ ◉ ◉ │               │ ◉ ◉ │               │ ◉ ◉ │     │
│     │  ⌂  │      ▓▓▓      │  ⌂  │      ▓▓▓      │  ⌂  │     │
│     ╰─────╯   ╭─────────╮  ╰─────╯   ╭─────────╮  ╰─────╯     │
│        ┃      │ GROQ    │     ┃      │ GPT-4   │     ┃       │
│     ╭──┻──╮   │ MODELS  │  ╭──┻──╮   │ CLAUDE  │  ╭──┻──╮    │
│     │█▓▓▓█│   ╰─────────╯  │█▓▓▓█│   ╰─────────╯  │█▓▓▓█│    │
│     └─────┘                └─────┘                └─────┘    │
╰──────────────────────────────────────────────────────────╯

⚡ CAPABILITIES: Advanced Code Generation • Real-time Analysis • Debug Assistance ⚡
🚀 POWERED BY: Groq Lightning • GPT-4 • Claude-3 • Gemini Pro • Local Models 🚀
"""

# Compact Logo (60-79 columns, 15-19 rows)
COMPACT_LOGO = """
╔═══════════════════════════════════════════════════════╗
║             🤖 AI HELPER AGENT v2.0 🤖                ║
║          YOUR AUTONOMOUS CODING ASSISTANT            ║
╚═══════════════════════════════════════════════════════╝

    ███████ ███████ ███████ 
    ██   ██ ██   ██ ██   ██ 
    ███████ ███████ ███████ 
    ██   ██ ██   ██ ██   ██ 
    ██   ██ ██   ██ ██   ██ 

╭──────── AI NEURAL INTERFACE ────────╮
│    ◉ ◉     ◉ ◉     ◉ ◉     ◉ ◉      │
│     ⌂       ⌂       ⌂       ⌂       │
│  ╭─███─╮ ╭─███─╮ ╭─███─╮ ╭─███─╮   │
│  │GROQ │ │GPT-4│ │CLAUDE│ │GEMINI│  │
│  ╰─────╯ ╰─────╯ ╰─────╯ ╰─────╯   │
╰─────────────────────────────────────╯

⚡ Multi-Provider AI Coding Assistant ⚡
"""

# Tiny Logo (40-59 columns, minimal height)
TINY_LOGO = """
╭────────────────────────────────╮
│  🤖 AI HELPER AGENT v2.0 🤖    │
│     ◉ ◉  ◉ ◉  ◉ ◉             │
│      ⌂    ⌂    ⌂              │
│    GROQ GPT CLAUDE             │
╰────────────────────────────────╯
⚡ Multi-Provider AI ⚡
"""

class MultiProviderStartup:
    """Enhanced startup interface with provider-first selection"""
    
    def __init__(self, cli_type: str = "multiple"):
        self.console = Console()
        # Use user-specific directory with CLI type separation
        # C:\Users\<user_name>\.ai_helper_agent\multiple\<username>\ or single\<username>\
        self.cli_type = cli_type  # "single" or "multiple"
        self.base_config_dir = Path.home() / ".ai_helper_agent"
        
        # Get current username
        import getpass
        self.username = getpass.getuser()
        
        # Create CLI-type specific directory structure
        self.config_dir = self.base_config_dir / self.cli_type / self.username
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sessions directory
        self.sessions_dir = self.config_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
        self.env_file = self.config_dir / ".env"
        self.config_file = self.config_dir / "config.json"
        
        # Provider information - conditional based on CLI type
        if self.cli_type == "single":
            # Single provider CLI - Only Groq
            self.providers = {
                "1": {
                    "name": "Groq",
                    "id": "groq",
                    "description": "⚡ Lightning-fast inference with Llama & Gemma models",
                    "color": "bright_yellow",
                    "icon": "🚀",
                    "key_name": "GROQ_API_KEY",
                    "signup_url": "https://console.groq.com/keys"
                }
            }
        else:
            # Multi-provider CLI - All providers
            self.providers = {
                "1": {
                    "name": "Groq",
                    "id": "groq",
                    "description": "⚡ Lightning-fast inference with Llama & Gemma models",
                    "color": "bright_yellow",
                    "icon": "🚀",
                    "key_name": "GROQ_API_KEY",
                    "signup_url": "https://console.groq.com/keys"
                },
                "2": {
                    "name": "OpenAI", 
                    "id": "openai",
                    "description": "🧠 GPT-4, GPT-4o, and O1 reasoning models",
                    "color": "bright_green",
                    "icon": "🤖",
                    "key_name": "OPENAI_API_KEY",
                    "signup_url": "https://platform.openai.com/api-keys"
                },
                "3": {
                    "name": "Anthropic",
                    "id": "anthropic", 
                    "description": "🎯 Claude models for thoughtful conversations",
                    "color": "bright_blue",
                    "icon": "💭",
                    "key_name": "ANTHROPIC_API_KEY",
                    "signup_url": "https://console.anthropic.com/"
                },
                "4": {
                    "name": "Google",
                    "id": "google",
                    "description": "🌟 Gemini models with multimodal capabilities",
                    "color": "bright_red", 
                    "icon": "🔬",
                    "key_name": "GOOGLE_API_KEY",
                    "signup_url": "https://makersuite.google.com/app/apikey"
                },
                "5": {
                    "name": "Ollama (Local)",
                    "id": "ollama",
                    "description": "🏠 Local models running on your machine",
                    "color": "bright_magenta",
                    "icon": "💻",
                    "key_name": "OLLAMA_HOST",
                    "signup_url": "https://ollama.ai/"
                }
            }
        
        # Available models organized by provider (Remove Mixtral as requested)
        self.models_by_provider = {
            "groq": {
                "1": {
                    "name": "Llama 3.3 70B Versatile",
                    "model_id": "llama-3.3-70b-versatile",
                    "description": "Latest Meta Llama model for complex reasoning",
                    "speed": "⚡ Fast"
                },
                "2": {
                    "name": "Llama 3.1 8B Instant",
                    "model_id": "llama-3.1-8b-instant", 
                    "description": "Ultra-fast instant responses, great for coding",
                    "speed": "⚡⚡ Lightning"
                },
                "3": {
                    "name": "Gemma 2 9B IT",
                    "model_id": "gemma2-9b-it",
                    "description": "Google's fine-tuned chat model - Balanced performance",
                    "speed": "⚡ Fast"
                },
                "4": {
                    "name": "Llama 3.1 70B Versatile", 
                    "model_id": "llama-3.1-70b-versatile",
                    "description": "Large 70B model for complex reasoning tasks",
                    "speed": "⚡ Fast"
                }
            },
            "openai": {
                "1": {
                    "name": "GPT-4.5",
                    "model_id": "gpt-4.5",
                    "description": "Released early 2025 - better dialogue, fewer hallucinations",
                    "speed": "🚀 Moderate"
                },
                "2": {
                    "name": "GPT-4o",
                    "model_id": "gpt-4o",
                    "description": "Multimodal model with structured outputs and JSON support",
                    "speed": "🚀 Moderate"
                },
                "3": {
                    "name": "GPT-4o Mini",
                    "model_id": "gpt-4o-mini",
                    "description": "Smaller, faster version suitable for high throughput",
                    "speed": "🚀 Fast"
                },
                "4": {
                    "name": "O1 Preview",
                    "model_id": "o1-preview",
                    "description": "Advanced reasoning optimized for technical/STEM tasks",
                    "speed": "🐢 Slower"
                },
                "5": {
                    "name": "O3 Pro",
                    "model_id": "o3-pro",
                    "description": "Successor reasoning family for high-precision tasks",
                    "speed": "🐢 Slower"
                }
            },
            "anthropic": {
                "1": {
                    "name": "Claude-3.5 Sonnet",
                    "model_id": "claude-3-5-sonnet-20240620",
                    "description": "Latest Claude model with enhanced capabilities",
                    "speed": "🚀 Moderate"
                },
                "2": {
                    "name": "Claude-3 Opus",
                    "model_id": "claude-3-opus-20240229",
                    "description": "Most powerful Claude model for complex tasks", 
                    "speed": "🚀 Moderate"
                },
                "3": {
                    "name": "Claude-3 Haiku",
                    "model_id": "claude-3-haiku-20240307",
                    "description": "Fast and efficient for everyday tasks",
                    "speed": "🚀 Fast"
                }
            },
            "google": {
                "1": {
                    "name": "Gemini 2.5 Pro",
                    "model_id": "gemini-2.5-pro",
                    "description": "Latest Gemini Pro with enhanced capabilities",
                    "speed": "🚀 Moderate"
                },
                "2": {
                    "name": "Gemini 2.5 Flash",
                    "model_id": "gemini-2.5-flash", 
                    "description": "Fast version of Gemini 2.5 for quick responses",
                    "speed": "🚀 Fast"
                },
                "3": {
                    "name": "Gemini 2.0 Flash",
                    "model_id": "gemini-2.0-flash",
                    "description": "Balanced performance and speed",
                    "speed": "🚀 Fast"
                },
                "4": {
                    "name": "Gemini 1.5 Pro",
                    "model_id": "gemini-1.5-pro",
                    "description": "Previous generation Pro model, reliable",
                    "speed": "🚀 Moderate"
                }
            },
            "ollama": {
                "1": {
                    "name": "Llama 3",
                    "model_id": "llama3",
                    "description": "Meta's Llama 3 running locally",
                    "speed": "🏠 Local"
                },
                "2": {
                    "name": "Code Llama",
                    "model_id": "codellama",
                    "description": "Specialized for code generation",
                    "speed": "🏠 Local"
                },
                "3": {
                    "name": "Mistral",
                    "model_id": "mistral",
                    "description": "High-quality open model",
                    "speed": "🏠 Local"
                }
            }
        }
    
    
    def display_responsive_logo(self):
        """Display logo based on terminal size with CLI type info"""
        logo = get_responsive_logo()
        
        # Add CLI type indicator
        cli_type_indicator = f"{'🔥 MULTI-PROVIDER' if self.cli_type == 'multiple' else '⚡ SINGLE PROVIDER'} CLI"
        config_path = f"📁 Config: {self.config_dir}"
        
        # Create enhanced panel with CLI type info
        enhanced_logo = f"{logo}\n\n{cli_type_indicator}\n{config_path}"
        
        panel = Panel(
            enhanced_logo,
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        # Center the logo
        centered_panel = Align.center(panel)
        self.console.print()
        self.console.print(centered_panel)
        self.console.print()
    
    def create_provider_selection_table(self) -> Table:
        """Create provider selection table"""
        cli_title = f"🤖 Choose Your AI Provider ({'Multi-Provider' if self.cli_type == 'multiple' else 'Single Provider'} CLI)"
        table = Table(title=cli_title, show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Provider", style="bold", width=15)
        table.add_column("Description", style="white", width=60)
        
        for provider_id, provider_info in self.providers.items():
            table.add_row(
                provider_id,
                f"{provider_info['icon']} {provider_info['name']}",
                provider_info['description'],
                style=provider_info['color']
            )
        
        return table
    
    def create_model_selection_table(self, provider_id: str) -> Table:
        """Create model selection table for specific provider"""
        provider_info = self.providers[provider_id]
        models = self.models_by_provider[provider_info['id']]
        
        table = Table(
            title=f"{provider_info['icon']} {provider_info['name']} Models", 
            show_header=True, 
            header_style=f"bold {provider_info['color']}"
        )
        table.add_column("ID", style="dim", width=4)
        table.add_column("Model Name", style="cyan", width=30)
        table.add_column("Speed", style="green", width=15)
        table.add_column("Description", style="white", width=50)
        
        for model_id, model_info in models.items():
            table.add_row(
                model_id,
                model_info['name'],
                model_info['speed'],
                model_info['description']
            )
        
        return table
        
        for provider in providers:
            # Add provider header
            table.add_row("", "", "", "", "", style="dim")
            
            provider_models = [
                (k, v) for k, v in self.available_models.items() 
                if v["provider"] == provider
            ]
            
            for model_id, model_info in provider_models:
                table.add_row(
                    model_id,
                    f"[{provider_colors[provider]}]{provider.upper()}[/{provider_colors[provider]}]",
                    model_info["name"],
                    model_info["speed"],
                    model_info["description"],
                    style=provider_colors.get(provider, "white")
                )
        
        return table
    
    def get_api_key_quick(self, provider: str) -> Optional[str]:
        """Get API key quickly without testing - for fast startup"""
        if provider == "groq":
            key_name = "GROQ_API_KEY"
            service_name = "Groq"
        elif provider == "openai":
            key_name = "OPENAI_API_KEY"
            service_name = "OpenAI"
        elif provider == "anthropic":
            key_name = "ANTHROPIC_API_KEY"
            service_name = "Anthropic"
        elif provider == "google":
            key_name = "GOOGLE_API_KEY"
            service_name = "Google"
        elif provider == "ollama":
            # Ollama doesn't need API key
            return "localhost:11434"
        else:
            return None
        
        # Check if key exists in environment first
        existing_key = os.getenv(key_name)
        if existing_key:
            return existing_key
        
        # Check .env file
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            parts = line.split('=', 1)
                            if len(parts) == 2:
                                k, v = parts
                                if k.strip() == key_name:
                                    return v.strip()
            except Exception:
                pass
        
        # Get new API key without testing
        self.console.print(f"\n🔑 Please enter your {service_name} API key:")
        self.console.print(f"You can get it from: {self.get_provider_url(provider)}")
        
        api_key = Prompt.ask(f"{service_name} API Key", password=True)
        
        if api_key and api_key.strip():
            # Save to .env file without testing
            self.save_api_key_to_env(key_name, api_key.strip())
            self.console.print(f"✅ {key_name} saved to .env file")
            return api_key.strip()
        
        return None

    def get_api_key_for_provider(self, provider_choice: str) -> Optional[str]:
        """Get API key for specific provider with user-specific storage"""
        provider_info = self.providers[provider_choice]
        provider_name = provider_info['name']
        key_name = provider_info['key_name']
        
        # Handle Ollama separately (doesn't need API key)
        if provider_info['id'] == 'ollama':
            return self.setup_ollama_host()
        
        # Check if API key exists in user's .env file
        existing_key = self.get_existing_api_key(key_name)
        
        if existing_key:
            masked_key = existing_key[:8] + "..." + existing_key[-4:] if len(existing_key) > 12 else "***"
            if Confirm.ask(f"Use existing {provider_name} API key ({masked_key})?"):
                return existing_key
        
        # Get new API key
        self.console.print(f"\n🔑 Please enter your {provider_name} API key:")
        self.console.print(f"Get your key from: {provider_info['signup_url']}")
        
        api_key = Prompt.ask(f"{provider_name} API Key", password=True)
        
        if api_key and api_key.strip():
            # Test the API key
            if self.test_provider_api_key(provider_info['id'], api_key.strip()):
                # Save to user-specific .env file
                self.save_api_key_to_env(key_name, api_key.strip())
                self.console.print(f"✅ {provider_name} API key saved to {self.env_file}")
                return api_key.strip()
            else:
                self.console.print(f"❌ Invalid {provider_name} API key. Please try again.")
                return None
        
        return None
    
    def save_configuration(self, provider_id: str, model_id: str, api_key: str):
        """Save configuration to CLI-type specific directory"""
        config_data = {
            "cli_type": self.cli_type,
            "username": self.username,
            "provider_id": provider_id,
            "model_id": model_id,
            "last_updated": datetime.now().isoformat(),
            "config_path": str(self.config_dir)
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.console.print(f"✅ Configuration saved to: {self.config_file}")
        except Exception as e:
            self.console.print(f"❌ Failed to save configuration: {e}")

    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from CLI-type specific directory"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.console.print(f"⚠️ Failed to load configuration: {e}")
        return {}

    def get_existing_api_key(self, key_name: str) -> Optional[str]:
        """Get existing API key from user's .env file or environment"""
        # First check environment variables
        api_key = os.getenv(key_name)
        if api_key:
            return api_key
        
        # Then check user's .env file
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f"{key_name}="):
                            return line.split('=', 1)[1].strip('"\'')
            except Exception:
                pass
        
        return None
    
    def get_provider_url(self, provider: str) -> str:
        """Get sign-up URL for each provider"""
        urls = {
            "groq": "https://console.groq.com/keys",
            "openai": "https://platform.openai.com/api-keys",
            "anthropic": "https://console.anthropic.com/",
            "google": "https://makersuite.google.com/app/apikey"
        }
        return urls.get(provider, "")
    
    def setup_ollama_host(self) -> str:
        """Setup Ollama host configuration"""
        default_host = "http://localhost:11434"
        existing_host = os.getenv("OLLAMA_HOST", default_host)
        
        host = Prompt.ask(f"Ollama Host", default=existing_host)
        
        # Test Ollama connection
        if self.test_ollama_connection(host):
            self.save_api_key_to_env("OLLAMA_HOST", host)
            return host
        else:
            self.console.print("❌ Cannot connect to Ollama. Please ensure Ollama is running.")
            return existing_host
    
    def test_ollama_connection(self, host: str) -> bool:
        """Test Ollama connection"""
        try:
            import requests
            response = requests.get(f"{host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_provider_api_key(self, provider: str, api_key: str) -> bool:
        """Test API key for specific provider"""
        try:
            if provider == "groq":
                test_client = Groq(api_key=api_key)
                # Simple test
                response = test_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                return bool(response.choices[0].message.content)
            
            elif provider == "openai" and ChatOpenAI:
                test_llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
                response = test_llm.invoke("Hi")
                return bool(response.content)
            
            elif provider == "anthropic" and ChatAnthropic:
                test_llm = ChatAnthropic(model="claude-3-haiku-20240307", api_key=api_key)
                response = test_llm.invoke("Hi")
                return bool(response.content)
            
            elif provider == "google" and ChatGoogleGenerativeAI:
                test_llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
                response = test_llm.invoke("Hi")
                return bool(response.content)
            
            return False
            
        except Exception as e:
            self.console.print(f"❌ API test failed: {e}")
            return False
    
    def save_api_key_to_env(self, key_name: str, api_key: str):
        """Save API key to .env file"""
        env_content = {}
        
        # Read existing .env file
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            parts = line.split('=', 1)
                            if len(parts) == 2:
                                k, v = parts
                                env_content[k.strip()] = v.strip()
            except Exception:
                pass  # Continue if there's an error reading the file
        
        # Update with new key
        env_content[key_name] = api_key
        
        # Write back to .env file
        try:
            with open(self.env_file, 'w') as f:
                f.write("# AI Helper Agent Configuration\n")
                for k, v in env_content.items():
                    f.write(f"{k}={v}\n")
        except Exception:
            pass  # Silent fail for now
        
        self.console.print(f"✅ {key_name} saved to .env file")
    
    def create_llm_instance(self, model_info: Dict) -> Optional[object]:
        """Create LLM instance based on provider"""
        provider = model_info["provider"]
        model_id = model_info["model_id"]
        
        try:
            if provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    self.console.print("❌ GROQ_API_KEY not found")
                    return None
                return ChatGroq(model=model_id, api_key=api_key, temperature=0.1)
            
            elif provider == "openai" and ChatOpenAI:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    self.console.print("❌ OPENAI_API_KEY not found")
                    return None
                return ChatOpenAI(model=model_id, api_key=api_key, temperature=0.1)
            
            elif provider == "anthropic" and ChatAnthropic:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    self.console.print("❌ ANTHROPIC_API_KEY not found")
                    return None
                return ChatAnthropic(model=model_id, api_key=api_key, temperature=0.1)
            
            elif provider == "google" and ChatGoogleGenerativeAI:
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    self.console.print("❌ GOOGLE_API_KEY not found")
                    return None
                return ChatGoogleGenerativeAI(model=model_id, google_api_key=api_key, temperature=0.1)
            
            elif provider == "ollama" and ChatOllama:
                host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                return ChatOllama(model=model_id, base_url=host, temperature=0.1)
            
            else:
                self.console.print(f"❌ Provider {provider} not supported or not installed")
                return None
                
        except Exception as e:
            self.console.print(f"❌ Error creating LLM instance: {e}")
            return None
    
    def run_startup_sequence(self) -> Tuple[str, str, object]:
        """Run the complete provider-first startup sequence"""
        self.console.clear()
        
        # Display responsive logo
        self.display_responsive_logo()
        
        # Step 1: Show provider selection
        provider_table = self.create_provider_selection_table()
        self.console.print(provider_table)
        
        # Get provider selection
        while True:
            provider_choice = Prompt.ask("\n🤖 Select your AI provider", default="1")
            
            if provider_choice in self.providers:
                selected_provider = self.providers[provider_choice]
                break
            else:
                self.console.print("❌ Invalid choice. Please try again.")
        
        self.console.print(f"\n✅ Selected Provider: {selected_provider['icon']} {selected_provider['name']}")
        
        # Step 2: Get API key for selected provider
        api_key = self.get_api_key_for_provider(provider_choice)
        
        if not api_key and selected_provider['id'] != "ollama":
            self.console.print("❌ Cannot proceed without valid API key")
            return None, None, None
        
        # Step 3: Show models for selected provider only
        self.console.print(f"\n{selected_provider['icon']} Available {selected_provider['name']} Models:")
        model_table = self.create_model_selection_table(provider_choice)
        self.console.print(model_table)
        
        # Get model selection
        available_models = self.models_by_provider[selected_provider['id']]
        while True:
            model_choice = Prompt.ask(f"\n🚀 Select a {selected_provider['name']} model", default="1")
            
            if model_choice in available_models:
                selected_model = available_models[model_choice]
                break
            else:
                self.console.print("❌ Invalid choice. Please try again.")
        
        self.console.print(f"\n✅ Selected Model: {selected_model['name']}")
        
        # Step 4: Create LLM instance
        model_info = {
            "provider": selected_provider['id'],
            "model_id": selected_model['model_id'],
            "name": selected_model['name']
        }
        
        # Set API key in environment so create_llm_instance can find it
        if api_key and selected_provider['id'] != "ollama":
            key_name = selected_provider.get('key_name', f"{selected_provider['id'].upper()}_API_KEY")
            os.environ[key_name] = api_key
        
        llm_instance = self.create_llm_instance(model_info)
        
        if llm_instance:
            # Save configuration to CLI-type specific directory
            self.save_configuration(provider_choice, selected_model['model_id'], api_key or "")
            
            self.console.print("🚀 LLM instance created successfully!")
            self.console.print(f"📁 Configuration saved to: {self.config_dir}")
            return selected_model['model_id'], api_key, llm_instance
        else:
            self.console.print("❌ Failed to create LLM instance")
            return None, None, None
    
    def quick_setup(self, model_id: str = "llama-3.1-8b-instant") -> Tuple[str, str, object]:
        """Quick setup with default Groq model - optimized for speed"""
        # Find model info from the new structure
        model_info = None
        selected_provider_id = None
        
        # Search through all providers for the model
        for provider_id, models in self.models_by_provider.items():
            for model_key, model_data in models.items():
                if model_data["model_id"] == model_id:
                    model_info = {
                        "provider": provider_id,
                        "model_id": model_data["model_id"],
                        "name": model_data["name"]
                    }
                    # Find the provider choice number
                    for p_choice, p_info in self.providers.items():
                        if p_info['id'] == provider_id:
                            selected_provider_id = p_choice
                            break
                    break
            if model_info:
                break
        
        if not model_info:
            # Default to first Groq model
            model_info = {
                "provider": "groq",
                "model_id": "llama-3.1-8b-instant",
                "name": "Llama 3.1 8B Instant"
            }
            selected_provider_id = "1"  # Groq
        
        # Get API key quickly without extensive testing
        api_key = self.get_api_key_quick(selected_provider_id)
        
        if api_key or model_info["provider"] == "ollama":
            llm_instance = self.create_llm_instance(model_info)
            return model_info["model_id"], api_key, llm_instance
        
        return None, None, None
    
    def get_api_key_quick(self, provider_choice: str) -> Optional[str]:
        """Quick API key retrieval without testing"""
        provider_info = self.providers[provider_choice]
        key_name = provider_info['key_name']
        
        # Handle Ollama
        if provider_info['id'] == 'ollama':
            return os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Get existing key from environment or user .env
        return self.get_existing_api_key(key_name)


# Backward compatibility - maintain the original StartupInterface class
class StartupInterface(MultiProviderStartup):
    """Backward compatible startup interface"""
    pass


# Demo function for testing
def demo_startup():
    """Demo the startup interface"""
    startup = MultiProviderStartup()
    
    # Test responsive logo
    print("🖥️ Testing responsive logo...")
    startup.display_responsive_logo()
    
    # Test model table
    print("\n📊 Testing model selection table...")
    table = startup.create_model_selection_table()
    startup.console.print(table)
    
    print("\n✅ Startup interface demo completed!")


if __name__ == "__main__":
    demo_startup()
