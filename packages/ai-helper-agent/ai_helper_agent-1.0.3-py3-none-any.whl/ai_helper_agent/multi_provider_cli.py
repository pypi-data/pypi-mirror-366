"""
AI Helper Agent - Multi-Provider LLM Integration
Enhanced CLI with support for Groq, OpenAI, Anthropic, Google, and Ollama
"""

import os
import sys
import asyncio
import getpass
from typing import Dict, Any, Optional, Union
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

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}


class MultiProviderAIHelperCLI:
    """Enhanced CLI with multi-provider LLM support and responsive design"""
    
    def __init__(self, session_id: str = "default", model: str = None, skip_startup: bool = False):
        self.session_id = session_id
        self.api_key: Optional[str] = None
        self.llm: Optional[Union[ChatGroq, ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama]] = None
        self.chain = None
        self.workspace_path = Path.cwd()
        self.model = model
        self.provider = None
        
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
        
        # Multi-provider startup interface
        self.startup_interface: Optional[MultiProviderStartup] = None
        self.skip_startup = skip_startup
        self.enable_streaming: bool = True
        
        # Model configuration
        self.model_config = {}
        
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
            print("""
🤖 AI HELPER AGENT v2.0 🤖
Multi-Provider AI Assistant
⚡ Lightning-Fast Responses ⚡
            """)
    
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
        elif ChatOllama and isinstance(llm, ChatOllama):
            return "ollama"
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
                print("🔑 Please enter your Groq API key:")
                print("Get your key from: https://console.groq.com/keys")
                self.api_key = getpass.getpass("Groq API Key: ")
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("🔑 Please enter your OpenAI API key:")
                print("Get your key from: https://platform.openai.com/api-keys")
                self.api_key = getpass.getpass("OpenAI API Key: ")
        elif self.provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                print("🔑 Please enter your Anthropic API key:")
                print("Get your key from: https://console.anthropic.com/")
                self.api_key = getpass.getpass("Anthropic API Key: ")
        elif self.provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                print("🔑 Please enter your Google API key:")
                print("Get your key from: https://makersuite.google.com/app/apikey")
                self.api_key = getpass.getpass("Google API Key: ")
        elif self.provider == "ollama":
            # No API key needed for local Ollama
            pass
        
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
            elif self.provider == "ollama" and ChatOllama:
                self.llm = ChatOllama(
                    model=self.model,
                    temperature=0.1
                )
            else:
                print(f"❌ Provider {self.provider} not available or not installed")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Failed to create {self.provider} LLM: {e}")
            return False
    
    def test_api_key_and_model(self) -> bool:
        \"\"\"Test API key and model with the current provider\"\"\"
        try:
            if not self.llm:
                if not self.create_llm_instance():
                    return False
            
            print(f"🔄 Testing {self.provider.upper()} connection with model {self.model}...")
            response = self.llm.invoke([HumanMessage(content="Hello")])
            
            if response and response.content:
                print(f"✅ {self.provider.upper()} connection successful!")
                # Store in environment for this session
                if self.api_key:
                    os.environ[f"{self.provider.upper()}_API_KEY"] = self.api_key
                return True
            else:
                print(f"❌ Invalid configuration for {self.provider}. Please try again.")
                return False
                
        except Exception as e:
            print(f"❌ Error testing {self.provider} connection: {e}")
            print("Please check your settings and try again.")
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
            
            print(f"✅ AI Helper Agent initialized with {self.provider.upper()}!")
            print("🔄 Enhanced streaming mode enabled for real-time responses")
            print(f"🚀 Using model: {self.model}")
            
        except Exception as e:
            print(f"❌ Failed to initialize AI Helper: {e}")
            return False
        
        return True
    
    def _get_system_prompt(self) -> str:
        \"\"\"Get system prompt for the AI assistant\"\"\"
        return f\"\"\"You are an AI Helper Agent, a sophisticated coding assistant powered by {self.provider.upper()}.

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

Please provide helpful, accurate, and well-structured responses to assist with coding and development tasks.\"\"\"
    
    def switch_provider(self, new_provider: str, new_model: str = None, new_api_key: str = None):
        \"\"\"Switch to a different AI provider\"\"\"
        print(f"🔄 Switching from {self.provider} to {new_provider}...")
        
        self.provider = new_provider
        if new_model:
            self.model = new_model
        if new_api_key:
            self.api_key = new_api_key
        
        # Reinitialize LLM and chain
        if self.setup_llm_and_chain():
            print(f"✅ Successfully switched to {new_provider.upper()}")
        else:
            print(f"❌ Failed to switch to {new_provider}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        \"\"\"Get current provider information\"\"\"
        return {
            "provider": self.provider,
            "model": self.model,
            "has_api_key": bool(self.api_key),
            "llm_type": type(self.llm).__name__ if self.llm else None,
            "streaming_enabled": self.enable_streaming
        }


# Backwards compatibility alias
AIHelperCLI = MultiProviderAIHelperCLI
