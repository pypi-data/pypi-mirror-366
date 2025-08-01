"""
AI Helper Agent - Single Provider CLI with Internet Access (Groq Only)
Internet-enabled CLI that automatically searches the web when needed
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path

from langchain_groq import ChatGroq
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
from .startup import MultiProviderStartup
from .internet_access import InternetAccessManager, create_internet_access_manager, PermissionLevel, SearchProvider

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}


class InternetSingleProviderCLI:
    """Single Provider CLI with Internet Access - Groq Only with Web Search"""
    
    # Available Groq models only
    AVAILABLE_MODELS = {
        "llama-3.3-70b-versatile": "Llama 3.3 70B (Meta - General purpose, Large)",
        "llama-3.1-8b-instant": "Llama 3.1 8B (Meta - Instant response, Fast)",
        "gemma2-9b-it": "Gemma 2 9B (Google - Chat fine-tuned, Balanced)",
        "llama-3.1-70b-versatile": "Llama 3.1 70B (Meta - Complex reasoning)",
        "llama3-8b-8192": "Llama 3 8B (Legacy - Fast, Good for coding)",
        "llama3-70b-8192": "Llama 3 70B (Legacy - Better reasoning)"
    }
    
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
        
        # Internet access manager - Initialize after LLM is ready
        self.internet_manager: Optional[InternetAccessManager] = None
        
        # Streaming enabled for simple streaming approach
        self.streaming_enabled = True
        
        # Single provider startup interface
        if not self.skip_startup:
            self.startup_interface = MultiProviderStartup()
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show enhanced splash screen with internet access logo"""
        if hasattr(self, 'startup_interface'):
            self.startup_interface.display_responsive_logo()
            print("\n🌐 INTERNET ACCESS ENABLED")
            print("🔍 AI will automatically search the web when needed")
        else:
            # Fallback simple logo
            print("⚡ AI HELPER AGENT - INTERNET ENABLED ⚡")
            print("🌐 GROQ POWERED + WEB SEARCH - SMART & FAST")
    
    def setup_user_session(self) -> bool:
        """Setup user session with single provider startup and internet access"""
        if not self.skip_startup:
            # Use the single provider startup interface
            self.show_splash_screen()
            
            # Run startup sequence (will only show Groq)
            model_id, api_key, llm_instance = self.startup_interface.run_startup_sequence()
            
            if model_id and llm_instance:
                self.model = model_id
                self.api_key = api_key
                self.llm = llm_instance
                
                # Setup internet access after LLM is ready
                self.setup_internet_access()
                return True
            else:
                print("❌ Failed to setup user session")
                return False
        else:
            # Quick setup for programmatic use
            self.show_splash_screen()
            success = self.setup_llm_and_chain()
            if success:
                self.setup_internet_access()
            return success
    
    def setup_internet_access(self):
        """Setup internet access manager"""
        try:
            # Create user directory for internet access data
            user_dir = Path.home() / ".ai_helper_agent" / "internet_data"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Create internet access manager with the LLM for query analysis
            self.internet_manager = create_internet_access_manager(user_dir, self.llm)
            
            # Configure default permission level to smart analysis
            self.internet_manager.configure_permissions(level="smart")
            
            print("🌐 Internet access configured successfully")
            print("📊 Permission level: Smart Analysis (AI decides when to search)")
            
        except Exception as e:
            print(f"⚠️ Warning: Internet access setup failed: {e}")
            print("📍 Continuing without internet access...")
            self.internet_manager = None
    
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
            
            print("✅ LLM and conversation chain initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup LLM chain: {e}")
            return False
    
    def _get_system_prompt(self) -> str:
        """Get the enhanced system prompt for the AI assistant with internet access"""
        base_prompt = """You are an expert AI programming assistant with internet access, powered by Groq's lightning-fast inference. You specialize in:

🔧 CODE GENERATION & COMPLETION
- Generate complete code from natural language descriptions
- Provide intelligent code completion and suggestions
- Support multiple programming languages (Python, JavaScript, TypeScript, Go, Rust, Java, C++, etc.)
- Generate functions, classes, modules, and entire applications
- Create boilerplate code and project structures

🌐 INTERNET ACCESS & RESEARCH
- Access real-time information from the web when needed
- Search for latest documentation, tutorials, and examples
- Get current information about libraries, frameworks, and tools
- Find solutions to specific error messages and issues
- Research best practices and recent developments

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
- Search for solutions to specific errors online when needed

🔍 SMART WEB SEARCH INTEGRATION
- I automatically determine when internet search would be helpful
- I search for current information, documentation, and solutions
- I provide up-to-date answers with web-sourced information
- I can find examples, tutorials, and best practices from the web

Current workspace: {self.workspace_path}
Current model: {self.model} (GROQ)
Provider: GROQ (Lightning Fast) + Internet Access

IMPORTANT: When you need current information, documentation, API changes, or solutions to specific problems, I will automatically search the internet to provide you with the most up-to-date and accurate information."""

        if self.prompt_enhancer:
            enhanced_prompt = self.prompt_enhancer.get_enhanced_system_prompt()
            # Combine the enhanced prompt with internet access information
            return f"{enhanced_prompt}\n\n{base_prompt}"
        
        return base_prompt.format(workspace_path=self.workspace_path, model=self.model)
    
    def _search_and_enhance_response(self, user_input: str, context: str = "") -> Optional[str]:
        """Search the internet and return enhanced context if needed"""
        if not self.internet_manager:
            return None
        
        try:
            # Let the AI decide if search is needed and perform search
            search_results = self.internet_manager.search_with_permission(
                user_input,
                context,
                "user",
                self.session_id
            )
            
            if search_results and search_results.get('results'):
                # Format search results for the AI
                search_context = "🌐 **INTERNET SEARCH RESULTS:**\n\n"
                for i, result in enumerate(search_results['results'][:3]):  # Top 3 results
                    search_context += f"**{i+1}. {result.title}**\n"
                    search_context += f"URL: {result.url}\n"
                    search_context += f"Summary: {result.snippet}\n\n"
                
                search_context += "---\n"
                search_context += "Use the above information to provide a comprehensive answer.\n\n"
                return search_context
            
        except Exception as e:
            print(f"🔍 Search error: {e}")
        
        return None
    
    def handle_command(self, user_input: str) -> str:
        """Handle user commands with internet search integration"""
        try:
            # Check for special commands
            if user_input.lower() in ['exit', 'quit', 'goodbye']:
                return "👋 Goodbye! Thanks for using AI Helper Agent with Internet Access!"
            
            if user_input.lower() in ['help', '?']:
                return self._get_help_text()
            
            if user_input.lower().startswith('internet'):
                return self._handle_internet_commands(user_input)
            
            # Get conversation history for context
            history = self.get_session_history(self.session_id)
            context = ""
            if history.messages:
                # Get last few messages for context
                recent_messages = history.messages[-4:]
                context = "\n".join([msg.content for msg in recent_messages])
            
            # Check if internet search might be helpful and perform it
            search_context = self._search_and_enhance_response(user_input, context)
            
            # Prepare the input with search context if available
            enhanced_input = user_input
            if search_context:
                enhanced_input = f"{search_context}\n**USER QUESTION:** {user_input}"
                print("🔍 Found relevant information online, incorporating into response...")
            
            # Handle streaming response
            if self.streaming_enabled:
                print("🤖 AI Helper: ", end="", flush=True)
                
                # Use simple streaming like the original CLI
                full_response = ""
                for chunk in self.conversation_chain.stream(
                    {"input": enhanced_input},
                    config={"configurable": {"session_id": self.session_id}}
                ):
                    if chunk:
                        print(chunk, end="", flush=True)
                        full_response += chunk
                
                print()  # New line after streaming
                return ""  # Response already printed via streaming
            else:
                # Non-streaming response
                response = self.conversation_chain.invoke(
                    {"input": enhanced_input},
                    config={"configurable": {"session_id": self.session_id}}
                )
                return response
                
        except Exception as e:
            error_msg = f"❌ Error processing request: {e}"
            print(error_msg)
            return error_msg
    
    def _handle_internet_commands(self, user_input: str) -> str:
        """Handle internet-specific commands"""
        if not self.internet_manager:
            return "❌ Internet access is not available"
        
        parts = user_input.lower().split()
        
        if len(parts) == 1:
            # Show internet status
            status = self.internet_manager.get_status()
            status_text = "🌐 **INTERNET ACCESS STATUS**\n\n"
            status_text += f"Permission Level: {status.get('permission_level', 'Unknown')}\n"
            status_text += f"Total Searches: {status.get('total_searches', 0)}\n"
            status_text += f"Approved Searches: {status.get('approved_searches', 0)}\n\n"
            
            status_text += "**Available Providers:**\n"
            providers = status.get('available_providers', {})
            for provider, available in providers.items():
                status_text += f"- {provider.title()}: {'✅' if available else '❌'}\n"
            
            return status_text
        
        elif parts[1] == 'permission':
            if len(parts) >= 3:
                level = parts[2]
                self.internet_manager.configure_permissions(level=level)
                return f"✅ Permission level set to: {level}"
            else:
                return "Usage: internet permission [always|ask|never|smart]"
        
        elif parts[1] == 'search':
            if len(parts) >= 3:
                query = ' '.join(parts[2:])
                try:
                    results = self.internet_manager.search_with_permission(
                        query, user="user", session_id=self.session_id
                    )
                    if results and results.get('results'):
                        response = f"🔍 **SEARCH RESULTS FOR:** {query}\n\n"
                        for i, result in enumerate(results['results'][:5]):
                            response += f"**{i+1}. {result.title}**\n"
                            response += f"URL: {result.url}\n"
                            response += f"Summary: {result.snippet}\n\n"
                        return response
                    else:
                        return "No search results found."
                except Exception as e:
                    return f"❌ Search failed: {e}"
            else:
                return "Usage: internet search <your search query>"
        
        return "Available internet commands: internet, internet permission <level>, internet search <query>"
    
    def _get_help_text(self) -> str:
        """Get help text with internet features"""
        return """🌐 **AI HELPER AGENT - INTERNET ENABLED**

**Basic Usage:**
- Just type your question or request
- The AI will automatically search the internet when helpful
- Ask about current events, latest documentation, or specific problems

**Internet Commands:**
- `internet` - Show internet access status
- `internet permission <level>` - Set permission level (always/ask/never/smart)
- `internet search <query>` - Manual web search

**Permission Levels:**
- `smart` - AI decides when to search (recommended)
- `always` - Search for every query
- `ask` - Ask permission before each search
- `never` - Disable internet access

**Examples:**
- "What's the latest version of Python?"
- "How to use the new features in React 18?"
- "Show me examples of async/await in JavaScript"
- "What are the recent changes in TensorFlow?"

**Special Commands:**
- `help` or `?` - Show this help
- `exit`, `quit`, or `goodbye` - Exit the program

🚀 **Features:**
- Ultra-fast Groq models for instant responses
- Automatic web search when current information is needed
- Smart analysis to determine when internet search is helpful
- Real-time streaming responses
- Conversation history maintained across sessions

Ready to help with internet-powered AI assistance!"""
    
    def start(self):
        """Start the interactive CLI with internet access"""
        print(f"\n🌐 AI Helper Agent - Internet Enabled CLI")
        print(f"⚡ Model: {self.model} (GROQ)")
        print(f"🔍 Internet Access: {'✅ Enabled' if self.internet_manager else '❌ Disabled'}")
        print(f"💾 Session: {self.session_id}")
        print(f"📁 Workspace: {self.workspace_path}")
        print()
        print("💡 Type 'help' for available commands, or just start chatting!")
        print("🌐 AI will automatically search the web when helpful information is needed")
        print("⚡ Ultra-fast streaming responses enabled for real-time interaction")
        print()
        
        # Main interaction loop
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                response = self.handle_command(user_input)
                
                if response:
                    if user_input.lower() not in ['exit', 'quit', 'goodbye']:
                        if not self.streaming_enabled:
                            print(f"🤖 AI Helper: {response}")
                    else:
                        print(response)
                        break
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main CLI entry point for internet-enabled single provider"""
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Internet-Enabled Single Provider CLI (Groq Only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper-internet-single                    # Start with Groq + Internet
  ai-helper-internet-single --quick           # Skip startup, use last config
  ai-helper-internet-single --session work   # Start with named session
  ai-helper-internet-single --model 2         # Start with specific Groq model
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
        choices=list(InternetSingleProviderCLI.AVAILABLE_MODELS.keys()),
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
        version="AI Helper Agent Internet Single Provider CLI v1.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Create CLI instance with internet access
        cli = InternetSingleProviderCLI(
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
        
        # Setup user session with internet access
        if not cli.setup_user_session():
            print("❌ Failed to setup CLI. Exiting...")
            sys.exit(1)
        
        # Setup LLM chain
        if not cli.setup_llm_and_chain():
            print("❌ Failed to setup LLM chain. Exiting...")
            sys.exit(1)
        
        # Start the application
        cli.start()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
