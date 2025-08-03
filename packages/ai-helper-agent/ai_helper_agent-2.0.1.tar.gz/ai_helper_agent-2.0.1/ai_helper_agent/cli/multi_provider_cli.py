"""
AI Helper Agent - Multi-Provider LLM Integration
Enhanced CLI with support for Groq, OpenAI, Anthropic, and Google
"""

import os
import sys
import asyncio
import getpass
import re
import time
import warnings
import argparse
from typing import Dict, Any, Optional, Union, TYPE_CHECKING
from pathlib import Path
from datetime import datetime

# Type imports only used for type checking
if TYPE_CHECKING:
    from langchain_core.chat_history import BaseChatMessageHistory

# Rich imports - make lazy to improve startup time
def _lazy_import_rich_full():
    """Lazy import all Rich components to avoid startup delays"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.prompt import Prompt, Confirm
        from rich.text import Text
        from rich import print as rich_print
        from rich.live import Live
        from rich.spinner import Spinner
        from rich.progress import Progress, SpinnerColumn, TextColumn
        from rich.markdown import Markdown
        return {
            'Console': Console,
            'Panel': Panel,
            'Table': Table,
            'Prompt': Prompt,
            'Confirm': Confirm,
            'Text': Text,
            'rich_print': rich_print,
            'Live': Live,
            'Spinner': Spinner,
            'Progress': Progress,
            'SpinnerColumn': SpinnerColumn,
            'TextColumn': TextColumn,
            'Markdown': Markdown,
            'available': True
        }
    except ImportError:
        return {'available': False}

# Filter out warnings to keep CLI clean
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
warnings.filterwarnings("ignore", message=".*avconv.*")
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*")
warnings.filterwarnings("ignore", module="pydub")

# LAZY LOADING: Heavy provider imports moved to functions for faster startup
def _lazy_import_providers():
    """Lazy import LLM provider dependencies only when needed"""
    providers = {}
    
    # Groq import
    try:
        from langchain_groq import ChatGroq
        providers['groq'] = ChatGroq
    except ImportError:
        providers['groq'] = None
    
    # OpenAI import
    try:
        from langchain_openai import ChatOpenAI
        providers['openai'] = ChatOpenAI
    except ImportError:
        providers['openai'] = None
    
    # Anthropic import
    try:
        from langchain_anthropic import ChatAnthropic
        providers['anthropic'] = ChatAnthropic
    except ImportError:
        providers['anthropic'] = None
    
    # Google import
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        providers['google'] = ChatGoogleGenerativeAI
    except ImportError:
        providers['google'] = None
    
    return providers


# LAZY LOADING: Move heavy LangChain imports to functions for faster startup
def _lazy_import_langchain():
    """Lazy import LangChain dependencies only when needed"""
    try:
        from langchain_community.chat_message_histories import ChatMessageHistory
        from langchain_core.chat_history import BaseChatMessageHistory
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_core.runnables import RunnableLambda, RunnablePassthrough
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        
        return {
            'ChatMessageHistory': ChatMessageHistory,
            'BaseChatMessageHistory': BaseChatMessageHistory,
            'RunnableWithMessageHistory': RunnableWithMessageHistory,
            'RunnableLambda': RunnableLambda,
            'RunnablePassthrough': RunnablePassthrough,
            'SystemMessage': SystemMessage,
            'HumanMessage': HumanMessage,
            'AIMessage': AIMessage,
            'trim_messages': trim_messages,
            'ChatPromptTemplate': ChatPromptTemplate,
            'MessagesPlaceholder': MessagesPlaceholder,
            'StrOutputParser': StrOutputParser
        }
    except ImportError as e:
        print(f"Warning: Failed to import LangChain components: {e}")
        # Return fallback classes for when LangChain is not available
        class SystemMessage:
            def __init__(self, content):
                self.content = content
        
        class HumanMessage:
            def __init__(self, content):
                self.content = content
        
        class AIMessage:
            def __init__(self, content):
                self.content = content
        
        class ChatMessageHistory:
            def __init__(self):
                self.messages = []
        
        class BaseChatMessageHistory:
            def __init__(self):
                self.messages = []
        
        return {
            'ChatMessageHistory': ChatMessageHistory,
            'BaseChatMessageHistory': BaseChatMessageHistory,
            'SystemMessage': SystemMessage,
            'HumanMessage': HumanMessage,
            'AIMessage': AIMessage,
            'RunnableWithMessageHistory': None,
            'RunnableLambda': None,
            'RunnablePassthrough': None,
            'trim_messages': None,
            'ChatPromptTemplate': None,
            'MessagesPlaceholder': None,
            'StrOutputParser': None
        }

# Global variables for lazy loading
_langchain_components = None
_provider_components = None
_rich_components = None
_utility_components = None

def get_langchain_components():
    """Get LangChain components with lazy loading"""
    global _langchain_components
    if _langchain_components is None:
        _langchain_components = _lazy_import_langchain()
    return _langchain_components

def get_provider_components():
    """Get provider components with lazy loading"""
    global _provider_components
    if _provider_components is None:
        _provider_components = _lazy_import_providers()
    return _provider_components

def get_rich_components():
    """Get Rich components with lazy loading"""
    global _rich_components
    if _rich_components is None:
        _rich_components = _lazy_import_rich_full()
    return _rich_components

def get_utility_components():
    """Get utility components with lazy loading"""
    global _utility_components
    if _utility_components is None:
        _utility_components = _lazy_import_utilities()
    return _utility_components

# Module-level initialization - REMOVE automatic initialization for faster startup
def _init_lazy_classes():
    """Initialize lazy class references - only call when needed"""
    lc_components = get_langchain_components()
    provider_components = get_provider_components()
    
    global BaseChatMessageHistory, ChatMessageHistory, HumanMessage, ChatGroq
    
    BaseChatMessageHistory = lc_components.get('BaseChatMessageHistory')
    ChatMessageHistory = lc_components.get('ChatMessageHistory') 
    HumanMessage = lc_components.get('HumanMessage')
    ChatGroq = provider_components.get('groq')

# Initialize classes as None initially - only load when needed
BaseChatMessageHistory = None
ChatMessageHistory = None
HumanMessage = None
ChatGroq = None

def _ensure_classes_loaded():
    """Ensure classes are loaded before use"""
    global BaseChatMessageHistory, ChatMessageHistory, HumanMessage, ChatGroq
    if BaseChatMessageHistory is None:
        _init_lazy_classes()

# Provider imports moved to lazy functions - NO MODULE LEVEL IMPORTS
ChatOpenAI = None
ChatAnthropic = None

def _lazy_import_managers():
    """Lazy import manager dependencies only when needed"""
    try:
        from ..managers.api_key_manager import api_key_manager
        from ..managers.conversation_manager import conversation_manager, MessageRole
        return {
            'api_key_manager': api_key_manager,
            'conversation_manager': conversation_manager,
            'MessageRole': MessageRole
        }
    except ImportError as e:
        print(f"Warning: Failed to import managers: {e}")
        return {}

def _lazy_import_core():
    """Lazy import core dependencies only when needed"""
    try:
        from ..core.core import InteractiveAgent
        from ..core.config import config
        from ..core.security import security_manager
        from ..managers.user_manager import user_manager
        return {
            'InteractiveAgent': InteractiveAgent,
            'config': config,
            'security_manager': security_manager,
            'user_manager': user_manager
        }
    except ImportError as e:
        print(f"Warning: Failed to import core: {e}")
        return {}

def _lazy_import_rich():
    """Lazy import Rich formatting only when needed"""
    try:
        from ..utils.rich_formatting import rich_formatter
        return rich_formatter
    except ImportError:
        # Create minimal dummy rich formatter
        class DummyRichFormatter:
            def is_available(self): return False
            def print_status(self, msg, status): print(msg)
        return DummyRichFormatter()

def _lazy_import_utilities():
    """Lazy import utility dependencies only when needed"""
    utilities = {}
    
    try:
        from ..utils.prompt_enhancer import AdvancedPromptEnhancer
        utilities['AdvancedPromptEnhancer'] = AdvancedPromptEnhancer
    except ImportError:
        utilities['AdvancedPromptEnhancer'] = None

    try:
        from ..core.system_config import SystemConfigurationManager
        utilities['SystemConfigurationManager'] = SystemConfigurationManager
    except ImportError:
        utilities['SystemConfigurationManager'] = None

    try:
        from ..utils.streaming import StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
        utilities['StreamingResponseHandler'] = StreamingResponseHandler
        utilities['AdvancedStreamingHandler'] = AdvancedStreamingHandler
        utilities['CustomStreamingCallback'] = CustomStreamingCallback
        utilities['EnhancedStreamingHandler'] = EnhancedStreamingHandler
    except ImportError:
        utilities['StreamingResponseHandler'] = None
        utilities['AdvancedStreamingHandler'] = None
        utilities['CustomStreamingCallback'] = None
        utilities['EnhancedStreamingHandler'] = None

    try:
        from ..utilities.simple_logo import get_simple_logo, display_cli_header
        utilities['get_simple_logo'] = get_simple_logo
        utilities['display_cli_header'] = display_cli_header
    except ImportError:
        utilities['get_simple_logo'] = None
        utilities['display_cli_header'] = None

    try:
        from .multi_provider_startup import MultiProviderStartup
        utilities['MultiProviderStartup'] = MultiProviderStartup
    except ImportError:
        utilities['MultiProviderStartup'] = None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        utilities['ChatGoogleGenerativeAI'] = ChatGoogleGenerativeAI
    except ImportError:
        utilities['ChatGoogleGenerativeAI'] = None
    
    return utilities

# Remove heavy imports from module level - make them lazy

# ALL OPTIONAL IMPORTS MOVED TO LAZY FUNCTIONS - NO MODULE LEVEL IMPORTS
AdvancedPromptEnhancer = None
SystemConfigurationManager = None
StreamingResponseHandler = None
AdvancedStreamingHandler = None
CustomStreamingCallback = None
EnhancedStreamingHandler = None
get_simple_logo = None
display_cli_header = None
MultiProviderStartup = None
ChatGoogleGenerativeAI = None

# Remove module-level rich_formatter import - make it fully lazy

# Fallback with dummy classes for graceful degradation
class DummyAPIKeyManager:
        def get_api_key(self, *args, **kwargs): return None
        def save_api_key(self, *args, **kwargs): pass
        def is_api_key_valid(self, *args, **kwargs): return False

class DummyConversationManager:
    def get_conversation_history(self, *args, **kwargs): return []
    def save_message(self, *args, **kwargs): pass
    def clear_conversation(self, *args, **kwargs): pass

class MessageRole:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class DummyRichFormatter:
    def print_info(self, msg): print(f"INFO: {msg}")
    def print_success(self, msg): print(f"SUCCESS: {msg}")
    def print_error(self, msg): print(f"ERROR: {msg}")
    def print_warning(self, msg): print(f"WARNING: {msg}")
    def print_debug(self, msg): print(f"DEBUG: {msg}")
    def print_status(self, msg, status_type="info"): 
        print(f"{status_type.upper()}: {msg}")
    def print_divider(self): print("-" * 50)
    def print_header(self, title): print(f"\n=== {title} ===\n")
    def print_goodbye(self): print("👋 Goodbye! Thanks for using AI Helper Agent!")
    def setup_logging(self): pass
    def is_available(self): return False
    def show_table(self, title, headers, rows, styles=None): 
        print(f"\n{title}")
        print("-" * len(title))
        for row in rows:
            print(" | ".join(str(cell) for cell in row))

api_key_manager = DummyAPIKeyManager()
conversation_manager = DummyConversationManager()
rich_formatter = DummyRichFormatter()

# Global conversation store
conversation_store: Dict[str, Any] = {}


class MultiProviderAIHelperCLI:
    """Enhanced CLI with multi-provider LLM support and responsive design"""
    
    def __init__(self, session_id: str = "default", model: str = None, skip_startup: bool = False):
        self.session_id = f"multi_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.api_key: Optional[str] = None
        self.llm = None  # Union of various LLM providers
        self.chain = None
        self.workspace_path = Path.cwd()
        self.model = model
        self.provider = None
        
        # Check if we're in help mode or skip_startup (avoid heavy initialization)
        self.help_mode = '--help' in sys.argv or '-h' in sys.argv or skip_startup
        self.skip_startup = skip_startup
        
        # Initialize managers using lazy loading (always lazy)
        self._conversation_manager = None
        self._api_key_manager = None
        self._MessageRole = None
        self._langchain_components = None
        self._rich_formatter = None
        
        # Only initialize components if NOT in help mode and NOT skipping startup
        if not self.help_mode and not skip_startup:
            # Enhanced prompt system
            self.prompt_enhancer = None
            self.system_config = None
            self.streaming_handler = None
            self.advanced_streaming = None
            self.enhanced_streaming = None
            self.startup_interface = None
            self.enable_streaming: bool = True
            self.model_config = {}
        else:
            # Minimal initialization for help mode or skip_startup
            self.prompt_enhancer = None
            self.system_config = None
            self.streaming_handler = None
            self.advanced_streaming = None
            self.enhanced_streaming = None
            self.startup_interface = None
            self.enable_streaming = False
            self.model_config = {}
    
    @property
    def rich_formatter(self):
        """Lazy load Rich formatter"""
        if self._rich_formatter is None:
            self._rich_formatter = _lazy_import_rich()
            if not self.skip_startup and self._rich_formatter.is_available():
                self._rich_formatter.print_status("✅ Using Rich for enhanced display", "success")
            elif not self.skip_startup:
                print("⚠️ Rich not available - using basic display")
        return self._rich_formatter
    
    @property
    def conversation_manager(self):
        """Lazy load conversation manager"""
        if self._conversation_manager is None:
            managers = _lazy_import_managers()
            self._conversation_manager = managers.get('conversation_manager', DummyConversationManager())
        return self._conversation_manager
    
    @property
    def api_key_manager(self):
        """Lazy load API key manager"""
        if self._api_key_manager is None:
            managers = _lazy_import_managers()
            self._api_key_manager = managers.get('api_key_manager', DummyAPIKeyManager())
        return self._api_key_manager
    
    @property
    def MessageRole(self):
        """Lazy load MessageRole"""
        if self._MessageRole is None:
            managers = _lazy_import_managers()
            self._MessageRole = managers.get('MessageRole', MessageRole)
        return self._MessageRole
        
    def get_session_history(self, session_id: str) -> Any:
        """Get or create chat history for session"""
        _ensure_classes_loaded()  # Ensure classes are loaded
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_session_selection(self):
        """Show session selection with Rich table formatting"""
        if rich_formatter.is_available():
            from rich.console import Console
            console = Console()
            console.print("\n[bold cyan]📋 Session Management[/bold cyan]")
            console.print("1. 🆕 Start New Session")
            console.print("2. 📖 Continue Previous Session")
            console.print("3. 📚 View All Sessions")
        else:
            print("\n📋 Session Management:")
            print("1. 🆕 Start New Session")
            print("2. 📖 Continue Previous Session") 
            print("3. 📚 View All Sessions")
        
        try:
            try:
                choice = input("\nSelect option (1): ").strip() or "1"
            except (EOFError, KeyboardInterrupt):
                # Default to option 1 (new session) if no input available
                choice = "1"
                print("No input available, starting new session...")
            
            if choice == "1":
                # Generate new session ID
                self.session_id = f"multi_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if rich_formatter.is_available():
                    from rich.console import Console
                    console = Console()
                    console.print(f"[green]✅ New session created: {self.session_id}[/green]")
                else:
                    print(f"✅ New session created: {self.session_id}")
                return True
                
            elif choice == "2":
                return self.continue_previous_session()
                
            elif choice == "3":
                self.show_all_sessions()
                return self.show_session_selection()  # Show menu again after viewing sessions
                
            else:
                if rich_formatter.is_available():
                    from rich.console import Console
                    console = Console()
                    console.print("[red]❌ Invalid choice[/red]")
                else:
                    print("❌ Invalid choice")
                return self.show_session_selection()
                
        except KeyboardInterrupt:
            return False
        except Exception as e:
            if rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print(f"[red]❌ Error in session selection: {e}[/red]")
            else:
                print(f"❌ Error in session selection: {e}")
            return False
    
    def continue_previous_session(self):
        """Continue from a previous session"""
        recent_sessions = self.conversation_manager.get_recent_sessions(limit=10)
        
        if not recent_sessions:
            if rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print("[yellow]⚠️ No previous sessions found[/yellow]")
            else:
                print("⚠️ No previous sessions found")
            return False
        
        # Show recent sessions table
        if rich_formatter.is_available():
            from rich.console import Console
            from rich.table import Table
            console = Console()
            
            table = Table(
                title="📚 Recent Sessions", 
                show_header=True, 
                header_style="bold cyan",
                row_styles=["none", "dim"],  # Alternate row styling
                border_style="bright_cyan",
                show_lines=True  # Add row separators for better readability
            )
            table.add_column("ID", justify="center", style="yellow", width=3)
            table.add_column("Session", justify="left", style="green", max_width=30)
            table.add_column("Messages", justify="center", style="blue", width=8)
            table.add_column("Last Activity", justify="left", style="white", max_width=20)
            
            for i, session in enumerate(recent_sessions[:10], 1):
                # Format session ID for better display
                session_display = session['session_id']
                if len(session_display) > 25:
                    session_display = session_display[:22] + "..."
                
                # Format last message time
                try:
                    last_msg = datetime.fromisoformat(session['last_message'])
                    time_ago = datetime.now() - last_msg
                    if time_ago.days > 0:
                        time_display = f"{time_ago.days}d ago"
                    elif time_ago.seconds > 3600:
                        time_display = f"{time_ago.seconds // 3600}h ago" 
                    else:
                        time_display = f"{time_ago.seconds // 60}m ago"
                except:
                    time_display = "Unknown"
                
                table.add_row(
                    str(i),
                    session_display,
                    str(session['message_count']),
                    time_display
                )
            
            console.print(table)
        else:
            print("\n📚 Recent Sessions:")
            for i, session in enumerate(recent_sessions[:10], 1):
                print(f"{i:2d}. {session['session_id']} ({session['message_count']} messages)")
        
        try:
            try:
                choice = input(f"\nSelect session (1-{min(len(recent_sessions), 10)}) or Enter to cancel: ").strip()
            except (EOFError, KeyboardInterrupt):
                return False
            
            if not choice:
                return False
                
            session_idx = int(choice) - 1
            if 0 <= session_idx < len(recent_sessions):
                selected_session = recent_sessions[session_idx]
                self.session_id = selected_session['session_id']
                
                if rich_formatter.is_available():
                    from rich.console import Console
                    console = Console()
                    console.print(f"[green]✅ Continuing session: {self.session_id}[/green]")
                    console.print(f"[dim]Session has {selected_session['message_count']} messages[/dim]")
                else:
                    print(f"✅ Continuing session: {self.session_id}")
                    print(f"Session has {selected_session['message_count']} messages")
                
                # Show last few messages as context
                self.show_session_context()
                return True
            else:
                if rich_formatter.is_available():
                    from rich.console import Console
                    console = Console()
                    console.print("[red]❌ Invalid session selection[/red]")
                else:
                    print("❌ Invalid session selection")
                return False
                
        except (ValueError, KeyboardInterrupt):
            return False
        except Exception as e:
            if rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print(f"[red]❌ Error selecting session: {e}[/red]")
            else:
                print(f"❌ Error selecting session: {e}")
            return False
    
    def show_all_sessions(self):
        """Show all available sessions"""
        all_sessions = self.conversation_manager.get_recent_sessions(limit=50)
        
        if not all_sessions:
            if rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print("[yellow]⚠️ No sessions found[/yellow]")
            else:
                print("⚠️ No sessions found")
            return
        
        if rich_formatter.is_available():
            from rich.console import Console
            from rich.table import Table
            console = Console()
            
            table = Table(
                title=f"📚 All Sessions ({len(all_sessions)} total)", 
                show_header=True, 
                header_style="bold magenta",
                row_styles=["none", "dim"],  # Alternate row styling
                border_style="bright_magenta",
                show_lines=True  # Add row separators for better readability
            )
            table.add_column("Session ID", justify="left", style="green", max_width=40)
            table.add_column("Messages", justify="center", style="blue", width=8)
            table.add_column("First Message", justify="left", style="yellow", max_width=15)
            table.add_column("Last Activity", justify="left", style="white", max_width=15)
            
            for session in all_sessions:
                # Format timestamps
                try:
                    first_msg = datetime.fromisoformat(session['first_message']).strftime("%m/%d %H:%M")
                    last_msg = datetime.fromisoformat(session['last_message']).strftime("%m/%d %H:%M")
                except:
                    first_msg = "Unknown"
                    last_msg = "Unknown"
                
                table.add_row(
                    session['session_id'],
                    str(session['message_count']),
                    first_msg,
                    last_msg
                )
            
            console.print(table)
        else:
            print(f"\n📚 All Sessions ({len(all_sessions)} total):")
            for session in all_sessions:
                print(f"• {session['session_id']} - {session['message_count']} messages")
    
    def show_session_context(self, limit: int = 3):
        """Show last few messages from current session as context"""
        if not self.session_id:
            return
            
        history = self.conversation_manager.get_conversation_history(self.session_id, max_messages=limit)
        
        if not history:
            return
        
        if rich_formatter.is_available():
            from rich.console import Console
            console = Console()
            console.print(f"\n[bold blue]💬 Recent conversation context:[/bold blue]")
            for msg in history[-limit:]:
                role_icon = "👤" if msg.role == self.MessageRole.USER else "🤖"
                # Handle role properly - it might be enum or string
                if hasattr(msg.role, 'value'):
                    role_name = msg.role.value.title()
                else:
                    role_name = str(msg.role).title()
                
                # Truncate long messages for context display
                content = msg.content
                if len(content) > 100:
                    content = content[:97] + "..."
                
                console.print(f"[dim]{role_icon} {role_name}:[/dim] {content}")
            console.print("[dim]─── End of Context ───[/dim]")
        else:
            print("\n💬 Recent conversation context:")
            for msg in history[-limit:]:
                role_icon = "👤" if msg.role == self.MessageRole.USER else "🤖"
                # Handle role properly - it might be enum or string
                if hasattr(msg.role, 'value'):
                    role_name = msg.role.value.title()
                else:
                    role_name = str(msg.role).title()
                
                # Truncate long messages for context display
                content = msg.content
                if len(content) > 100:
                    content = content[:97] + "..."
                
                print(f"{role_icon} {role_name}: {content}")
            print("─── End of Context ───")
    
    def show_splash_screen(self):
        """Show AI Helper Agent splash screen with simple logo"""
        if not self.skip_startup and self.startup_interface:
            self.startup_interface.display_responsive_logo()
        else:
            display_cli_header(
                "AI HELPER AGENT v2.0",
                "Multi-Provider AI Assistant - Lightning-Fast Responses"
            )
    
    def setup_user_session(self) -> bool:
        """Setup user session with simplified multi-provider support"""
        try:
            self.show_splash_screen()
            
            # Session selection
            if not self.skip_startup:
                if not self.show_session_selection():
                    print("👋 Session selection cancelled. Goodbye!")
                    return False
            
            # Load existing configuration or prompt for simple setup
            if not self.model:
                if not self.skip_startup:
                    # Use simplified provider selection instead of complex startup
                    success = self.simple_provider_setup()
                    if not success:
                        return False
                else:
                    # Default to Groq
                    self.model = "llama-3.1-8b-instant"
                    self.provider = "groq"
            
            # Setup configuration if not done
            if not self.llm:
                if not self.setup_model_and_api():
                    return False
            
            # Initialize other components
            self.prompt_enhancer = AdvancedPromptEnhancer()
            self.system_config = SystemConfigurationManager()
            
            if not self.setup_llm_and_chain():
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def simple_provider_setup(self) -> bool:
        """Simplified provider setup without complex chains"""
        try:
            # Show provider menu with Rich table if available
            if self.rich_formatter.is_available():
                from rich.console import Console
                from rich.table import Table
                
                console = Console()
                table = Table(title="🚀 AI Provider Selection")
                table.add_column("ID", justify="center", style="cyan")
                table.add_column("Provider", style="green")
                table.add_column("Description", style="white")
                table.add_column("Speed", style="yellow")
                
                table.add_row("1", "Groq", "Lightning fast inference", "⚡ Ultra Fast")
                table.add_row("2", "OpenAI", "GPT-4 models", "🚀 Fast")
                table.add_row("3", "Anthropic", "Claude models", "💭 Thoughtful")
                
                console.print(table)
            else:
                print("🚀 Choose your AI provider:")
                print("1. Groq (Recommended - Fast & Free)")
                print("2. OpenAI (GPT-4)")
                print("3. Anthropic (Claude)")
            
            try:
                choice = input("Select provider (1-3, default 1): ").strip() or "1"
            except (EOFError, KeyboardInterrupt):
                # Default to Groq if no input available (e.g., piped input)
                choice = "1"
                print("No input available, defaulting to Groq...")
            
            if choice == "1":
                self.provider = "groq"
                return self._setup_groq_provider()
                    
            elif choice == "2":
                self.provider = "openai"
                return self._setup_openai_provider()
                    
            elif choice == "3":
                self.provider = "anthropic"
                return self._setup_anthropic_provider()
                
            else:
                print("❌ Invalid choice, using Groq as default")
                self.provider = "groq"
                return self._setup_groq_provider()
                
        except Exception as e:
            print(f"❌ Error in provider setup: {e}")
            return False
    
    def _setup_groq_provider(self) -> bool:
        """Setup Groq provider with model selection"""
        # Get API key from manager first, then environment
        self.api_key = self.api_key_manager.get_api_key('groq')
        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("🔑 Enter your Groq API key (get from https://console.groq.com/keys):")
            try:
                self.api_key = getpass.getpass("API Key: ")
            except (EOFError, KeyboardInterrupt):
                print("❌ No API key provided")
                return False
        
        # Show Groq model selection with Rich table
        if self.rich_formatter.is_available():
            from rich.console import Console
            from rich.table import Table
            
            console = Console()
            table = Table(title="🤖 Groq Models")
            table.add_column("ID", justify="center", style="cyan")
            table.add_column("Model", style="green")
            table.add_column("Description", style="white")
            
            groq_models = [
                ("llama-3.1-8b-instant", "Ultra fast responses"),
                ("llama-3.3-70b-versatile", "Latest Meta model"),
                ("gemma2-9b-it", "Google's balanced model"),
                ("llama-3.1-70b-versatile", "Large reasoning model")
            ]
            
            for i, (model_id, desc) in enumerate(groq_models, 1):
                table.add_row(str(i), model_id, desc)
            
            console.print(table)
        else:
            print("🤖 Groq Models:")
            print("1. llama-3.1-8b-instant (Ultra fast)")
            print("2. llama-3.3-70b-versatile (Latest)")
            print("3. gemma2-9b-it (Balanced)")
            print("4. llama-3.1-70b-versatile (Large)")
        
        try:
            choice = input("Select model (1): ").strip() or "1"
            choice_idx = int(choice) - 1
            models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it", "llama-3.1-70b-versatile"]
            
            if 0 <= choice_idx < len(models):
                self.model = models[choice_idx]
            else:
                self.model = "llama-3.1-8b-instant"
                
        except (ValueError, EOFError, KeyboardInterrupt):
            self.model = "llama-3.1-8b-instant"
        
        print(f"✅ Using Groq with {self.model}")
        return True
    
    def _setup_openai_provider(self) -> bool:
        """Setup OpenAI provider"""
        self.model = "gpt-4o-mini"
        # Get API key from manager first, then environment
        self.api_key = self.api_key_manager.get_api_key('openai')
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("🔑 Enter your OpenAI API key:")
            try:
                self.api_key = getpass.getpass("API Key: ")
            except (EOFError, KeyboardInterrupt):
                print("❌ No API key provided")
                return False
        print(f"✅ Using OpenAI with {self.model}")
        return True
    
    def _setup_anthropic_provider(self) -> bool:
        """Setup Anthropic provider"""
        try:
            self.model = "claude-3-haiku-20240307"
            # Get API key from manager first, then environment
            self.api_key = self.api_key_manager.get_api_key('anthropic')
            if not self.api_key:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                print("🔑 Enter your Anthropic API key:")
                try:
                    self.api_key = getpass.getpass("API Key: ")
                except (EOFError, KeyboardInterrupt):
                    print("❌ No API key provided")
                    return False
                
            print(f"✅ Using Anthropic with {self.model}")
            return True
                
        except Exception as e:
            print(f"❌ Provider setup failed: {e}")
            return False
    
    def _detect_provider(self, llm) -> str:
        """Detect provider from LLM instance"""
        _ensure_classes_loaded()  # Ensure classes are loaded for isinstance checks
        if isinstance(llm, ChatGroq):
            return "groq"
        elif ChatOpenAI and isinstance(llm, ChatOpenAI):
            return "openai"
        elif ChatAnthropic and isinstance(llm, ChatAnthropic):
            return "anthropic"
        elif ChatGoogleGenerativeAI and isinstance(llm, ChatGoogleGenerativeAI):
            return "google"
        else:
            return "unknown"
    
    def setup_model_and_api(self) -> bool:
        """Setup model and API key for the selected provider"""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        if not self.provider:
            self.provider = "groq"  # Default
        
        if self.provider == "groq":
            # Get API key from manager first, then environment
            self.api_key = self.api_key_manager.get_api_key('groq')
            if not self.api_key:
                self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your Groq API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://console.groq.com/keys", "info")
                self.api_key = getpass.getpass("Groq API Key: ")
        elif self.provider == "openai":
            # Get API key from manager first, then environment
            self.api_key = self.api_key_manager.get_api_key('openai')
            if not self.api_key:
                self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your OpenAI API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://platform.openai.com/api-keys", "info")
                self.api_key = getpass.getpass("OpenAI API Key: ")
        elif self.provider == "anthropic":
            # Get API key from manager first, then environment
            self.api_key = self.api_key_manager.get_api_key('anthropic')
            if not self.api_key:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your Anthropic API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://console.anthropic.com/", "info")
                self.api_key = getpass.getpass("Anthropic API Key: ")
        elif self.provider == "google":
            # Get API key from manager first, then environment
            self.api_key = self.api_key_manager.get_api_key('google')
            if not self.api_key:
                self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your Google API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://makersuite.google.com/app/apikey", "info")
                self.api_key = getpass.getpass("Google API Key: ")
        
        return True
    
    def create_llm_instance(self) -> bool:
        """Create LLM instance based on provider"""
        try:
            _ensure_classes_loaded()  # Ensure classes are loaded
            if self.provider == "groq":
                self.llm = ChatGroq(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            elif self.provider == "openai" and ChatOpenAI:
                self.llm = ChatOpenAI(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            elif self.provider == "anthropic" and ChatAnthropic:
                self.llm = ChatAnthropic(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            elif self.provider == "google" and ChatGoogleGenerativeAI:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model,
                    google_api_key=self.api_key,
                    temperature=0.1
                )
            else:
                self.rich_formatter.print_status(f"❌ Provider {self.provider} not available or not installed", "error")
                return False
                
            return True
            
        except Exception as e:
            self.rich_formatter.print_status(f"❌ Failed to create {self.provider} LLM: {e}", "error")
            return False
    
    def test_api_key_and_model(self) -> bool:
        """Test API key and model with the current provider"""
        try:
            if not self.llm:
                if not self.create_llm_instance():
                    return False
            
            self.rich_formatter.print_status(f"🔄 Testing {self.provider.upper()} connection with model {self.model}...", "info")
            _ensure_classes_loaded()  # Ensure classes are loaded
            response = self.llm.invoke([HumanMessage(content="Hello")])
            
            if response and response.content:
                self.rich_formatter.print_status(f"✅ {self.provider.upper()} connection successful!", "success")
                # Store in environment for this session
                if self.api_key:
                    os.environ[f"{self.provider.upper()}_API_KEY"] = self.api_key
                return True
            else:
                self.rich_formatter.print_status(f"❌ Invalid configuration for {self.provider}. Please try again.", "error")
                return False
                
        except Exception as e:
            self.rich_formatter.print_status(f"❌ Error testing {self.provider} connection: {e}", "error")
            self.rich_formatter.print_status("Please check your settings and try again.", "warning")
            return False
    
    def setup_llm_and_chain(self):
        """Setup LLM with simplified approach (no complex chains)"""
        try:
            if not self.llm:
                if not self.create_simple_llm_instance():
                    return False
            
            # Simple test - no complex chain setup
            try:
                if self.provider == "groq":
                    # Test with a simple message
                    from groq import Groq
                    client = Groq(api_key=self.api_key)
                    response = client.chat.completions.create(
                        messages=[{"role": "user", "content": "Hello"}],
                        model=self.model,
                        max_tokens=10
                    )
                    if response.choices[0].message.content:
                        self.rich_formatter.print_status("✅ Connection test successful!", "success")
                        return True
                else:
                    # For other providers, just assume it works to avoid hanging
                    self.rich_formatter.print_status("✅ Provider configured!", "success")
                    return True
                    
            except Exception as e:
                self.rich_formatter.print_status(f"❌ Connection test failed: {e}", "error")
                return False
                
        except Exception as e:
            self.rich_formatter.print_status(f"❌ LLM setup failed: {e}", "error")
            return False
    
    def create_simple_llm_instance(self) -> bool:
        """Create simple LLM instance without complex setup"""
        try:
            _ensure_classes_loaded()  # Ensure classes are loaded
            if self.provider == "groq":
                self.llm = ChatGroq(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
                return True
            elif self.provider == "openai" and ChatOpenAI:
                self.llm = ChatOpenAI(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
                return True
            elif self.provider == "anthropic" and ChatAnthropic:
                self.llm = ChatAnthropic(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
                return True
            else:
                self.rich_formatter.print_status(f"❌ Provider {self.provider} not available", "error")
                return False
                
        except Exception as e:
            self.rich_formatter.print_status(f"❌ Failed to create LLM: {e}", "error")
            return False
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI assistant"""
        return f"""You are AI Helper Agent v2.0.1, a sophisticated coding assistant created by Meet Solanki, an AIML Student.

🌟 ABOUT THIS SYSTEM:
- Name: AI Helper Agent v2.0.1
- Creator: Meet Solanki (AIML Student)
- Purpose: Comprehensive AI-powered programming assistance
- Mission: Making developers more productive and helping them learn

👨‍💻 CREATOR'S VISION:
This system was crafted by Meet Solanki to provide genuine programming assistance that helps developers grow their skills while solving real coding challenges.

CAPABILITIES:
- Advanced code generation and debugging
- Real-time analysis and explanations  
- Multi-language programming support
- Architecture design and best practices
- Problem-solving and optimization
- Educational guidance and learning support

PERSONALITY:
- Professional but friendly
- Detailed explanations when helpful
- Concise responses when appropriate
- Always aim to be helpful and accurate
- Focus on helping users learn and improve

CURRENT SETUP:
- Provider: {self.provider.upper()}
- Model: {self.model}
- Streaming: {"Enabled" if self.enable_streaming else "Disabled"}

💡 HELPING YOU SUCCEED:
As created by Meet Solanki (AIML Student), my goal is to make you a better developer. I provide not just code, but understanding, context, and learning opportunities.

Please provide helpful, accurate, and well-structured responses to assist with coding and development tasks. Let's build something amazing together! 🚀"""
    
    def switch_provider(self, new_provider: str, new_model: str = None, new_api_key: str = None):
        """Switch to a different AI provider"""
        self.rich_formatter.print_status(f"🔄 Switching from {self.provider} to {new_provider}...", "info")
        
        self.provider = new_provider
        if new_model:
            self.model = new_model
        if new_api_key:
            self.api_key = new_api_key
        
        # Reinitialize LLM and chain
        if self.setup_llm_and_chain():
            self.rich_formatter.print_status(f"✅ Successfully switched to {new_provider.upper()}", "success")
        else:
            self.rich_formatter.print_status(f"❌ Failed to switch to {new_provider}", "error")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get current provider information"""
        return {
            "provider": self.provider,
            "model": self.model,
            "has_api_key": bool(self.api_key),
            "llm_type": type(self.llm).__name__ if self.llm else None,
            "streaming_enabled": self.enable_streaming
        }
    
    def _show_available_providers(self) -> str:
        """Show available AI providers for switching"""
        providers_info = [
            ["🤖 Groq", "Fast inference, Llama models", "groq, llama"],
            ["🧠 OpenAI", "GPT models, ChatGPT API", "openai, gpt"],
            ["🎭 Anthropic", "Claude models", "anthropic, claude"]
        ]
        
        headers = ["Provider", "Description", "Aliases"]
        self.rich_formatter.show_table("🔄 Available AI Providers", headers, providers_info, ["bold cyan", "white", "dim"])
        
        current_provider_info = f"""
📍 **Current Configuration:**
• Provider: {self.provider.upper()}
• Model: {self.model}
• API Key: {'✅ Set' if self.api_key else '❌ Not set'}

💡 **Usage:** `switch <provider>` (e.g., `switch groq`, `switch openai`)
"""
        self.rich_formatter.print_status(current_provider_info, "info")
        return "PROVIDERS_SHOWN"
    
    async def generate_response(self, user_input: str) -> str:
        """Generate response with Rich formatting and streaming"""
        try:
            if not self.conversation_chain:
                return "❌ No conversation chain available"
            
            # Save user message to conversation history
            self.conversation_manager.add_message(self.session_id, MessageRole.USER, user_input)
            
            if self.enable_streaming:
                return await self._get_streaming_response(user_input)
            else:
                # Non-streaming response
                _ensure_classes_loaded()  # Ensure classes are loaded
                response = self.conversation_chain.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"session_id": self.session_id}}
                )
                
                # Display with Rich formatting
                self.rich_formatter.display_enhanced_rich_markdown(response)
                
                # Save to conversation history
                self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, response)
                
                return response
                
        except Exception as e:
            error_msg = f"❌ Error generating response: {str(e)}"
            self.rich_formatter.print_status(error_msg, "error")
            return error_msg
    
    async def _get_streaming_response(self, user_input: str) -> str:
        """Get streaming response with Rich formatting"""
        try:
            # Create streaming text chunks generator
            def stream_text_chunks():
                _ensure_classes_loaded()  # Ensure classes are loaded
                for chunk in self.conversation_chain.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"session_id": self.session_id}}
                ):
                    if chunk and hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content
                    elif isinstance(chunk, str):
                        yield chunk
            
            # Stream with Rich formatting - try rich_formatter first, then fallback to built-in method
            try:
                response = self.rich_formatter.stream_with_rich_formatting(
                    stream_text_chunks(), 
                    f"{self.provider.upper()} ({self.model})"
                )
            except Exception:
                # Fallback to built-in Rich streaming method
                response = self._stream_with_rich_formatting(
                    stream_text_chunks(),
                    f"{self.provider.upper()} ({self.model})"
                )
            
            # Save to conversation history
            self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, response)
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Streaming error: {str(e)}"
            self.rich_formatter.print_status(error_msg, "error")
            return error_msg
    
    def _stream_with_rich_formatting(self, text_chunks, provider_name="AI"):
        """Stream text with REAL-TIME Rich markdown formatting using Live Display"""
        from rich.live import Live
        from rich.markdown import Markdown
        from rich.text import Text
        import time
        
        if not self.rich_formatter.is_available():
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
        console = self.rich_formatter.console
        console.print(f"\n[bold blue]🤖 {provider_name}:[/bold blue]")
        console.print("[bold cyan]══════ Live Streaming View ══════[/bold cyan]")
        
        accumulated_text = ""
        
        # Use Rich Live Display for real-time updates with improved scrolling
        with Live(
            console=console, 
            refresh_per_second=10,  # Higher refresh rate for smoother streaming
            transient=False,
            vertical_overflow="visible",  # Allow content to scroll naturally
            auto_refresh=True
        ) as live:
            for chunk in text_chunks:
                if chunk and isinstance(chunk, str):
                    accumulated_text += chunk
                    
                    # Real-time rendering with enhanced markdown processing
                    try:
                        # Use markdown for better formatting during streaming
                        renderable = Markdown(accumulated_text, code_theme="github-dark")
                        live.update(renderable)
                        
                        # Small delay for smooth streaming effect
                        time.sleep(0.05)
                        
                    except Exception as e:
                        # Fallback to plain text if formatting fails
                        live.update(Text(accumulated_text))
        
        # Show final enhanced view after streaming completes
        console.print("[bold cyan]═══════════════════════════[/bold cyan]")
        console.print("[dim]✅ Streaming complete[/dim]")
        
        return accumulated_text

    def show_conversation_history(self, limit: int = 10):
        """Show recent conversation history with Rich formatting"""
        try:
            messages = self.conversation_manager.get_conversation_history(self.session_id, max_messages=limit)
            
            if not messages:
                self.rich_formatter.print_status("No conversation history found", "info")
                return
            
            headers = ["Time", "Role", "Message"]
            rows = []
            
            for msg in messages:
                role_icon = "👤" if msg.role == MessageRole.USER.value else "🤖"
                # Handle timestamp properly - it might be datetime object or string
                if isinstance(msg.timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(msg.timestamp).strftime("%H:%M:%S")
                    except (ValueError, TypeError):
                        timestamp = "Unknown"
                elif isinstance(msg.timestamp, datetime):
                    timestamp = msg.timestamp.strftime("%H:%M:%S")
                else:
                    timestamp = "Unknown"
                
                # Handle role properly - it might be enum or string
                if hasattr(msg.role, 'value'):
                    role_display = msg.role.value.title()
                else:
                    role_display = str(msg.role).title()
                
                # Truncate long messages for history display
                content = msg.content
                if len(content) > 100:
                    content = content[:100] + "..."
                
                rows.append([timestamp, f"{role_icon} {role_display}", content])
            
            self.rich_formatter.show_table(f"📚 Conversation History (Last {limit} messages)", headers, rows, ["dim", "bold", "white"])
                    
        except Exception as e:
            self.rich_formatter.print_status(f"❌ Error loading conversation history: {str(e)}", "error")
    
    async def handle_command(self, user_input: str) -> str:
        """Handle user commands and return AI response"""
        try:
            # Check for special commands
            if user_input.lower() in ['exit', 'quit', 'goodbye']:
                self.rich_formatter.print_goodbye()
                return "EXIT"
            
            if user_input.lower() in ['help', '?']:
                return self._get_help_message()
            
            if user_input.lower() == 'clear':
                # Clear conversation history
                _ensure_classes_loaded()  # Ensure classes are loaded
                if self.session_id in conversation_store:
                    conversation_store[self.session_id] = ChatMessageHistory()
                self.conversation_manager.clear_conversation(self.session_id)
                return "🧹 Conversation history cleared!"
            
            if user_input.lower() == 'history':
                self.show_conversation_history()
                return "HISTORY_SHOWN"
            
            if user_input.lower() == 'sessions':
                self.show_all_sessions()
                return "SESSIONS_SHOWN"
            
            if user_input.lower() == 'switch':
                if self.show_session_selection():
                    self.show_session_context()
                    return f"✅ Switched to session: {self.session_id}"
                return "Session switch cancelled"
            
            # Handle provider switching commands
            if user_input.lower().startswith('switch '):
                parts = user_input.split()
                if len(parts) >= 2:
                    new_provider = parts[1].lower()
                    # Map common provider names
                    provider_mapping = {
                        'groq': 'groq',
                        'openai': 'openai', 
                        'anthropic': 'anthropic',
                        'claude': 'anthropic',
                        'gpt': 'openai',
                        'llama': 'groq'
                    }
                    
                    if new_provider in provider_mapping:
                        try:
                            self.switch_provider(provider_mapping[new_provider])
                            return f"✅ Switched to {provider_mapping[new_provider].upper()} provider"
                        except Exception as e:
                            return f"❌ Failed to switch provider: {str(e)}"
                    else:
                        available_providers = ", ".join(provider_mapping.keys())
                        return f"❌ Unknown provider '{new_provider}'. Available: {available_providers}"
                else:
                    return "❌ Usage: switch <provider> (e.g., 'switch groq', 'switch openai')"
            
            if user_input.lower() == 'providers':
                return self._show_available_providers()
            
            if user_input.lower() == 'info':
                return self._show_provider_info()
            
            # Regular AI response
            return await self.generate_response(user_input)
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"
    
    def _get_help_message(self) -> str:
        """Get help message with available commands"""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            
            console = Console()
            
            # Create main title panel
            title_panel = Panel.fit(
                "[bold blue]🤖 AI Helper Agent - Multi-Provider CLI[/bold blue]\n"
                "[dim]Switch between multiple AI providers seamlessly[/dim]",
                border_style="blue"
            )
            console.print(title_panel)
            
            # Basic Commands Table
            basic_table = Table(
                title="📝 BASIC COMMANDS",
                show_header=True,
                header_style="bold green",
                border_style="bright_blue",
                row_styles=["none", "dim"],
                show_lines=True
            )
            basic_table.add_column("Command", style="cyan", width=15)
            basic_table.add_column("Description", style="white")
            
            basic_table.add_row("help, ?", "Show this help message")
            basic_table.add_row("exit, quit", "Exit the application")
            basic_table.add_row("clear", "Clear conversation history")
            basic_table.add_row("history", "View recent conversation history")
            basic_table.add_row("info", "Show current provider information")
            
            console.print("\n")
            console.print(basic_table)
            
            # Session Management Table
            session_table = Table(
                title="🗂️ SESSION MANAGEMENT",
                show_header=True,
                header_style="bold yellow",
                border_style="bright_yellow",
                row_styles=["none", "dim"],
                show_lines=True
            )
            session_table.add_column("Command", style="cyan", width=15)
            session_table.add_column("Description", style="white")
            
            session_table.add_row("sessions", "View all available sessions")
            session_table.add_row("switch", "Switch to another session")
            session_table.add_row("", "Session persistence enabled with history")
            
            console.print(session_table)
            
            # Provider Commands Table
            provider_table = Table(
                title="🔧 PROVIDER COMMANDS",
                show_header=True,
                header_style="bold magenta",
                border_style="bright_magenta",
                row_styles=["none", "dim"],
                show_lines=True
            )
            provider_table.add_column("Command", style="cyan", width=20)
            provider_table.add_column("Description", style="white")
            
            provider_table.add_row("providers", "Show all available AI providers")
            provider_table.add_row("switch <provider>", "Switch to different AI provider")
            provider_table.add_row("info", "Show current provider information")
            provider_table.add_row("", "Available: groq, openai, anthropic, google")
            provider_table.add_row("", "Aliases: llama, gpt, claude, gemini")
            
            console.print(provider_table)
            
            # Coding Assistance Table
            coding_table = Table(
                title="💡 CODING ASSISTANCE",
                show_header=True,
                header_style="bold cyan",
                border_style="bright_cyan",
                row_styles=["none", "dim"],
                show_lines=True
            )
            coding_table.add_column("Command", style="cyan", width=20)
            coding_table.add_column("Description", style="white")
            
            coding_table.add_row("generate <desc>", "Generate code from description")
            coding_table.add_row("complete <code>", "Complete code snippets")
            coding_table.add_row("explain <code>", "Explain what code does")
            coding_table.add_row("debug <code>", "Find and fix bugs")
            coding_table.add_row("translate <lang>", "Convert between languages")
            coding_table.add_row("refactor <code>", "Improve code structure")
            
            console.print(coding_table)
            
            # Current Configuration Table
            config_table = Table(
                title="⚙️ CURRENT CONFIGURATION",
                show_header=True,
                header_style="bold red",
                border_style="bright_red",
                row_styles=["none", "dim"],
                show_lines=True
            )
            config_table.add_column("Setting", style="cyan", width=20)
            config_table.add_column("Value", style="white")
            
            config_table.add_row("Provider", f"{self.provider.upper() if self.provider else 'None'}")
            config_table.add_row("Model", f"{self.model if self.model else 'None'}")
            config_table.add_row("Session", f"{self.session_id}")
            config_table.add_row("Streaming", f"{'✅ Enabled' if self.enable_streaming else '❌ Disabled'}")
            config_table.add_row("Rich Formatting", f"{'✅ Enabled' if self.rich_formatter.is_available() else '❌ Disabled'}")
            
            console.print(config_table)
            
            # Features Panel
            features_panel = Panel(
                f"""🎨 [bold green]RICH FORMATTING FEATURES:[/bold green]
• Real-time streaming with Live Display
• Syntax-highlighted code blocks
• Enhanced markdown rendering
• Beautiful tables and panels

🔄 [bold yellow]MULTI-PROVIDER ADVANTAGES:[/bold yellow]
• Switch between AI providers instantly
• Compare responses from different models
• Choose the best provider for each task
• Unified interface for all providers

[italic]Just type your question or request, and I'll help you with {self.provider.upper() if self.provider else 'AI'} responses![/italic]""",
                border_style="green"
            )
            console.print("\n")
            console.print(features_panel)
            
            # Return empty string since we printed directly
            return ""
            
        except ImportError:
            # Fallback to plain text if Rich is not available
            return f"""
🤖 AI Helper Agent - Multi-Provider CLI

📝 BASIC COMMANDS:
• help, ? - Show this help message
• exit, quit, goodbye - Exit the application
• clear - Clear conversation history
• history - View recent conversation history
• info - Show current provider information

🗂️ SESSION MANAGEMENT:
• sessions - View all available sessions
• switch - Switch to another session
• Session persistence enabled with conversation history

🔧 PROVIDER COMMANDS:
• providers - Show all available AI providers
• switch <provider> - Switch to different AI provider
• info - Show current provider information
• Available providers: groq, openai, anthropic (aliases: llama, gpt, claude)

💡 CODING ASSISTANCE:
• generate <description> - Generate code from description
• complete <partial_code> - Complete code snippets
• explain <code> - Explain what code does
• debug <code> - Find and fix bugs
• translate <from> to <to> - Convert between languages
• refactor <code> - Improve code structure

⚙️ CURRENT CONFIGURATION:
• Provider: {self.provider.upper() if self.provider else 'None'}
• Model: {self.model if self.model else 'None'}
• Session: {self.session_id}
• Streaming: {'✅ Enabled' if self.enable_streaming else '❌ Disabled'}
• Rich Formatting: {'✅ Enabled' if self.rich_formatter.is_available() else '❌ Disabled'}

🎨 RICH FORMATTING FEATURES:
• Real-time streaming with Live Display
• Syntax-highlighted code blocks
• Enhanced markdown rendering
• Beautiful tables and panels

Just type your question or request, and I'll help you with {self.provider.upper() if self.provider else 'AI'} responses!
"""
    
    def _show_provider_info(self) -> str:
        """Show current provider configuration"""
        info = self.get_provider_info()
        return f"""
⚙️ AI Helper Agent - Multi-Provider Configuration:

🤖 PROVIDER SETTINGS:

� SESSION MANAGEMENT:
• sessions - View all available sessions
• switch - Switch to another session
• Session persistence enabled with conversation history

�🔧 PROVIDER COMMANDS:
• providers - Show all available AI providers
• switch <provider> - Switch to different AI provider
• info - Show current provider information
• Available providers: groq, openai, anthropic (aliases: llama, gpt, claude)

💡 CODING ASSISTANCE:
• generate <description> - Generate code from description
• complete <partial_code> - Complete code snippets
• explain <code> - Explain what code does
• debug <code> - Find and fix bugs
• translate <from> to <to> - Convert between languages
• refactor <code> - Improve code structure

⚙️ CURRENT CONFIGURATION:
• Provider: {self.provider.upper() if self.provider else 'None'}
• Model: {self.model if self.model else 'None'}
• Session: {self.session_id}
• Streaming: {'✅ Enabled' if self.enable_streaming else '❌ Disabled'}
• Rich Formatting: {'✅ Enabled' if self.rich_formatter.is_available() else '❌ Disabled'}

🎨 RICH FORMATTING FEATURES:
• Real-time streaming with Live Display
• Syntax-highlighted code blocks
• Enhanced markdown rendering
• Beautiful tables and panels

Just type your question or request, and I'll help you with {self.provider.upper() if self.provider else 'AI'} responses!
"""
    
    def _show_provider_info(self) -> str:
        """Show current provider configuration"""
        _ensure_classes_loaded()  # Ensure classes are loaded for status display
        info = self.get_provider_info()
        return f"""
⚙️ AI Helper Agent - Multi-Provider Configuration:

🤖 PROVIDER SETTINGS:
• Current Provider: {info['provider'].upper() if info['provider'] else 'None'}
• Current Model: {info['model'] if info['model'] else 'None'}
• API Key: {'✅ Set' if info['has_api_key'] else '❌ Not Set'}
• LLM Type: {info['llm_type'] if info['llm_type'] else 'None'}

🔧 SESSION SETTINGS:
• Session ID: {self.session_id}
• Workspace: {self.workspace_path}
• Streaming: {'✅ Enabled' if info['streaming_enabled'] else '❌ Disabled'}
• CLI Type: Multi-Provider

💬 CONVERSATION:
• Messages in History: {len(conversation_store.get(self.session_id, ChatMessageHistory()).messages)}

🌐 AVAILABLE PROVIDERS:
• Groq: {'✅ Available' if ChatGroq else '❌ Not installed'}
• OpenAI: {'✅ Available' if ChatOpenAI else '❌ Not installed'}  
• Anthropic: {'✅ Available' if ChatAnthropic else '❌ Not installed'}
• Google: {'✅ Available' if ChatGoogleGenerativeAI else '❌ Not installed'}
"""
    
    async def start(self):
        """Start the multi-provider CLI application"""
        self.rich_formatter.print_status("\n⚡ Starting AI Helper Agent (Multi-Provider)...", "info")
        
        # Setup user session
        if not self.setup_user_session():
            self.rich_formatter.print_status("❌ Failed to setup user session. Exiting.", "error")
            return
        
        self.rich_formatter.print_status(f"✅ AI Helper Agent ready! Using {self.provider.upper()} - {self.model}", "success")
        self.rich_formatter.print_status("💡 Type 'help' for available commands, or just start chatting!", "info")
        self.rich_formatter.print_status("🔄 Enhanced streaming with Rich formatting enabled", "info")
        self.rich_formatter.print_status("Type 'quit', 'exit', or press Ctrl+C to exit", "info")
        self.rich_formatter.print_status("Type 'history' to view conversation history", "info")
        self.rich_formatter.print_status("Type 'info' to show provider information", "info")
        print()
        
        # Main interaction loop
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                response = await self.handle_command(user_input)
                
                if response == "EXIT":
                    break
                elif response == "HISTORY_SHOWN":
                    continue  # History already shown
                elif response in ["🧹 Conversation history cleared!"]:
                    self.rich_formatter.print_status(response, "success")
                elif response.startswith("⚙️"):
                    # Provider info or help - display as markdown
                    self.rich_formatter.display_enhanced_rich_markdown(response)
                        
            except KeyboardInterrupt:
                self.rich_formatter.print_goodbye()
                break
            except EOFError:
                self.rich_formatter.print_goodbye()
                break
            except Exception as e:
                self.rich_formatter.print_status(f"❌ Error: {e}", "error")


# Backwards compatibility alias
AIHelperCLI = MultiProviderAIHelperCLI


def show_rich_help():
    """Show Rich-formatted help for Multi-Provider CLI"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        
        console = Console()
        
        # Main title
        console.print("\n")
        console.print(Panel.fit(
            "[bold blue]AI Helper Agent - Multi-Provider CLI[/bold blue]\n"
            "[dim]🤖 Access all major AI providers in one interface[/dim]",
            border_style="blue"
        ))
        
        # Usage section
        console.print("\n[bold green]USAGE:[/bold green]")
        console.print("  [cyan]ai-smart-chat[/cyan] [dim][options][/dim]")
        
        # Commands table
        commands_table = Table(
            title="🚀 Available Commands",
            show_header=True, 
            header_style="bold magenta",
            width=100,
            expand=False,
            show_lines=True
        )
        commands_table.add_column("Command", style="cyan", width=30)
        commands_table.add_column("Aliases", style="green", width=25)
        commands_table.add_column("Description", style="white", width=35)
        
        commands_table.add_row("ai-smart-chat", "ai-multi, ai-pro", "Start with provider selection")
        commands_table.add_row("ai-smart-chat --provider groq", "ai-multi --provider groq", "Start directly with Groq")
        commands_table.add_row("ai-smart-chat --quick", "ai-pro --quick", "Skip startup, use existing config")
        
        console.print("\n[bold green]COMMANDS:[/bold green]")
        console.print(commands_table)
        
        # Providers table
        providers_table = Table(
            title="🤖 Supported AI Providers",
            show_header=True, 
            header_style="bold gold1",
            width=90,
            expand=False,
            show_lines=True
        )
        providers_table.add_column("Provider", style="bold white", width=15)
        providers_table.add_column("Models", style="cyan", width=35)
        providers_table.add_column("Features", style="white", width=30)
        
        providers_table.add_row("Groq", "llama-3.1-70b, mixtral-8x7b, gemma-7b", "Ultra-fast responses")
        providers_table.add_row("OpenAI", "gpt-4, gpt-3.5-turbo, gpt-4-turbo", "Advanced reasoning")
        providers_table.add_row("Anthropic", "claude-3-sonnet, claude-3-haiku", "Excellent code analysis")
        providers_table.add_row("Google", "gemini-pro, gemini-1.5-pro", "Multi-modal capabilities")
        
        console.print("\n[bold green]PROVIDERS:[/bold green]")
        console.print(providers_table)
        
        # Options table
        options_table = Table(
            show_header=True, 
            header_style="bold magenta",
            width=80,
            expand=False,
            show_lines=True
        )
        options_table.add_column("Option", style="cyan", width=20)
        options_table.add_column("Description", style="white", width=50)
        
        options_table.add_row("-h, --help", "Show this help message and exit")
        options_table.add_row("-s, --session ID", "Session ID for conversation history")
        options_table.add_row("-p, --provider NAME", "AI provider (groq/openai/anthropic/google)")
        options_table.add_row("-m, --model NAME", "Model to use with selected provider")
        options_table.add_row("--quick", "Skip startup interface")
        options_table.add_row("--version, -v", "Show version information")
        
        console.print("\n[bold green]OPTIONS:[/bold green]")
        console.print(options_table)
        
        # Examples section
        console.print("\n[bold green]EXAMPLES:[/bold green]")
        examples = [
            ("ai-smart-chat", "Interactive provider selection"),
            ("ai-multi --provider groq", "Start directly with Groq"),
            ("ai-pro --session coding --provider openai", "Coding session with OpenAI"),
        ]
        
        for cmd, desc in examples:
            console.print(f"  [cyan]{cmd}[/cyan]  [dim]# {desc}[/dim]")
        
        console.print("")
        
    except ImportError:
        # Fallback to plain text
        print("AI Helper Agent - Multi-Provider CLI")
        print("\nUsage: ai-smart-chat [options]")
        print("\nProviders: groq, openai, anthropic, google")
        print("Examples:")
        print("  ai-smart-chat                    # Interactive selection")
        print("  ai-smart-chat --provider groq    # Start with Groq")


async def main_async():
    """Async main entry point for multi-provider CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Multi-Provider CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-smart-chat                       # Start with provider selection
  ai-smart-chat --provider groq       # Start with specific provider
  ai-smart-chat --quick               # Skip startup, use existing config
  ai-smart-chat --session work        # Start with named session
        """
    )
    
    parser.add_argument(
        "--session", "-s",
        default="default",
        help="Session ID for conversation history"
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["groq", "openai", "anthropic", "google"],
        help="AI provider to use"
    )
    
    parser.add_argument(
        "--model", "-m",
        help="Model to use with the selected provider"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip startup interface and use existing configuration"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent Multi-Provider CLI v2.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Create CLI instance
        cli = MultiProviderAIHelperCLI(
            session_id=args.session,
            model=args.model,
            skip_startup=args.quick
        )
        
        # Set provider if specified
        if args.provider:
            cli.provider = args.provider
        
        # Start the application
        await cli.start()
        
    except KeyboardInterrupt:
        rich_formatter.print_goodbye()
        sys.exit(0)
    except Exception as e:
        rich_formatter.print_status(f"❌ Error: {e}", "error")
        sys.exit(1)


def main():
    """Main entry point for multi-provider CLI - handles async execution"""
    # Show Rich help if requested
    if '--help' in sys.argv or '-h' in sys.argv:
        show_rich_help()
        return
        
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Alias for backward compatibility
MultiProviderCLI = MultiProviderAIHelperCLI
