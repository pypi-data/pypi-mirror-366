"""
Enhanced Internet CLI with G4F Support
AI Helper Agent - Internet-Enabled CLI with Groq and G4F providers
"""

import os
import sys
import json
import asyncio
import warnings
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Filter out warnings to keep CLI clean
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
warnings.filterwarnings("ignore", message=".*avconv.*")
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*")
warnings.filterwarnings("ignore", module="pydub")

# Import our managers
try:
    from .api_key_manager import api_key_manager
    from .conversation_manager import conversation_manager, MessageRole
except ImportError:
    # Fallback for direct execution
    from api_key_manager import api_key_manager
    from conversation_manager import conversation_manager, MessageRole

# Rich for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.markdown import Markdown
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

# G4F imports
try:
    from g4f.client import Client as G4FClient
    from g4f.client import AsyncClient as G4FAsyncClient
    from g4f import Provider
    import g4f
    G4F_AVAILABLE = True
except ImportError:
    G4F_AVAILABLE = False
    G4FClient = None

# Groq imports
try:
    from groq import AsyncGroq
    from langchain_groq import ChatGroq  # Keep for compatibility
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    AsyncGroq = None
    ChatGroq = None

class G4FProviderManager:
    """Manages G4F providers and models dynamically"""
    
    def __init__(self):
        self.all_providers = self._get_all_providers_dynamic()
        self.provider_models = self._organize_by_provider()
    
    def _get_all_providers_dynamic(self) -> List[Dict[str, Any]]:
        """Get all available G4F providers dynamically from the g4f package"""
        if not G4F_AVAILABLE:
            return []
        
        all_providers = []
        
        # Get all provider classes from g4f.Provider
        for name in dir(Provider):
            if not name.startswith('_'):
                try:
                    provider_class = getattr(Provider, name)
                    
                    # Check if it's a class and has the expected attributes
                    if hasattr(provider_class, 'working') and provider_class.working:
                        provider_info = {
                            'name': name,
                            'class_name': provider_class.__name__,
                            'working': getattr(provider_class, 'working', False),
                            'supports_stream': getattr(provider_class, 'supports_stream', False),
                            'supports_system_message': getattr(provider_class, 'supports_system_message', False),
                            'needs_auth': getattr(provider_class, 'needs_auth', False),
                            'url': getattr(provider_class, 'url', 'N/A'),
                            'models': list(getattr(provider_class, 'models', [])) if getattr(provider_class, 'models', None) else []
                        }
                        
                        all_providers.append(provider_info)
                        
                except Exception as e:
                    # Skip providers that can't be processed
                    continue
        
        # Sort by name for better organization
        return sorted(all_providers, key=lambda x: x['name'])
    
    def _organize_by_provider(self) -> Dict[str, List[str]]:
        """Organize models by provider"""
        organized = {}
        for provider in self.all_providers:
            organized[provider['name']] = provider['models']
        return organized
    
    def get_featured_providers(self) -> List[Dict[str, Any]]:
        """Get a curated list of featured/popular providers"""
        featured_names = [
            'OpenaiChat', 'ChatGpt', 'BingChat', 'Blackbox', 'Claude',
            'Gemini', 'PerplexityAi', 'You', 'Groq', 'DeepInfra',
            'HuggingChat', 'Llama', 'Meta', 'Anthropic', 'CopilotMicrosoft'
        ]
        
        featured = []
        for provider in self.all_providers:
            if provider['name'] in featured_names:
                featured.append(provider)
        
        # Add remaining providers if featured list is small
        if len(featured) < 10:
            remaining = [p for p in self.all_providers if p not in featured]
            featured.extend(remaining[:10-len(featured)])
        
        return featured[:15]  # Limit to 15 featured
    
    def show_provider_selection(self, show_all: bool = False) -> Table:
        """Create provider selection table"""
        if not RICH_AVAILABLE:
            return None
        
        providers_to_show = self.all_providers if show_all else self.get_featured_providers()
        
        table = Table(
            title=f"🤖 G4F AI Providers ({'All' if show_all else 'Featured'} - {len(providers_to_show)} providers)", 
            show_header=True, 
            header_style="bold magenta"
        )
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Provider", justify="left", style="green")
        table.add_column("Auth", justify="center", style="yellow")
        table.add_column("Stream", justify="center", style="blue")
        table.add_column("Models", justify="center", style="white")
        table.add_column("URL", justify="left", style="dim white", max_width=30)
        
        for i, provider in enumerate(providers_to_show, 1):
            auth_status = "🔐 Yes" if provider['needs_auth'] else "🆓 No"
            stream_status = "⚡ Yes" if provider['supports_stream'] else "❌ No"
            model_count = len(provider['models']) if provider['models'] else "Auto"
            url = provider['url'] if provider['url'] and provider['url'] != 'N/A' else "Not specified"
            
            table.add_row(
                str(i),
                provider['name'],
                auth_status,
                stream_status,
                str(model_count),
                url
            )
        
        return table
    
    def show_model_selection(self, provider_name: str) -> Table:
        """Create model selection table for a provider"""
        if not RICH_AVAILABLE or provider_name not in self.provider_models:
            return None
        
        models = self.provider_models[provider_name]
        if not models:
            if RICH_AVAILABLE:
                console.print(f"[yellow]⚠️ No specific models listed for {provider_name}. Will use default model.[/yellow]")
            return None
        
        table = Table(title=f"🤖 {provider_name} Models ({len(models)} available)", show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Model", justify="left", style="green")
        table.add_column("Type", justify="left", style="white")
        
        for i, model in enumerate(models, 1):
            # Categorize models
            model_type = "Unknown"
            if "gpt" in model.lower():
                model_type = "OpenAI GPT"
            elif "claude" in model.lower():
                model_type = "Anthropic Claude"
            elif "gemini" in model.lower():
                model_type = "Google Gemini"
            elif "llama" in model.lower():
                model_type = "Meta Llama"
            elif "dall-e" in model.lower():
                model_type = "Image Generation"
            elif any(term in model.lower() for term in ["vision", "image"]):
                model_type = "Multimodal"
            elif any(term in model.lower() for term in ["mini", "small", "7b", "8b"]):
                model_type = "Lightweight"
            elif any(term in model.lower() for term in ["large", "70b", "405b"]):
                model_type = "Large Model"
            
            table.add_row(str(i), model, model_type)
        
        return table

class EnhancedInternetCLI:
    """Enhanced CLI with both Groq and G4F support"""
    
    def __init__(self):
        # Check if we're in help mode (avoid heavy initialization)
        self.help_mode = '--help' in sys.argv or '-h' in sys.argv
        
        self.provider_type = None  # 'groq' or 'g4f'
        self.llm_client = None
        self.selected_model = None
        self.selected_provider = None
        self.g4f_manager = G4FProviderManager()
        self.session_id = f"enhanced_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_manager = conversation_manager  # Initialize conversation manager
        
        # Configure console (only if not in help mode)
        if not self.help_mode:
            if RICH_AVAILABLE:
                console.print("✅ Using Rich for enhanced display")
            else:
                print("⚠️ Rich not available - using basic display")
    
    def show_main_banner(self):
        """Show the main application banner"""
        if RICH_AVAILABLE:
            banner = """
╔═══════════════════════════════════════════════════════╗
║                🤖 AI HELPER AGENT v2.0 🤖             ║
║           INTERNET-ENABLED MULTI-PROVIDER CLI         ║
╚═══════════════════════════════════════════════════════╝

🌐 INTERNET ACCESS ENABLED
🔍 AI will automatically search when needed
⚡ Multiple AI providers available
"""
            console.print(Panel(banner, style="bold blue"))
        else:
            print("🤖 AI HELPER AGENT v2.0 - INTERNET-ENABLED MULTI-PROVIDER CLI")
            print("🌐 Internet access enabled - AI will search automatically")
    
    def show_provider_choice(self):
        """Show provider selection menu"""
        if RICH_AVAILABLE:
            table = Table(title="🚀 Choose Your AI Provider", show_header=True, header_style="bold magenta")
            table.add_column("ID", justify="center", style="cyan", no_wrap=True)
            table.add_column("Provider", justify="left", style="green")
            table.add_column("Features", justify="left", style="white")
            
            table.add_row("1", "🚀 Groq", "⚡ Lightning-fast inference with Llama models")
            table.add_row("2", "🌐 G4F", "🆓 Free access to multiple AI providers (GPT, Claude, Gemini)")
            
            console.print(table)
        else:
            print("\n🚀 Choose Your AI Provider:")
            print("1. 🚀 Groq - Lightning-fast inference")  
            print("2. 🌐 G4F - Free access to multiple providers")
    
    def setup_groq_provider(self):
        """Setup Groq provider"""
        if not GROQ_AVAILABLE:
            if RICH_AVAILABLE:
                console.print("[red]❌ Groq not available. Please install: pip install langchain-groq[/red]")
            else:
                print("❌ Groq not available. Please install: pip install langchain-groq")
            return False
        
        # Get API key from manager first
        api_key = api_key_manager.get_api_key('groq')
        
        if not api_key:
            if RICH_AVAILABLE:
                console.print("[yellow]🔑 Enter your Groq API key:[/yellow]")
            else:
                print("🔑 Enter your Groq API key:")
            api_key = input().strip()
            
            if not api_key:
                if RICH_AVAILABLE:
                    console.print("[red]❌ API key required for Groq[/red]")
                else:
                    print("❌ API key required for Groq")
                return False
            
            # Offer to save the key
            if RICH_AVAILABLE:
                save_key = console.input("💾 Save this API key for future use? (y/N): ").strip().lower()
            else:
                save_key = input("💾 Save this API key for future use? (y/N): ").strip().lower()
            
            if save_key == 'y':
                if api_key_manager.set_api_key('groq', api_key):
                    if RICH_AVAILABLE:
                        console.print("[green]✅ API key saved securely[/green]")
                    else:
                        print("✅ API key saved securely")
        
        # Show Groq models
        groq_models = [
            ("llama-3.3-70b-versatile", "Llama 3.3 70B - Latest Meta model"),
            ("llama-3.1-8b-instant", "Llama 3.1 8B - Ultra fast responses"),
            ("gemma2-9b-it", "Gemma 2 9B - Google's balanced model"),
            ("llama-3.1-70b-versatile", "Llama 3.1 70B - Large reasoning model")
        ]
        
        if RICH_AVAILABLE:
            table = Table(title="🚀 Groq Models", show_header=True, header_style="bold cyan")
            table.add_column("ID", justify="center", style="cyan", no_wrap=True)
            table.add_column("Model", justify="left", style="green")
            table.add_column("Description", justify="left", style="white")
            
            for i, (model, desc) in enumerate(groq_models, 1):
                table.add_row(str(i), model, desc)
            
            console.print(table)
        else:
            print("\n🚀 Groq Models:")
            for i, (model, desc) in enumerate(groq_models, 1):
                print(f"{i}. {model} - {desc}")
        
        # Get model selection
        try:
            choice = int(input("🚀 Select model (1): ") or "1")
            if 1 <= choice <= len(groq_models):
                selected_model = groq_models[choice-1][0]
                
                # Create Groq clients (both for different use cases)
                if ChatGroq:
                    self.llm_client = ChatGroq(
                        model=selected_model,
                        temperature=0.1,
                        api_key=api_key
                    )
                else:
                    self.llm_client = None
                    
                if AsyncGroq:
                    self.async_groq_client = AsyncGroq(api_key=api_key)
                else:
                    self.async_groq_client = None
                
                self.provider_type = 'groq'
                self.selected_model = selected_model
                self.api_key = api_key
                
                if RICH_AVAILABLE:
                    console.print(f"[green]✅ Groq configured with {selected_model}[/green]")
                else:
                    print(f"✅ Groq configured with {selected_model}")
                return True
            else:
                if RICH_AVAILABLE:
                    console.print("[red]❌ Invalid choice[/red]")
                else:
                    print("❌ Invalid choice")
                return False
                
        except ValueError:
            if RICH_AVAILABLE:
                console.print("[red]❌ Invalid input[/red]")
            else:
                print("❌ Invalid input")
            return False
    
    def setup_g4f_provider(self):
        """Setup G4F provider with dynamic provider selection"""
        if not G4F_AVAILABLE:
            if RICH_AVAILABLE:
                console.print("[red]❌ G4F not available. Please install: pip install -U g4f[all][/red]")
            else:
                print("❌ G4F not available. Please install: pip install -U g4f[all]")
            return False
        
        # Show provider selection options
        if RICH_AVAILABLE:
            console.print("\n🌐 G4F Provider Options:")
            console.print("1. 📋 Featured Providers (15 popular providers)")
            console.print("2. 📖 All Providers (84+ providers)")
        else:
            print("\n🌐 G4F Provider Options:")
            print("1. 📋 Featured Providers (15 popular providers)")
            print("2. 📖 All Providers (84+ providers)")
        
        try:
            view_choice = input("Select view (1): ").strip() or "1"
            show_all = view_choice == "2"
        except:
            show_all = False
        
        # Show provider selection
        table = self.g4f_manager.show_provider_selection(show_all=show_all)
        if table:
            console.print(table)
        else:
            # Fallback display
            providers = self.g4f_manager.all_providers if show_all else self.g4f_manager.get_featured_providers()
            print(f"\n🌐 G4F Providers ({len(providers)} available):")
            for i, provider in enumerate(providers, 1):
                auth = "🔐" if provider['needs_auth'] else "🆓"
                stream = "📡" if provider['supports_stream'] else ""
                models = len(provider['models']) if provider['models'] else "?"
                print(f"{i:2d}. {auth}{stream} {provider['name']} ({models} models)")
        
        # Get provider selection
        try:
            providers_list = self.g4f_manager.all_providers if show_all else self.g4f_manager.get_featured_providers()
            choice = int(input(f"\n🌐 Select provider (1-{len(providers_list)}): ") or "1")
            
            if 1 <= choice <= len(providers_list):
                selected_provider = providers_list[choice-1]
                
                if RICH_AVAILABLE:
                    console.print(f"\n[green]✅ Selected: {selected_provider['name']}[/green]")
                    if selected_provider['needs_auth']:
                        console.print("[yellow]🔐 This provider requires authentication[/yellow]")
                    else:
                        console.print("[green]🆓 This provider is free to use[/green]")
                
                # Handle authentication if needed
                api_key = None
                if selected_provider['needs_auth']:
                    if RICH_AVAILABLE:
                        console.print(f"[yellow]🔑 Enter API key for {selected_provider['name']} (or press Enter to skip):[/yellow]")
                    else:
                        print(f"🔑 Enter API key for {selected_provider['name']} (or press Enter to skip):")
                    
                    api_key = input().strip()
                    if not api_key:
                        if RICH_AVAILABLE:
                            console.print("[yellow]⚠️ No API key provided. Some providers may not work properly.[/yellow]")
                        else:
                            print("⚠️ No API key provided. Some providers may not work properly.")
                
                # Show model selection
                models = selected_provider['models']
                selected_model = "default"
                
                if models and len(models) > 0:
                    model_table = self.g4f_manager.show_model_selection(selected_provider['name'])
                    if model_table:
                        console.print(model_table)
                    else:
                        print(f"\n🤖 Available models for {selected_provider['name']}:")
                        for i, model in enumerate(models[:20], 1):  # Show first 20 models
                            print(f"  {i:2d}. {model}")
                        if len(models) > 20:
                            print(f"  ... and {len(models) - 20} more models")
                    
                    try:
                        model_choice = input(f"🤖 Select model (1-{min(len(models), 20)}) or Enter for default: ").strip()
                        if model_choice and model_choice.isdigit():
                            model_idx = int(model_choice) - 1
                            if 0 <= model_idx < len(models):
                                selected_model = models[model_idx]
                        else:
                            selected_model = models[0] if models else "default"
                    except:
                        selected_model = models[0] if models else "default"
                
                # Create G4F client
                try:
                    self.llm_client = G4FClient()
                    self.provider_type = 'g4f'
                    self.selected_model = selected_model
                    self.selected_provider = selected_provider
                    self.api_key = api_key
                    
                    if RICH_AVAILABLE:
                        console.print(f"[green]✅ G4F configured successfully![/green]")
                        console.print(f"[dim]Provider: {selected_provider['name']}[/dim]")
                        console.print(f"[dim]Model: {selected_model}[/dim]")
                        console.print(f"[dim]Auth: {'Yes' if api_key else 'No'}[/dim]")
                        console.print(f"[dim]Streaming: {'Yes' if selected_provider['supports_stream'] else 'No'}[/dim]")
                    else:
                        print(f"✅ G4F configured with {selected_provider['name']} - {selected_model}")
                    
                    return True
                    
                except Exception as e:
                    if RICH_AVAILABLE:
                        console.print(f"[red]❌ Error setting up G4F client: {str(e)}[/red]")
                    else:
                        print(f"❌ Error setting up G4F client: {str(e)}")
                    return False
            else:
                if RICH_AVAILABLE:
                    console.print("[red]❌ Invalid choice[/red]")
                else:
                    print("❌ Invalid choice")
                return False
                
        except ValueError:
            if RICH_AVAILABLE:
                console.print("[red]❌ Invalid input[/red]")
            else:
                print("❌ Invalid input")
            return False
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[red]❌ Setup error: {str(e)}[/red]")
            else:
                print(f"❌ Setup error: {str(e)}")
            return False
    
    async def generate_json_response(self, user_input: str, response_format: dict = None) -> dict:
        """Generate JSON response using AsyncGroq for structured output"""
        if self.provider_type != 'groq' or not self.async_groq_client:
            return {"error": "JSON responses only supported with Groq AsyncGroq client"}
        
        try:
            # Default JSON response format if none provided
            if not response_format:
                response_format = {
                    "type": "json_object"
                }
            
            chat_completion = await self.async_groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Always respond with valid JSON format."
                    },
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ],
                model=self.selected_model,
                temperature=0.1,
                response_format=response_format
            )
            
            import json
            json_response = json.loads(chat_completion.choices[0].message.content)
            return json_response
            
        except Exception as e:
            return {"error": f"JSON generation failed: {str(e)}"}
    
    def _stream_with_rich_formatting(self, text_chunks, provider_name="AI"):
        """Stream text with REAL-TIME Rich markdown formatting using Live Display"""
        from rich.live import Live
        from rich.markdown import Markdown
        from rich.text import Text
        import time
        
        if not RICH_AVAILABLE:
            # Fallback for non-Rich environments
            print(f"\n🤖 {provider_name}:")
            full_response = ""
            for chunk in text_chunks:
                if chunk and isinstance(chunk, str):
                    print(chunk, end="", flush=True)
                    full_response += chunk
            print()  # Final newline
            return full_response
        
        # Initialize for real-time streaming
        console.print(f"\n[bold blue]🤖 {provider_name}:[/bold blue]")
        console.print("[bold cyan]══════ Live Streaming View ══════[/bold cyan]")
        
        accumulated_text = ""
        
        # Use Rich Live Display for real-time updates
        with Live(console=console, refresh_per_second=8, transient=False) as live:
            for chunk in text_chunks:
                if chunk and isinstance(chunk, str):
                    accumulated_text += chunk
                    
                    # Real-time rendering with enhanced markdown processing
                    try:
                        # Always use manual formatting for better control during streaming
                        renderable = self._create_enhanced_streaming_renderable(accumulated_text)
                        live.update(renderable)
                        
                        # Small delay for smooth streaming effect
                        time.sleep(0.05)
                        
                    except Exception as e:
                        # Fallback to plain text if formatting fails
                        live.update(Text(accumulated_text))
        
        # Show final enhanced view after streaming completes
        console.print("[bold cyan]═══════════════════════════[/bold cyan]")
        console.print("[dim]✅ Streaming complete[/dim]")
        
        # Save to conversation history if available
        if hasattr(self, 'conversation_manager') and hasattr(self, 'session_id'):
            try:
                self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, accumulated_text)
            except:
                pass  # Fail silently if conversation manager not available
        
        return accumulated_text
    
    def _display_enhanced_rich_markdown(self, text: str):
        """Display text with robust Rich markdown formatting"""
        try:
            console.print("\n[bold cyan]══════ Enhanced View ══════[/bold cyan]")
            
            # Preprocess the text for better markdown handling
            processed_text = self._preprocess_markdown_text(text)
            
            # Create Rich Markdown with optimal settings
            markdown_obj = Markdown(
                processed_text,
                code_theme="github-dark",
                inline_code_theme="github-dark",
                hyperlinks=True,
                justify="left"
            )
            
            console.print(markdown_obj)
            console.print("[bold cyan]═══════════════════════════[/bold cyan]")
            
        except Exception as e:
            # Robust fallback formatting
            console.print(f"[yellow]⚠️ Rich Markdown failed: {e}[/yellow]")
            self._display_manual_formatted_text(text)
    
    def _preprocess_streaming_markdown(self, text: str) -> str:
        """Optimized preprocessing for streaming markdown content"""
        # Clean up the text
        text = text.strip()
        
        # Fix incomplete code blocks during streaming
        if text.count('```') % 2 == 1:
            # If we have an odd number of ```, we're in the middle of a code block
            # Don't process this as markdown yet - treat as plain text
            return text
        
        # Apply the same preprocessing as the static version but optimized for streaming
        return self._preprocess_markdown_text(text)
    
    def _has_complete_markdown_blocks(self, text: str) -> bool:
        """Check if text has complete markdown blocks suitable for Rich Markdown rendering"""
        # Check for complete code blocks
        if '```' in text:
            if text.count('```') % 2 != 0:
                return False  # Incomplete code block
        
        # Check for complete headers (lines starting with #)
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith('#') and not line.strip().endswith('#'):
                return True
        
        # Check for complete formatting
        if any(marker in text for marker in ['**', '*', '`', '- ', '1. ']):
            return True
            
        return False
    
    def _create_enhanced_streaming_renderable(self, text: str):
        """Create enhanced Rich renderable with proper code block and markdown handling for streaming"""
        from rich.text import Text
        from rich.syntax import Syntax
        from rich.console import Group
        import re
        
        renderables = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Handle code blocks
            if line.startswith('```'):
                # Start of code block
                language = line[3:].strip() or "text"
                code_lines = []
                i += 1
                
                # Collect code lines until we find closing ``` or end of text
                while i < len(lines):
                    if lines[i].rstrip().startswith('```'):
                        # End of code block found
                        i += 1
                        break
                    code_lines.append(lines[i])
                    i += 1
                
                # Create syntax-highlighted code block
                if code_lines:
                    code_content = '\n'.join(code_lines)
                    try:
                        # Map language names
                        lang_map = {
                            'python': 'python',
                            'javascript': 'javascript', 
                            'js': 'javascript',
                            'bash': 'bash',
                            'shell': 'bash',
                            'sh': 'bash'
                        }
                        mapped_lang = lang_map.get(language.lower(), language.lower())
                        
                        syntax = Syntax(
                            code_content, 
                            mapped_lang,
                            theme="github-dark",
                            line_numbers=False,
                            word_wrap=True,
                            background_color="default"
                        )
                        renderables.append(syntax)
                    except:
                        # Fallback to colored text
                        code_text = Text()
                        for code_line in code_lines:
                            if language.lower() in ['python', 'py']:
                                code_text.append(code_line + '\n', style="green")
                            elif language.lower() in ['javascript', 'js']:
                                code_text.append(code_line + '\n', style="yellow")
                            elif language.lower() in ['bash', 'shell', 'sh']:
                                code_text.append(code_line + '\n', style="cyan")
                            else:
                                code_text.append(code_line + '\n', style="white")
                        renderables.append(code_text)
                continue
            
            # Handle regular text with inline formatting
            formatted_text = self._format_streaming_line(line)
            if formatted_text.plain:  # Only add non-empty lines
                renderables.append(formatted_text)
            else:
                # Add empty line
                renderables.append(Text(""))
            
            i += 1
        
        return Group(*renderables) if renderables else Text(text)
    
    def _format_streaming_line(self, line: str) -> Text:
        """Format a single line with inline markdown during streaming"""
        from rich.text import Text
        import re
        
        formatted_text = Text()
        
        # Handle headers first
        if line.strip().startswith('### '):
            formatted_text.append(line[4:], style="bold blue")
            return formatted_text
        elif line.strip().startswith('## '):
            formatted_text.append(line[3:], style="bold yellow")  
            return formatted_text
        elif line.strip().startswith('# '):
            formatted_text.append(line[2:], style="bold green")
            return formatted_text
        
        # Handle bullet points
        if re.match(r'^(\s*)[-*+]\s+', line):
            indent = re.match(r'^(\s*)', line).group(1)
            content = re.sub(r'^(\s*)[-*+]\s+', '', line)
            formatted_text.append(indent + "• ", style="bright_blue")
            # Process the rest of the line for inline formatting
            self._apply_inline_formatting(formatted_text, content)
            return formatted_text
        
        # Handle numbered lists
        if re.match(r'^(\s*)\d+\.\s+', line):
            match = re.match(r'^(\s*)(\d+\.\s+)(.*)', line)
            if match:
                indent, number, content = match.groups()
                formatted_text.append(indent, style="white")
                formatted_text.append(number, style="bright_blue bold")
                self._apply_inline_formatting(formatted_text, content)
                return formatted_text
        
        # Regular text with inline formatting
        self._apply_inline_formatting(formatted_text, line)
        return formatted_text
    
    def _apply_inline_formatting(self, text_obj: Text, content: str):
        """Apply inline formatting (bold, italic, code) to text content"""
        import re
        
        if not content:
            return
        
        current_pos = 0
        
        # Find all formatting markers
        markers = []
        
        # Bold text
        for match in re.finditer(r'\*\*([^*\n]+?)\*\*', content):
            markers.append((match.start(), match.end(), 'bold', match.group(1)))
        
        # Italic text (avoid conflicts with bold)
        for match in re.finditer(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', content):
            # Check if this overlaps with bold markers
            overlaps = any(match.start() >= m[0] and match.end() <= m[1] for m in markers if m[2] == 'bold')
            if not overlaps:
                markers.append((match.start(), match.end(), 'italic', match.group(1)))
        
        # Inline code
        for match in re.finditer(r'`([^`]+)`', content):
            markers.append((match.start(), match.end(), 'code', match.group(1)))
        
        # Sort markers by position
        markers.sort(key=lambda x: x[0])
        
        # Apply formatting
        for start, end, style, formatted_content in markers:
            # Add text before marker
            if current_pos < start:
                text_obj.append(content[current_pos:start])
            
            # Add formatted content
            if style == 'bold':
                text_obj.append(formatted_content, style="bold")
            elif style == 'italic':
                text_obj.append(formatted_content, style="italic")
            elif style == 'code':
                text_obj.append(formatted_content, style="cyan on grey23")
            
            current_pos = end
        
        # Add remaining text
        if current_pos < len(content):
            text_obj.append(content[current_pos:])
    
    def _append_streaming_formatted_line(self, rich_text, line):
        """Append a line with streaming-safe inline formatting"""
        from rich.text import Text
        import re
        
        # Split line into parts and apply formatting
        current_pos = 0
        
        # Find all formatting markers in order
        markers = []
        
        # Find bold markers
        for match in re.finditer(r'\*\*([^*\n]+?)\*\*', line):
            markers.append((match.start(), match.end(), 'bold', match.group(1)))
        
        # Find italic markers (avoid conflicts with bold)
        for match in re.finditer(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', line):
            markers.append((match.start(), match.end(), 'italic', match.group(1)))
        
        # Find inline code markers
        for match in re.finditer(r'`([^`]+)`', line):
            markers.append((match.start(), match.end(), 'code', match.group(1)))
        
        # Sort markers by position
        markers.sort(key=lambda x: x[0])
        
        # Apply formatting
        for start, end, style, content in markers:
            # Add text before marker
            if current_pos < start:
                rich_text.append(line[current_pos:start])
            
            # Add formatted content
            if style == 'bold':
                rich_text.append(content, style="bold")
            elif style == 'italic':
                rich_text.append(content, style="italic")
            elif style == 'code':
                rich_text.append(content, style="cyan on grey23")
            
            current_pos = end
        
        # Add remaining text
        if current_pos < len(line):
            rich_text.append(line[current_pos:])
    
    def _preprocess_markdown_text(self, text: str) -> str:
        """Preprocess text for optimal Rich markdown parsing"""
        import re
        
        # Clean up the text
        text = text.strip()
        
        # Fix code blocks - add proper language detection
        # Python code blocks
        text = re.sub(
            r'```\s*\n?(import\s|from\s|def\s|class\s|if\s|for\s|while\s|pip\sinstall)',
            r'```python\n\1', text
        )
        
        # JavaScript/Node.js code blocks
        text = re.sub(
            r'```\s*\n?(const\s|let\s|var\s|function\s|require\(|import.*from|npm\sinstall)',
            r'```javascript\n\1', text
        )
        
        # Shell/Bash code blocks
        text = re.sub(
            r'```\s*\n?(pip\sinstall|npm\sinstall|yarn\s|git\s|cd\s|mkdir\s|ls\s)',
            r'```bash\n\1', text
        )
        
        # Fix code block spacing
        text = re.sub(r'([^\n])\n```', r'\1\n\n```', text)  # Space before code blocks
        text = re.sub(r'```([^\n])', r'```\n\1', text)      # Space after opening ```
        
        # FIXED: Proper bold and italic formatting without regex issues
        # Bold formatting - ensure proper word boundaries
        text = re.sub(r'\*\*([^*\n]+?)\*\*', r'**\1**', text)
        
        # Italic formatting - avoid conflicts with bold, use word boundaries  
        text = re.sub(r'(?<!\*)\*([^*\n\*]+?)\*(?!\*)', r'*\1*', text)
        
        # Fix list formatting
        text = re.sub(r'^(\s*)[-*+]\s+', r'\1- ', text, flags=re.MULTILINE)
        
        # Ensure proper paragraph spacing
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _display_manual_formatted_text(self, text: str):
        """Manual formatting fallback when Rich Markdown fails"""
        import re
        
        console.print("\n[bold cyan]══════ Manual Format View ══════[/bold cyan]")
        
        lines = text.split('\n')
        in_code_block = False
        code_language = ""
        
        for line in lines:
            line = line.rstrip()
            
            # Handle code blocks
            if line.startswith('```'):
                if not in_code_block:
                    # Start of code block
                    code_language = line[3:].strip() or "text"
                    in_code_block = True
                    console.print(f"[dim white on blue] {code_language.upper()} CODE [/dim white on blue]")
                else:
                    # End of code block
                    in_code_block = False
                    console.print(f"[dim blue]{'─' * 40}[/dim blue]")
                continue
            
            if in_code_block:
                # Display code with appropriate syntax coloring
                if code_language.lower() in ['python', 'py']:
                    console.print(f"[green]{line}[/green]")
                elif code_language.lower() in ['javascript', 'js', 'node']:
                    console.print(f"[yellow]{line}[/yellow]")
                elif code_language.lower() in ['bash', 'shell', 'sh']:
                    console.print(f"[cyan]{line}[/cyan]")
                else:
                    console.print(f"[white]{line}[/white]")
            else:
                # Handle regular text formatting
                formatted_line = line
                
                # Handle headers
                if formatted_line.startswith('### '):
                    console.print(f"[bold blue]{formatted_line[4:]}[/bold blue]")
                elif formatted_line.startswith('## '):
                    console.print(f"[bold yellow]{formatted_line[3:]}[/bold yellow]")
                elif formatted_line.startswith('# '):
                    console.print(f"[bold green]{formatted_line[2:]}[/bold green]")
                else:
                    # Handle inline formatting with simpler regex patterns
                    formatted_line = line
                    
                    # Handle bold text with simpler pattern
                    formatted_line = re.sub(r'\*\*([^*\n]+?)\*\*', r'[bold]\1[/bold]', formatted_line)
                    
                    # Handle italic text - avoid conflicts with bold
                    formatted_line = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'[italic]\1[/italic]', formatted_line)
                    
                    # Handle inline code
                    formatted_line = re.sub(r'`([^`]+)`', r'[cyan]\1[/cyan]', formatted_line)
                    
                    # Handle bullet points
                    if re.match(r'^(\s*)[-*+]\s+', formatted_line):
                        formatted_line = re.sub(r'^(\s*)[-*+]\s+', r'\1• ', formatted_line)
                        console.print(f"[white]{formatted_line}[/white]")
                    else:
                        console.print(formatted_line)
        
        console.print("[bold cyan]═══════════════════════════[/bold cyan]")
    
    def _is_streaming_response(self):
        """Check if current provider uses streaming"""
        if self.provider_type == 'groq':
            return True  # Groq always uses streaming in our implementation
        elif self.provider_type == 'g4f':
            return self.selected_provider.get('supports_stream', False)
        return False
    
    def generate_response(self, user_input: str) -> str:
        """Generate response using selected provider with streaming support"""
        try:
            if self.provider_type == 'groq':
                return self._generate_groq_response(user_input)
            elif self.provider_type == 'g4f':
                return self._generate_g4f_response(user_input)
            else:
                return "❌ No provider configured"
        except Exception as e:
            error_msg = f"❌ Error generating response: {str(e)}"
            if RICH_AVAILABLE:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            return error_msg
    
    def _generate_groq_response(self, user_input: str) -> str:
        """Generate response using Groq with streaming"""
        try:
            if not self.async_groq_client:
                return "❌ Groq client not available"
            
            # Create the chat completion with streaming
            stream = self.async_groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant with internet access. You can search for current information when needed."},
                    {"role": "user", "content": user_input}
                ],
                model=self.selected_model,
                temperature=0.1,
                stream=True
            )
            
            # Process streaming response
            def text_chunks():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    async def get_chunks():
                        async for chunk in stream:
                            if chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content
                    
                    async def collect_chunks():
                        chunks = []
                        async for chunk in get_chunks():
                            chunks.append(chunk)
                        return chunks
                    
                    return loop.run_until_complete(collect_chunks())
                finally:
                    loop.close()
            
            # Get all chunks and stream them with Rich formatting
            chunks = text_chunks()
            return self._stream_with_rich_formatting(chunks, f"Groq ({self.selected_model})")
            
        except Exception as e:
            error_msg = f"❌ Groq error: {str(e)}"
            if RICH_AVAILABLE:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            return error_msg
    
    def _generate_g4f_response(self, user_input: str) -> str:
        """Generate response using G4F with streaming"""
        try:
            if not self.llm_client:
                return "❌ G4F client not available"
            
            # Get the provider class
            provider_class = getattr(Provider, self.selected_provider['name'])
            
            # Check if provider supports streaming
            if self.selected_provider.get('supports_stream', False):
                # Streaming response
                try:
                    stream = self.llm_client.chat.completions.create(
                        model=self.selected_model,
                        messages=[
                            {"role": "system", "content": "You are a helpful AI assistant with internet access. You can search for current information when needed."},
                            {"role": "user", "content": user_input}
                        ],
                        provider=provider_class,
                        stream=True
                    )
                    
                    # Process streaming chunks
                    def text_chunks():
                        for chunk in stream:
                            if hasattr(chunk, 'choices') and chunk.choices:
                                if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta:
                                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                                        yield chunk.choices[0].delta.content
                    
                    return self._stream_with_rich_formatting(text_chunks(), f"G4F ({self.selected_provider['name']})")
                    
                except Exception as stream_error:
                    if RICH_AVAILABLE:
                        console.print(f"[yellow]⚠️ Streaming failed, trying non-streaming: {stream_error}[/yellow]")
                    else:
                        print(f"⚠️ Streaming failed, trying non-streaming: {stream_error}")
            
            # Non-streaming response (fallback or default)
            response = self.llm_client.chat.completions.create(
                model=self.selected_model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant with internet access. You can search for current information when needed."},
                    {"role": "user", "content": user_input}
                ],
                provider=provider_class
            )
            
            # Extract response content
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
                
                # Display with Rich formatting
                if RICH_AVAILABLE:
                    self._display_enhanced_rich_markdown(content)
                else:
                    print(f"\n🤖 G4F ({self.selected_provider['name']}):")
                    print(content)
                
                # Save to conversation history
                self.conversation_manager.add_message(self.session_id, MessageRole.USER, user_input)
                self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, content)
                
                return content
            else:
                return "❌ No response content received"
                
        except Exception as e:
            error_msg = f"❌ G4F error: {str(e)}"
            if RICH_AVAILABLE:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            return error_msg
    
    def show_conversation_history(self, limit: int = 10):
        """Show recent conversation history"""
        try:
            messages = self.conversation_manager.get_conversation_history(self.session_id, limit)
            
            if not messages:
                if RICH_AVAILABLE:
                    console.print("[dim]No conversation history found[/dim]")
                else:
                    print("No conversation history found")
                return
            
            if RICH_AVAILABLE:
                console.print(f"\n[bold blue]📚 Conversation History (Last {limit} messages)[/bold blue]")
                console.print("[dim]" + "─" * 60 + "[/dim]")
                
                for msg in messages:
                    role_icon = "👤" if msg['role'] == MessageRole.USER.value else "🤖"
                    timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M:%S")
                    
                    console.print(f"\n[dim]{timestamp}[/dim] [bold]{role_icon} {msg['role'].title()}:[/bold]")
                    
                    # Truncate long messages for history display
                    content = msg['content']
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    console.print(content)
                    console.print("[dim]" + "─" * 40 + "[/dim]")
            else:
                print(f"\n📚 Conversation History (Last {limit} messages)")
                print("─" * 60)
                
                for msg in messages:
                    role_icon = "👤" if msg['role'] == MessageRole.USER.value else "🤖"
                    timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M:%S")
                    print(f"\n{timestamp} {role_icon} {msg['role'].title()}:")
                    
                    content = msg['content']
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    print(content)
                    print("─" * 40)
                    
        except Exception as e:
            error_msg = f"❌ Error loading conversation history: {str(e)}"
            if RICH_AVAILABLE:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
    
    def run(self):
        """Main CLI execution loop"""
        # Skip run in help mode
        if hasattr(self, 'help_mode') and self.help_mode:
            return
            
        try:
            # Show banner
            self.show_main_banner()
            
            # Provider selection
            self.show_provider_choice()
            
            # Get provider choice
            try:
                choice = input("🚀 Select provider (1-2): ").strip() or "1"
                
                if choice == "1":
                    if not self.setup_groq_provider():
                        return
                elif choice == "2":
                    if not self.setup_g4f_provider():
                        return
                else:
                    if RICH_AVAILABLE:
                        console.print("[red]❌ Invalid choice[/red]")
                    else:
                        print("❌ Invalid choice")
                    return
                    
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    console.print("\n[yellow]👋 Thanks for using AI Helper Agent! Goodbye![/yellow]")
                else:
                    print("\n👋 Thanks for using AI Helper Agent! Goodbye!")
                return
            
            # Main conversation loop
            if RICH_AVAILABLE:
                console.print(f"\n[bold green]✅ {self.provider_type.upper()} configured successfully![/bold green]")
                console.print("[dim]Type 'quit', 'exit', or press Ctrl+C to exit[/dim]")
                console.print("[dim]Type 'history' to view conversation history[/dim]")
                console.print("[dim]Type 'clear' to clear conversation history[/dim]")
            else:
                print(f"\n✅ {self.provider_type.upper()} configured successfully!")
                print("Type 'quit', 'exit', or press Ctrl+C to exit")
                print("Type 'history' to view conversation history")
                print("Type 'clear' to clear conversation history")
            
            while True:
                try:
                    # Get user input
                    if RICH_AVAILABLE:
                        user_input = console.input("\n[bold blue]🤔 You:[/bold blue] ").strip()
                    else:
                        user_input = input("\n🤔 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        if RICH_AVAILABLE:
                            console.print("[yellow]👋 Thanks for using AI Helper Agent! Goodbye![/yellow]")
                        else:
                            print("👋 Thanks for using AI Helper Agent! Goodbye!")
                        break
                    
                    elif user_input.lower() == 'history':
                        self.show_conversation_history()
                        continue
                    
                    elif user_input.lower() == 'clear':
                        try:
                            self.conversation_manager.clear_conversation(self.session_id)
                            if RICH_AVAILABLE:
                                console.print("[green]✅ Conversation history cleared[/green]")
                            else:
                                print("✅ Conversation history cleared")
                        except Exception as e:
                            if RICH_AVAILABLE:
                                console.print(f"[red]❌ Error clearing history: {str(e)}[/red]")
                            else:
                                print(f"❌ Error clearing history: {str(e)}")
                        continue
                    
                    # Generate response
                    self.generate_response(user_input)
                    
                except KeyboardInterrupt:
                    if RICH_AVAILABLE:
                        console.print("\n[yellow]👋 Thanks for using AI Helper Agent! Goodbye![/yellow]")
                    else:
                        print("\n👋 Thanks for using AI Helper Agent! Goodbye!")
                    break
                except EOFError:
                    if RICH_AVAILABLE:
                        console.print("\n[yellow]👋 Thanks for using AI Helper Agent! Goodbye![/yellow]")
                    else:
                        print("\n👋 Thanks for using AI Helper Agent! Goodbye!")
                    break
                except Exception as e:
                    error_msg = f"❌ Unexpected error: {str(e)}"
                    if RICH_AVAILABLE:
                        console.print(f"[red]{error_msg}[/red]")
                    else:
                        print(error_msg)
                    continue
                    
        except Exception as e:
            error_msg = f"❌ Fatal error: {str(e)}"
            if RICH_AVAILABLE:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Enhanced Internet CLI with G4F & Groq Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper-enhanced-internet              # Start with provider selection
  ai-helper-enhanced-internet --provider groq    # Start with Groq
  ai-helper-enhanced-internet --provider g4f     # Start with G4F
        """
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["groq", "g4f"],
        help="AI provider to use (groq for fast responses, g4f for free access)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent Enhanced Internet CLI v2.0"
    )
    
    args = parser.parse_args()
    
    try:
        cli = EnhancedInternetCLI()
        
        # Set provider if specified
        if args.provider:
            cli.provider_type = args.provider
        
        # Skip startup if we're in help mode
        if not (hasattr(cli, 'help_mode') and cli.help_mode):
            cli.run()
            
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n[yellow]👋 Thanks for using AI Helper Agent! Goodbye![/yellow]")
        else:
            print("\n👋 Thanks for using AI Helper Agent! Goodbye!")
    except Exception as e:
        error_msg = f"❌ Fatal startup error: {str(e)}"
        if RICH_AVAILABLE and console:
            console.print(f"[red]{error_msg}[/red]")
        else:
            print(error_msg)


if __name__ == "__main__":
    main()