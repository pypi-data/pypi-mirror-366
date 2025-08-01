"""
AI Helper Agent CLI Module - Multi-Provider Support
Interactive command-line interface with conversation history and message trimming
Enhanced with multi-provider LLM support and responsive design
"""

import os
import sys
import asyncio
import getpass
from typing import Dict, Any, Optional
from pathlib import Path

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

try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    ChatOllama = None

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

# Import file handler
try:
    from .file_handler import file_handler
    FILE_HANDLER_AVAILABLE = True
except ImportError:
    FILE_HANDLER_AVAILABLE = False

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}


class MultiProviderCLI:
    """Enhanced CLI with multi-provider LLM support and responsive design"""
    
    def __init__(self, session_id: str = "default", model: str = None, skip_startup: bool = False):
        self.session_id = session_id
        self.model = model or "llama-3.1-8b-instant"
        self.api_key = None
        self.llm = None
        self.chain = None
        self.skip_startup = skip_startup
        self.workspace_path = Path(".")
        
        # Initialize components
        self.user_manager = user_manager
        self.security_manager = security_manager
        self.system_config = SystemConfigurationManager()
        self.prompt_enhancer = AdvancedPromptEnhancer(workspace_path=self.workspace_path)
        
        # Streaming components - Initialize as None first, will be set up after LLM is ready
        self.streaming_handler: Optional[StreamingResponseHandler] = None
        self.advanced_streaming: Optional[AdvancedStreamingHandler] = None
        self.enhanced_streaming: Optional[EnhancedStreamingHandler] = None
        self.streaming_enabled = True
        
        # Multi-provider startup interface
        if not self.skip_startup:
            self.startup_interface = MultiProviderStartup()
        
        # File processing capabilities
        self.current_files: Dict[str, Any] = {}
        self.file_context = ""
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show enhanced splash screen with responsive logo"""
        if hasattr(self, 'startup_interface'):
            self.startup_interface.display_responsive_logo()
        else:
            # Fallback simple logo
            print("🤖 AI HELPER AGENT v2.0 🤖")
            print("YOUR AUTONOMOUS CODING ASSISTANT")
    
    def setup_user_session(self) -> bool:
        """Setup user session with enhanced startup"""
        if not self.skip_startup:
            # Use the enhanced startup interface
            self.show_splash_screen()
            
            # Run full startup sequence
            model_id, api_key, llm_instance = self.startup_interface.run_startup_sequence()
            
            if model_id and llm_instance:
                self.model = model_id
                self.api_key = api_key
                self.llm = llm_instance
                return True
            else:
                print("❌ Setup failed. Please try again.")
                return False
        else:
            # Quick setup for programmatic use
            self.show_splash_screen()
            return self.setup_llm_and_chain()
    
    def setup_llm_and_chain(self):
        """Setup LLM and conversation chain with multi-provider support"""
        if self.llm:
            # LLM already set up by startup interface
            pass
        else:
            # Fallback to Groq
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                print("❌ No API key found. Please run setup.")
                return False
            
            self.llm = ChatGroq(
                model=self.model,
                temperature=0.1,
                api_key=self.api_key
            )
        
        try:
            # Create the conversation chain with history (simplified approach)
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])

            # Create conversation chain with history
            self.chain_with_history = RunnableWithMessageHistory(
                prompt | self.llm | StrOutputParser(),
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="history",
            )
            
            # Initialize streaming handlers now that LLM and conversation chain are ready
            self.streaming_handler = StreamingResponseHandler(self.llm, self.chain_with_history)
            self.advanced_streaming = AdvancedStreamingHandler(self.llm, self.chain_with_history)
            self.enhanced_streaming = EnhancedStreamingHandler(self.llm, self.chain_with_history)
            
        except Exception as e:
            print(f"❌ Error setting up LLM chain: {e}")
            return False
        
        return True
    
    def get_model_provider(self) -> str:
        """Determine the provider for the current model"""
        # Groq models
        groq_models = [
            "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it",
            "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "llama3-8b-8192", "llama3-70b-8192"
        ]
        
        # OpenAI models
        openai_models = [
            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4.5",
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo",
            "o1-preview", "o1-mini", "o3-pro", "gpt-4", "gpt-4-1106-preview"
        ]
        
        # Anthropic models
        anthropic_models = [
            "claude-3-5-sonnet-20240620", "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
            "claude-2.1", "claude-2.0"
        ]
        
        # Google models
        google_models = [
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash",
            "gemini-1.5-pro", "gemini-pro", "models/text-bison-001"
        ]
        
        # Common Ollama models (user can have any model)
        common_ollama_models = [
            "llama2", "llama3", "codellama", "mistral", "phi", "gemma",
            "qwen", "dolphin", "orca", "vicuna", "alpaca", "wizardcoder"
        ]
        
        # Check model against each provider
        if self.model in groq_models:
            return "groq"
        elif self.model in openai_models:
            return "openai"
        elif self.model in anthropic_models:
            return "anthropic"
        elif self.model in google_models:
            return "google"
        elif self.model in common_ollama_models:
            return "ollama"
        else:
            # For custom models, try to detect by format/pattern
            # Ollama models are typically simple names without special characters
            if (":" in self.model or "/" in self.model or 
                self.model.startswith("gpt") or self.model.startswith("claude") or 
                self.model.startswith("gemini") or "llama" in self.model.lower()):
                # Try to guess based on name patterns
                if self.model.startswith("gpt") or "openai" in self.model.lower():
                    return "openai"
                elif self.model.startswith("claude") or "anthropic" in self.model.lower():
                    return "anthropic"
                elif self.model.startswith("gemini") or "google" in self.model.lower():
                    return "google"
                elif ("llama" in self.model.lower() or "mistral" in self.model.lower() or 
                      "phi" in self.model.lower() or "qwen" in self.model.lower()):
                    # Could be either Groq or Ollama, prefer Ollama for custom names
                    return "ollama"
                else:
                    return "groq"  # Default fallback for Groq (most permissive)
            else:
                # Simple name without special chars, likely Ollama
                return "ollama"
    
    def _format_history(self, history: BaseChatMessageHistory) -> list:
        """Format history for the prompt"""
        messages = history.messages
        
        # Trim messages if too many
        if len(messages) > 20:
            trimmed = trim_messages(
                messages,
                max_tokens=4000,
                strategy="last",
                token_counter=len,
                include_system=False,
            )
            return trimmed
        
        return messages
    
    def _get_system_prompt(self) -> str:
        """Get the enhanced system prompt for the AI assistant"""
        if self.prompt_enhancer:
            return self.prompt_enhancer.get_enhanced_system_prompt()
        
        # Fallback to basic prompt if enhancer not available
        provider = self.get_model_provider()
        return f"""You are an expert AI programming assistant with advanced code generation capabilities similar to GitHub Codex and Google CLI tools. You specialize in:

🔧 CODE GENERATION & COMPLETION
- Generate complete code from natural language descriptions
- Provide intelligent code completion and suggestions
- Support multiple programming languages (Python, JavaScript, TypeScript, Go, Rust, Java, C++, etc.)
- Generate functions, classes, modules, and entire applications
- Create boilerplate code and project structures

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

📊 CODE ANALYSIS & REVIEW
- Analyze code quality, complexity, and maintainability
- Identify security vulnerabilities and suggest fixes
- Review architecture and design patterns
- Suggest improvements and best practices

Current workspace: {self.workspace_path}
Current model: {self.model} ({provider.upper()})
Provider: {provider.upper()}

I'm ready to help you with any programming task, from simple scripts to complex applications!"""
    
    async def _get_ai_response(self, prompt: str, use_streaming: bool = True) -> str:
        """Utility method to get AI response with streaming (replaces ainvoke)"""
        try:
            config = {"configurable": {"session_id": self.session_id}}
            
            if use_streaming and self.streaming_enabled and self.streaming_handler:
                try:
                    # Use streaming for real-time response
                    response = await self.streaming_handler.stream_generate(
                        prompt, config
                    )
                    if response and response.strip():
                        return response
                except Exception as stream_error:
                    print(f"\n⚠️ Streaming failed: {stream_error}")
                    print("🔄 Falling back to regular response...")
            
            # Fallback to regular invoke
            if self.chain_with_history:
                response = await self.chain_with_history.ainvoke(
                    {"input": prompt}, config=config
                )
                return response if response else "❌ No response generated"
            else:
                return "❌ Conversation chain not initialized"
                
        except Exception as e:
            print(f"\n❌ Error generating response: {e}")
            return f"❌ Error generating response: {e}"
    
    async def handle_command(self, user_input: str) -> str:
        """Handle user commands and return AI response"""
        try:
            # Check for file commands first
            if FILE_HANDLER_AVAILABLE:
                file_response = self._process_file_command(user_input)
                if file_response:
                    return file_response
            
            # Check for special commands
            if user_input.lower().startswith("streaming "):
                return await self._handle_streaming_command(user_input)
            elif user_input.lower() in ["exit", "quit", "goodbye"]:
                return "👋 Goodbye! Thank you for using AI Helper Agent."
            elif user_input.lower() in ["help", "?"]:
                return self._get_help_message()
            elif user_input.lower().startswith("change_name "):
                return await self._handle_name_change(user_input)
            elif user_input.lower() == "clear":
                conversation_store[self.session_id] = ChatMessageHistory()
                return "✅ Conversation history cleared."
            elif user_input.lower() == "config":
                return self._show_configuration()
            
            # Enhanced prompt processing
            enhanced_prompt = user_input
            if self.prompt_enhancer:
                enhanced_prompt = self.prompt_enhancer.enhance_user_prompt(user_input)
            
            # Add file context if available
            if self.file_context:
                enhanced_prompt = f"[File Context: {self.file_context}]\n\nUser: {enhanced_prompt}"
            
            # Get AI response with streaming
            response = await self._get_ai_response(enhanced_prompt, use_streaming=True)
            return response
            
        except Exception as e:
            return f"❌ Error processing command: {e}"
    
    def _process_file_command(self, user_input: str) -> Optional[str]:
        """Process file-related commands"""
        if not FILE_HANDLER_AVAILABLE:
            return None
            
        input_lower = user_input.lower().strip()
        
        # Read file command
        if input_lower.startswith('read '):
            file_path = user_input[5:].strip()
            return self._read_file(file_path)
            
        # Analyze file command  
        elif input_lower.startswith('analyze '):
            file_path = user_input[8:].strip()
            return self._analyze_file(file_path)
            
        # List files command
        elif input_lower in ['files', 'list files', 'show files']:
            return self._list_files()
            
        # File help command
        elif input_lower in ['file help', 'files help']:
            return self._show_file_help()
            
        return None
    
    def _read_file(self, file_path: str) -> str:
        """Read and process a file"""
        try:
            # Check if file exists and is accessible
            if not os.path.exists(file_path):
                return f"❌ File not found: {file_path}"
                
            if not self.security_manager.is_file_accessible(file_path):
                return f"❌ File access denied: {file_path}"
                
            # Use file handler to read content
            result = file_handler.read_file_content(file_path)
            
            if "error" in result:
                return f"❌ Error reading file: {result['error']}"
                
            # Store file info for context
            self.current_files[file_path] = result
            
            # Update file context
            file_info = result.get('file_info', {})
            content = result.get('content', '')
            
            self.file_context = f"File: {file_path} ({file_info.get('file_type', 'unknown')} - {file_info.get('size_human', 'unknown size')})"
            
            # Return formatted response
            response = f"📁 **File Read Successfully: {file_path}**\n\n"
            response += f"**File Type:** {file_info.get('file_type', 'unknown')}\n"
            response += f"**Size:** {file_info.get('size_human', 'unknown')}\n"
            
            if 'lines' in result:
                response += f"**Lines:** {result['lines']}\n"
            if 'words' in result:
                response += f"**Words:** {result['words']}\n"
                
            response += f"\n**Content Preview:**\n```{file_info.get('file_type', 'text')}\n{content[:1500]}{'...' if len(content) > 1500 else ''}\n```\n"
            response += "\n✅ File content is now available in our conversation context. You can ask questions about it!"
            
            return response
            
        except Exception as e:
            return f"❌ Error processing file: {str(e)}"
    
    def _analyze_file(self, file_path: str) -> str:
        """Perform analysis of a file"""
        try:
            # First read the file
            read_result = self._read_file(file_path)
            if read_result.startswith("❌"):
                return read_result
                
            # Get file data for analysis
            file_data = self.current_files.get(file_path)
            if not file_data:
                return "❌ File not found in current context"
                
            file_info = file_data.get('file_info', {})
            content = file_data.get('content', '')
            
            analysis = f"🔍 **File Analysis: {file_path}**\n\n"
            analysis += f"**File Statistics:**\n"
            analysis += f"- Type: {file_info.get('file_type', 'unknown')}\n"
            analysis += f"- Size: {file_info.get('size_human', 'unknown')}\n"
            
            if 'lines' in file_data:
                analysis += f"- Lines: {file_data['lines']}\n"
            if 'words' in file_data:
                analysis += f"- Words: {file_data['words']}\n"
                
            analysis += "\n✅ File analyzed and ready for questions!"
            return analysis
            
        except Exception as e:
            return f"❌ Error analyzing file: {str(e)}"
    
    def _list_files(self) -> str:
        """List supported files in current directory"""
        try:
            suggestions = file_handler.get_file_suggestions(str(self.workspace_path))
            
            if not suggestions:
                return "📁 No supported files found in current directory"
                
            response = "📁 **Supported Files in Current Directory:**\n\n"
            
            # Show first 20 files
            for file_info in suggestions[:20]:
                response += f"- {file_info['relative_path']} ({file_info['type']}, {file_info['size']})\n"
                
            if len(suggestions) > 20:
                response += f"... and {len(suggestions) - 20} more files\n"
                
            response += "\n💡 Use 'read <filepath>' to read any file!"
            return response
            
        except Exception as e:
            return f"❌ Error listing files: {str(e)}"
    
    def _show_file_help(self) -> str:
        """Show file command help"""
        return """📁 **File Processing Commands:**

**Basic Commands:**
- `read <filepath>` - Read and display file content
- `analyze <filepath>` - Analyze file with statistics
- `files` - List all supported files in current directory
- `file help` - Show this help message

**Supported File Types:**
- **Code:** .py, .js, .ts, .html, .css, .java, .cpp, .c, .cs, .php, .rb, .go, .rs, .sql
- **Text:** .txt, .md, .rst, .log
- **Data:** .json, .yaml, .yml, .csv, .xml
- **Config:** .ini, .cfg, .env, .conf, .toml

**Examples:**
- `read myfile.py` - Read Python file
- `analyze data.csv` - Analyze CSV data file
- `files` - Show all files in current directory

💡 **Tip:** After reading a file, you can ask questions about its content!"""
    
    async def _handle_streaming_command(self, command: str) -> str:
        """Handle streaming control commands"""
        parts = command.split()
        if len(parts) < 2:
            return "Usage: streaming [on|off|test]"
        
        action = parts[1].lower()
        
        if action == "on":
            self.streaming_enabled = True
            return "✅ Streaming enabled"
        elif action == "off":
            self.streaming_enabled = False
            return "✅ Streaming disabled"
        elif action == "test":
            test_prompt = "Say hello and confirm streaming is working"
            response = await self.streaming_handler.stream_generate(
                self.llm, test_prompt, session_id=self.session_id
            )
            return f"🌊 Streaming test: {response}"
        else:
            return "❌ Invalid streaming command. Use: on, off, or test"
    
    async def _handle_name_change(self, command: str) -> str:
        """Handle username change command"""
        try:
            parts = command.split('"')
            if len(parts) >= 2:
                new_name = parts[1].strip()
            else:
                parts = command.split()
                if len(parts) >= 2:
                    new_name = parts[1].strip()
                else:
                    return "❌ Usage: change_name \"New Name\""
            
            # Update username
            old_name = self.user_manager.get_current_username()
            self.user_manager.set_username(new_name)
            
            return f"✅ Username changed from '{old_name}' to '{new_name}'"
        except Exception as e:
            return f"❌ Error changing username: {e}"
    
    def _get_help_message(self) -> str:
        """Get help message with available commands"""
        provider = self.get_model_provider()
        
        file_commands = ""
        if FILE_HANDLER_AVAILABLE:
            file_commands = """
📁 FILE OPERATIONS:
• read <file> - Read and analyze any supported file
• analyze <file> - Detailed file analysis with statistics
• files - List supported files in directory
• file help - Show detailed file processing help
"""
        
        return f"""
🤖 AI Helper Agent - Available Commands:

📝 BASIC COMMANDS:
• help, ? - Show this help message
• exit, quit, goodbye - Exit the application
• clear - Clear conversation history
• config - Show current configuration
{file_commands}
🔧 ADVANCED COMMANDS:
• change_name "New Name" - Change your username
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
• Provider: {provider.upper()}
• Session: {self.session_id}
• Workspace: {self.workspace_path}
• Streaming: {'✅ Enabled' if self.streaming_enabled else '❌ Disabled'}
• File Processing: {'✅ Enabled' if FILE_HANDLER_AVAILABLE else '❌ Disabled'}

Just type your question or request, and I'll help you with code generation, debugging, analysis, and more!
"""
    
    def _show_configuration(self) -> str:
        """Show current configuration"""
        provider = self.get_model_provider()
        
        config_info = f"""
⚙️ AI Helper Agent Configuration:

🤖 MODEL SETTINGS:
• Current Model: {self.model}
• Provider: {provider.upper()}
• API Key: {'✅ Set' if self.api_key else '❌ Not Set'}

🔧 SESSION SETTINGS:
• Session ID: {self.session_id}
• Workspace: {self.workspace_path}
• Streaming: {'✅ Enabled' if self.streaming_enabled else '❌ Disabled'}

💬 CONVERSATION:
• Messages in History: {len(conversation_store.get(self.session_id, ChatMessageHistory()).messages)}

🌐 AVAILABLE PROVIDERS:
• GROQ: {'✅' if os.getenv('GROQ_API_KEY') else '❌'} API Key
• OPENAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'} API Key  
• ANTHROPIC: {'✅' if os.getenv('ANTHROPIC_API_KEY') else '❌'} API Key
• GOOGLE: {'✅' if os.getenv('GOOGLE_API_KEY') else '❌'} API Key
• OLLAMA: {'✅' if os.getenv('OLLAMA_HOST') else '❌'} Host Set
"""
        return config_info
    
    async def start(self):
        """Start the CLI application"""
        print("\n🚀 Starting AI Helper Agent...")
        
        # Setup user session
        if not self.setup_user_session():
            print("❌ Failed to setup user session. Exiting.")
            return
        
        # Setup LLM and chain
        if not self.setup_llm_and_chain():
            print("❌ Failed to setup LLM. Exiting.")
            return
        
        print(f"✅ AI Helper Agent ready! Using {self.model}")
        print("💡 Type 'help' for available commands, or just start chatting!")
        print("🔄 Streaming responses enabled for real-time interaction")
        print()
        
        # Main interaction loop
        while True:
            try:
                user_input = input(f"👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Show thinking indicator before processing (includes AI indicator)
                self._show_thinking_indicator("Analyzing your request...")
                
                # Get AI response - streaming will display content directly
                response = await self.handle_command(user_input)
                
                # Only print response if streaming didn't handle it or streaming is disabled
                if response and response.strip() and not self.streaming_enabled:
                    print(f"🤖 {response}")
                elif self.streaming_enabled:
                    # Response was already displayed via streaming with AI indicator
                    pass
                    
                print()  # Add spacing
                
                # Exit conditions
                if user_input.lower() in ["exit", "quit", "goodbye"]:
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _show_thinking_indicator(self, message: str = "Thinking..."):
        """Show animated thinking indicator"""
        import time
        indicators = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        # Show thinking for a brief moment
        for i in range(8):  # Show for about 0.8 seconds
            print(f"\r🤖 {indicators[i % len(indicators)]} {message}", end="", flush=True)
            time.sleep(0.1)
            
        # Clear the thinking line and show AI response indicator
        print(f"\r🤖 ", end="", flush=True)


# Backward compatibility - maintain the original AIHelperCLI class
class AIHelperCLI(MultiProviderCLI):
    """Backward compatible CLI class"""
    pass


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Your Autonomous Coding Assistant with Multi-Provider Support"
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
        help="Select model to use (will show selection during startup)"
    )
    
    parser.add_argument(
        "--skip-startup",
        action="store_true",
        help="Skip interactive startup sequence"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent CLI v2.0 - Multi-Provider Edition"
    )
    
    args = parser.parse_args()
    
    try:
        # Create CLI instance with multi-provider support
        cli = MultiProviderCLI(
            session_id=args.session, 
            model=args.model,
            skip_startup=args.skip_startup
        )
        
        # Set workspace
        workspace_path = Path(args.workspace).resolve()
        if workspace_path.exists():
            cli.workspace_path = workspace_path
        else:
            print(f"⚠️  Workspace directory not found: {args.workspace}")
            print(f"Using current directory: {cli.workspace_path}")
        
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
