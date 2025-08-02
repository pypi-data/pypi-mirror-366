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

from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Groq Async client for streaming
try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    AsyncGroq = None

from .core import InteractiveAgent
from .config import config
from .security import security_manager
from .user_manager import user_manager
from .prompt_enhancer import AdvancedPromptEnhancer
from .system_config import SystemConfigurationManager
from .streaming import StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler

# Import our managers
try:
    from .api_key_manager import api_key_manager
    from .conversation_manager import conversation_manager, MessageRole
    from .rich_formatting import rich_formatter
except ImportError:
    # Fallback for direct execution
    from api_key_manager import api_key_manager
    from conversation_manager import conversation_manager, MessageRole
    from rich_formatting import rich_formatter

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}


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
        self.api_key = None
        self.llm = None
        self.async_groq_client = None
        self.chain = None
        self.skip_startup = skip_startup
        self.workspace_path = Path(".")
        
        # Check if we're in help mode (avoid heavy initialization)
        self.help_mode = '--help' in sys.argv or '-h' in sys.argv
        
        # Initialize components (only if not in help mode)
        if not self.help_mode:
            self.user_manager = user_manager
            self.security_manager = security_manager
            self.system_config = SystemConfigurationManager()
            self.prompt_enhancer = AdvancedPromptEnhancer(workspace_path=self.workspace_path)
            self.conversation_manager = conversation_manager
        
        self.rich_formatter = rich_formatter
        
        # Streaming components - Initialize as None first, will be set up after LLM is ready
        self.streaming_handler: Optional[StreamingResponseHandler] = None
        self.advanced_streaming: Optional[AdvancedStreamingHandler] = None
        self.enhanced_streaming: Optional[EnhancedStreamingHandler] = None
        self.streaming_enabled = True
        
        # Configure Rich formatter (only when not in help mode)
        if not self.help_mode and rich_formatter.is_available():
            rich_formatter.print_status("✅ Using Rich for enhanced display", "success")
        elif not self.help_mode:
            print("⚠️ Rich not available - using basic display")
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show Groq-only splash screen"""
        self.rich_formatter.show_banner(
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
            
            # Setup Groq-only interface (no provider selection)
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
            self.show_splash_screen()
            return self.setup_llm_and_chain()
    
    def setup_groq_only_interface(self):
        """Setup Groq-only interface without provider selection"""
        # Get API key from manager first
        api_key = api_key_manager.get_api_key('groq')
        
        if not api_key:
            self.rich_formatter.print_status("🔑 Enter your Groq API key:", "info")
            api_key = input().strip()
            
            if not api_key:
                self.rich_formatter.print_status("❌ API key required for Groq", "error")
                return None, None, None
            
            # Offer to save the key
            save_key = input("💾 Save this API key for future use? (y/N): ").strip().lower()
            
            if save_key == 'y':
                if api_key_manager.set_api_key('groq', api_key):
                    self.rich_formatter.print_status("✅ API key saved securely", "success")
        
        # Show Groq model selection
        groq_models = [
            ("llama-3.3-70b-versatile", "Llama 3.3 70B - Latest Meta model"),
            ("llama-3.1-8b-instant", "Llama 3.1 8B - Ultra fast responses"),
            ("gemma2-9b-it", "Gemma 2 9B - Google's balanced model"),
            ("llama-3.1-70b-versatile", "Llama 3.1 70B - Large reasoning model")
        ]
        
        # Show model selection table
        headers = ["ID", "Model", "Description"]
        rows = []
        for i, (model_id, description) in enumerate(groq_models, 1):
            rows.append([str(i), model_id, description])
        
        self.rich_formatter.show_table("🚀 Groq Models", headers, rows, ["cyan", "green", "white"])
        
        # Model selection
        try:
            choice = input("🤖 Select model (1): ").strip() or "1"
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(groq_models):
                selected_model_id, description = groq_models[choice_idx]
                self.rich_formatter.print_status(f"✅ Selected: {selected_model_id}", "success")
                
                # Create LLM instance and async client
                llm_instance = ChatGroq(
                    temperature=0.1,
                    model_name=selected_model_id,
                    groq_api_key=api_key,
                    streaming=True
                )
                
                # Create async client for streaming
                if GROQ_AVAILABLE:
                    self.async_groq_client = AsyncGroq(api_key=api_key)
                
                return selected_model_id, api_key, llm_instance
            else:
                self.rich_formatter.print_status("❌ Invalid selection", "error")
                return None, None, None
                
        except (ValueError, KeyboardInterrupt):
            self.rich_formatter.print_status("❌ Invalid input", "error")
            return None, None, None
    
    def setup_llm_and_chain(self):
        """Setup LLM and conversation chain with Groq only"""
        if self.llm:
            # LLM already set up by startup interface
            pass
        else:
            # Fallback to environment
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                print("❌ GROQ_API_KEY not found in environment variables")
                return False
            
            self.llm = ChatGroq(
                model=self.model,
                temperature=0.1,
                api_key=self.api_key
            )
        
        try:
            # Create the conversation chain with history
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])

            # Create conversation chain with history
            self.conversation_chain = RunnableWithMessageHistory(
                prompt | self.llm | StrOutputParser(),
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
        return f"""You are an expert AI programming assistant powered by Groq's lightning-fast inference. You specialize in:

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

Current workspace: {str(self.workspace_path)}
Current model: {self.model or 'Unknown'} (GROQ)
Provider: GROQ (Lightning Fast)

I'm ready to help you with any programming task with Groq's ultra-fast responses!"""
    
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
                    conversation_store[self.session_id] = ChatMessageHistory()
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
            
            # Regular AI response
            if self.streaming_enabled:
                return await self._get_ai_response_streaming(user_input)
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
            messages = self.conversation_manager.get_conversation_history(self.session_id, limit)
            
            if not messages:
                self.rich_formatter.print_status("No conversation history found", "info")
                return
            
            headers = ["Time", "Role", "Message"]
            rows = []
            
            for msg in messages:
                role_icon = "👤" if msg['role'] == MessageRole.USER.value else "🤖"
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M:%S")
                
                # Truncate long messages for history display
                content = msg['content']
                if len(content) > 100:
                    content = content[:100] + "..."
                
                rows.append([timestamp, f"{role_icon} {msg['role'].title()}", content])
            
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
        """Get help message with available commands"""
        return f"""
🤖 AI Helper Agent - Single Provider CLI (Groq Only)

📝 BASIC COMMANDS:
• help, ? - Show this help message
• exit, quit, goodbye - Exit the application
• clear - Clear conversation history
• history - View recent conversation history
• config - Show current configuration

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
• Messages in History: {len(conversation_store.get(self.session_id, ChatMessageHistory()).messages)}

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
            except Exception as e:
                self.rich_formatter.print_status(f"❌ Error: {e}", "error")


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
        options_table = Table(show_header=True, header_style="bold magenta")
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
        models_table = Table(show_header=True, header_style="bold magenta")
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
        version="AI Helper Agent Single Provider CLI v1.0"
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
        
        # Start the application
        asyncio.run(cli.start())
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
