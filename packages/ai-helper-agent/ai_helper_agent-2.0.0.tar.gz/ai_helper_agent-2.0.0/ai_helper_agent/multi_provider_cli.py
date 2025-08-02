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
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

# Rich imports for enhanced terminal experience
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

# Filter out warnings to keep CLI clean
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
warnings.filterwarnings("ignore", message=".*avconv.*")
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*")
warnings.filterwarnings("ignore", module="pydub")

# Multi-provider LLM imports
from langchain_groq import ChatGroq
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

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from .core import InteractiveAgent
from .config import config
from .security import security_manager
from .user_manager import user_manager
from .prompt_enhancer import AdvancedPromptEnhancer
from .system_config import SystemConfigurationManager
from .streaming import StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
from .multi_provider_startup import MultiProviderStartup

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


class MultiProviderAIHelperCLI:
    """Enhanced CLI with multi-provider LLM support and responsive design"""
    
    def __init__(self, session_id: str = "default", model: str = None, skip_startup: bool = False):
        self.session_id = f"multi_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.api_key: Optional[str] = None
        self.llm: Optional[Union[ChatGroq, ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI]] = None
        self.chain = None
        self.workspace_path = Path.cwd()
        self.model = model
        self.provider = None
        
        # Check if we're in help mode (avoid heavy initialization)
        self.help_mode = '--help' in sys.argv or '-h' in sys.argv
        
        # LangChain conversation setup
        self.conversation_chain = None
        self.trimmer = None
        
        # Initialize components (only if not in help mode)
        if not self.help_mode:
            # Enhanced prompt system
            self.prompt_enhancer: Optional[AdvancedPromptEnhancer] = None
            
            # System configuration manager
            self.system_config: Optional[SystemConfigurationManager] = None
            
            # Streaming handlers
            self.streaming_handler: Optional[StreamingResponseHandler] = None
            self.advanced_streaming: Optional[AdvancedStreamingHandler] = None
            self.enhanced_streaming: Optional[EnhancedStreamingHandler] = None
            
            # Multi-provider startup interface
            self.startup_interface: Optional[MultiProviderStartup] = None
            self.skip_startup = skip_startup
            self.enable_streaming: bool = True
            
            # Model configuration
            self.model_config = {}
        else:
            # Minimal initialization for help mode
            self.prompt_enhancer = None
            self.system_config = None
            self.streaming_handler = None
            self.advanced_streaming = None
            self.enhanced_streaming = None
            self.startup_interface = None
            self.skip_startup = True
            self.enable_streaming = False
            self.model_config = {}
        
        # Initialize managers
        self.conversation_manager = conversation_manager
        self.rich_formatter = rich_formatter
        
        # Configure Rich formatter
        if rich_formatter.is_available():
            rich_formatter.print_status("✅ Using Rich for enhanced display", "success")
        else:
            print("⚠️ Rich not available - using basic display")
        
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for session"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show AI Helper Agent splash screen with responsive logo"""
        if not self.skip_startup and self.startup_interface:
            self.startup_interface.display_responsive_logo()
        else:
            self.rich_formatter.show_banner(
                "AI HELPER AGENT v2.0",
                "Multi-Provider AI Assistant - Lightning-Fast Responses"
            )
    
    def setup_user_session(self) -> bool:
        """Setup user session with multi-provider support"""
        try:
            if not self.skip_startup:
                self.startup_interface = MultiProviderStartup()
            
            self.show_splash_screen()
            
            # Load existing configuration
            if not self.model:
                if not self.skip_startup:
                    model_id, api_key, llm = self.startup_interface.run_multi_provider_setup()
                    if llm:
                        self.model = model_id
                        self.api_key = api_key
                        self.llm = llm
                        self.provider = self._detect_provider(llm)
                    else:
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
    
    def _detect_provider(self, llm) -> str:
        """Detect provider from LLM instance"""
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
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your Groq API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://console.groq.com/keys", "info")
                self.api_key = getpass.getpass("Groq API Key: ")
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your OpenAI API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://platform.openai.com/api-keys", "info")
                self.api_key = getpass.getpass("OpenAI API Key: ")
        elif self.provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your Anthropic API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://console.anthropic.com/", "info")
                self.api_key = getpass.getpass("Anthropic API Key: ")
        elif self.provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                self.rich_formatter.print_status("🔑 Please enter your Google API key:", "info")
                self.rich_formatter.print_status("Get your key from: https://makersuite.google.com/app/apikey", "info")
                self.api_key = getpass.getpass("Google API Key: ")
        
        return True
    
    def create_llm_instance(self) -> bool:
        """Create LLM instance based on provider"""
        try:
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
        """Setup LLM and conversation chain with history"""
        try:
            if not self.llm:
                if not self.create_llm_instance():
                    return False
            
            # Test the connection
            if not self.test_api_key_and_model():
                return False
            
            # Setup message trimmer (keep last 8 messages + system)
            self.trimmer = trim_messages(
                max_tokens=4000,
                strategy="last",
                token_counter=self.llm,
                include_system=True,
                allow_partial=False,
                start_on="human"
            )
            
            # Create prompt template with history
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="messages"),
            ])
            
            # Create the chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Add trimming to the chain
            chain_with_trimming = (
                RunnablePassthrough.assign(
                    messages=lambda x: self.trimmer.invoke(x["messages"])
                )
                | chain
            )
            
            # Wrap with message history
            self.conversation_chain = RunnableWithMessageHistory(
                chain_with_trimming,
                self.get_session_history,
                input_messages_key="messages",
                history_messages_key="messages",
            )
            
            # Initialize streaming handlers with multi-provider support
            self.streaming_handler = StreamingResponseHandler(self.llm, self.conversation_chain)
            self.advanced_streaming = AdvancedStreamingHandler(self.llm, self.conversation_chain)
            self.enhanced_streaming = EnhancedStreamingHandler(self.llm, self.conversation_chain)
            
            self.rich_formatter.print_status(f"✅ AI Helper Agent initialized with {self.provider.upper()}!", "success")
            self.rich_formatter.print_status("🔄 Enhanced streaming mode enabled for real-time responses", "info")
            self.rich_formatter.print_status(f"🚀 Using model: {self.model}", "info")
            
        except Exception as e:
            self.rich_formatter.print_status(f"❌ Failed to initialize AI Helper: {e}", "error")
            return False
        
        return True
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI assistant"""
        return f"""You are an AI Helper Agent, a sophisticated coding assistant powered by {self.provider.upper()}.

CAPABILITIES:
- Advanced code generation and debugging
- Real-time analysis and explanations  
- Multi-language programming support
- Architecture design and best practices
- Problem-solving and optimization

PERSONALITY:
- Professional but friendly
- Detailed explanations when helpful
- Concise responses when appropriate
- Always aim to be helpful and accurate

CURRENT SETUP:
- Provider: {self.provider.upper()}
- Model: {self.model}
- Streaming: {"Enabled" if self.enable_streaming else "Disabled"}

Please provide helpful, accurate, and well-structured responses to assist with coding and development tasks."""
    
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
            # Create streaming chunks generator
            def stream_chunks():
                chunks = []
                for chunk in self.conversation_chain.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"session_id": self.session_id}}
                ):
                    if chunk:
                        chunks.append(chunk)
                return chunks
            
            # Stream with Rich formatting
            response = self.rich_formatter.stream_with_rich_formatting(
                stream_chunks(), 
                f"{self.provider.upper()} ({self.model})"
            )
            
            # Save to conversation history
            self.conversation_manager.add_message(self.session_id, MessageRole.ASSISTANT, response)
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Streaming error: {str(e)}"
            self.rich_formatter.print_status(error_msg, "error")
            return error_msg
    
    def show_conversation_history(self, limit: int = 10):
        """Show recent conversation history with Rich formatting"""
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
            
            if user_input.lower() == 'info':
                return self._show_provider_info()
            
            # Regular AI response
            return await self.generate_response(user_input)
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"
    
    def _get_help_message(self) -> str:
        """Get help message with available commands"""
        return f"""
🤖 AI Helper Agent - Multi-Provider CLI

📝 BASIC COMMANDS:
• help, ? - Show this help message
• exit, quit, goodbye - Exit the application
• clear - Clear conversation history
• history - View recent conversation history
• info - Show current provider information

🔧 PROVIDER COMMANDS:
• switch <provider> - Switch to different AI provider
• Available providers: groq, openai, anthropic, google

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
            except Exception as e:
                self.rich_formatter.print_status(f"❌ Error: {e}", "error")


# Backwards compatibility alias
AIHelperCLI = MultiProviderAIHelperCLI


async def main():
    """Main entry point for multi-provider CLI"""
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


if __name__ == "__main__":
    asyncio.run(main())
