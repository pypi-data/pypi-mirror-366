"""
AI Helper Agent - Enhanced CLI with File Input and Thinking Indicator
Fixed duplicate display issues and added comprehensive file support
"""

import os
import sys
import asyncio
import time
import getpass
import re
import warnings
import argparse
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path
from datetime import datetime

# Filter out warnings to keep CLI clean
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
warnings.filterwarnings("ignore", message=".*avconv.*")
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*")
warnings.filterwarnings("ignore", module="pydub")

# Lazy loading globals - initialized to None
ChatGroq = None
ChatOpenAI = None
ChatAnthropic = None
ChatGoogleGenerativeAI = None
ChatOllama = None
ChatMessageHistory = None
BaseChatMessageHistory = None
RunnableWithMessageHistory = None 
RunnableLambda = None
RunnablePassthrough = None
SystemMessage = None
HumanMessage = None
AIMessage = None
trim_messages = None
ChatPromptTemplate = None
MessagesPlaceholder = None
StrOutputParser = None

if TYPE_CHECKING:
    from langchain_groq import ChatGroq
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import ChatOllama
    from langchain_community.chat_message_histories import ChatMessageHistory
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from ..core.core import InteractiveAgent
    from ..core.config import config
    from ..core.security import security_manager
    from ..managers.user_manager import user_manager
    from ..utils.prompt_enhancer import AdvancedPromptEnhancer
    from ..core.system_config import SystemConfigurationManager

# Lazy loading for internal modules - these are the heavy ones!
InteractiveAgent = None
config = None
security_manager = None
user_manager = None
AdvancedPromptEnhancer = None
# Lazy loading for internal modules - these are the heavy ones!
InteractiveAgent = None
config = None
security_manager = None
user_manager = None
AdvancedPromptEnhancer = None
SystemConfigurationManager = None

# Lazy loading for utilities - these can also be heavy
StreamingResponseHandler = None
AdvancedStreamingHandler = None
CustomStreamingCallback = None
EnhancedStreamingHandler = None
get_simple_logo = None
display_cli_header = None
MultiProviderStartup = None
file_handler = None

# Lazy loading for managers
api_key_manager = None
conversation_manager = None
MessageRole = None
rich_formatter = None

def _ensure_utilities_loaded():
    """Lazy load utilities and managers when needed"""
    global StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
    global get_simple_logo, display_cli_header, MultiProviderStartup, file_handler
    global api_key_manager, conversation_manager, MessageRole, rich_formatter
    
    if StreamingResponseHandler is None:
        try:
            from ..utils.streaming import StreamingResponseHandler, AdvancedStreamingHandler, CustomStreamingCallback, EnhancedStreamingHandler
            from ..utilities.simple_logo import get_simple_logo, display_cli_header
            from .multi_provider_startup import MultiProviderStartup
            from ..utils.file_handler import file_handler
            from ..managers.api_key_manager import api_key_manager
            from ..managers.conversation_manager import conversation_manager, MessageRole
            from ..utils.rich_formatting import rich_formatter
        except ImportError:
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
                def print_divider(self): print("-" * 50)
                def print_header(self, title): print(f"\n=== {title} ===\n")
                def setup_logging(self): pass
            
            class DummyStreamingHandler:
                def __init__(self, *args, **kwargs): pass
                def stream_response(self, *args, **kwargs): return "Response"
            
            class DummyFileHandler:
                def read_file(self, *args, **kwargs): return "File content"
            
            def dummy_logo(): return "AI Helper Agent"
            def dummy_header(title): print(f"=== {title} ===")
            
            api_key_manager = DummyAPIKeyManager()
            conversation_manager = DummyConversationManager()
            rich_formatter = DummyRichFormatter()
            StreamingResponseHandler = DummyStreamingHandler
            AdvancedStreamingHandler = DummyStreamingHandler
            CustomStreamingCallback = DummyStreamingHandler
            EnhancedStreamingHandler = DummyStreamingHandler
            file_handler = DummyFileHandler()
            get_simple_logo = dummy_logo
            display_cli_header = dummy_header
            MultiProviderStartup = object


def _ensure_classes_loaded():
    """Lazy load all LangChain classes when needed"""
    global ChatGroq, ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama
    global ChatMessageHistory, BaseChatMessageHistory, RunnableWithMessageHistory
    global RunnableLambda, RunnablePassthrough, SystemMessage, HumanMessage, AIMessage
    global trim_messages, ChatPromptTemplate, MessagesPlaceholder, StrOutputParser
    global InteractiveAgent, config, security_manager, user_manager
    global AdvancedPromptEnhancer, SystemConfigurationManager
    
    if ChatGroq is None:
        from langchain_groq import ChatGroq
        
    if ChatMessageHistory is None:
        from langchain_community.chat_message_histories import ChatMessageHistory
        from langchain_core.chat_history import BaseChatMessageHistory
        from langchain_core.runnables.history import RunnableWithMessageHistory
        from langchain_core.runnables import RunnableLambda, RunnablePassthrough
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        
    # Lazy load internal modules - these are heavy!
    if InteractiveAgent is None:
        from ..core.core import InteractiveAgent
        from ..core.config import config
        from ..core.security import security_manager
        from ..managers.user_manager import user_manager
        from ..utils.prompt_enhancer import AdvancedPromptEnhancer
        from ..core.system_config import SystemConfigurationManager
        
    if ChatOpenAI is None:
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            ChatOpenAI = None
            
    if ChatAnthropic is None:
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            ChatAnthropic = None
            
    if ChatGoogleGenerativeAI is None:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            ChatGoogleGenerativeAI = None
            
    if ChatOllama is None:
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            ChatOllama = None


# Global conversation store
conversation_store: Dict[str, Any] = {}  # type: ignore


class EnhancedMultiProviderCLI:
    """Enhanced CLI with file input, thinking indicator, and fixed display issues"""
    
    def __init__(self, session_id: str = "default", model: str = None, skip_startup: bool = False):
        self.session_id = f"enhanced_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.model = model or "llama-3.1-8b-instant"
        self.provider = "groq"
        self.api_key = None
        self.llm = None
        self.chain = None
        self.skip_startup = skip_startup
        self.workspace_path = Path(".")
        
        # Check if we're in help mode (avoid heavy initialization)
        self.help_mode = '--help' in sys.argv or '-h' in sys.argv
        
        # Initialize components (only if not in help mode)
        if not self.help_mode:
            # Load utilities and managers when needed
            _ensure_utilities_loaded()
            _ensure_classes_loaded()
            
            self.user_manager = user_manager
            self.security_manager = security_manager
            self.system_config = SystemConfigurationManager()
            self.prompt_enhancer = AdvancedPromptEnhancer(workspace_path=self.workspace_path)
            self.conversation_manager = conversation_manager
            self.rich_formatter = rich_formatter
            
            # Streaming components
            self.streaming_handler: Optional[Any] = None  # type: ignore
            self.advanced_streaming: Optional[Any] = None  # type: ignore
            self.enhanced_streaming: Optional[Any] = None  # type: ignore
            
            # Configure Rich formatter (only when not in help mode)
            self.streaming_enabled = True
            
            # Multi-provider startup interface
            if not self.skip_startup:
                self.startup_interface = MultiProviderStartup()
        else:
            # Minimal initialization for help mode
            self.rich_formatter = rich_formatter
        
        # File processing state
        self.current_files: Dict[str, Any] = {}
        self.file_context = ""
        
        # Display control - prevent duplicate AI Agent messages
        self.last_display_time = 0
        self.display_cooldown = 0.5  # 500ms cooldown between displays
        
    def get_session_history(self, session_id: str) -> Any:  # type: ignore
        """Get or create session history"""
        _ensure_classes_loaded()
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show enhanced splash screen with simple logo"""  
        if hasattr(self, 'startup_interface'):
            self.startup_interface.display_responsive_logo()
        else:
            display_cli_header(
                "AI HELPER AGENT v2.0",
                "YOUR AUTONOMOUS CODING ASSISTANT"
            )
    
    def setup_user_session(self) -> bool:
        """Setup user session with startup interface"""
        # Skip setup in help mode
        if hasattr(self, 'help_mode') and self.help_mode:
            return True
            
        try:
            # Show splash screen
            self.show_splash_screen()
            
            if not self.skip_startup and hasattr(self, 'startup_interface') and self.startup_interface:
                # Use multi-provider startup interface
                print("🔄 Setting up multi-provider interface...")
                result = self.startup_interface.run_multi_provider_setup()
                
                if result and "llm_instance" in result:
                    self.llm = result["llm_instance"]
                    self.model = result.get("model_id", self.model)
                    self.provider = result.get("provider", self.provider)
                    self.api_key = result.get("api_key")
                    
                    # Setup conversation chain
                    self.setup_llm_and_chain()
                    return True
                else:
                    print("⚠️ Setup failed or cancelled, using fallback")
                    return self.setup_fallback_llm()
            else:
                # Quick start - skip complex setup
                print("⚡ Quick start mode - using fallback setup")
                return self.setup_fallback_llm()
                
        except Exception as e:
            print(f"❌ Error in user session setup: {e}")
            return self.setup_fallback_llm()
    
    def setup_fallback_llm(self) -> bool:
        """Fallback LLM setup for cases where startup interface fails"""
        try:
            _ensure_classes_loaded()
            # Try API key manager first, then environment
            api_key = api_key_manager.get_api_key('groq')
            if not api_key:
                api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                api_key = getpass.getpass("🔑 Enter your Groq API key: ")
                
            self.api_key = api_key
            self.llm = ChatGroq(model=self.model, api_key=api_key, temperature=0.1)
            self.setup_llm_and_chain()
            return True
            
        except Exception as e:
            print(f"❌ Fallback setup failed: {e}")
            return False
    
    def setup_llm_and_chain(self):
        """Setup LLM and conversation chain with enhanced features"""
        _ensure_classes_loaded()
        if not self.llm:
            raise ValueError("LLM not initialized")
            
        # Initialize streaming handlers
        if self.streaming_enabled:
            self.streaming_handler = StreamingResponseHandler(self.llm)
            self.advanced_streaming = AdvancedStreamingHandler(self.llm, None)
            
        # Create enhanced system prompt
        system_prompt = self._get_system_prompt()
        
        # Create the conversation chain with message history
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Create the chain with message trimming for long conversations
        chain = prompt | self.llm | StrOutputParser()
        
        # Add conversation history
        self.chain = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        
        print(f"✅ Setup complete! Using {self.provider.upper()} - {self.model}")
        
    def _get_system_prompt(self) -> str:
        """Get the enhanced system prompt with file processing capabilities"""
        base_prompt = f"""You are AI Helper Agent v2.0.1, an expert programming assistant created by Meet Solanki, an AIML Student.

🌟 ABOUT THIS SYSTEM:
- Name: AI Helper Agent v2.0.1
- Creator: Meet Solanki (AIML Student)
- Purpose: Advanced programming assistance with file processing
- Mission: Empowering developers with intelligent code analysis and file operations

👨‍💻 CREATOR'S VISION:
This enhanced system was developed by Meet Solanki to provide comprehensive programming assistance that goes beyond simple code generation to include intelligent file processing and analysis.

🔧 CODE ANALYSIS & DEBUGGING
- Analyze Python, JavaScript, TypeScript, and other programming languages
- Identify syntax errors, logic bugs, and performance issues  
- Provide complete, working fixes with explanations

📁 ENHANCED FILE OPERATIONS
- Process multiple file formats (.py, .js, .ts, .java, .cpp, .c, .txt, .md, .json, .csv, .yaml, .xml)
- Read and analyze document files (.pdf, .docx)
- Handle structured data (CSV, JSON, YAML, XML)
- Provide intelligent file content analysis and suggestions

🤖 INTELLIGENT ASSISTANCE
- Provide contextual help based on file content
- Suggest improvements and optimizations
- Generate code examples and documentation
- Debug and fix code issues
- Help users learn and understand code better

CURRENT SESSION INFO:
- Model: {self.model} ({self.provider.upper()})
- Workspace: {self.workspace_path}
- File Processing: Enabled
- Streaming: {'Enabled' if self.streaming_enabled else 'Disabled'}

FILE COMMANDS:
- Type 'read <filepath>' to read and analyze any supported file
- Type 'files' to see supported file types and current directory files
- Type 'analyze <filepath>' for deep file analysis
- Files are automatically processed and their content is available in our conversation

INTERACTION RULES:
1. Always provide clear, helpful responses
2. Show code examples when relevant
3. Explain your reasoning step by step
4. Ask clarifying questions when needed
5. Be concise but thorough
6. Help users learn and improve their coding skills

💡 HELPING YOU SUCCEED:
As created by Meet Solanki (AIML Student), I'm here to make you a better developer through intelligent file analysis and coding assistance. Let's explore your code together! 🚀

Ready to assist with your coding and file analysis needs!"""
        
        if self.file_context:
            base_prompt += f"\n\nCURRENT FILE CONTEXT:\n{self.file_context}"
            
        return base_prompt
    
    def show_thinking_indicator(self, message: str = "Thinking..."):
        """Show animated thinking indicator"""
        current_time = time.time()
        if current_time - self.last_display_time < self.display_cooldown:
            return  # Skip if too soon after last display
            
        indicators = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        # Show thinking for a brief moment
        for i in range(10):  # Show for about 1 second
            print(f"\r🤖 {indicators[i % len(indicators)]} {message}", end="", flush=True)
            time.sleep(0.1)
            
        print(f"\r🤖 {message} ✓", end="", flush=True)
        print()  # New line
        self.last_display_time = time.time()
    
    def process_file_command(self, user_input: str) -> Optional[str]:
        """Process file-related commands"""
        input_lower = user_input.lower().strip()
        
        # Read file command
        if input_lower.startswith('read '):
            file_path = user_input[5:].strip()
            return self.read_file(file_path)
            
        # Analyze file command  
        elif input_lower.startswith('analyze '):
            file_path = user_input[8:].strip()
            return self.analyze_file(file_path)
            
        # List files command
        elif input_lower in ['files', 'list files', 'show files']:
            return self.list_files()
            
        # File help command
        elif input_lower in ['file help', 'files help']:
            return self.show_file_help()
            
        return None
    
    def read_file(self, file_path: str) -> str:
        """Read and process a file"""
        try:
            self.show_thinking_indicator("Reading file...")
            
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
                
            response += f"\n**Content:**\n```{file_info.get('file_type', 'text')}\n{content[:2000]}{'...' if len(content) > 2000 else ''}\n```\n"
            response += "\n✅ File content is now available in our conversation context. You can ask questions about it!"
            
            return response
            
        except Exception as e:
            return f"❌ Error processing file: {str(e)}"
    
    def analyze_file(self, file_path: str) -> str:
        """Perform deep analysis of a file"""
        try:
            self.show_thinking_indicator("Analyzing file...")
            
            # First read the file
            read_result = self.read_file(file_path)
            if read_result.startswith("❌"):
                return read_result
                
            # Get file data
            file_data = self.current_files.get(file_path)
            if not file_data:
                return "❌ File not found in current context"
                
            file_info = file_data.get('file_info', {})
            content = file_data.get('content', '')
            
            # Perform analysis based on file type
            file_type = file_info.get('file_type', 'unknown')
            
            analysis = f"🔍 **Deep Analysis: {file_path}**\n\n"
            
            # Basic file statistics
            analysis += f"**File Statistics:**\n"
            analysis += f"- Type: {file_type}\n"
            analysis += f"- Size: {file_info.get('size_human', 'unknown')}\n"
            analysis += f"- Encoding: {file_data.get('encoding', 'unknown')}\n"
            
            if 'lines' in file_data:
                analysis += f"- Lines: {file_data['lines']}\n"
            if 'words' in file_data:
                analysis += f"- Words: {file_data['words']}\n"
            if 'characters' in file_data:
                analysis += f"- Characters: {file_data['characters']}\n"
                
            # Type-specific analysis
            if file_type == 'python':
                analysis += self._analyze_python_file(content)
            elif file_type in ['javascript', 'typescript']:
                analysis += self._analyze_js_file(content)
            elif file_type == 'json':
                analysis += self._analyze_json_file(file_data)
            elif file_type == 'csv':
                analysis += self._analyze_csv_file(file_data)
            else:
                analysis += self._analyze_generic_file(content, file_type)
                
            return analysis
            
        except Exception as e:
            return f"❌ Error analyzing file: {str(e)}"
    
    def _analyze_python_file(self, content: str) -> str:
        """Analyze Python file content"""
        analysis = "\n**Python Code Analysis:**\n"
        
        # Count different elements
        lines = content.split('\n')
        imports = len([l for l in lines if l.strip().startswith(('import ', 'from '))])
        functions = len([l for l in lines if l.strip().startswith('def ')])
        classes = len([l for l in lines if l.strip().startswith('class ')])
        comments = len([l for l in lines if l.strip().startswith('#')])
        
        analysis += f"- Import statements: {imports}\n"
        analysis += f"- Functions: {functions}\n" 
        analysis += f"- Classes: {classes}\n"
        analysis += f"- Comments: {comments}\n"
        
        # Check for common patterns
        if 'if __name__ == "__main__"' in content:
            analysis += "- Has main execution block ✅\n"
        if 'try:' in content:
            analysis += "- Uses exception handling ✅\n"
        if 'logging' in content:
            analysis += "- Uses logging ✅\n"
            
        return analysis
    
    def _analyze_js_file(self, content: str) -> str:
        """Analyze JavaScript/TypeScript file content"""
        analysis = "\n**JavaScript/TypeScript Analysis:**\n"
        
        lines = content.split('\n')
        functions = len([l for l in lines if 'function' in l or '=>' in l])
        classes = len([l for l in lines if l.strip().startswith('class ')])
        imports = len([l for l in lines if l.strip().startswith(('import ', 'const ', 'require('))])
        
        analysis += f"- Functions: {functions}\n"
        analysis += f"- Classes: {classes}\n"
        analysis += f"- Import/Require statements: {imports}\n"
        
        if 'async' in content:
            analysis += "- Uses async/await ✅\n"
        if 'Promise' in content:
            analysis += "- Uses Promises ✅\n"
            
        return analysis
    
    def _analyze_json_file(self, file_data: Dict) -> str:
        """Analyze JSON file"""
        analysis = "\n**JSON Analysis:**\n"
        
        if 'parsed_data' in file_data:
            data = file_data['parsed_data']
            analysis += f"- Data type: {type(data).__name__}\n"
            
            if isinstance(data, dict):
                analysis += f"- Keys: {len(data)}\n"
                analysis += f"- Top-level keys: {list(data.keys())[:10]}\n"
            elif isinstance(data, list):
                analysis += f"- Array length: {len(data)}\n"
                
        return analysis
    
    def _analyze_csv_file(self, file_data: Dict) -> str:
        """Analyze CSV file"""
        analysis = "\n**CSV Analysis:**\n"
        
        if 'csv_info' in file_data:
            csv_info = file_data['csv_info']
            analysis += f"- Rows: {csv_info.get('row_count', 0)}\n"
            analysis += f"- Columns: {csv_info.get('column_count', 0)}\n"
            analysis += f"- Column names: {csv_info.get('columns', [])}\n"
            analysis += f"- Delimiter: '{csv_info.get('delimiter', ',')}'\n"
            
        return analysis
    
    def _analyze_generic_file(self, content: str, file_type: str) -> str:
        """Generic file analysis"""
        analysis = f"\n**{file_type.title()} File Analysis:**\n"
        
        lines = content.split('\n')
        empty_lines = len([l for l in lines if not l.strip()])
        analysis += f"- Empty lines: {empty_lines}\n"
        
        # Look for common patterns
        if file_type == 'markdown':
            headers = len([l for l in lines if l.strip().startswith('#')])
            analysis += f"- Headers: {headers}\n"
            
        return analysis
    
    def list_files(self) -> str:
        """List supported files in current directory"""
        try:
            self.show_thinking_indicator("Listing files...")
            
            suggestions = file_handler.get_file_suggestions(str(self.workspace_path))
            
            if not suggestions:
                return "📁 No supported files found in current directory"
                
            response = "📁 **Supported Files in Current Directory:**\n\n"
            
            # Group by file type
            by_type = {}
            for file_info in suggestions[:50]:  # Limit to 50 files
                file_type = file_info['type']
                if file_type not in by_type:
                    by_type[file_type] = []
                by_type[file_type].append(file_info)
                
            for file_type, files in by_type.items():
                response += f"**{file_type.upper()} Files:**\n"
                for file_info in files[:10]:  # Limit to 10 per type
                    response += f"- {file_info['relative_path']} ({file_info['size']})\n"
                if len(files) > 10:
                    response += f"... and {len(files) - 10} more\n"
                response += "\n"
                
            response += "💡 Use 'read <filepath>' to read any file or 'analyze <filepath>' for detailed analysis!"
            
            return response
            
        except Exception as e:
            return f"❌ Error listing files: {str(e)}"
    
    def show_file_help(self) -> str:
        """Show file command help"""
        return """📁 **File Processing Commands:**

**Basic Commands:**
- `read <filepath>` - Read and display file content
- `analyze <filepath>` - Perform deep analysis of file
- `files` - List all supported files in current directory
- `file help` - Show this help message

**Supported File Types:**
- **Code:** .py, .js, .ts, .html, .css, .java, .cpp, .c, .cs, .php, .rb, .go, .rs, .sql
- **Text:** .txt, .md, .rst, .log
- **Data:** .json, .yaml, .yml, .csv, .xml
- **Documents:** .pdf, .docx
- **Config:** .ini, .cfg, .env, .conf, .toml
- **Database:** .sqlite, .db

**Examples:**
- `read myfile.py` - Read Python file
- `analyze data.csv` - Analyze CSV data file
- `read config.json` - Read JSON configuration
- `files` - Show all files in current directory

**Features:**
- Automatic file type detection
- Content analysis and statistics
- Security checks for file access
- Support for large files (up to 50MB)
- Multiple encoding detection

💡 **Tip:** After reading a file, you can ask questions about its content!"""
    
    async def get_response(self, user_input: str) -> str:
        """Get AI response with enhanced processing"""
        try:
            # Check for file commands first
            file_response = self.process_file_command(user_input)
            if file_response:
                return file_response
                
            # Show thinking indicator for AI processing
            self.show_thinking_indicator("Processing your request...")
            
            # Enhance input with file context if available
            enhanced_input = user_input
            if self.file_context:
                enhanced_input = f"[File Context: {self.file_context}]\n\nUser: {user_input}"
            
            # Use streaming if available
            if self.streaming_enabled and self.streaming_handler:
                print("🤖 ", end="", flush=True)  # Single AI indicator
                response = await self.streaming_handler.stream_generate(
                    enhanced_input, 
                    {"configurable": {"session_id": self.session_id}}
                )
                print()  # New line after streaming
                return response
            else:
                # Non-streaming response
                response = self.chain.invoke(
                    {"input": enhanced_input},
                    config={"configurable": {"session_id": self.session_id}}
                )
                return response
                
        except Exception as e:
            return f"❌ Error getting response: {str(e)}"
    
    def show_help(self) -> str:
        """Show comprehensive help"""
        return """🤖 **AI Helper Agent - Multi-Provider CLI**

**Basic Commands:**
- `help` - Show this help message
- `exit` or `quit` - Exit the application
- `clear` - Clear conversation history
- `model` - Show current model information

**File Operations:**
- `read <file>` - Read and analyze any supported file
- `analyze <file>` - Deep analysis with statistics
- `files` - List supported files in directory
- `file help` - Detailed file processing help

**AI Capabilities:**
- Code analysis and debugging
- File content processing
- Multi-language support
- Real-time assistance

**Current Configuration:**
- Model: {self.model}
- Provider: {self.provider.upper()}
- Streaming: {'Enabled' if self.streaming_enabled else 'Disabled'}
- File Processing: Enabled
- Workspace: {self.workspace_path}

**Examples:**
- "read mycode.py" - Analyze Python file
- "debug this function" - Get debugging help
- "explain the CSV data" - After reading a CSV file
- "optimize this algorithm" - Code optimization

💡 **Pro Tips:**
- Files are automatically added to conversation context
- Ask follow-up questions about file content
- Use specific file paths or drag-and-drop files
- Combine file analysis with coding questions"""
    
    async def start(self):
        """Start the enhanced CLI with file support"""
        try:
            # Setup user session
            if not self.setup_user_session():
                print("❌ Failed to setup session. Exiting.")
                return
                
            print(f"\n✅ **AI Helper Agent Ready!**")
            print(f"📂 Workspace: {self.workspace_path}")
            print(f"🤖 Model: {self.model} ({self.provider.upper()})")
            print(f"📁 File Processing: Enabled")
            print("💡 Type 'help' for commands or 'files' to see available files\n")
            
            # Main interaction loop
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        continue
                        
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        print("👋 Goodbye!")
                        break
                        
                    elif user_input.lower() == 'help':
                        print(self.show_help())
                        continue
                        
                    elif user_input.lower() == 'clear':
                        conversation_store[self.session_id] = ChatMessageHistory()
                        print("🗑️ Conversation history cleared!")
                        continue
                        
                    elif user_input.lower() == 'model':
                        print(f"🤖 Current Model: {self.model} ({self.provider.upper()})")
                        continue
                        
                    # Get AI response
                    response = await self.get_response(user_input)
                    
                    # Display response (only once, avoid duplicates)
                    if not self.streaming_enabled:
                        print(f"🤖 {response}")
                        
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Failed to start CLI: {str(e)}")


# Backward compatibility
class MultiProviderCLI(EnhancedMultiProviderCLI):
    """Backward compatibility wrapper"""
    pass


def show_rich_help():
    """Show Rich-formatted help for Enhanced CLI"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        
        console = Console()
        
        # Main title
        console.print("\n")
        console.print(Panel.fit(
            "[bold blue]AI Helper Agent - Enhanced CLI[/bold blue]\n"
            "[dim]🔧 Advanced features with file processing and multi-provider support[/dim]",
            border_style="blue"
        ))
        
        # Usage section
        console.print("\n[bold green]USAGE:[/bold green]")
        console.print("  [cyan]ai-advanced[/cyan] [dim][options][/dim]")
        
        # Commands table
        commands_table = Table(
            title="🚀 Available Commands",
            show_header=True, 
            header_style="bold magenta",
            width=100,
            expand=False,
            show_lines=True
        )
        commands_table.add_column("Command", style="cyan", width=25)
        commands_table.add_column("Aliases", style="green", width=20)
        commands_table.add_column("Description", style="white", width=45)
        
        commands_table.add_row("ai-advanced", "ai-dev, ai-expert", "Start enhanced CLI with all features")
        commands_table.add_row("ai-advanced --quick", "ai-dev --quick", "Skip startup, use existing config")
        commands_table.add_row("ai-advanced --session NAME", "ai-expert -s NAME", "Start with named session")
        
        console.print("\n[bold green]COMMANDS:[/bold green]")
        console.print(commands_table)
        
        # Features table
        features_table = Table(
            title="🌟 Enhanced Features",
            show_header=True, 
            header_style="bold gold1",
            width=90,
            expand=False,
            show_lines=True
        )
        features_table.add_column("Feature", style="bold white", width=25)
        features_table.add_column("Description", style="white", width=55)
        
        features_table.add_row("📁 File Processing", "Analyze and process files in your workspace")
        features_table.add_row("🤖 Multi-Provider", "Access Groq, OpenAI, Anthropic, and Google AI")
        features_table.add_row("🔍 Code Analysis", "Deep code review and analysis capabilities")
        features_table.add_row("🎨 Rich Formatting", "Beautiful syntax highlighting and markdown")
        features_table.add_row("💾 Session Memory", "Persistent conversation history")
        features_table.add_row("⚡ Streaming", "Real-time response streaming")
        
        console.print("\n[bold green]FEATURES:[/bold green]")
        console.print(features_table)
        
        # Options table
        options_table = Table(
            show_header=True, 
            header_style="bold magenta",
            width=80,
            expand=False,
            show_lines=True
        )
        options_table.add_column("Option", style="cyan", width=18)
        options_table.add_column("Description", style="white", width=50)
        
        options_table.add_row("-h, --help", "Show this help message and exit")
        options_table.add_row("-s, --session ID", "Session ID for conversation history")
        options_table.add_row("-m, --model NAME", "Model to use with selected provider")
        options_table.add_row("--quick", "Skip startup interface")
        options_table.add_row("--version, -v", "Show version information")
        
        console.print("\n[bold green]OPTIONS:[/bold green]")
        console.print(options_table)
        
        # Examples section
        console.print("\n[bold green]EXAMPLES:[/bold green]")
        examples = [
            ("ai-advanced", "Start enhanced CLI with all features"),
            ("ai-dev --quick", "Quick start for development work"),
            ("ai-expert --session project", "Start project session with expert features"),
        ]
        
        for cmd, desc in examples:
            console.print(f"  [cyan]{cmd}[/cyan]  [dim]# {desc}[/dim]")
        
        console.print("")
        
    except ImportError:
        # Fallback to plain text
        print("AI Helper Agent - Enhanced CLI")
        print("\nUsage: ai-advanced [options]")
        print("\nFeatures: File processing, Multi-provider, Code analysis")
        print("Examples:")
        print("  ai-advanced              # Start enhanced CLI")
        print("  ai-advanced --quick      # Quick start")


def main():
    """Main entry point with argument parsing"""
    # Show Rich help if requested
    if '--help' in sys.argv or '-h' in sys.argv:
        show_rich_help()
        return
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Enhanced Multi-Provider CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper-enhanced                      # Start with provider selection
  ai-helper-enhanced --quick             # Skip startup, use existing config
  ai-helper-enhanced --session work     # Start with named session
  ai-helper-enhanced --model llama       # Start with specific model
        """
    )
    
    parser.add_argument(
        "--session", "-s",
        default="default",
        help="Session ID for conversation history"
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
        "--workspace", "-w",
        default=".",
        help="Workspace directory path"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent Enhanced CLI v2.0.1"
    )
    
    args = parser.parse_args()
    
    try:
        # Create CLI instance
        cli = EnhancedMultiProviderCLI(
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
        
        # Initialize Rich formatter here (after argument parsing)
        if rich_formatter.is_available():
            rich_formatter.print_status("✅ Using Rich for enhanced display", "success")
        else:
            print("⚠️ Rich not available - using basic display")
        
        # Start the application
        asyncio.run(cli.start())
        
    except KeyboardInterrupt:
        if rich_formatter.is_available():
            rich_formatter.print_goodbye()
        else:
            print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
