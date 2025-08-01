"""
AI Helper Agent - Single Provider CLI (Groq Only)
Simplified CLI with only Groq models for faster startup and focused use
"""

import os
import sys
import asyncio
import argparse
from typing import Dict, Any, Optional
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
from .streaming import StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
from .startup import MultiProviderStartup

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
        
        # Single provider startup interface
        if not self.skip_startup:
            self.startup_interface = MultiProviderStartup()
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show enhanced splash screen with single provider logo"""
        if hasattr(self, 'startup_interface'):
            self.startup_interface.display_responsive_logo()
        else:
            # Fallback simple logo
            print("⚡ AI HELPER AGENT - SINGLE PROVIDER ⚡")
            print("GROQ POWERED - LIGHTNING FAST")
    
    def setup_user_session(self) -> bool:
        """Setup user session with single provider startup"""
        if not self.skip_startup:
            # Use the single provider startup interface
            self.show_splash_screen()
            
            # Run startup sequence (will only show Groq)
            model_id, api_key, llm_instance = self.startup_interface.run_startup_sequence()
            
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

Current workspace: {self.workspace_path}
Current model: {self.model} (GROQ)
Provider: GROQ (Lightning Fast)

I'm ready to help you with any programming task with Groq's ultra-fast responses!"""
    
    async def handle_command(self, user_input: str) -> str:
        """Handle user commands and return AI response"""
        try:
            # Check for special commands
            if user_input.lower() in ['exit', 'quit', 'goodbye']:
                return "👋 Goodbye! Thanks for using AI Helper Agent!"
            
            if user_input.lower() in ['help', '?']:
                return self._get_help_message()
            
            if user_input.lower() == 'clear':
                # Clear conversation history
                if self.session_id in conversation_store:
                    conversation_store[self.session_id] = ChatMessageHistory()
                return "🧹 Conversation history cleared!"
            
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
                return response
                
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"
    
    async def _get_ai_response_streaming(self, prompt: str) -> str:
        """Get AI response with streaming"""
        try:
            full_response = ""
            print("🤖 AI Helper: ", end="", flush=True)
            
            for chunk in self.conversation_chain.stream(
                {"input": prompt},
                config={"configurable": {"session_id": self.session_id}}
            ):
                if chunk:
                    print(chunk, end="", flush=True)
                    full_response += chunk
            
            print()  # New line after streaming
            return full_response
            
        except Exception as e:
            return f"❌ Error generating response: {str(e)}"
    
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

⚡ GROQ ADVANTAGES:
• Ultra-fast responses for real-time coding
• Optimized for programming tasks
• Instant feedback for development

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
        print("\n⚡ Starting AI Helper Agent (Single Provider - Groq)...")
        
        # Setup user session
        if not self.setup_user_session():
            print("❌ Failed to setup user session. Exiting.")
            return
        
        # Setup LLM and chain
        if not self.setup_llm_and_chain():
            print("❌ Failed to setup LLM. Exiting.")
            return
        
        print(f"✅ AI Helper Agent ready! Using {self.model} (Groq)")
        print("💡 Type 'help' for available commands, or just start chatting!")
        print("⚡ Ultra-fast streaming responses enabled for real-time interaction")
        print()
        
        # Main interaction loop
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                response = await self.handle_command(user_input)
                
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
    """Main CLI entry point for single provider"""
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Single Provider CLI (Groq Only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper-single                    # Start with Groq startup page
  ai-helper-single --quick           # Skip startup, use last config
  ai-helper-single --session work   # Start with named session
  ai-helper-single --model 2         # Start with specific Groq model
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
