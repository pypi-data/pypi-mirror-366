"""
AI Helper Agent - Single Provider CLI (Groq Only)
Simplified CLI with only Groq models for faster startup and focused use
"""

import os
import sys
import asyncio
import argparse
import re
import time
import warnings
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Filter out warnings to keep CLI clean
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
warnings.filterwarnings("ignore", message=".*avconv.*")
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*")
warnings.filterwarnings("ignore", module="pydub")

# LAZY LOADING: Heavy imports moved to functions for faster startup
def _lazy_import_langchain():
    """Lazy import LangChain and Groq dependencies only when needed"""
    try:
        from langchain_groq import ChatGroq
        from langchain_community.chat_message_histories import ChatMessageHistory
        from langchain_core.chat_history import BaseChatMessageHistory
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_core.runnables import RunnableLambda, RunnablePassthrough
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        
        return {
            'ChatGroq': ChatGroq,
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
        return None

def _lazy_import_groq_async():
    """Lazy import Groq Async client only when needed"""
    try:
        from groq import AsyncGroq
        return AsyncGroq, True
    except ImportError:
        return None, False

# Set availability flag - will be checked when needed
GROQ_AVAILABLE = False

# Lazy loading for heavy internal modules
InteractiveAgent = None
config = None
security_manager = None
user_manager = None
AdvancedPromptEnhancer = None
SystemConfigurationManager = None
StreamingResponseHandler = None
AdvancedStreamingHandler = None
CustomStreamingCallback = None
EnhancedStreamingHandler = None
get_simple_logo = None
display_cli_header = None

# Lazy loading for managers
api_key_manager = None
conversation_manager = None
MessageRole = None
rich_formatter = None

def _lazy_load_internal_modules():
    """Lazy load heavy internal modules when needed"""
    global InteractiveAgent, config, security_manager, user_manager
    global AdvancedPromptEnhancer, SystemConfigurationManager
    global StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
    global get_simple_logo, display_cli_header
    global api_key_manager, conversation_manager, MessageRole, rich_formatter
    
    if InteractiveAgent is None:
        try:
            from ..core.core import InteractiveAgent
            from ..core.config import config
            from ..core.security import security_manager
            from ..managers.user_manager import user_manager
            from ..utils.prompt_enhancer import AdvancedPromptEnhancer
            from ..core.system_config import SystemConfigurationManager
            from ..utils.streaming import StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
            from ..utilities.simple_logo import get_simple_logo, display_cli_header
            from ..managers.api_key_manager import api_key_manager
            from ..managers.conversation_manager import conversation_manager, MessageRole
            from ..utils.rich_formatting import rich_formatter
        except ImportError:
            # Fallback for direct execution with dummy classes
            class DummyClass:
                def __init__(self, *args, **kwargs): pass
                def __call__(self, *args, **kwargs): return self
                def __getattr__(self, name): return lambda *args, **kwargs: None
            
            InteractiveAgent = DummyClass()
            config = DummyClass()
            security_manager = DummyClass()
            user_manager = DummyClass()
            AdvancedPromptEnhancer = DummyClass
            SystemConfigurationManager = DummyClass
            StreamingResponseHandler = DummyClass
            AdvancedStreamingHandler = DummyClass
            CustomStreamingCallback = DummyClass
            EnhancedStreamingHandler = DummyClass
            get_simple_logo = lambda: "AI Helper Agent"
            display_cli_header = lambda x: print(f"=== {x} ===")
            api_key_manager = DummyClass()
            conversation_manager = DummyClass()
            rich_formatter = DummyClass()


# Global conversation store
conversation_store: Dict[str, Any] = {}  # type: ignore


class SingleProviderCLI:
    """Single Provider CLI - Groq Only for fast and focused use"""
    
    # Available Groq models only (Remove Mixtral as requested)
    AVAILABLE_MODELS = {
        "llama-3.3-70b-versatile": "Llama 3.3 70B (Meta - General purpose, Large)",
        "llama-3.1-8b-instant": "Llama 3.1 8B (Meta - Instant response, Fast)",
        "gemma2-9b-it": "Gemma 2 9B (Google - Chat fine-tuned, Balanced)",
        "llama-3.1-70b-versatile": "Llama 3.1 70B (Meta - Complex reasoning)",
        "llama3-8b-8192": "Llama 3 8B (Legacy - Fast, Good for coding)",
        "llama3-70b-8192": "Llama 3 70B (Legacy - Better reasoning)"
    }
    
    def __init__(self, session_id: str = "default", model: str = None, skip_startup: bool = False):
        self.session_id = f"single_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.model = model or "llama-3.1-8b-instant"
        
        # Check if we're in help mode first (avoid heavy initialization)
        self.help_mode = '--help' in sys.argv or '-h' in sys.argv
        
        # Initialize components early (only if not in help mode)
        if not self.help_mode:
            # Load heavy modules FIRST to make managers available
            _lazy_load_internal_modules()
        
        # Initialize API key from manager after loading modules
        self.api_key = None
        if not self.help_mode:
            # Get API key from manager first, then environment
            self.api_key = api_key_manager.get_api_key('groq')
            if not self.api_key:
                self.api_key = os.getenv("GROQ_API_KEY")
        
        self.llm = None
        self.async_groq_client = None
        self.chain = None
        self.skip_startup = skip_startup
        self.workspace_path = Path(".")
        
        # Initialize remaining components (only if not in help mode)
        if not self.help_mode:
            self.user_manager = user_manager
            self.security_manager = security_manager
            self.system_config = SystemConfigurationManager()
            self.prompt_enhancer = AdvancedPromptEnhancer(workspace_path=self.workspace_path)
            self.conversation_manager = conversation_manager
        
        self.rich_formatter = rich_formatter
        
        # Streaming components - Initialize as None first, will be set up after LLM is ready
        self.streaming_handler: Optional[Any] = None  # type: ignore
        self.advanced_streaming: Optional[Any] = None  # type: ignore
        self.enhanced_streaming: Optional[Any] = None  # type: ignore
        self.streaming_enabled = True
        
        # Configure Rich formatter (only when not in help mode)
        if not self.help_mode and rich_formatter.is_available():
            rich_formatter.print_status("✅ Using Rich for enhanced display", "success")
        elif not self.help_mode:
            print("⚠️ Rich not available - using basic display")
        
        # Sync mode flag for event loop handling
        self.force_sync_mode = False
    
    def get_session_history(self, session_id: str) -> Any:  # type: ignore
        """Get or create session history"""
        langchain = _lazy_import_langchain()
        if session_id not in conversation_store:
            conversation_store[session_id] = langchain['ChatMessageHistory']()
        return conversation_store[session_id]
    
    def show_session_selection(self):
        """Show session selection with Rich table formatting"""
        if self.rich_formatter.is_available():
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
            choice = input("\nSelect option (1): ").strip() or "1"
            
            if choice == "1":
                # Generate new session ID
                self.session_id = f"single_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if self.rich_formatter.is_available():
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
                if self.rich_formatter.is_available():
                    from rich.console import Console
                    console = Console()
                    console.print("[red]❌ Invalid choice[/red]")
                else:
                    print("❌ Invalid choice")
                return self.show_session_selection()
                
        except KeyboardInterrupt:
            return False
        except Exception as e:
            if self.rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print(f"[red]❌ Error in session selection: {e}[/red]")
            else:
                print(f"❌ Error in session selection: {e}")
            return False
    
    def continue_previous_session(self):
        """Continue from a previous session"""
        recent_sessions = conversation_manager.get_recent_sessions(limit=10)
        
        if not recent_sessions:
            if self.rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print("[yellow]⚠️ No previous sessions found[/yellow]")
            else:
                print("⚠️ No previous sessions found")
            return False
        
        # Show recent sessions table
        if self.rich_formatter.is_available():
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
            choice = input(f"\nSelect session (1-{min(len(recent_sessions), 10)}) or Enter to cancel: ").strip()
            
            if not choice:
                return False
                
            session_idx = int(choice) - 1
            if 0 <= session_idx < len(recent_sessions):
                selected_session = recent_sessions[session_idx]
                self.session_id = selected_session['session_id']
                
                if self.rich_formatter.is_available():
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
                if self.rich_formatter.is_available():
                    from rich.console import Console
                    console = Console()
                    console.print("[red]❌ Invalid session selection[/red]")
                else:
                    print("❌ Invalid session selection")
                return False
                
        except (ValueError, KeyboardInterrupt):
            return False
        except Exception as e:
            if self.rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print(f"[red]❌ Error selecting session: {e}[/red]")
            else:
                print(f"❌ Error selecting session: {e}")
            return False
    
    def show_all_sessions(self):
        """Show all available sessions"""
        all_sessions = conversation_manager.get_recent_sessions(limit=50)
        
        if not all_sessions:
            if self.rich_formatter.is_available():
                from rich.console import Console
                console = Console()
                console.print("[yellow]⚠️ No sessions found[/yellow]")
            else:
                print("⚠️ No sessions found")
            return
        
        if self.rich_formatter.is_available():
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
            
        history = conversation_manager.get_conversation_history(self.session_id, max_messages=limit)
        
        if not history:
            return
        
        if self.rich_formatter.is_available():
            from rich.console import Console
            console = Console()
            console.print(f"\n[bold blue]💬 Recent conversation context:[/bold blue]")
            for msg in history[-limit:]:
                role_icon = "👤" if msg.role == MessageRole.USER else "🤖"
                role_name = msg.role.value.title()
                
                # Truncate long messages for context display
                content = msg.content
                if len(content) > 100:
                    content = content[:97] + "..."
                
                console.print(f"[dim]{role_icon} {role_name}:[/dim] {content}")
            console.print("[dim]─── End of Context ───[/dim]")
        else:
            print("\n💬 Recent conversation context:")
            for msg in history[-limit:]:
                role_icon = "👤" if msg.role == MessageRole.USER else "🤖"
                role_name = msg.role.value.title()
                
                # Truncate long messages for context display
                content = msg.content
                if len(content) > 100:
                    content = content[:97] + "..."
                
                print(f"{role_icon} {role_name}: {content}")
            print("─── End of Context ───")
    
    def show_splash_screen(self):
        """Show Groq-only splash screen with simple logo"""
        display_cli_header(
            "AI HELPER AGENT - GROQ POWERED ⚡",
            "Lightning-fast inference with Llama & Gemma models"
        )
    
    def setup_user_session(self) -> bool:
        """Setup user session with Groq-only provider"""
        # Skip setup in help mode
        if hasattr(self, 'help_mode') and self.help_mode:
            return True
            
        if not self.skip_startup:
            # Show Groq-only splash screen
            self.show_splash_screen()
            
            # Quick session setup - avoid blocking
            print(f"✅ Starting session: {self.session_id}")
            
            # Setup Groq-only interface (non-blocking)
            model_id, api_key, llm_instance = self.setup_groq_only_interface()
            
            if model_id and llm_instance:
                self.model = model_id
                self.api_key = api_key
                self.llm = llm_instance
                return True
            else:
                print("❌ Failed to setup user session")
                return False
        else:
            # Quick setup for programmatic use
            print("⚡ Quick start mode enabled")
            return self.setup_llm_and_chain()
    
    def setup_groq_only_interface(self):
        """Setup Groq-only interface without provider selection"""
        # Ensure modules are loaded first
        if api_key_manager is None:
            _lazy_load_internal_modules()
            
        # Get API key from manager first, then environment
        api_key = api_key_manager.get_api_key('groq')
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            print("🔑 Groq API key required. Get one free at: https://console.groq.com/keys")
            try:
                api_key = input("Enter your Groq API key: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("❌ API key required")
                return None, None, None
            
            if not api_key:
                print("❌ API key required for Groq")
                return None, None, None
            
            # Offer to save the key
            try:
                save_key = input("💾 Save this API key for future use? (y/N): ").strip().lower()
                if save_key == 'y':
                    if api_key_manager.set_api_key('groq', api_key):
                        print("✅ API key saved securely")
            except (EOFError, KeyboardInterrupt):
                pass  # Skip saving if interrupted
        
        # Show simplified model selection
        print("\n🤖 Available Groq Models:")
        print("1. llama-3.1-8b-instant (Default - Ultra fast)")
        print("2. llama-3.3-70b-versatile (Latest Meta model)")
        print("3. gemma2-9b-it (Google's balanced model)")
        print("4. llama-3.1-70b-versatile (Large reasoning model)")
        
        # Model selection with timeout
        try:
            choice = input("Select model (1): ").strip() or "1"
            choice_idx = int(choice) - 1
            
            groq_models = [
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile", 
                "gemma2-9b-it",
                "llama-3.1-70b-versatile"
            ]
            
            if 0 <= choice_idx < len(groq_models):
                selected_model_id = groq_models[choice_idx]
                print(f"✅ Selected: {selected_model_id}")
                
                # Create LLM instance using lazy loading
                langchain = _lazy_import_langchain()
                llm_instance = langchain['ChatGroq'](
                    temperature=0.1,
                    model_name=selected_model_id,
                    groq_api_key=api_key,
                    streaming=True
                )
                
                # Create async client for streaming
                if GROQ_AVAILABLE:
                    self.async_groq_client = langchain['AsyncGroq'](api_key=api_key)
                
                return selected_model_id, api_key, llm_instance
            else:
                print("❌ Invalid selection, using default")
                selected_model_id = "llama-3.1-8b-instant"
                langchain = _lazy_import_langchain()
                llm_instance = langchain['ChatGroq'](
                    temperature=0.1,
                    model_name=selected_model_id,
                    groq_api_key=api_key,
                    streaming=True
                )
                if GROQ_AVAILABLE:
                    self.async_groq_client = langchain['AsyncGroq'](api_key=api_key)
                return selected_model_id, api_key, llm_instance
                
        except (ValueError, KeyboardInterrupt, EOFError):
            print("Using default model: llama-3.1-8b-instant")
            selected_model_id = "llama-3.1-8b-instant"
            langchain = _lazy_import_langchain()
            llm_instance = langchain['ChatGroq'](
                temperature=0.1,
                model_name=selected_model_id,
                groq_api_key=api_key,
                streaming=True
            )
            if GROQ_AVAILABLE:
                self.async_groq_client = langchain['AsyncGroq'](api_key=api_key)
            return selected_model_id, api_key, llm_instance
    
    def setup_llm_and_chain(self):
        """Setup LLM and conversation chain with Groq only"""
        if self.llm:
            # LLM already set up by startup interface
            pass
        else:
            # Ensure modules are loaded first
            if api_key_manager is None:
                _lazy_load_internal_modules()
                
            # Get API key from manager first, fallback to environment
            self.api_key = api_key_manager.get_api_key('groq')
            if not self.api_key:
                self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                print("❌ GROQ API key not found")
                print("💡 Please set up your API keys using:")
                print("   python -m ai_helper_agent.utilities.api_key_setup manage")
                return False
            
            langchain = _lazy_import_langchain()
            self.llm = langchain['ChatGroq'](
                model=self.model,
                temperature=0.1,
                api_key=self.api_key
            )
        
        try:
            # Create the conversation chain with history
            langchain = _lazy_import_langchain()
            prompt = langchain['ChatPromptTemplate'].from_messages([
                ("system", self._get_system_prompt()),
                langchain['MessagesPlaceholder'](variable_name="history"),
                ("human", "{input}")
            ])

            # Create conversation chain with history
            self.conversation_chain = langchain['RunnableWithMessageHistory'](
                prompt | self.llm | langchain['StrOutputParser'](),
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="history",
            )
            
            # Initialize streaming handlers now that LLM and conversation chain are ready
            self.streaming_handler = StreamingResponseHandler(self.llm, self.conversation_chain)
            self.advanced_streaming = AdvancedStreamingHandler(self.llm, self.conversation_chain)
            self.enhanced_streaming = EnhancedStreamingHandler(self.llm, self.conversation_chain)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup LLM chain: {e}")
            return False
    
    def _get_system_prompt(self) -> str:
        """Get the enhanced system prompt for the AI assistant"""
        if self.prompt_enhancer:
            return self.prompt_enhancer.get_enhanced_system_prompt()
        
        # Fallback to basic prompt if enhancer not available
        return f"""You are AI Helper Agent v2.0.1, an expert programming assistant created by Meet Solanki, an AIML Student, powered by Groq's lightning-fast inference.

🌟 ABOUT THIS SYSTEM:
- Name: AI Helper Agent v2.0.1
- Creator: Meet Solanki (AIML Student)
- Purpose: Ultra-fast programming assistance with Groq
- Mission: Providing instant coding help with lightning speed

👨‍💻 CREATOR'S VISION:
This system was developed by Meet Solanki to harness Groq's incredible speed for real-time programming assistance that helps developers code faster and learn better.

🔧 CODE GENERATION & COMPLETION
- Generate complete code from natural language descriptions
- Provide intelligent code completion and suggestions
- Support multiple programming languages (Python, JavaScript, TypeScript, Go, Rust, Java, C++, etc.)
- Generate functions, classes, modules, and entire applications
- Create boilerplate code and project structures

⚡ GROQ ADVANTAGES
- Ultra-fast responses for real-time coding assistance
- Optimized for code generation and completion tasks
- Excellent performance on programming-related queries
- Instant feedback for iterative development

🔄 CODE TRANSFORMATION & TRANSLATION
- Convert code between different programming languages
- Refactor code for better performance, readability, and maintainability
- Modernize legacy code to use current best practices
- Transform coding patterns and paradigms

🐛 DEBUGGING & ERROR FIXING
- Identify and fix syntax errors, logic bugs, and runtime issues
- Explain error messages and suggest solutions
- Provide step-by-step debugging guidance
- Optimize code for better performance
- Help users understand and learn from their mistakes

Current workspace: {str(self.workspace_path)}
Current model: {self.model or 'Unknown'} (GROQ)
Provider: GROQ (Lightning Fast)

💡 HELPING YOU SUCCEED:
As created by Meet Solanki (AIML Student), I combine Groq's incredible speed with intelligent programming assistance to help you code faster and learn better.

I'm ready to help you with any programming task with Groq's ultra-fast responses! 🚀"""
    
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
                if self.session_id in conversation_store:
                    langchain = _lazy_import_langchain()
                    conversation_store[self.session_id] = langchain['ChatMessageHistory']()
                self.conversation_manager.clear_conversation(self.session_id)
                return "🧹 Conversation history cleared!"
            
            if user_input.lower() == 'history':
                self.show_conversation_history()
                return "HISTORY_SHOWN"
            
            if user_input.lower() == 'config':
                return self._show_configuration()
            
            # Handle streaming control
            if user_input.lower().startswith('streaming'):
                return await self._handle_streaming_command(user_input)
            
            # Regular AI response - use sync method to avoid event loop issues
            if self.streaming_enabled:
                # Use sync response generation to avoid nested event loop issues
                return self._get_ai_response_sync(user_input)
            else:
                response = self.conversation_chain.invoke(
                    {"input": user_input},
                    config={"configurable": {"session_id": self.session_id}}
                )
                
                # Save to conversation history
                self.conversation_manager.add_message(self.session_id, MessageRole.USER, user_input)
                self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, response)
                
                return response
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"
    
    def show_conversation_history(self, limit: int = 10):
        """Show recent conversation history"""
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
                
                # Truncate long messages for history display
                content = msg.content
                if len(content) > 100:
                    content = content[:100] + "..."
                
                rows.append([timestamp, f"{role_icon} {msg.role.value.title()}", content])
            
            self.rich_formatter.show_table(f"📚 Conversation History (Last {limit} messages)", headers, rows, ["dim", "bold", "white"])
                    
        except Exception as e:
            self.rich_formatter.print_status(f"❌ Error loading conversation history: {str(e)}", "error")
    
    async def _get_ai_response_streaming(self, prompt: str) -> str:
        """Get AI response with enhanced Rich streaming"""
        try:
            if not self.async_groq_client:
                # Fallback to basic streaming
                full_response = ""
                self.rich_formatter.print_status("🤖 AI Helper:", "info")
                
                for chunk in self.conversation_chain.stream(
                    {"input": prompt},
                    config={"configurable": {"session_id": self.session_id}}
                ):
                    if chunk:
                        print(chunk, end="", flush=True)
                        full_response += chunk
                
                print()  # New line after streaming
                
                # Save to conversation history
                self.conversation_manager.add_message(self.session_id, MessageRole.USER, prompt)
                self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, full_response)
                
                return full_response
            
            # Enhanced streaming with Rich formatting
            stream = self.async_groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                stream=True
            )
            
            # Process streaming response with Rich formatting
            def text_chunks():
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
            response = self.rich_formatter.stream_with_rich_formatting(chunks, f"Groq ({self.model})")
            
            # Save to conversation history
            self.conversation_manager.add_message(self.session_id, MessageRole.USER, prompt)
            self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, response)
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error generating response: {str(e)}"
            self.rich_formatter.print_status(error_msg, "error")
            return error_msg
    
    async def _handle_streaming_command(self, command: str) -> str:
        """Handle streaming control commands"""
        parts = command.split()
        if len(parts) < 2:
            return "Usage: streaming [on|off|test]"
        
        action = parts[1].lower()
        
        if action == "on":
            self.streaming_enabled = True
            return "✅ Streaming responses enabled"
        elif action == "off":
            self.streaming_enabled = False
            return "❌ Streaming responses disabled"
        elif action == "test":
            return await self._get_ai_response_streaming("Say hello and confirm streaming is working!")
        else:
            return "Usage: streaming [on|off|test]"
    
    def _get_help_message(self) -> str:
        """Get help message with available commands using Rich UI"""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            
            console = Console()
            
            # Create main title panel
            title_panel = Panel.fit(
                "[bold blue]🤖 AI Helper Agent - Single Provider CLI (Groq Only)[/bold blue]\n"
                "[dim]Lightning-fast responses with Groq's powerful models[/dim]",
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
            basic_table.add_row("config", "Show current configuration")
            
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
            
            # Advanced Commands Table
            advanced_table = Table(
                title="🔧 ADVANCED COMMANDS",
                show_header=True,
                header_style="bold magenta",
                border_style="bright_magenta",
                row_styles=["none", "dim"],
                show_lines=True
            )
            advanced_table.add_column("Command", style="cyan", width=15)
            advanced_table.add_column("Description", style="white")
            
            advanced_table.add_row("streaming", "Control streaming responses [on|off|test]")
            
            console.print(advanced_table)
            
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
            
            config_table.add_row("Model", f"{self.model}")
            config_table.add_row("Provider", "GROQ (Lightning Fast)")
            config_table.add_row("Session", f"{self.session_id}")
            config_table.add_row("Workspace", f"{self.workspace_path}")
            config_table.add_row("Streaming", f"{'✅ Enabled' if self.streaming_enabled else '❌ Disabled'}")
            config_table.add_row("Rich Formatting", f"{'✅ Enabled' if self.rich_formatter.is_available() else '❌ Disabled'}")
            
            console.print(config_table)
            
            # Features Panel
            features_panel = Panel(
                """⚡ [bold yellow]GROQ ADVANTAGES:[/bold yellow]
• Ultra-fast responses for real-time coding
• Optimized for programming tasks  
• Instant feedback for development
• Rich markdown formatting with syntax highlighting

🎨 [bold green]RICH FORMATTING FEATURES:[/bold green]
• Real-time streaming with Live Display
• Syntax-highlighted code blocks
• Enhanced markdown rendering
• Beautiful tables and panels

[italic]Just type your question or request, and I'll help you with lightning-fast responses![/italic]""",
                border_style="green"
            )
            console.print("\n")
            console.print(features_panel)
            
            # Return empty string since we printed directly
            return ""
            
        except ImportError:
            # Fallback to plain text if Rich is not available
            return f"""
🤖 AI Helper Agent - Single Provider CLI (Groq Only)

📝 BASIC COMMANDS:
• help, ? - Show this help message
• exit, quit, goodbye - Exit the application
• clear - Clear conversation history
• history - View recent conversation history
• config - Show current configuration

🗂️ SESSION MANAGEMENT:
• sessions - View all available sessions
• switch - Switch to another session
• Session persistence enabled with conversation history

🔧 ADVANCED COMMANDS:
• streaming [on|off|test] - Control streaming responses

💡 CODING ASSISTANCE:
• generate <description> - Generate code from description
• complete <partial_code> - Complete code snippets  
• explain <code> - Explain what code does
• debug <code> - Find and fix bugs
• translate <from> to <to> - Convert between languages
• refactor <code> - Improve code structure

⚙️ CURRENT CONFIGURATION:
• Model: {self.model}
• Provider: GROQ (Lightning Fast)
• Session: {self.session_id}
• Workspace: {self.workspace_path}
• Streaming: {'✅ Enabled' if self.streaming_enabled else '❌ Disabled'}
• Rich Formatting: {'✅ Enabled' if self.rich_formatter.is_available() else '❌ Disabled'}

⚡ GROQ ADVANTAGES:
• Ultra-fast responses for real-time coding
• Optimized for programming tasks
• Instant feedback for development
• Rich markdown formatting with syntax highlighting

🎨 RICH FORMATTING FEATURES:
• Real-time streaming with Live Display
• Syntax-highlighted code blocks
• Enhanced markdown rendering
• Beautiful tables and panels

Just type your question or request, and I'll help you with lightning-fast responses!

    def _show_configuration(self) -> str:

� SESSION MANAGEMENT:
• sessions - View all available sessions
• switch - Switch to another session
• Session persistence enabled with conversation history

�🔧 ADVANCED COMMANDS:
• streaming [on|off|test] - Control streaming responses

💡 CODING ASSISTANCE:
• generate <description> - Generate code from description
• complete <partial_code> - Complete code snippets  
• explain <code> - Explain what code does
• debug <code> - Find and fix bugs
• translate <from> to <to> - Convert between languages
• refactor <code> - Improve code structure

⚙️ CURRENT CONFIGURATION:
• Model: {self.model}
• Provider: GROQ (Lightning Fast)
• Session: {self.session_id}
• Workspace: {self.workspace_path}
• Streaming: {'✅ Enabled' if self.streaming_enabled else '❌ Disabled'}
• Rich Formatting: {'✅ Enabled' if self.rich_formatter.is_available() else '❌ Disabled'}

⚡ GROQ ADVANTAGES:
• Ultra-fast responses for real-time coding
• Optimized for programming tasks
• Instant feedback for development
• Rich markdown formatting with syntax highlighting

🎨 RICH FORMATTING FEATURES:
• Real-time streaming with Live Display
• Syntax-highlighted code blocks
• Enhanced markdown rendering
• Beautiful tables and panels

"""
    
    def _show_configuration(self) -> str:
        """Show current configuration"""
        config_info = f"""
⚙️ AI Helper Agent Configuration (Single Provider):

🤖 MODEL SETTINGS:
• Current Model: {self.model}
• Provider: GROQ (Lightning Fast)
• API Key: {'✅ Set' if self.api_key else '❌ Not Set'}

🔧 SESSION SETTINGS:
• Session ID: {self.session_id}
• Workspace: {self.workspace_path}
• Streaming: {'✅ Enabled' if self.streaming_enabled else '❌ Disabled'}
• CLI Type: Single Provider (Groq Only)

💬 CONVERSATION:
• Messages in History: {len(conversation_store.get(self.session_id, _lazy_import_langchain()['ChatMessageHistory']()).messages)}

📁 CONFIG DIRECTORY:
• Single Provider Config: C:\\Users\\{os.getenv('USERNAME', 'user')}\\.ai_helper_agent\\single\\{os.getenv('USERNAME', 'user')}\\

⚡ GROQ FEATURES:
• Ultra-fast inference for coding tasks
• Real-time responses for interactive development
• Optimized for programming assistance
"""
        return config_info
    
    async def start(self):
        """Start the CLI application"""
        # Skip startup in help mode
        if hasattr(self, 'help_mode') and self.help_mode:
            return
            
        self.rich_formatter.print_status("\n⚡ Starting AI Helper Agent (Single Provider - Groq)...", "info")
        
        # Setup user session
        if not self.setup_user_session():
            self.rich_formatter.print_status("❌ Failed to setup user session. Exiting.", "error")
            return
        
        # Setup LLM and chain
        if not self.setup_llm_and_chain():
            self.rich_formatter.print_status("❌ Failed to setup LLM. Exiting.", "error")
            return
        
        self.rich_formatter.print_status(f"✅ AI Helper Agent ready! Using {self.model} (Groq)", "success")
        self.rich_formatter.print_status("💡 Type 'help' for available commands, or just start chatting!", "info")
        self.rich_formatter.print_status("⚡ Ultra-fast streaming responses enabled for real-time interaction", "info")
        self.rich_formatter.print_status("Type 'quit', 'exit', or press Ctrl+C to exit", "info")
        self.rich_formatter.print_status("Type 'history' to view conversation history", "info")
        print()
        
        # Main interaction loop
        while True:
            try:
                if self.rich_formatter.is_available():
                    user_input = input("👤 You: ").strip()
                else:
                    user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                response = await self.handle_command(user_input)
                
                if response == "EXIT":
                    break
                elif response == "HISTORY_SHOWN":
                    continue  # History already shown
                elif response:
                    if not self.streaming_enabled and response not in ["🧹 Conversation history cleared!"]:
                        self.rich_formatter.display_enhanced_rich_markdown(response)
                    elif response in ["🧹 Conversation history cleared!"]:
                        self.rich_formatter.print_status(response, "success")
                        
            except KeyboardInterrupt:
                self.rich_formatter.print_goodbye()
                break
            except EOFError:
                self.rich_formatter.print_goodbye()
                break
            except Exception as e:
                self.rich_formatter.print_status(f"❌ Error: {e}", "error")

    def start_sync(self):
        """Start the CLI application in synchronous mode (for when event loop is already running)"""
        # Skip startup in help mode
        if hasattr(self, 'help_mode') and self.help_mode:
            return
            
        self.rich_formatter.print_status("\n⚡ Starting AI Helper Agent (Single Provider - Groq) [SYNC MODE]...", "info")
        
        # Setup user session
        if not self.setup_user_session():
            self.rich_formatter.print_status("❌ Failed to setup user session. Exiting.", "error")
            return
        
        # Setup LLM and chain
        if not self.setup_llm_and_chain():
            self.rich_formatter.print_status("❌ Failed to setup LLM. Exiting.", "error")
            return
        
        self.rich_formatter.print_status(f"✅ AI Helper Agent ready! Using {self.model} (Groq) [SYNC MODE]", "success")
        self.rich_formatter.print_status("💡 Type 'help' for available commands, or just start chatting!", "info")
        self.rich_formatter.print_status("⚡ Ultra-fast streaming responses enabled for real-time interaction", "info")
        self.rich_formatter.print_status("Type 'quit', 'exit', or press Ctrl+C to exit", "info")
        self.rich_formatter.print_status("Type 'history' to view conversation history", "info")
        print()
        
        # Main interaction loop (synchronous version)
        while True:
            try:
                if self.rich_formatter.is_available():
                    user_input = input("👤 You: ").strip()
                else:
                    user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands synchronously
                response = self.handle_command_sync(user_input)
                
                if response == "EXIT":
                    break
                elif response == "HISTORY_SHOWN":
                    continue  # History already shown
                elif response:
                    if not self.streaming_enabled and response not in ["🧹 Conversation history cleared!"]:
                        self.rich_formatter.display_enhanced_rich_markdown(response)
                    elif response in ["🧹 Conversation history cleared!"]:
                        self.rich_formatter.print_status(response, "success")
                        
            except KeyboardInterrupt:
                self.rich_formatter.print_goodbye()
                break
            except EOFError:
                self.rich_formatter.print_goodbye()
                break
            except Exception as e:
                self.rich_formatter.print_status(f"❌ Error: {e}", "error")

    def handle_command_sync(self, user_input: str) -> str:
        """Handle command synchronously (no async/await)"""
        try:
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                self.rich_formatter.print_goodbye()
                return "EXIT"
            
            elif user_input.lower() == 'history':
                self.show_conversation_history()
                return "HISTORY_SHOWN"
            
            elif user_input.lower() == 'clear':
                try:
                    self.conversation_manager.clear_conversation(self.session_id)
                    return "🧹 Conversation history cleared!"
                except Exception as e:
                    return f"❌ Error clearing history: {str(e)}"
            
            elif user_input.lower() == 'sessions':
                self.show_all_sessions()
                return "SESSIONS_SHOWN"
            
            elif user_input.lower() == 'switch':
                if self.show_session_selection():
                    self.show_session_context()
                    return f"✅ Switched to session: {self.session_id}"
                return "Session switch cancelled"
            
            elif user_input.lower() == 'help':
                show_rich_help()
                return "HELP_SHOWN"
            
            else:
                # Generate AI response using sync method
                response = self._get_ai_response_sync(user_input)
                return response
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"

    def _get_ai_response_sync(self, prompt: str) -> str:
        """Get AI response synchronously with Rich live formatting"""
        try:
            if not self.api_key:
                return "❌ API key not available"
            
            # Use synchronous Groq client for streaming - import here to avoid async issues
            try:
                from groq import Groq
            except ImportError:
                return "❌ Groq client not available"
            
            # Create sync client if not available
            if not hasattr(self, 'sync_groq_client') or not self.sync_groq_client:
                self.sync_groq_client = Groq(api_key=self.api_key)
            
            # Create streaming response
            stream = self.sync_groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                stream=True
            )
            
            # Use Rich live formatting if available
            if hasattr(self, 'rich_formatter') and self.rich_formatter.is_available():
                # Create generator function for streaming chunks
                def text_chunks():
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                
                # Use Rich live formatting
                full_response = self._stream_with_rich_formatting(text_chunks(), f"Groq ({self.model})")
            else:
                # Fallback to simple terminal output
                full_response = ""
                print("🤖 AI Helper: ", end="", flush=True)
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        print(content, end="", flush=True)
                
                print()  # New line after streaming
            
            # Save to conversation history (sync only - avoid any async operations)
            try:
                if hasattr(self.conversation_manager, 'add_message'):
                    self.conversation_manager.add_message(self.session_id, MessageRole.USER, prompt)
                    self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, full_response)
            except Exception as hist_error:
                # Ignore history errors in sync mode to avoid blocking
                print(f"\n[DEBUG] History save failed (non-critical): {hist_error}")
            
            return full_response
            
        except Exception as e:
            error_msg = f"❌ Error generating response: {str(e)}"
            print(error_msg)
            return error_msg

    def _stream_with_rich_formatting(self, text_chunks, provider_name="AI"):
        """Stream text with REAL-TIME Rich markdown formatting using Live Display"""
        from rich.live import Live
        from rich.markdown import Markdown
        from rich.text import Text
        
        if not hasattr(self, 'rich_formatter') or not self.rich_formatter.is_available():
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
                        # Always use manual formatting for better control during streaming
                        renderable = self._create_enhanced_streaming_renderable(accumulated_text)
                        live.update(renderable)
                        
                        # Small delay for smooth streaming effect
                        import time
                        time.sleep(0.05)
                        
                    except Exception as e:
                        # Fallback to plain text if formatting fails
                        live.update(Text(accumulated_text))
        
        # Show final enhanced view after streaming completes
        console.print("[bold cyan]═══════════════════════════[/bold cyan]")
        console.print("[dim]✅ Streaming complete[/dim]")
        
        return accumulated_text
    
    def _create_enhanced_streaming_renderable(self, text: str):
        """Create enhanced Rich renderable with proper code block and markdown handling for streaming"""
        from rich.text import Text
        from rich.syntax import Syntax
        from rich.console import Group
        
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
    
    def _format_streaming_line(self, line: str):
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
    
    def _apply_inline_formatting(self, text_obj, content: str):
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


def show_rich_help():
    """Show Rich-formatted help for Single Provider CLI"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        
        console = Console()
        
        # Main title
        console.print("\n")
        console.print(Panel.fit(
            "[bold blue]AI Chat - Simple & Fast Groq AI[/bold blue]\n"
            "[dim]Lightning-fast responses with Groq's powerful models[/dim]",
            border_style="blue"
        ))
        
        # Usage section
        console.print("\n[bold green]USAGE:[/bold green]")
        console.print("  [cyan]ai-chat[/cyan] [dim][options][/dim]")
        
        # Options table
        options_table = Table(
            show_header=True, 
            header_style="bold magenta",
            row_styles=["none", "dim"],  # Alternate row styling
            border_style="bright_blue",
            show_lines=True  # Add row separators for better readability
        )
        options_table.add_column("Option", style="cyan", width=20)
        options_table.add_column("Description", style="white")
        
        options_table.add_row("-h, --help", "Show this help message and exit")
        options_table.add_row("--session SESSION", "Session ID for conversation history")
        options_table.add_row("--model MODEL", "Select specific Groq model to use")
        options_table.add_row("--quick", "Skip startup, use existing configuration")
        options_table.add_row("--version, -v", "Show program's version number")
        
        console.print("\n[bold green]OPTIONS:[/bold green]")
        console.print(options_table)
        
        # Available models
        console.print("\n[bold green]AVAILABLE GROQ MODELS:[/bold green]")
        models_table = Table(
            show_header=True, 
            header_style="bold magenta",
            row_styles=["none", "dim"],  # Alternate row styling
            border_style="bright_green",
            show_lines=True  # Add row separators for better readability
        )
        models_table.add_column("#", style="yellow", width=3)
        models_table.add_column("Model", style="cyan", width=25)
        models_table.add_column("Description", style="white")
        
        for i, (key, desc) in enumerate(SingleProviderCLI.AVAILABLE_MODELS.items(), 1):
            models_table.add_row(str(i), key, desc)
        
        console.print(models_table)
        
        # Examples section
        console.print("\n[bold green]EXAMPLES:[/bold green]")
        examples = [
            ("ai-chat", "Start with interactive Groq setup"),
            ("ai-chat --quick", "Skip startup, use last configuration"),
            ("ai-chat --session work", "Start with named session 'work'"),
            ("ai-chat --model llama-3.1-8b-instant", "Start with specific model"),
        ]
        
        for cmd, desc in examples:
            console.print(f"  [cyan]{cmd}[/cyan]  [dim]# {desc}[/dim]")
        
        console.print("")
        
    except ImportError:
        # Fallback to plain text
        print("AI Chat - Simple & Fast Groq AI")
        print("\nUsage: ai-chat [options]")
        print("\nOptions:")
        print("  -h, --help            Show this help message")
        print("  --session SESSION     Session ID for conversation history") 
        print("  --model MODEL         Select specific Groq model")
        print("  --quick               Skip startup interface")
        print("  --version, -v         Show version")
        print("\nExamples:")
        print("  ai-chat                    # Interactive startup")
        print("  ai-chat --quick           # Skip startup")
        print("  ai-chat --model llama-3.1-8b-instant  # Specific model")


def main():
    """Main CLI entry point for single provider"""
    # Show Rich help if no arguments or help requested
    if '--help' in sys.argv or '-h' in sys.argv:
        show_rich_help()
        return
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Single Provider CLI (Groq Only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-chat                    # Start with Groq startup page
  ai-chat --quick           # Skip startup, use last config
  ai-chat --session work   # Start with named session
  ai-chat --model 2         # Start with specific Groq model
        """
    )
    
    parser.add_argument(
        "--session", "-s",
        default="default",
        help="Session ID for conversation history"
    )
    
    parser.add_argument(
        "--workspace", "-w",
        default=".",
        help="Workspace directory path"
    )
    
    parser.add_argument(
        "--model", "-m",
        choices=list(SingleProviderCLI.AVAILABLE_MODELS.keys()),
        help="Select Groq model to use"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip startup interface and use existing configuration"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent Single Provider CLI v2.0.1"
    )
    
    args = parser.parse_args()
    
    try:
        # Create CLI instance with single provider support
        cli = SingleProviderCLI(
            session_id=args.session, 
            model=args.model,
            skip_startup=args.quick
        )
        
        # Set workspace
        workspace_path = Path(args.workspace).resolve()
        if workspace_path.exists():
            cli.workspace_path = workspace_path
        else:
            print(f"⚠️ Workspace path doesn't exist: {workspace_path}")
            cli.workspace_path = Path.cwd()
        
        # Start the application - handle nested event loops properly
        try:
            # Check if there's already an event loop running
            try:
                # Try to get the running loop
                loop = asyncio.get_running_loop()
                print("⚠️ Event loop already running, using synchronous mode...")
                # Force completely synchronous mode
                cli.force_sync_mode = True
                cli.streaming_enabled = True  # Keep streaming enabled but use sync streaming
                # Start sync version without any asyncio
                cli.start_sync()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                print("ℹ️ Starting CLI with new event loop...")
                asyncio.run(cli.start())
        except Exception as e:
            print(f"❌ Error starting CLI: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
