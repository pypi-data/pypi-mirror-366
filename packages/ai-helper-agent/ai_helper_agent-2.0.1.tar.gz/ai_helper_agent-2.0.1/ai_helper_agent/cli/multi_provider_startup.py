"""
AI Helper Agent - Enhanced Multi-Provider Startup Interface
Responsive logo design and multi-provider LLM support
"""

import os
import sys
import time
import subprocess
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
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

from langchain_groq import ChatGroq

console = Console()

def get_terminal_size():
    """Get terminal dimensions for responsive logo sizing"""
    try:
        import shutil
        size = shutil.get_terminal_size()
        width, height = size.columns, size.lines
        
        # Ensure minimum values to prevent layout issues
        width = max(width, 40)  # Minimum 40 columns
        height = max(height, 10)  # Minimum 10 rows
        
        return width, height
    except:
        return 80, 24  # Default fallback

# Simple logo for all terminal sizes to prevent overflow
SIMPLE_LOGO = """

🤖 AI HELPER AGENT - MULTI-PROVIDER v2.0 🤖
YOUR AUTONOMOUS CODING ASSISTANT

⚡ Multi-Provider AI Coding Assistant ⚡
� Groq | OpenAI | Anthropic | Google | Ollama �

"""

def get_responsive_logo():
    """Get simple logo that works on all terminal sizes"""
    return SIMPLE_LOGO
class MultiProviderStartup:
    """Enhanced startup interface with multi-provider LLM support and responsive design"""
    
    def __init__(self):
        self.console = Console()
        self.env_file = Path(".env")
        self.config = {}
        self.ollama_models = self._get_ollama_models()
        self.available_models = self._get_multi_provider_models()
        
    def _get_ollama_models(self) -> Dict[str, str]:
        """Get available Ollama models from local installation"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                models = {}
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        model_name = line.split()[0]  # First column is model name
                        models[f"ollama_{i}"] = {
                            "name": f"Ollama - {model_name}",
                            "model_id": model_name,
                            "provider": "ollama",
                            "key_name": None,  # No API key needed for local
                            "description": f"Local Ollama model: {model_name}",
                            "speed": "🏠 Local",
                            "category": "local"
                        }
                return models
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Ollama not available: {e}[/yellow]")
            return {}
        return {}
    
    def _get_multi_provider_models(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive model list across all providers"""
        models = {
            # Custom Model Options - For user-specified models
            "custom_groq": {
                "name": "🎯 Custom Groq Model",
                "model_id": "custom",
                "provider": "groq",
                "key_name": "GROQ_API_KEY",
                "description": "Enter your own Groq model name (any model available to your account)",
                "speed": "⚡ Variable",
                "category": "custom_models"
            },
            "custom_openai": {
                "name": "🎯 Custom OpenAI Model", 
                "model_id": "custom",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Enter your own OpenAI model name (gpt-4, gpt-3.5-turbo, etc.)",
                "speed": "🚀 Variable",
                "category": "custom_models"
            },
            "custom_anthropic": {
                "name": "🎯 Custom Anthropic Model",
                "model_id": "custom", 
                "provider": "anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "description": "Enter your own Anthropic model name (claude-3-opus, claude-3-sonnet, etc.)",
                "speed": "🤖 Variable",
                "category": "custom_models"
            },
            "custom_google": {
                "name": "🎯 Custom Google Model",
                "model_id": "custom",
                "provider": "google", 
                "key_name": "GOOGLE_API_KEY",
                "description": "Enter your own Google model name (gemini-pro, gemini-1.5-pro, etc.)",
                "speed": "🌟 Variable",
                "category": "custom_models"
            },
            "custom_ollama": {
                "name": "🎯 Custom Ollama Model",
                "model_id": "custom",
                "provider": "ollama",
                "key_name": None,
                "description": "Enter your own Ollama model name (any model you have installed locally)",
                "speed": "🏠 Variable", 
                "category": "custom_models"
            },
            
            # Groq Models - Lightning Fast
            "1": {
                "name": "Llama 3.3 70B Versatile",
                "model_id": "llama-3.3-70b-versatile",
                "provider": "groq",
                "key_name": "GROQ_API_KEY",
                "description": "Meta's latest large model - General purpose, excellent reasoning",
                "speed": "⚡ Ultra Fast",
                "category": "groq_production"
            },
            "2": {
                "name": "Llama 3.1 8B Instant",
                "model_id": "llama-3.1-8b-instant",
                "provider": "groq",
                "key_name": "GROQ_API_KEY",
                "description": "Ultra-fast instant responses, great for coding",
                "speed": "⚡⚡ Lightning",
                "category": "groq_production"
            },
            "3": {
                "name": "Gemma 2 9B IT",
                "model_id": "gemma2-9b-it",
                "provider": "groq",
                "key_name": "GROQ_API_KEY",
                "description": "Google's fine-tuned chat model - Balanced performance",
                "speed": "⚡ Fast",
                "category": "groq_production"
            },
            "4": {
                "name": "Mixtral 8x7B",
                "model_id": "mixtral-8x7b-32768",
                "provider": "groq",
                "key_name": "GROQ_API_KEY",
                "description": "Excellent for complex tasks and long context",
                "speed": "⚡ Fast",
                "category": "groq_production"
            },
            "5": {
                "name": "DeepSeek R1 70B",
                "model_id": "deepseek-r1-distill-llama-70b",
                "provider": "groq",
                "key_name": "GROQ_API_KEY",
                "description": "Advanced reasoning model with chat distillation",
                "speed": "⚡ Fast",
                "category": "groq_preview"
            },
            "6": {
                "name": "Llama 4 Maverick 17B",
                "model_id": "meta-llama/llama-4-maverick-17b-128e-instruct",
                "provider": "groq",
                "key_name": "GROQ_API_KEY",
                "description": "Next-generation Llama 4 preview model",
                "speed": "⚡ Fast",
                "category": "groq_preview"
            },
            
            # OpenAI Models - Latest Generation
            "7": {
                "name": "GPT-4.1",
                "model_id": "gpt-4.1",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Latest generation April 2025 - Higher performance",
                "speed": "🚀 Fast",
                "category": "openai_latest"
            },
            "8": {
                "name": "GPT-4.1 Mini",
                "model_id": "gpt-4.1-mini",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Widely available mini version - Lower cost",
                "speed": "🚀 Fast",
                "category": "openai_latest"
            },
            "9": {
                "name": "GPT-4.1 Nano",
                "model_id": "gpt-4.1-nano",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Ultra-lightweight for high throughput use cases",
                "speed": "🚀 Very Fast",
                "category": "openai_latest"
            },
            "10": {
                "name": "GPT-4.5",
                "model_id": "gpt-4.5",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Released early 2025 - Better dialogue, fewer hallucinations",
                "speed": "🚀 Moderate",
                "category": "openai_latest"
            },
            "11": {
                "name": "GPT-4o (Omni)",
                "model_id": "gpt-4o",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Multimodal with structured outputs and JSON support",
                "speed": "🚀 Moderate",
                "category": "openai_advanced"
            },
            "12": {
                "name": "GPT-4o Mini",
                "model_id": "gpt-4o-mini",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Smaller, faster version of GPT-4o for cost-sensitive use",
                "speed": "🚀 Fast",
                "category": "openai_advanced"
            },
            "13": {
                "name": "GPT-4 Turbo",
                "model_id": "gpt-4-turbo",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "High-capability chat with latest training",
                "speed": "🚀 Moderate",
                "category": "openai_standard"
            },
            "14": {
                "name": "GPT-3.5 Turbo",
                "model_id": "gpt-3.5-turbo",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Baseline chat model optimized for general use",
                "speed": "🚀 Fast",
                "category": "openai_standard"
            },
            
            # OpenAI Reasoning Models
            "15": {
                "name": "o3",
                "model_id": "o3",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Successor reasoning family for high-precision tasks",
                "speed": "🧠 Slow",
                "category": "openai_reasoning"
            },
            "16": {
                "name": "o3 Mini",
                "model_id": "o3-mini",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Faster version of o3 reasoning model",
                "speed": "🧠 Moderate",
                "category": "openai_reasoning"
            },
            "17": {
                "name": "o3 Mini High",
                "model_id": "o3-mini-high",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "High-performance version of o3 mini",
                "speed": "🧠 Slow",
                "category": "openai_reasoning"
            },
            "18": {
                "name": "o3 Pro",
                "model_id": "o3-pro",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Professional-grade reasoning model",
                "speed": "🧠 Very Slow",
                "category": "openai_reasoning"
            },
            "19": {
                "name": "o1",
                "model_id": "o1",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Advanced reasoning optimized for technical and STEM tasks",
                "speed": "🧠 Slow",
                "category": "openai_reasoning"
            },
            "20": {
                "name": "o1 Mini",
                "model_id": "o1-mini",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Smaller version of o1 reasoning model",
                "speed": "🧠 Moderate",
                "category": "openai_reasoning"
            },
            "21": {
                "name": "o1 Preview",
                "model_id": "o1-preview",
                "provider": "openai",
                "key_name": "OPENAI_API_KEY",
                "description": "Preview version of o1 reasoning capabilities",
                "speed": "🧠 Slow",
                "category": "openai_reasoning"
            },
            
            # Anthropic Models - Complete Claude Family
            "22": {
                "name": "Claude-3.5 Sonnet",
                "model_id": "claude-3-5-sonnet-20240620",
                "provider": "anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "description": "Latest Claude with enhanced reasoning and creativity",
                "speed": "🚀 Moderate",
                "category": "anthropic_latest"
            },
            "23": {
                "name": "Claude-3 Opus",
                "model_id": "claude-3-opus-20240229",
                "provider": "anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "description": "Most capable Claude model for complex tasks",
                "speed": "🚀 Slow",
                "category": "anthropic_advanced"
            },
            "24": {
                "name": "Claude-3 Sonnet",
                "model_id": "claude-3-sonnet-20240229",
                "provider": "anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "description": "Balanced reasoning and creativity model",
                "speed": "🚀 Moderate",
                "category": "anthropic_standard"
            },
            "25": {
                "name": "Claude-3 Haiku",
                "model_id": "claude-3-haiku-20240307",
                "provider": "anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "description": "Fastest Claude model for quick responses",
                "speed": "🚀 Fast",
                "category": "anthropic_standard"
            },
            "26": {
                "name": "Claude-2.1",
                "model_id": "claude-2.1",
                "provider": "anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "description": "Previous generation Claude with good performance",
                "speed": "🚀 Moderate",
                "category": "anthropic_legacy"
            },
            "27": {
                "name": "Claude-2.0",
                "model_id": "claude-2.0",
                "provider": "anthropic",
                "key_name": "ANTHROPIC_API_KEY",
                "description": "Earlier Claude version for basic tasks",
                "speed": "🚀 Fast",
                "category": "anthropic_legacy"
            },
            
            # Google Models - Complete Gemini Family
            "28": {
                "name": "Gemini 2.5 Pro",
                "model_id": "gemini-2.5-pro",
                "provider": "google",
                "key_name": "GOOGLE_API_KEY",
                "description": "Latest Gemini Pro with enhanced capabilities",
                "speed": "🚀 Moderate",
                "category": "google_latest"
            },
            "29": {
                "name": "Gemini 2.5 Flash",
                "model_id": "gemini-2.5-flash",
                "provider": "google",
                "key_name": "GOOGLE_API_KEY",
                "description": "Fast version of Gemini 2.5 for quick responses",
                "speed": "🚀 Fast",
                "category": "google_latest"
            },
            "30": {
                "name": "Gemini 2.0 Flash",
                "model_id": "gemini-2.0-flash",
                "provider": "google",
                "key_name": "GOOGLE_API_KEY",
                "description": "High-speed multimodal AI model",
                "speed": "🚀 Fast",
                "category": "google_standard"
            },
            "31": {
                "name": "Gemini 1.5 Pro",
                "model_id": "gemini-1.5-pro",
                "provider": "google",
                "key_name": "GOOGLE_API_KEY",
                "description": "Advanced multimodal model with long context",
                "speed": "🚀 Moderate",
                "category": "google_standard"
            },
            "32": {
                "name": "Text Bison",
                "model_id": "models/text-bison-001",
                "provider": "google",
                "key_name": "GOOGLE_API_KEY",
                "description": "Google's text generation model for specialized tasks",
                "speed": "🚀 Fast",
                "category": "google_specialized"
            }
        }
        
        # Add Ollama models
        models.update(self.ollama_models)
        return models
    
    def create_llm_instance(self, model_info: Dict[str, Any], api_key: Optional[str] = None) -> Any:
        """Create appropriate LLM instance based on provider"""
        provider = model_info["provider"]
        model_id = model_info["model_id"]
        
        try:
            if provider == "groq":
                return ChatGroq(
                    model=model_id,
                    temperature=0.1,
                    api_key=api_key
                )
            elif provider == "openai" and ChatOpenAI:
                return ChatOpenAI(
                    model=model_id,
                    temperature=0.1,
                    api_key=api_key
                )
            elif provider == "anthropic" and ChatAnthropic:
                return ChatAnthropic(
                    model=model_id,
                    temperature=0.1,
                    api_key=api_key
                )
            elif provider == "google" and ChatGoogleGenerativeAI:
                return ChatGoogleGenerativeAI(
                    model=model_id,
                    google_api_key=api_key,
                    temperature=0.1
                )
            elif provider == "ollama" and ChatOllama:
                return ChatOllama(
                    model=model_id,
                    temperature=0.1
                )
            else:
                raise ValueError(f"Provider {provider} not available or not installed")
                
        except Exception as e:
            self.console.print(f"[red]❌ Failed to create {provider} LLM: {e}[/red]")
            return None
    
    def test_llm_connection(self, llm: Any, provider: str) -> bool:
        """Test LLM connection with a simple query"""
        try:
            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content="Hello")])
            if response and response.content:
                self.console.print(f"[green]✅ {provider.upper()} connection successful![/green]")
                return True
        except Exception as e:
            self.console.print(f"[red]❌ {provider.upper()} connection failed: {e}[/red]")
        return False
    
    def display_responsive_logo(self) -> None:
        """Display logo that adapts to terminal size"""
        logo = get_responsive_logo()
        width, height = get_terminal_size()
        
        # Create animated startup sequence
        with Live(refresh_per_second=4) as live:
            # Phase 1: Logo appears
            live.update(Panel(
                logo, 
                title="[bold cyan]SYSTEM INITIALIZATION[/bold cyan]", 
                border_style="cyan", 
                padding=(1, 2)
            ))
            # Removed time.sleep(1.5) for faster startup
            
            # Phase 2: Systems online
            systems_text = Text()
            systems_text.append("🔋 Power Systems: ", style="dim white")
            systems_text.append("ONLINE", style="bold green")
            systems_text.append("\n🧠 Neural Core: ", style="dim white") 
            systems_text.append("ACTIVE", style="bold green")
            systems_text.append("\n🔧 Multi-Provider Tools: ", style="dim white")
            systems_text.append("READY", style="bold green")
            systems_text.append("\n📡 Terminal Size: ", style="dim white")
            systems_text.append(f"{width}x{height}", style="bold yellow")
            systems_text.append("\n🚀 Ready for Commands!", style="bold cyan")
            
            startup_panel = Panel(
                logo + "\n" + str(systems_text),
                title="[bold green]AI HELPER AGENT - MULTI-PROVIDER READY[/bold green]",
                border_style="green",
                padding=(1, 2)
            )
            live.update(startup_panel)
            # Removed time.sleep(2) for faster startup
    
    def show_enhanced_model_table(self) -> Table:
        """Create enhanced model selection table with all providers"""
        table = Table(
            title="🤖 Multi-Provider AI Models - Enhanced Edition", 
            show_header=True, 
            header_style="bold cyan",
            row_styles=["none", "dim"],  # Alternate row styling
            border_style="bright_cyan",
            show_lines=True  # Add row separators for better readability
        )
        table.add_column("ID", style="dim", width=4)
        table.add_column("Model Name", style="bold magenta", width=25)
        table.add_column("Provider", style="blue", width=12)
        table.add_column("Speed", justify="center", width=12)
        table.add_column("Description", style="dim white", width=40)
        table.add_column("Status", justify="center", width=12)
        
        # Load existing config
        config = self.load_existing_config()
        
        # Group models by category
        categories = {
            "custom_models": "🎨 CUSTOM MODELS (Enter Your Own)",
            "groq_production": "🚀 GROQ PRODUCTION (Lightning Fast)",
            "groq_preview": "🔬 GROQ PREVIEW (Experimental)",
            "openai_latest": "� OPENAI LATEST (2025 Generation)",
            "openai_advanced": "🎯 OPENAI ADVANCED (Multimodal)",
            "openai_reasoning": "🧠 OPENAI REASONING (o1/o3 Series)",
            "openai_standard": "🏢 OPENAI STANDARD (GPT Series)",
            "anthropic_latest": "🔥 ANTHROPIC LATEST (Claude 3.5)",
            "anthropic_advanced": "💎 ANTHROPIC ADVANCED (Claude 3 Opus)",
            "anthropic_standard": "🎭 ANTHROPIC STANDARD (Claude 3)",
            "anthropic_legacy": "📚 ANTHROPIC LEGACY (Claude 2)",
            "google_latest": "⭐ GOOGLE LATEST (Gemini 2.5)",
            "google_standard": "🌟 GOOGLE STANDARD (Gemini 1.5-2.0)",
            "google_specialized": "🔧 GOOGLE SPECIALIZED (Text Models)",
            "local": "🏠 LOCAL OLLAMA MODELS"
        }
        
        # Add models by category
        row_counter = 1
        for category, title in categories.items():
            # Add category header
            table.add_row("", f"[bold yellow]{title}[/bold yellow]", "", "", "", "")
            
            # Add models in this category
            for model_id, model_info in self.available_models.items():
                if model_info.get("category") == category:
                    # Check if provider is available
                    provider = model_info["provider"]
                    status = "✅ Ready"
                    if provider == "openai" and not ChatOpenAI:
                        status = "❌ Install langchain-openai"
                    elif provider == "anthropic" and not ChatAnthropic:
                        status = "❌ Install langchain-anthropic"
                    elif provider == "google" and not ChatGoogleGenerativeAI:
                        status = "❌ Install langchain-google-genai"
                    elif provider == "ollama" and not ChatOllama:
                        status = "❌ Install langchain-community"
                    
                    # Check API key
                    key_name = model_info.get("key_name")
                    if key_name and key_name not in config:
                        status = f"🔑 Need {key_name}"
                    
                    table.add_row(
                        str(row_counter),  # Add numeric ID
                        model_info["name"],
                        model_info["provider"].upper(),
                        model_info["speed"],
                        model_info["description"],
                        status
                    )
                    row_counter += 1
            
            table.add_row("", "", "", "", "", "")  # Spacer
        
        return table
    
    def get_api_key_for_provider(self, provider: str, key_name: str) -> Optional[str]:
        """Get API key for specific provider with validation"""
        config = self.load_existing_config()
        
        if key_name in config:
            # Use existing key
            existing_key = config[key_name]
            if Confirm.ask(f"Use existing {provider.upper()} API key ({existing_key[:8]}...)?"):
                return existing_key
        
        # Get new API key
        self.console.print(f"\n[bold cyan]🔑 {provider.upper()} API Key Setup[/bold cyan]")
        self.console.print(f"Please enter your {provider.upper()} API key:")
        
        if provider == "openai":
            self.console.print("Get your key from: https://platform.openai.com/api-keys")
        elif provider == "anthropic":
            self.console.print("Get your key from: https://console.anthropic.com/")
        elif provider == "google":
            self.console.print("Get your key from: https://makersuite.google.com/app/apikey")
        elif provider == "groq":
            self.console.print("Get your key from: https://console.groq.com/keys")
        
        api_key = Prompt.ask(f"\n{provider.upper()} API Key", password=True)
        
        if api_key:
            # Save to config
            config[key_name] = api_key
            self.save_config(config)
            return api_key
        
        return None
    
    def load_existing_config(self) -> Dict[str, str]:
        """Load existing configuration from .env file"""
        config = {}
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            parts = line.strip().split('=', 1)
                            if len(parts) == 2:
                                key, value = parts
                                config[key] = value
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Error reading .env file: {e}[/yellow]")
        return config
    
    def save_config(self, config: Dict[str, str]) -> bool:
        """Save configuration to .env file"""
        try:
            with open(self.env_file, 'w') as f:
                f.write("# AI Helper Agent Configuration\n")
                for key, value in config.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            self.console.print(f"[red]❌ Error saving config: {e}[/red]")
            return False
    
    def run_multi_provider_setup(self) -> Tuple[Optional[str], Optional[str], Optional[Any]]:
        """Complete multi-provider setup flow"""
        self.display_responsive_logo()
        
        # Show model selection
        table = self.show_enhanced_model_table()
        self.console.print(table)
        
        # Create mapping from numeric ID to model key
        id_to_model = {}
        row_counter = 1
        categories = {
            "custom_models": "🎨 CUSTOM MODELS (Enter Your Own)",
            "groq_production": "🚀 GROQ PRODUCTION (Lightning Fast)",
            "groq_preview": "🔬 GROQ PREVIEW (Experimental)",
            "openai_latest": "⭐ OPENAI LATEST (2025 Generation)",
            "openai_advanced": "🎯 OPENAI ADVANCED (Multimodal)",
            "openai_reasoning": "🧠 OPENAI REASONING (o1/o3 Series)",
            "openai_standard": "🏢 OPENAI STANDARD (GPT Series)",
            "anthropic_latest": "🔥 ANTHROPIC LATEST (Claude 3.5)",
            "anthropic_advanced": "💎 ANTHROPIC ADVANCED (Claude 3 Opus)",
            "anthropic_standard": "🎭 ANTHROPIC STANDARD (Claude 3)",
            "anthropic_legacy": "📚 ANTHROPIC LEGACY (Claude 2)",
            "google_latest": "⭐ GOOGLE LATEST (Gemini 2.5)",
            "google_standard": "🌟 GOOGLE STANDARD (Gemini 1.5-2.0)",
            "google_specialized": "🔧 GOOGLE SPECIALIZED (Text Models)",
            "local": "🏠 LOCAL OLLAMA MODELS"
        }
        
        for category in categories:
            for model_id, model_info in self.available_models.items():
                if model_info.get("category") == category:
                    id_to_model[str(row_counter)] = model_id
                    row_counter += 1
        
        # Get model selection
        self.console.print("\n[bold cyan]📋 How to select a model:[/bold cyan]")
        self.console.print("• Look at the [bold blue]ID[/bold blue] column in the table above")
        self.console.print("• Enter the [bold green]number[/bold green] from the ID column (e.g., [bold yellow]1[/bold yellow], [bold yellow]2[/bold yellow], [bold yellow]15[/bold yellow], etc.)")
        self.console.print("• [bold red]Do NOT[/bold red] enter the model name directly")
        self.console.print("\n[dim]Example: If you want 'qwen2.5-coder:3b', find its ID number in the table and enter that[/dim]")
        
        while True:
            model_choice = Prompt.ask("\n🤖 Select a model by ID number")
            
            # Check if it's a numeric ID
            if model_choice in id_to_model:
                # Convert numeric ID to model key
                model_key = id_to_model[model_choice]
                selected_model = self.available_models[model_key]
            elif model_choice in self.available_models:
                # Direct model key (backward compatibility)
                selected_model = self.available_models[model_choice]
            else:
                available_ids = list(id_to_model.keys())[:10]  # Show first 10 numeric IDs as examples
                self.console.print(f"[red]❌ Invalid model ID '[bold]{model_choice}[/bold]'. Please enter a number from the ID column.[/red]")
                self.console.print(f"[yellow]💡 Available IDs (first 10): {', '.join(available_ids)}...[/yellow]")
                continue
                
                # Handle custom model selection
                if selected_model["model_id"] == "custom":
                    provider = selected_model["provider"]
                    custom_model_name = Prompt.ask(f"\n🎯 Enter the {provider.upper()} model name you want to use")
                    
                    if not custom_model_name.strip():
                        self.console.print("[red]❌ Model name cannot be empty. Please try again.[/red]")
                        continue
                    
                    # Create a new model dict with the custom model name
                    selected_model = selected_model.copy()
                    selected_model["model_id"] = custom_model_name.strip()
                    selected_model["name"] = f"Custom {provider.upper()} - {custom_model_name}"
                    
                    self.console.print(f"[green]✅ Using custom model: {custom_model_name}[/green]")
                
                break
        
        # Get API key if needed
        provider = selected_model["provider"]
        key_name = selected_model.get("key_name")
        api_key = None
        
        if key_name:  # Provider needs API key
            api_key = self.get_api_key_for_provider(provider, key_name)
            if not api_key:
                self.console.print("[red]❌ API key required for this provider.[/red]")
                return None, None, None
        
        # Create and test LLM instance
        self.console.print(f"\n[cyan]🔄 Creating {provider.upper()} LLM instance...[/cyan]")
        llm = self.create_llm_instance(selected_model, api_key)
        
        if llm and self.test_llm_connection(llm, provider):
            self.console.print(f"\n[green]✅ Successfully configured {selected_model['name']}![/green]")
            return selected_model["model_id"], api_key, llm
        else:
            self.console.print(f"\n[red]❌ Failed to configure {selected_model['name']}[/red]")
            return None, None, None

    def run_startup_sequence(self) -> Tuple[Optional[str], Optional[str], Optional[Any]]:
        """Run the complete startup sequence - alias for run_multi_provider_setup for backward compatibility"""
        return self.run_multi_provider_setup()


def demo_multi_provider_startup():
    """Demonstrate the multi-provider startup interface"""
    startup = MultiProviderStartup()
    model_id, api_key, llm = startup.run_multi_provider_setup()
    
    if llm:
        print(f"\n🎉 Setup complete! Using model: {model_id}")
        print("Ready to start AI Helper Agent with multi-provider support!")
    else:
        print("\n❌ Setup failed. Please try again.")


if __name__ == "__main__":
    demo_multi_provider_startup()
