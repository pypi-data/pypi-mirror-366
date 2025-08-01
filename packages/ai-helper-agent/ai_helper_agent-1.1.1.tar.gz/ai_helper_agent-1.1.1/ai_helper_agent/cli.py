"""
AI Helper Agent CLI Module
Interactive command-line interface with conversation history and message trimming
Enhanced with Codex-like capabilities and latest Groq models
"""

import os
import sys
import asyncio
import getpass
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging to suppress debug messages and cache logs
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logging.getLogger("structlog").setLevel(logging.WARNING)
logging.getLogger("secure_cache").setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.WARNING)

from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Multi-provider LLM imports
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

from .core import InteractiveAgent
from .config import config
from .security import security_manager
from .user_manager import user_manager
from .prompt_enhancer import AdvancedPromptEnhancer
from .system_config import SystemConfigurationManager
from .streaming import StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
from .startup import StartupInterface, MultiProviderStartup

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}


class AIHelperCLI:
    """Enhanced CLI with LangChain conversation history and multi-provider support"""
    
    # Available models across all providers (Remove Mixtral, add proper multi-provider support)
    AVAILABLE_MODELS = {
        # GROQ Models - Lightning Fast (Remove Mixtral as it's decommissioned)
        "llama-3.3-70b-versatile": "Llama 3.3 70B (Meta - General purpose, Large)",
        "llama-3.1-8b-instant": "Llama 3.1 8B (Meta - Instant response, Fast)",
        "gemma2-9b-it": "Gemma 2 9B (Google - Chat fine-tuned, Balanced)",
        "llama-3.1-70b-versatile": "Llama 3.1 70B (Meta - Complex reasoning)",
        
        # OpenAI Models (if available)
        "gpt-4.5": "GPT-4.5 (OpenAI - Latest 2025, fewer hallucinations)",
        "gpt-4o": "GPT-4o (OpenAI - Multimodal, structured outputs)",
        "gpt-4o-mini": "GPT-4o Mini (OpenAI - Faster, cost-effective)",
        "o1-preview": "O1 Preview (OpenAI - Advanced reasoning)",
        "o3-pro": "O3 Pro (OpenAI - Latest reasoning family)",
        
        # Anthropic Models (if available)
        "claude-3-5-sonnet-20240620": "Claude-3.5 Sonnet (Anthropic - Latest)",
        "claude-3-opus-20240229": "Claude-3 Opus (Anthropic - Most powerful)",
        "claude-3-haiku-20240307": "Claude-3 Haiku (Anthropic - Fast)",
        
        # Google Models (if available)
        "gemini-2.5-pro": "Gemini 2.5 Pro (Google - Latest)",
        "gemini-2.5-flash": "Gemini 2.5 Flash (Google - Fast)",
        "gemini-2.0-flash": "Gemini 2.0 Flash (Google - Balanced)",
        "gemini-1.5-pro": "Gemini 1.5 Pro (Google - Reliable)",
        
        # Local Models (if available)
        "llama3": "Llama 3 (Local - Ollama)",
        "codellama": "Code Llama (Local - Ollama)",
        "mistral": "Mistral (Local - Ollama)"
    }
    
    def __init__(self, session_id: str = "default", model: str = None):
        self.session_id = session_id
        self.api_key: Optional[str] = None
        self.llm: Optional[ChatGroq] = None
        self.chain = None
        self.workspace_path = Path.cwd()
        self.model = model or "llama-3.1-8b-instant"  # Default to latest instant model
        
        # LangChain conversation setup
        self.conversation_chain = None
        self.trimmer = None
        
        # Enhanced prompt system
        self.prompt_enhancer: Optional[AdvancedPromptEnhancer] = None
        
        # System configuration manager
        self.system_config: Optional[SystemConfigurationManager] = None
        
        # Streaming handlers
        self.streaming_handler: Optional[StreamingResponseHandler] = None
        self.advanced_streaming: Optional[AdvancedStreamingHandler] = None
        self.enhanced_streaming: Optional[EnhancedStreamingHandler] = None
        
        self.enable_streaming: bool = True  # Enable streaming by default
        
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for session"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show AI Helper Agent splash screen with enhanced ASCII robot"""
        # Simple splash screen
        robot_logo = """
        🤖 ╔══════════════════════════════════════╗
           ║          AI HELPER AGENT             ║
           ║      Your Autonomous Coding          ║
           ║         Assistant v1.0               ║
           ╚══════════════════════════════════════╝
           
                  ╭─────────────╮
                  │  ( ◕   ◕ )  │
                  │      ▾      │
                  ╰─────────────╯
                      │███│
                  ╭───┴───┴───╮
                  │  CODING   │
                  │  EXPERT   │
                  ╰───────────╯
            """
        
        print(robot_logo)
        print("Welcome to AI Helper Agent - Your Autonomous Programming Assistant!")
        print("Enhanced with Groq models and advanced capabilities\n")
    
    def setup_user_session(self) -> bool:
        """Setup user session with username and session management"""
        self.show_splash_screen()
        
        try:
            # Ask for username
            print("👤 User Setup")
            print("-" * 20)
            
            username = input("Enter your username: ").strip()
            
            if not username:
                print("❌ Username cannot be empty. Please try again.")
                return self.setup_user_session()
            
            # Setup user environment
            if not user_manager.setup_user(username):
                print("❌ Failed to setup user environment")
                return False
            
            # Check for existing sessions
            sessions = user_manager.get_user_sessions(username)
            
            if sessions:
                print(f"\n📁 Found {len(sessions)} existing sessions:")
                print("0. Create new session")
                
                for i, session in enumerate(sessions[:5], 1):  # Show last 5 sessions
                    created_date = session['created_at'][:10]  # YYYY-MM-DD
                    print(f"{i}. Session from {created_date} (ID: {session['session_id'][:8]}...)")
                
                try:
                    choice = input(f"\nSelect session (0-{min(len(sessions), 5)} or Enter for new): ").strip()
                    
                    if choice and choice != "0":
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(sessions):
                            selected_session = sessions[choice_num - 1]
                            if user_manager.load_session(selected_session['session_id']):
                                print(f"✅ Loaded session from {selected_session['created_at'][:10]}")
                                self.session_id = selected_session['session_id']
                            else:
                                print("⚠️  Could not load session, creating new one")
                        else:
                            print("⚠️  Invalid choice, creating new session")
                    
                except (ValueError, KeyboardInterrupt):
                    print("⚠️  Creating new session")
            
            print(f"✅ User session ready for: {username}")
            print(f"📁 Data directory: {user_manager.user_dir}")
            print(f"🔗 Session ID: {user_manager.session_id}")
            
            # Initialize enhanced prompt system
            self.prompt_enhancer = AdvancedPromptEnhancer(
                username=username,
                workspace_path=self.workspace_path,
                model=self.model
            )
            
            # Initialize system configuration manager
            self.system_config = SystemConfigurationManager(self.workspace_path)
            
            return True
            
        except KeyboardInterrupt:
            print("\n👋 Setup cancelled. Goodbye!")
            return False
        except Exception as e:
            print(f"❌ Error during user setup: {e}")
            return False
    
    def setup_api_key(self) -> bool:
        """Setup API key with user interaction"""
        print("\n🔑 API Configuration")
        print("-" * 20)
        
        # Check if API key exists in environment
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if self.api_key:
            print(f"✅ Found GROQ_API_KEY in environment")
        else:
            print("🔑 Groq API Key required for AI Helper Agent")
            print("You can get a free API key at: https://groq.com/")
            print()
            
            while True:
                try:
                    self.api_key = getpass.getpass("Enter your Groq API key: ").strip()
                    
                    if not self.api_key:
                        print("❌ API key cannot be empty. Please try again.")
                        continue
                    break
                    
                except KeyboardInterrupt:
                    print("\n👋 Setup cancelled. Goodbye!")
                    return False
        
        # Model selection
        return self.setup_model_selection()
    
    def setup_model_selection(self) -> bool:
        """Allow user to select or confirm model"""
        print(f"\n🤖 Current model: {self.model}")
        print("📋 Available models:")
        
        for i, (model_id, description) in enumerate(self.AVAILABLE_MODELS.items(), 1):
            marker = "👉" if model_id == self.model else "  "
            print(f"{marker} {i}. {model_id} - {description}")
        
        print("\nPress Enter to use current model, or enter number to change:")
        
        try:
            choice = input(f"Choice (1-{len(self.AVAILABLE_MODELS)} or Enter): ").strip()
            
            if choice:
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(self.AVAILABLE_MODELS):
                        model_list = list(self.AVAILABLE_MODELS.keys())
                        self.model = model_list[choice_num - 1]
                        print(f"✅ Selected model: {self.model}")
                    else:
                        print("❌ Invalid choice, using default model")
                except ValueError:
                    print("❌ Invalid input, using default model")
            
            # Test the API key and model
            return self.test_api_key_and_model()
            
        except KeyboardInterrupt:
            print("\n👋 Setup cancelled. Goodbye!")
            return False
    
    def test_api_key_and_model(self) -> bool:
        """Test API key and model"""
        try:
            test_llm = ChatGroq(
                model=self.model,
                temperature=0.1,
                api_key=self.api_key
            )
            
            print(f"🔄 Testing API key with model {self.model}...")
            response = test_llm.invoke([HumanMessage(content="Hello")])
            
            if response and response.content:
                print("✅ API key and model validated successfully!")
                # Store in environment for this session
                os.environ["GROQ_API_KEY"] = self.api_key
                return True
            else:
                print("❌ Invalid API key or model. Please try again.")
                return False
                
        except Exception as e:
            print(f"❌ Error testing API key/model: {e}")
            print("Please check your settings and try again.")
            return False
    
    def setup_llm_and_chain(self):
        """Setup LLM and conversation chain with multi-provider support"""
        try:
            print("🔄 Initializing AI Helper Agent...")
            
            # Determine provider and create appropriate LLM
            provider = self.get_model_provider()
            
            if provider == "groq":
                self.llm = ChatGroq(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            elif provider == "openai" and ChatOpenAI:
                self.llm = ChatOpenAI(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            elif provider == "anthropic" and ChatAnthropic:
                self.llm = ChatAnthropic(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            elif provider == "google" and ChatGoogleGenerativeAI:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model,
                    google_api_key=self.api_key,
                    temperature=0.1
                )
            elif provider == "ollama" and ChatOllama:
                self.llm = ChatOllama(
                    model=self.model,
                    temperature=0.1
                )
            else:
                # Fallback to Groq
                print(f"⚠️  Provider {provider} not available, falling back to Groq")
                self.llm = ChatGroq(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            
            print(f"✅ Initialized {provider.upper()} LLM: {self.model}")
            
            # Setup message trimmer (keep last 8 messages + system)
            self.trimmer = trim_messages(
                max_tokens=4000,  # Adjust based on model limits
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
            
            # Initialize streaming handlers
            self.streaming_handler = StreamingResponseHandler(self.llm, self.conversation_chain)
            self.advanced_streaming = AdvancedStreamingHandler(self.llm, self.conversation_chain)
            self.enhanced_streaming = EnhancedStreamingHandler(self.llm, self.conversation_chain)
            
            print("✅ AI Helper Agent initialized successfully!")
            print("🔄 Enhanced streaming mode enabled for real-time responses")
            print("🚀 Multiple streaming handlers available for optimal performance")
            
        except Exception as e:
            print(f"❌ Failed to initialize AI Helper: {e}")
            return False
        
        return True
    
    def setup_conversation_chain(self):
        """Setup conversation chain and streaming handlers using existing LLM"""
        try:
            print("🔄 Setting up conversation chain with existing LLM...")
            
            # Setup message trimmer (keep last 8 messages + system)
            self.trimmer = trim_messages(
                max_tokens=4000,  # Adjust based on model limits
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
            
            # Initialize streaming handlers
            self.streaming_handler = StreamingResponseHandler(self.llm, self.conversation_chain)
            self.advanced_streaming = AdvancedStreamingHandler(self.llm, self.conversation_chain)
            self.enhanced_streaming = EnhancedStreamingHandler(self.llm, self.conversation_chain)
            
            print("✅ Conversation chain and streaming handlers ready!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup conversation chain: {e}")
            return False
    
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
        
        # Check model against each provider
        if self.model in groq_models:
            return "groq"
        elif self.model in openai_models:
            return "openai"
        elif self.model in anthropic_models:
            return "anthropic"
        elif self.model in google_models:
            return "google"
        else:
            # Check if it looks like a local Ollama model
            if ":" not in self.model and "/" not in self.model and self.model.isalnum():
                return "ollama"
            return "groq"  # Default fallback
    
    def _get_system_prompt(self) -> str:
        """Get the enhanced system prompt for the AI assistant"""
        if self.prompt_enhancer:
            return self.prompt_enhancer.get_enhanced_system_prompt()
        
        # Fallback to basic prompt if enhancer not available
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

Current workspace: {str(self.workspace_path)}
Current model: {self.model or 'Unknown'}

I'm ready to help you with any programming task, from simple scripts to complex applications!"""
    
    async def _get_ai_response(self, prompt: str, use_streaming: bool = True) -> str:
        """Utility method to get AI response with streaming (replaces ainvoke)"""
        try:
            config = {"configurable": {"session_id": self.session_id}}
            
            # Use enhanced streaming if enabled and available
            if use_streaming and self.enable_streaming:
                if self.enhanced_streaming:
                    # Use enhanced streaming with progress indicators
                    return await self.enhanced_streaming.stream_with_progress(prompt, config)
                elif self.advanced_streaming:
                    # Fallback to advanced streaming
                    return await self.advanced_streaming.stream_with_indicators(prompt, config)
                elif self.streaming_handler:
                    # Fallback to basic streaming
                    return await self.streaming_handler.stream_generate(prompt, config)
            
            # Last resort: blocking response (if streaming fails)
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            return response
        except Exception as e:
            return f"❌ Error processing request: {e}"
    
    async def handle_command(self, user_input: str) -> str:
        """Handle user commands and return AI response"""
        try:
            # Special command handling
            cmd_lower = user_input.lower()
            
            if cmd_lower.startswith('analyze '):
                return await self._handle_analyze_command(user_input[8:].strip())
            elif cmd_lower.startswith('fix '):
                return await self._handle_fix_command(user_input[4:].strip())
            elif cmd_lower.startswith('create '):
                return await self._handle_create_command(user_input[7:].strip())
            elif cmd_lower.startswith('generate '):
                return await self._handle_generate_command(user_input[9:].strip())
            elif cmd_lower.startswith('complete '):
                return await self._handle_complete_command(user_input[9:].strip())
            elif cmd_lower.startswith('translate '):
                return await self._handle_translate_command(user_input[10:].strip())
            elif cmd_lower.startswith('explain '):
                return await self._handle_explain_command(user_input[8:].strip())
            elif cmd_lower.startswith('refactor '):
                return await self._handle_refactor_command(user_input[9:].strip())
            elif cmd_lower.startswith('debug '):
                return await self._handle_debug_command(user_input[6:].strip())
            elif cmd_lower.startswith('shell '):
                return await self._handle_shell_command(user_input[6:].strip())
            elif cmd_lower.startswith('optimize '):
                return await self._handle_optimize_command(user_input[9:].strip())
            elif cmd_lower.startswith('search '):
                return self._handle_search_command(user_input[7:].strip())
            elif cmd_lower.startswith('find '):
                return self._handle_find_command(user_input[5:].strip())
            elif cmd_lower.startswith('save '):
                return await self._handle_save_command(user_input[5:].strip())
            elif cmd_lower in ['help', '/help', '?']:
                return self._get_help_text()
            elif cmd_lower.startswith('workspace '):
                return self._handle_workspace_command(user_input[10:].strip())
            elif cmd_lower.startswith('model '):
                return self._handle_model_command(user_input[6:].strip())
            elif cmd_lower.startswith('change_name '):
                return self._handle_change_name_command(user_input[12:].strip())
            elif cmd_lower.startswith('streaming ') or cmd_lower == 'streaming':
                return self._handle_streaming_command(user_input[10:].strip() if len(user_input) > 10 else "")
            elif cmd_lower.startswith('startup ') or cmd_lower == 'startup':
                return self._handle_startup_command(user_input[8:].strip() if len(user_input) > 8 else "")
            elif cmd_lower == 'structure' or cmd_lower.startswith('structure'):
                return self._handle_structure_command(user_input[9:].strip() if len(user_input) > 9 else "")
            elif cmd_lower == 'sysinfo' or cmd_lower.startswith('sysinfo'):
                return self._handle_sysinfo_command()
            elif cmd_lower.startswith('shell '):
                return self._handle_shell_execution_command(user_input[6:].strip())
            elif cmd_lower == 'workspace_info':
                return self._handle_workspace_info_command()
            elif cmd_lower == 'model':
                return self._handle_model_command("")
            
            # Regular conversation with history and enhanced prompting
            config = {"configurable": {"session_id": self.session_id}}
            
            # Enhance the user input with context if prompt enhancer is available
            enhanced_input = user_input
            if self.prompt_enhancer:
                try:
                    # Get conversation history for context
                    history = user_manager.get_conversation_history(limit=5)
                    enhanced_input = self.prompt_enhancer.enhance_user_prompt(user_input, history)
                except Exception:
                    # Fallback to original input if enhancement fails
                    enhanced_input = user_input
            
            # Use the utility method for consistent streaming/non-streaming response
            response = await self._get_ai_response(enhanced_input)
            
            return response
            
        except Exception as e:
            return f"❌ Error processing your request: {e}"
    
    async def _handle_analyze_command(self, filename: str) -> str:
        """Handle file analysis command"""
        try:
            file_path = self.workspace_path / filename
            
            if not file_path.exists():
                return f"❌ File not found: {filename}\nCurrent workspace: {self.workspace_path}"
            
            if not security_manager.is_file_accessible(str(file_path)):
                return f"❌ Access denied to file: {filename}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use InteractiveAgent for analysis
            agent = InteractiveAgent(api_key=self.api_key, workspace_path=str(self.workspace_path))
            result = await agent.analyze_code(content, filename)
            
            if result["success"]:
                return f"📊 Analysis of {filename}:\n\n{result['analysis']}"
            else:
                return f"❌ Analysis failed: {result['error']}"
                
        except Exception as e:
            return f"❌ Error analyzing file: {e}"
    
    async def _handle_fix_command(self, filename: str) -> str:
        """Handle file fix command"""
        try:
            file_path = self.workspace_path / filename
            
            if not file_path.exists():
                return f"❌ File not found: {filename}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            agent = InteractiveAgent(api_key=self.api_key, workspace_path=str(self.workspace_path))
            result = await agent.fix_code(content, filename=filename)
            
            if result["success"]:
                return f"🔧 Fixed version of {filename}:\n\n```python\n{result['fixed_code']}\n```\n\nUse 'save {filename}_fixed.py last' to save this fix."
            else:
                return f"❌ Fix failed: {result['error']}"
                
        except Exception as e:
            return f"❌ Error fixing file: {e}"
    
    async def _handle_create_command(self, filename: str) -> str:
        """Handle file creation command"""
        return f"📝 I can help you create {filename}. What should this file contain? Describe the functionality you need."
    
    async def _handle_generate_command(self, description: str) -> str:
        """Handle code generation from natural language"""
        try:
            prompt = f"""Generate complete, working code based on this description: {description}

Requirements:
1. Provide complete, executable code
2. Include proper error handling
3. Add comments explaining the logic
4. Follow best practices for the language
5. Include usage examples if appropriate

Generate the code now:"""
            
            config = {"configurable": {"session_id": self.session_id}}
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"🚀 Generated code for: {description}\n\n{response}"
            
        except Exception as e:
            return f"❌ Error generating code: {e}"
    
    async def _handle_complete_command(self, partial_code: str) -> str:
        """Handle code completion"""
        try:
            prompt = f"""Complete this partial code. Provide the missing parts to make it functional:

```
{partial_code}
```

Requirements:
1. Complete the code logically
2. Maintain consistent style
3. Add necessary imports
4. Include error handling
5. Add comments for complex parts

Complete the code:"""
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"✅ Code completion:\n\n{response}"
            
        except Exception as e:
            return f"❌ Error completing code: {e}"
    
    async def _handle_translate_command(self, args: str) -> str:
        """Handle code translation between languages"""
        try:
            # Parse "from_lang to to_lang code" format
            if " to " in args:
                parts = args.split(" to ", 1)
                if len(parts) == 2:
                    from_lang = parts[0].strip()
                    rest = parts[1].strip()
                    
                    # Check if there's code after the target language
                    words = rest.split(None, 1)  # Split on first whitespace
                    if len(words) >= 2:
                        to_lang = words[0]
                        code = words[1]
                    else:
                        to_lang = rest
                        return f"❌ Please provide code to translate. Usage: translate {from_lang} to {to_lang} <code>"
                else:
                    return "❌ Usage: translate <from_language> to <to_language> <code>"
            else:
                return "❌ Usage: translate <from_language> to <to_language> <code>"
            
            prompt = f"""Translate this {from_lang} code to {to_lang}:

```{from_lang}
{code}
```

Requirements:
1. Maintain the same functionality
2. Use idiomatic {to_lang} patterns
3. Include proper error handling
4. Add comments explaining any {to_lang}-specific features
5. Ensure the code is production-ready

Translated {to_lang} code:"""
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"🔄 Translated from {from_lang} to {to_lang}:\n\n{response}"
            
        except Exception as e:
            return f"❌ Error translating code: {e}"
    
    async def _handle_explain_command(self, code_or_file: str) -> str:
        """Handle code explanation"""
        try:
            # Check if it's a filename or code
            if len(code_or_file.split()) == 1 and '.' in code_or_file:
                # Likely a filename
                file_path = self.workspace_path / code_or_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    source = f"file '{code_or_file}'"
                else:
                    return f"❌ File not found: {code_or_file}"
            else:
                # Direct code
                code = code_or_file
                source = "provided code"
            
            prompt = f"""Explain this code in plain English. Break down what it does, how it works, and any important concepts:

```
{code}
```

Provide:
1. High-level overview of what the code does
2. Step-by-step explanation of the logic
3. Explanation of any algorithms or patterns used
4. Potential improvements or considerations
5. Key learning points

Explanation:"""
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"📖 Explanation of {source}:\n\n{response}"
            
        except Exception as e:
            return f"❌ Error explaining code: {e}"
    
    async def _handle_refactor_command(self, code_or_file: str) -> str:
        """Handle code refactoring"""
        try:
            # Check if it's a filename or code
            if len(code_or_file.split()) == 1 and '.' in code_or_file:
                file_path = self.workspace_path / code_or_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    source = f"file '{code_or_file}'"
                else:
                    return f"❌ File not found: {code_or_file}"
            else:
                code = code_or_file
                source = "provided code"
            
            prompt = f"""Refactor this code to improve its structure, readability, and maintainability:

```
{code}
```

Focus on:
1. Better variable and function names
2. Improved code structure and organization
3. Following best practices and design patterns
4. Better error handling
5. Performance optimizations where appropriate
6. Code documentation and comments

Refactored code:"""
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"♻️ Refactored {source}:\n\n{response}"
            
        except Exception as e:
            return f"❌ Error refactoring code: {e}"
    
    async def _handle_debug_command(self, code_or_file: str) -> str:
        """Handle code debugging"""
        try:
            # Check if it's a filename or code
            if len(code_or_file.split()) == 1 and '.' in code_or_file:
                file_path = self.workspace_path / code_or_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    source = f"file '{code_or_file}'"
                else:
                    return f"❌ File not found: {code_or_file}"
            else:
                code = code_or_file
                source = "provided code"
            
            prompt = f"""Debug this code and identify any issues:

```
{code}
```

Analyze for:
1. Syntax errors
2. Logic bugs
3. Runtime errors
4. Performance issues
5. Security vulnerabilities
6. Edge cases not handled

Provide:
1. List of identified issues
2. Corrected code
3. Explanation of fixes
4. Prevention strategies

Debug analysis:"""
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"🐛 Debug analysis of {source}:\n\n{response}"
            
        except Exception as e:
            return f"❌ Error debugging code: {e}"
    
    async def _handle_shell_command(self, description: str) -> str:
        """Handle shell command generation"""
        try:
            prompt = f"""Generate shell/terminal commands for: {description}

Requirements:
1. Provide cross-platform commands when possible
2. Include Windows (PowerShell/CMD) and Unix/Linux variants
3. Add safety warnings for destructive operations
4. Explain what each command does
5. Include common flags and options

Shell commands:"""
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"💻 Shell commands for: {description}\n\n{response}"
            
        except Exception as e:
            return f"❌ Error generating shell commands: {e}"
    
    async def _handle_optimize_command(self, code_or_file: str) -> str:
        """Handle code optimization"""
        try:
            # Check if it's a filename or code
            if len(code_or_file.split()) == 1 and '.' in code_or_file:
                file_path = self.workspace_path / code_or_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    source = f"file '{code_or_file}'"
                else:
                    return f"❌ File not found: {code_or_file}"
            else:
                code = code_or_file
                source = "provided code"
            
            prompt = f"""Optimize this code for better performance:

```
{code}
```

Focus on:
1. Algorithm efficiency improvements
2. Memory usage optimization
3. I/O operations optimization
4. Better data structures
5. Caching strategies
6. Parallel processing opportunities

Provide:
1. Optimized code
2. Performance analysis
3. Explanation of optimizations
4. Benchmarking suggestions

Optimized code:"""
            
            # Use the unified streaming method
            response = await self._get_ai_response(prompt)
            
            return f"⚡ Optimized {source}:\n\n{response}"
            
        except Exception as e:
            return f"❌ Error optimizing code: {e}"
    
    def _handle_search_command(self, pattern: str) -> str:
        """Handle file search command"""
        try:
            results = security_manager.search_files(pattern)
            
            if not results:
                return f"🔍 No files found matching '{pattern}'"
            
            response = f"🔍 Found {len(results)} files matching '{pattern}':\n\n"
            for i, file_path in enumerate(results, 1):
                response += f"{i}. {file_path}\n"
            
            if len(results) > 10:
                response += f"\n... and {len(results) - 10} more files"
            
            return response
            
        except Exception as e:
            return f"❌ Error searching files: {e}"
    
    def _handle_find_command(self, search_text: str) -> str:
        """Handle text search in files command"""
        try:
            results = security_manager.search_in_files(search_text)
            
            if not results:
                return f"🔍 No text matches found for '{search_text}'"
            
            response = f"🔍 Found '{search_text}' in {len(results)} files:\n\n"
            
            for file_path, matches in results.items():
                response += f"📄 {file_path} ({len(matches)} matches):\n"
                
                for match in matches[:3]:  # Show first 3 matches per file
                    response += f"   Line {match['line_number']}: {match['line_content']}\n"
                
                if len(matches) > 3:
                    response += f"   ... and {len(matches) - 3} more matches\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error searching in files: {e}"
    
    async def _handle_save_command(self, args: str) -> str:
        """Handle save file command"""
        try:
            parts = args.split(" ", 1)
            if len(parts) < 2:
                return "❌ Usage: save <filename> <content or 'last'>"
            
            filename, content_spec = parts
            
            if content_spec.lower() == "last":
                # Get last AI response from conversation history
                history = self.get_session_history(self.session_id)
                if history.messages:
                    last_ai_message = None
                    for msg in reversed(history.messages):
                        if isinstance(msg, AIMessage):
                            last_ai_message = msg
                            break
                    
                    if last_ai_message:
                        content = last_ai_message.content
                        # Extract code from markdown if present
                        import re
                        code_matches = re.findall(r'```(?:python|py|javascript|js|typescript|ts|java|cpp|c|go|rust)?\n(.*?)\n```', 
                                               content, re.DOTALL)
                        if code_matches:
                            # Use the first code block found
                            content = code_matches[0]
                    else:
                        return "❌ No AI response found to save"
                else:
                    return "❌ No conversation history found"
            else:
                content = content_spec
            
            # Save file using security manager
            if security_manager.create_safe_file(filename, content):
                return f"✅ File saved successfully: generated/{filename}"
            else:
                return f"❌ Failed to save file: {filename}"
                
        except Exception as e:
            return f"❌ Error saving file: {e}"
    
    def _handle_model_command(self, args: str) -> str:
        """Handle model change command"""
        try:
            if not args:
                # Show current model and available options
                response = f"🤖 Current model: {self.model}\n\n📋 Available models:\n"
                for i, (model_id, description) in enumerate(self.AVAILABLE_MODELS.items(), 1):
                    marker = "👉" if model_id == self.model else "  "
                    response += f"{marker} {i}. {model_id} - {description}\n"
                response += "\nUse 'model <number>' to change model"
                return response
            
            try:
                choice = int(args)
                model_list = list(self.AVAILABLE_MODELS.keys())
                
                if 1 <= choice <= len(model_list):
                    new_model = model_list[choice - 1]
                    self.model = new_model
                    
                    # Reinitialize LLM with new model
                    self.llm = ChatGroq(
                        model=self.model,
                        temperature=0.1,
                        api_key=self.api_key
                    )
                    
                    # Update conversation chain
                    self.setup_llm_and_chain()
                    
                    return f"✅ Model changed to: {self.model}"
                else:
                    return f"❌ Invalid choice. Use 1-{len(model_list)}"
                    
            except ValueError:
                return "❌ Invalid input. Use 'model <number>' (e.g., 'model 2')"
                
        except Exception as e:
            return f"❌ Error changing model: {e}"
    
    def _handle_change_name_command(self, new_name: str) -> str:
        """Handle username change command with enhanced session migration"""
        try:
            if not new_name:
                return "❌ Usage: change_name \"new_username\"\n💡 Changes your username and optionally migrates session data"
            
            # Remove quotes if present
            new_name = new_name.strip('"\'')
            
            if not new_name:
                return "❌ Username cannot be empty"
            
            # Check if username already exists
            if user_manager.current_user == new_name:
                return f"⚠️  You are already using username: {new_name}"
            
            # Store current session info for migration
            old_username = user_manager.current_user
            old_session_id = user_manager.session_id
            old_conversation_count = len(user_manager.get_conversation_history(limit=100))
            
            # Ask about session migration if there's existing data
            migration_choice = False
            if old_conversation_count > 0:
                try:
                    response = input(f"\n🔄 Found {old_conversation_count} conversations in current session.\n" +
                                   f"   Migrate session data to new username '{new_name}'? (y/N): ").strip().lower()
                    migration_choice = response == 'y'
                except (KeyboardInterrupt, EOFError):
                    return "❌ Username change cancelled"
            
            # Change username using user manager
            if user_manager.change_username(new_name):
                # Update prompt enhancer with new username
                if self.prompt_enhancer:
                    self.prompt_enhancer.username = new_name
                
                response = f"✅ Username changed from '{old_username}' to '{new_name}'\n"
                response += f"📁 User data directory: {user_manager.user_dir}\n"
                response += f"🆔 New session ID: {user_manager.session_id}\n"
                
                # Handle session migration if requested
                if migration_choice and old_conversation_count > 0:
                    try:
                        # Get conversation history from old session
                        old_conversations = user_manager.get_conversation_history(limit=100)
                        migrated_count = 0
                        
                        # Migrate conversations to new session
                        for conv in old_conversations:
                            if user_manager.save_conversation(
                                conv.get('user_input', ''),
                                conv.get('assistant_response', ''),
                                metadata={'migrated_from': old_username, 'original_timestamp': conv.get('timestamp')}
                            ):
                                migrated_count += 1
                        
                        response += f"🔄 Migrated {migrated_count}/{old_conversation_count} conversations\n"
                        
                        if migrated_count > 0:
                            response += f"✅ Session migration completed successfully"
                        else:
                            response += f"⚠️  No conversations were migrated"
                            
                    except Exception as e:
                        response += f"⚠️  Session migration failed: {e}\n"
                        response += f"💡 Your data is still available under the old username directory"
                
                return response
            else:
                return "❌ Failed to change username"
                
        except Exception as e:
            return f"❌ Error changing username: {e}"
    
    def _handle_structure_command(self, args: str) -> str:
        """Handle workspace structure visualization command"""
        try:
            if not self.system_config:
                return "❌ System configuration not available"
            
            # Parse arguments
            max_depth = 3
            max_items = 50
            
            if args:
                parts = args.split()
                if len(parts) >= 1 and parts[0].isdigit():
                    max_depth = int(parts[0])
                if len(parts) >= 2 and parts[1].isdigit():
                    max_items = int(parts[1])
            
            # Get workspace structure
            structure = self.system_config.get_workspace_structure(max_depth, max_items)
            
            response = "📂 WORKSPACE STRUCTURE\n"
            response += "=" * 50 + "\n"
            response += f"📍 Root: {structure['root']}\n"
            response += f"📄 Files: {structure['total_files']} | 📁 Directories: {structure['total_dirs']}\n\n"
            
            # File types
            if structure['file_types']:
                response += "📋 FILE TYPES:\n"
                sorted_types = sorted(structure['file_types'].items(), key=lambda x: x[1], reverse=True)
                for ext, count in sorted_types[:10]:
                    response += f"  {ext}: {count} files\n"
                response += "\n"
            
            # Languages detected
            if structure['languages']:
                response += "💻 LANGUAGES DETECTED:\n"
                sorted_langs = sorted(structure['languages'].items(), key=lambda x: x[1], reverse=True)
                for lang, count in sorted_langs:
                    response += f"  {lang}: {count} files\n"
                response += "\n"
            
            # Frameworks
            if structure['frameworks']:
                response += "🛠️ FRAMEWORKS/TOOLS:\n"
                for framework in structure['frameworks']:
                    response += f"  • {framework}\n"
                response += "\n"
            
            # Git info
            if structure['git_info']:
                git = structure['git_info']
                response += "🔗 GIT REPOSITORY:\n"
                if 'current_branch' in git:
                    response += f"  Branch: {git['current_branch']}\n"
                if 'remote_url' in git:
                    response += f"  Remote: {git['remote_url']}\n"
                if 'last_commit' in git:
                    response += f"  Last commit: {git['last_commit']}\n"
                if 'has_changes' in git:
                    status = "✅ Clean" if not git['has_changes'] else f"⚠️ {git['changes']} changes"
                    response += f"  Status: {status}\n"
                response += "\n"
            
            # Package files
            if structure['package_files']:
                response += "📦 PACKAGE FILES:\n"
                for pkg in structure['package_files']:
                    response += f"  • {pkg}\n"
                response += "\n"
            
            # Directory tree
            response += "🌲 DIRECTORY TREE:\n"
            response += self.system_config.render_tree_structure(structure['tree'])
            
            response += f"\n\n💡 Use 'structure <depth> <max_items>' to customize (current: depth={max_depth}, items={max_items})"
            
            return response
            
        except Exception as e:
            return f"❌ Error getting workspace structure: {e}"
    
    def _handle_sysinfo_command(self) -> str:
        """Handle system information command"""
        try:
            if not self.system_config:
                return "❌ System configuration not available"
            
            config = self.system_config.get_system_configuration()
            sys_info = config['system_info']
            
            response = "🖥️ SYSTEM INFORMATION\n"
            response += "=" * 50 + "\n"
            
            # Basic system info
            response += f"🔧 Platform: {sys_info['platform']} {sys_info['platform_release']}\n"
            response += f"🏗️ Architecture: {sys_info['architecture']}\n"
            response += f"🖥️ Hostname: {sys_info['hostname']}\n"
            response += f"👤 User: {sys_info['current_user']}\n"
            response += f"🐍 Python: {sys_info['python_version'].split()[0]}\n"
            response += f"💾 CPU Cores: {sys_info['cpu_count']}\n"
            response += f"🧠 Memory: {self._format_bytes(sys_info['memory_total'])} total, {self._format_bytes(sys_info['memory_available'])} available\n"
            response += f"💽 Disk Space: {self._format_bytes(sys_info['disk_usage'])}\n\n"
            
            # Workspace info
            workspace = config['workspace_info']
            response += "📂 WORKSPACE:\n"
            response += f"  Path: {workspace['path']}\n"
            response += f"  Exists: {'✅' if workspace['exists'] else '❌'}\n"
            response += f"  Permissions: R:{'✅' if workspace['permissions']['readable'] else '❌'} "
            response += f"W:{'✅' if workspace['permissions']['writable'] else '❌'} "
            response += f"X:{'✅' if workspace['permissions']['executable'] else '❌'}\n\n"
            
            # Development tools
            tools = config['tools']
            response += "🛠️ DEVELOPMENT TOOLS:\n"
            for tool, available in tools.items():
                status = "✅" if available else "❌"
                response += f"  {tool}: {status}\n"
            response += "\n"
            
            # Network info
            if 'network' in config and 'error' not in config['network']:
                net = config['network']
                response += "🌐 NETWORK:\n"
                response += f"  Hostname: {net.get('hostname', 'Unknown')}\n"
                response += f"  Local IP: {net.get('local_ip', 'Unknown')}\n"
                response += f"  Internet: {'✅' if net.get('has_internet') else '❌'}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error getting system information: {e}"
    
    def _handle_shell_execution_command(self, command: str) -> str:
        """Handle shell command execution"""
        try:
            if not command:
                return "❌ Usage: shell <command>"
            
            if not self.system_config:
                return "❌ System configuration not available"
            
            # Execute command
            result = self.system_config.execute_shell_command(command)
            
            response = f"🔧 SHELL COMMAND: {command}\n"
            response += "=" * 50 + "\n"
            
            if result['success']:
                response += "✅ Command executed successfully\n\n"
                if result['stdout']:
                    response += "📤 OUTPUT:\n"
                    response += result['stdout']
                    if not result['stdout'].endswith('\n'):
                        response += '\n'
                else:
                    response += "📤 No output\n"
            else:
                response += f"❌ Command failed (exit code: {result.get('returncode', 'unknown')})\n\n"
                if result.get('error'):
                    response += f"🚨 ERROR: {result['error']}\n"
                if result.get('stderr'):
                    response += "📤 STDERR:\n"
                    response += result['stderr']
                    if not result['stderr'].endswith('\n'):
                        response += '\n'
            
            response += "\n💡 Use 'shell <command>' to execute system commands safely"
            
            return response
            
        except Exception as e:
            return f"❌ Error executing shell command: {e}"
    
    def _handle_workspace_info_command(self) -> str:
        """Handle workspace information command"""
        try:
            if not self.system_config:
                return "❌ System configuration not available"
            
            # Get basic workspace structure (limited)
            structure = self.system_config.get_workspace_structure(max_depth=2, max_items=20)
            
            response = "📁 WORKSPACE INFORMATION\n"
            response += "=" * 50 + "\n"
            response += f"📍 Location: {structure['root']}\n"
            response += f"📊 Contents: {structure['total_files']} files, {structure['total_dirs']} directories\n\n"
            
            # Quick overview of file types
            if structure['file_types']:
                response += "📋 Main File Types:\n"
                sorted_types = sorted(structure['file_types'].items(), key=lambda x: x[1], reverse=True)
                for ext, count in sorted_types[:5]:
                    response += f"  {ext}: {count}\n"
                response += "\n"
            
            # Languages
            if structure['languages']:
                response += "💻 Programming Languages:\n"
                for lang in structure['languages']:
                    response += f"  • {lang}\n"
                response += "\n"
            
            # Quick suggestions
            response += "💡 QUICK COMMANDS:\n"
            response += "  • 'structure' - Full directory tree\n"
            response += "  • 'sysinfo' - System information\n"
            response += "  • 'shell <cmd>' - Execute shell command\n"
            response += "  • 'workspace <path>' - Change workspace\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error getting workspace info: {e}"
    
    def _handle_streaming_command(self, args: str) -> str:
        """Handle streaming configuration command"""
        try:
            if not args:
                # Show current streaming status
                status = "🟢 ENABLED" if self.enable_streaming else "🔴 DISABLED"
                response = f"🔄 STREAMING STATUS: {status}\n"
                response += "=" * 40 + "\n\n"
                
                if self.enable_streaming:
                    response += "🚀 Active Streaming Handlers:\n"
                    if self.enhanced_streaming:
                        response += "  ✅ EnhancedStreamingHandler (with progress)\n"
                    if self.advanced_streaming:
                        response += "  ✅ AdvancedStreamingHandler (with indicators)\n"
                    if self.streaming_handler:
                        response += "  ✅ StreamingResponseHandler (basic)\n"
                    
                    response += "\n💡 Features:\n"
                    response += "  • Real-time token streaming\n"
                    response += "  • Typing indicators\n"
                    response += "  • Performance metrics\n"
                    response += "  • Progress tracking\n"
                else:
                    response += "⚠️ Streaming is disabled - using blocking responses\n"
                
                response += "\n🔧 Commands:\n"
                response += "  streaming on    - Enable streaming\n"
                response += "  streaming off   - Disable streaming\n"
                response += "  streaming test  - Test streaming functionality\n"
                
                return response
            
            elif args.lower() == "on":
                self.enable_streaming = True
                return "✅ Streaming enabled! Responses will now stream in real-time."
            
            elif args.lower() == "off":
                self.enable_streaming = False
                return "⚠️ Streaming disabled. Responses will use blocking mode."
            
            elif args.lower() == "test":
                if not self.enable_streaming:
                    return "❌ Streaming is disabled. Enable it first with 'streaming on'"
                
                # Return a test message indicating streaming will be used
                return "🧪 Testing streaming functionality... Next response will demonstrate streaming."
            
            else:
                return f"❌ Unknown streaming command: {args}\nUse: streaming [on|off|test]"
                
        except Exception as e:
            return f"❌ Error handling streaming command: {e}"
    
    def _handle_startup_command(self, args: str = "") -> str:
        """Handle startup page/configuration command"""
        try:
            if not self.startup_interface:
                self.startup_interface = StartupInterface()
            
            if not args or args.lower() == "show":
                # Show current configuration
                config = self.startup_interface.load_existing_config()
                
                response = "🤖 AI HELPER AGENT - STARTUP CONFIGURATION\n"
                response += "=" * 50 + "\n\n"
                
                # Show configured models
                configured_count = 0
                for model_id, model_info in self.startup_interface.available_models.items():
                    key_name = model_info["key_name"]
                    has_key = key_name in config and config[key_name]
                    if has_key:
                        configured_count += 1
                        response += f"✅ {model_info['name']} ({model_info['provider'].title()})\n"
                
                if configured_count == 0:
                    response += "⚠️  No models configured yet\n"
                
                response += f"\n📊 Total configured models: {configured_count}/5\n"
                response += f"🔧 Current model: {self.model}\n"
                response += f"🗂️  Session: {self.session_id}\n"
                response += f"📁 Workspace: {self.workspace_path}\n"
                
                response += "\n🔧 Commands:\n"
                response += "  startup setup     - Run full configuration setup\n"
                response += "  startup quick     - Quick model selection\n"
                response += "  startup config    - Edit API keys\n"
                response += "  startup logo      - Show startup logo\n"
                
                return response
            
            elif args.lower() == "setup":
                response = "🚀 Starting full configuration setup...\n"
                response += "This will open the interactive startup interface.\n"
                response += "Use 'ai-helper --setup' command from terminal for best experience."
                return response
            
            elif args.lower() == "quick":
                response = "⚡ Quick setup available through startup interface.\n"
                response += "Use 'ai-helper' command from terminal to access quick setup."
                return response
            
            elif args.lower() == "config":
                config = self.startup_interface.load_existing_config()
                response = "🔑 API KEY CONFIGURATION\n"
                response += "=" * 30 + "\n\n"
                
                for model_id, model_info in self.startup_interface.available_models.items():
                    key_name = model_info["key_name"]
                    has_key = key_name in config and config[key_name]
                    status = "✅ Configured" if has_key else "❌ Missing"
                    response += f"{model_info['name']}: {status}\n"
                
                response += "\nTo configure API keys, use 'ai-helper --setup' from terminal."
                return response
            
            elif args.lower() == "logo":
                from .startup import ROBOT_LOGO, COMPACT_LOGO
                return f"\n{ROBOT_LOGO}\n🤖 AI Helper Agent - Your Coding Assistant!"
            
            else:
                return f"❌ Unknown startup command: {args}\nUse: startup [show|setup|quick|config|logo]"
                
        except Exception as e:
            return f"❌ Error handling startup command: {e}"
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} PB"
    
    def _handle_workspace_command(self, path: str) -> str:
        """Handle workspace change command"""
        try:
            new_path = Path(path).resolve()
            if new_path.exists() and new_path.is_dir():
                self.workspace_path = new_path
                
                # Reinitialize system config with new workspace
                if self.system_config:
                    self.system_config = SystemConfigurationManager(self.workspace_path)
                
                # Update prompt enhancer workspace
                if self.prompt_enhancer:
                    self.prompt_enhancer.workspace_path = self.workspace_path
                
                return f"📂 Workspace changed to: {self.workspace_path}\n✅ System configuration updated for new workspace"
            else:
                return f"❌ Directory not found: {path}"
        except Exception as e:
            return f"❌ Error changing workspace: {e}"
    
    def _get_help_text(self) -> str:
        """Get help text"""
        return f"""🤖 AI Helper Agent - Advanced Programming Assistant (Codex-like capabilities)

🚀 CODE GENERATION & COMPLETION:
  generate <description>    - Generate complete code from natural language
  complete <partial_code>   - Complete partially written code
  create <filename>         - Get help creating a new file
  
🔄 CODE TRANSFORMATION:
  translate <from> to <to> <code> - Convert code between languages
  refactor <code_or_file>   - Improve code structure and readability
  optimize <code_or_file>   - Optimize code for better performance
  
🐛 DEBUGGING & ANALYSIS:
  debug <code_or_file>      - Find and fix bugs in code
  analyze <filename>        - Analyze a code file for issues
  fix <filename>            - Get fixed version of a file
  explain <code_or_file>    - Explain code in plain English
  
📁 FILE OPERATIONS:
  save <filename> <content> - Save content to file in generated/ folder
  save <filename> last      - Save last AI response to file
  
🔍 SEARCH & DISCOVERY:
  search <pattern>          - Search for files by name pattern
  find <text>               - Search for text content in files
  
🏗️ SYSTEM & WORKSPACE:
  structure [depth] [items] - Show detailed workspace directory tree
  sysinfo                   - Display comprehensive system information
  workspace_info            - Quick workspace overview
  shell <command>           - Execute shell commands safely
  workspace <path>          - Change current workspace directory
  
💻 SHELL & CLI:
  shell <description>       - Generate shell/terminal commands from description
  
🛠️ MODEL & USER:
  model                     - Show current model and available options
  model <number>            - Change to different Groq model
  change_name "username"    - Change your username
  
� STREAMING CONTROL:
  streaming                 - Show streaming status and options
  streaming on              - Enable real-time streaming responses
  streaming off             - Disable streaming (use blocking mode)
  streaming test            - Test streaming functionality
  
�💬 NATURAL CONVERSATION:
  Just describe what you want to build or ask programming questions!
  Examples:
  - "Create a REST API with authentication"
  - "Build a data processing pipeline"
  - "Help me understand decorators in Python"
  - "Optimize this sorting algorithm"
  - "Convert this Python function to JavaScript"
  - "Show me the workspace structure"
  - "What's my system configuration?"
  
📚 ADVANCED FEATURES:
  • Multi-language support (Python, JS, TS, Go, Rust, Java, C++, etc.)
  • Intelligent code completion and generation
  • Cross-language code translation
  • Performance optimization suggestions
  • Security vulnerability detection
  • Best practices enforcement
  • System-aware workspace analysis
  • Safe shell command execution
  • Real-time directory structure visualization
  
💡 NEW SYSTEM COMMANDS:
  • structure - Visual workspace tree with file analysis
  • sysinfo - Complete system configuration details
  • shell <cmd> - Direct command execution with safety checks
  • workspace_info - Quick workspace overview
  
📋 Type 'quit' or 'exit' to end session
⚙️ SYSTEM:
  help or ?                 - Show this help
  quit, exit, bye           - Exit the program
  
🤖 Current Model: {self.model}
📂 Current workspace: {self.workspace_path}
🔄 Conversation history: Keeping last 8 messages with automatic trimming

💡 Pro Tips:
  • Use 'generate' for creating new code from scratch
  • Use 'complete' when you have partial code
  • Use 'translate' to convert between programming languages
  • Use 'explain' to understand complex code
  • Use 'debug' to find and fix issues
  • Use 'optimize' for performance improvements
  • Use 'shell' for command-line operations
  • All generated files are saved safely in 'generated/' folder

🎯 Example Commands:
  generate a web scraper for news articles
  complete def fibonacci(n):
  translate python to javascript print("hello")
  explain bubble_sort.py
  debug my_script.py
  optimize slow_function.py
  shell create a virtual environment"""
    
    def show_welcome(self):
        """Show welcome message"""
        print("\n🎉 Welcome to AI Helper Agent!")
        print("=" * 50)
        print("🚀 Your intelligent programming assistant with Codex-like capabilities")
        print(f"📂 Workspace: {self.workspace_path}")
        print(f"🔄 Session: {self.session_id}")
        print(f"🤖 Model: {self.model}")
        print("\nType 'help' for commands or just ask me anything!")
        print("Type 'quit' to exit")
        print("-" * 50)
    
    async def run_interactive_session(self):
        """Run the main interactive session"""
        self.show_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input("\n🔵 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thank you for using AI Helper Agent! Happy coding!")
                    break
                
                # Save user message to conversation history
                user_manager.save_conversation("user", user_input)
                
                # Process the input
                print("🤔 Thinking...")
                response = await self.handle_command(user_input)
                
                # Save AI response to conversation history  
                user_manager.save_conversation("assistant", response)
                
                print(f"\n🤖 AI Helper:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again or type 'help' for assistance.")
    
    async def start(self):
        """Start the CLI application"""
        try:
            # Check if we already have everything configured from startup
            already_configured = bool(self.api_key and self.llm)
            
            if not already_configured:
                # Only run setup if not already configured by multi-provider startup
                print("🔄 Running CLI setup (multi-provider startup didn't configure everything)...")
                
                if not self.setup_user_session():
                    return
                
                # Setup API key only if not already configured
                if not self.api_key and not self.setup_api_key():
                    return
                    
                # Setup LLM and chains only if not already configured
                if not self.llm and not self.setup_llm_and_chain():
                    return
            else:
                # Skip all setup if already configured
                print("✅ Multi-provider startup completed successfully!")
                print(f"🤖 Using model: {self.model}")
                print(f"🔑 API key: Configured")
                print(f"🚀 LLM instance: Ready")
                print("⚡ Setting up conversation chain and streaming...")
                
                # Setup conversation chain and streaming with existing LLM
                if not self.setup_conversation_chain():
                    print("❌ Failed to setup conversation chain")
                    return
                    
                print("✅ All components ready - starting interactive session...")
            
            # Start interactive session
            await self.run_interactive_session()
            
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            sys.exit(1)


def main():
    """Main entry point for the CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Interactive Programming Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper                          # Start with startup page
  ai-helper --setup                  # Force run startup configuration
  ai-helper --quick                  # Skip startup, use last config
  ai-helper --session mywork        # Start with named session
  ai-helper --workspace ./src        # Start in specific workspace
  ai-helper --model 2               # Start with specific model
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
        choices=list(AIHelperCLI.AVAILABLE_MODELS.keys()),
        help="Select Groq model to use"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Force run startup configuration interface"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true", 
        help="Skip startup interface and use existing configuration"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent CLI v1.0.3"
    )
    
    args = parser.parse_args()
    
    try:
        # Handle startup interface - show multi-provider selection unless quick mode
        selected_model = args.model
        api_key = None
        llm_instance = None  # Initialize to None
        
        # Always show startup interface unless explicitly using quick mode
        if not args.quick:
            # Run startup interface for multi-provider selection
            startup = MultiProviderStartup()  # Use the enhanced multi-provider startup
            
            if args.setup:
                # Force full setup with logo and provider selection
                model_name, api_key, llm_instance = startup.run_startup_sequence()
            else:
                # Show startup page but allow quick API key entry
                startup.display_responsive_logo()
                print("\n🚀 Welcome to AI Helper Agent - Multi-Provider AI Assistant")
                print("Choose from Groq, OpenAI, Anthropic, Google, and Local models!\n")
                
                # Quick check if user wants to use existing config
                existing_groq_key = os.getenv("GROQ_API_KEY")
                if existing_groq_key:
                    from rich.prompt import Confirm
                    use_existing = Confirm.ask("Use existing Groq configuration for quick start?")
                    if use_existing:
                        model_name = "llama-3.1-8b-instant"  # Default fast model
                        api_key = existing_groq_key
                        # Create the LLM instance directly to avoid further prompting
                        try:
                            llm_instance = ChatGroq(
                                model=model_name,
                                temperature=0.1,
                                api_key=api_key
                            )
                            print(f"✅ Using existing Groq API key with {model_name}")
                        except Exception as e:
                            print(f"❌ Error creating LLM instance: {e}")
                            # Fall back to full startup
                            model_name, api_key, llm_instance = startup.run_startup_sequence()
                    else:
                        # Run full startup sequence
                        model_name, api_key, llm_instance = startup.run_startup_sequence()
                else:
                    # No existing config, run full startup
                    model_name, api_key, llm_instance = startup.run_startup_sequence()
        else:
            # Quick mode - use existing environment variables
            api_key = os.getenv("GROQ_API_KEY")
            model_name = None
            llm_instance = None  # Will be created later if needed
            
            if not api_key:
                print("❌ Quick mode requires existing API key configuration")
                print("Run without --quick to configure providers")
                sys.exit(1)
        
        # Convert startup model format to CLI model format if needed
        if model_name and not selected_model:
            # Map startup model names to CLI model keys
            for key, description in AIHelperCLI.AVAILABLE_MODELS.items():
                if model_name.lower() in description.lower() or key in model_name:
                    selected_model = key
                    break
            
            # If no match found, use the model_name directly
            if not selected_model:
                selected_model = model_name
        
        # Create CLI instance with model and API key from startup
        cli = AIHelperCLI(session_id=args.session, model=selected_model or model_name)
        
        # Set API key and LLM instance if configured via startup (this prevents additional prompting)
        if api_key:
            cli.api_key = api_key
            # Also set in environment for consistency
            os.environ["GROQ_API_KEY"] = api_key
        
        # Set LLM instance if created during startup
        if llm_instance:
            cli.llm = llm_instance
            print(f"✅ Pre-configured LLM instance ready")
            
            # Initialize essential CLI components that would normally be set in setup_user_session
            # Since we're skipping user session setup, we need to initialize these here
            try:
                # Initialize enhanced prompt system (minimal setup without username prompt)
                cli.prompt_enhancer = AdvancedPromptEnhancer(
                    username="user",  # Use default username since we're skipping user setup
                    workspace_path=cli.workspace_path,
                    model=cli.model
                )
                
                # Initialize system configuration manager
                cli.system_config = SystemConfigurationManager(cli.workspace_path)
                
                print("✅ Essential CLI components initialized")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize some CLI components: {e}")
        
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
