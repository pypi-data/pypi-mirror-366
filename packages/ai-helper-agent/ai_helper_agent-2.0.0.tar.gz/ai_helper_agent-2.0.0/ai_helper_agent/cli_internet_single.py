"""
AI Helper Agent - Single Provider CLI with Internet Access (Groq Only)
Internet-enabled CLI that automatically searches the web when needed
"""

import os
import sys
import argparse
import time
import re
import asyncio
import warnings
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Filter out warnings to keep CLI clean
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
warnings.filterwarnings("ignore", message=".*avconv.*")
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*")
warnings.filterwarnings("ignore", module="pydub")

# Rich imports for colored output and markdown formatting
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.text import Text
    from rich import print as rich_print
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    rich_print = print

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    AsyncGroq = None
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Import API key manager
from .api_key_manager import APIKeyManager

# Initialize API key manager
api_key_manager = APIKeyManager()

from .core import InteractiveAgent
from .config import config
from .security import security_manager
from .user_manager import user_manager
from .prompt_enhancer import AdvancedPromptEnhancer
from .system_config import SystemConfigurationManager
from .internet_access import InternetAccessManager, create_internet_access_manager, PermissionLevel, SearchProvider
from .rich_formatting import RichFormattingManager

# Initialize Rich formatter
rich_formatter = RichFormattingManager()

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}

# Initialize Rich console for colored output (legacy compatibility)
if RICH_AVAILABLE:
    console = Console()
else:
    console = None


class InternetSingleProviderCLI:
    """Single Provider CLI with Internet Access - Groq Only with Web Search"""
    
    # Available Groq models only - ALL models from Groq API
    AVAILABLE_MODELS = {
        "llama-3.3-70b-versatile": "Llama 3.3 70B (Meta - Latest, 128K context, General purpose)",
        "llama-3.1-8b-instant": "Llama 3.1 8B (Meta - Ultra fast responses, Instant)",
        "llama-3.1-70b-versatile": "Llama 3.1 70B (Meta - Large reasoning model, Versatile)",
        "llama3-8b-8192": "Llama 3 8B (Meta - Fast, 8K context, Good for coding)",
        "llama3-70b-8192": "Llama 3 70B (Meta - Better reasoning, 8K context)",
        "gemma2-9b-it": "Gemma 2 9B (Google - Instruction-tuned, Balanced performance)",
        "allam-2-7b": "ALLAM 2 7B (IBM - Arabic-English bilingual model)",
        "compound-beta": "Compound Beta (Advanced reasoning, 70K context)",
        "compound-beta-mini": "Compound Beta Mini (Lightweight reasoning model)",
        "deepseek-r1-distill-llama-70b": "DeepSeek R1 70B (Distilled reasoning, Mathematical)",
        "meta-llama/llama-4-maverick-17b-128e-instruct": "Llama 4 Maverick 17B (Meta - Latest, 128E instruction)",
        "meta-llama/llama-4-scout-17b-16e-instruct": "Llama 4 Scout 17B (Meta - Latest, 16E instruction)",
        "meta-llama/llama-guard-4-12b": "Llama Guard 4 12B (Meta - Safety and moderation)",
        "meta-llama/llama-prompt-guard-2-22m": "Llama Prompt Guard 2 22M (Meta - Prompt safety, Small)",
        "meta-llama/llama-prompt-guard-2-86m": "Llama Prompt Guard 2 86M (Meta - Advanced prompt safety)",
        "moonshotai/kimi-k2-instruct": "Kimi K2 (Moonshot AI - Long context, Multilingual)",
        "qwen/qwen3-32b": "Qwen 3 32B (Alibaba - Large reasoning model, Multilingual)"
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
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create session history"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def show_splash_screen(self):
        """Show Groq-only splash screen with internet access logo"""
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        # Simple Groq + Internet logo (no multi-provider logos)
        logo = """
[bold cyan]╭─────────────────────────────────────────────────────────────────────────────╮[/bold cyan]
[bold cyan]│[/bold cyan]                                                                           [bold cyan]│[/bold cyan]
[bold cyan]│[/bold cyan]     [bold white]🚀 AI HELPER AGENT - GROQ + INTERNET 🌐[/bold white]                    [bold cyan]│[/bold cyan] 
[bold cyan]│[/bold cyan]     [dim]⚡ Lightning-fast Groq models with web search capability[/dim]     [bold cyan]│[/bold cyan]
[bold cyan]│[/bold cyan]                                                                           [bold cyan]│[/bold cyan]
[bold cyan]│[/bold cyan]     [green]✅ Groq API Ready[/green]    [blue]🌐 Internet Access Enabled[/blue]           [bold cyan]│[/bold cyan]
[bold cyan]│[/bold cyan]     [yellow]🔍 Smart Search Mode[/yellow] [magenta]📡 Real-time Streaming[/magenta]           [bold cyan]│[/bold cyan]
[bold cyan]│[/bold cyan]                                                                           [bold cyan]│[/bold cyan]
[bold cyan]╰─────────────────────────────────────────────────────────────────────────────╯[/bold cyan]
        """
        
        console.print(logo)
        print("\n🌐 INTERNET ACCESS ENABLED")
        print("🔍 AI will automatically search the web when needed")
    
    def setup_user_session(self) -> bool:
        """Setup user session with Groq-only provider and internet access"""
        if not self.skip_startup:
            # Show Groq-only splash screen
            self.show_splash_screen()
            
            # Setup Groq-only interface (no provider selection)
            model_id, api_key, llm_instance = self.setup_groq_only_interface()
            
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
    
    def setup_groq_only_interface(self):
        """Setup Groq-only interface without provider selection"""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Show Groq-only logo
        console.print(Panel.fit(
            "[bold cyan]🚀 AI HELPER AGENT - GROQ POWERED[/bold cyan]\n"
            "[dim]⚡ Lightning-fast inference with Llama & Gemma models[/dim]\n"
            "[dim]🌐 Internet Access Enabled[/dim]",
            border_style="bright_blue"
        ))
        
        # Get Groq API key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            console.print("❌ [red]GROQ_API_KEY not found in environment variables[/red]")
            console.print("Please set your Groq API key: export GROQ_API_KEY='your-key-here'")
            return None, None, None
        
        # Show Groq model selection
        console.print("\n[bold]🚀 Available Groq Models:[/bold]")
        
        # Create table of Groq models
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=3)
        table.add_column("Model", style="cyan")
        table.add_column("Description", style="white")
        
        models = list(self.AVAILABLE_MODELS.items())
        for i, (model_id, model_description) in enumerate(models, 1):
            # Extract model name from model_id for display
            model_name = model_id.replace('-', ' ').title()
            table.add_row(str(i), model_name, model_description)
        
        console.print(table)
        
        # Model selection
        try:
            choice = console.input("\n🤖 Select model (1): ").strip() or "1"
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(models):
                selected_model_id, selected_model_description = models[choice_idx]
                # Extract model name for display
                model_name = selected_model_id.replace('-', ' ').title()
                console.print(f"✅ Selected: {model_name}")
                
                # Create LLM instances
                from langchain_groq import ChatGroq
                from groq import AsyncGroq
                
                # ChatGroq for LangChain compatibility
                llm_instance = ChatGroq(
                    temperature=0.1,
                    model_name=selected_model_id,
                    groq_api_key=api_key,
                    streaming=True
                )
                
                # AsyncGroq for JSON responses
                self.async_groq_client = AsyncGroq(api_key=api_key)
                
                return selected_model_id, api_key, llm_instance
            else:
                console.print("❌ Invalid selection")
                return None, None, None
                
        except (ValueError, KeyboardInterrupt):
            console.print("❌ Invalid input")
            return None, None, None
    
    def setup_internet_access(self):
        """Setup internet access manager"""
        try:
            # Create user directory for internet access data
            user_dir = Path.home() / ".ai_helper_agent" / "internet_data"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Create internet access manager with the LLM for query analysis
            self.internet_manager = create_internet_access_manager(user_dir, self.llm)
            
            # Configure permission level to always allow - let LLM decide when to search
            self.internet_manager.configure_permissions(level="always")
            
            print("🌐 Internet access configured successfully")
            print("📊 Permission level: Always Allow (LLM decides automatically when to search)")
            
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
            
            # Create both AsyncGroq and ChatGroq clients for flexibility
            if GROQ_AVAILABLE:
                self.async_groq_client = AsyncGroq(api_key=self.api_key)
            else:
                self.async_groq_client = None
            
            # Keep ChatGroq for LangChain compatibility (fallback import)
            try:
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    model=self.model,
                    temperature=0.1,
                    api_key=self.api_key
                )
            except ImportError:
                print("❌ ChatGroq not available, using AsyncGroq only")
                self.llm = None
        
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
        # Get current date and time for context
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        base_prompt = f"""You are an expert AI programming assistant with internet access, powered by Groq's lightning-fast inference. You specialize in:

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

📅 CURRENT CONTEXT:
- Today's Date & Time: {current_datetime}
- Current workspace: {{workspace_path}}
- Current model: {{model}} (GROQ)
- Provider: GROQ (Lightning Fast) + Internet Access

IMPORTANT: When you need current information, documentation, API changes, or solutions to specific problems, I will automatically search the internet to provide you with the most up-to-date and accurate information. Always include relevant dates and timestamps in your responses when discussing current events or time-sensitive information."""

        if self.prompt_enhancer:
            enhanced_prompt = self.prompt_enhancer.get_enhanced_system_prompt()
            # Combine the enhanced prompt with internet access information
            return f"{enhanced_prompt}\n\n{base_prompt}"
        
        return base_prompt
    
    async def generate_json_response(self, user_input: str, response_format: dict = None) -> dict:
        """Generate JSON response using AsyncGroq for structured output"""
        if not GROQ_AVAILABLE or not self.async_groq_client:
            return {"error": "JSON responses only supported with AsyncGroq client"}
        
        try:
            # Default JSON response format if none provided
            if not response_format:
                response_format = {
                    "type": "json_object"
                }
            
            chat_completion = await self.async_groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Always respond with valid JSON format."
                    },
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ],
                model=self.model,
                temperature=0.1,
                response_format=response_format
            )
            
            import json
            json_response = json.loads(chat_completion.choices[0].message.content)
            return json_response
            
        except Exception as e:
            return {"error": f"JSON generation failed: {str(e)}"}
    
    def _search_and_enhance_response(self, user_input: str, context: str = "") -> Optional[str]:
        """Search the internet and return enhanced context if needed with LLM-guided decisions"""
        if not self.internet_manager:
            return None
        
        try:
            # First, let the LLM decide if search is needed and how many results
            search_decision = self._get_search_decision(user_input, context)
            
            if not search_decision.get('needs_search', False):
                return None
            
            # Show searching message
            max_results = search_decision.get('max_results', 6)
            self._print_colored(f"🔍 Searching the web for current information... (fetching {max_results} results)", "cyan")
            
            # Perform search with LLM-determined number of results
            search_results = self.internet_manager.search_with_permission(
                user_input,
                context,
                "user",
                self.session_id,
                max_results=max_results
            )
            
            # search_results is Optional[List[SearchResult]], not a dict
            if search_results and len(search_results) > 0:
                # Get current date and time
                current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
                
                # Format search results for the AI with comprehensive information but faster processing
                search_context = "🌐 **INTERNET SEARCH RESULTS:**\n\n"
                search_context += f"**Search performed on:** {current_datetime}\n\n"
                
                # Use up to 6 results for good understanding but faster response
                results_to_use = min(6, len(search_results))
                
                for i, result in enumerate(search_results[:results_to_use]):
                    search_context += f"**Source {i+1}: {result.title}**\n"
                    search_context += f"URL: {result.url}\n"
                    search_context += f"Content: {result.snippet}\n"
                    search_context += f"Provider: {result.provider.title()}\n\n"
                
                search_context += "---\n"
                search_context += f"**INSTRUCTIONS:** Use the above search results to provide a comprehensive, up-to-date answer for {current_datetime}. "
                search_context += "Format your response with proper markdown for bold text (**text**), italics (*text*), and code blocks (```language). "
                search_context += "At the end of your response, include a 'References' section with numbered citations.\n\n"
                
                # Add citation information for the AI to use
                search_context += "**CITATION FORMAT:**\n"
                search_context += "References:\n"
                for i, result in enumerate(search_results[:results_to_use]):
                    search_context += f"{i+1}. [{result.title}]({result.url})\n"
                search_context += "\n"
                
                return search_context
            
        except Exception as e:
            if console:
                console.print(f"🔍 [red]Search error:[/red] {e}")
            else:
                print(f"🔍 Search error: {e}")
        
        return None
    
    def _get_search_decision(self, user_input: str, context: str = "") -> dict:
        """Use LLM to decide if search is needed and how many results to fetch"""
        try:
            decision_prompt = f"""Analyze this user query to determine if internet search is needed:

Query: {user_input}
Context: {context}

Respond with a JSON object containing:
- needs_search: boolean (true if current/recent information needed)
- max_results: integer (3-10, how many search results needed)
- reasoning: string (brief explanation)

Examples:
- "What is Python?" -> {{"needs_search": false, "max_results": 0, "reasoning": "Basic concept, no current info needed"}}
- "Weather today" -> {{"needs_search": true, "max_results": 3, "reasoning": "Current weather data needed"}}
- "Latest AI news" -> {{"needs_search": true, "max_results": 8, "reasoning": "Recent news requires comprehensive search"}}
- "How to deploy Django 2024" -> {{"needs_search": true, "max_results": 5, "reasoning": "Recent deployment methods needed"}}

Respond with only the JSON object."""

            # Use the LLM to make the decision
            response = self.llm.invoke(decision_prompt)
            
            # Parse JSON response
            import json
            decision_dict = json.loads(response.content.strip())
            
            # Validate and set defaults
            decision_dict['needs_search'] = decision_dict.get('needs_search', False)
            decision_dict['max_results'] = max(3, min(10, decision_dict.get('max_results', 6)))
            decision_dict['reasoning'] = decision_dict.get('reasoning', 'Auto-decision')
            
            return decision_dict
            
        except Exception as e:
            # Fallback to basic heuristic
            query_lower = user_input.lower()
            search_keywords = ['latest', 'recent', 'current', 'today', 'now', 'news', '2024', '2025', 'weather', 'price', 'update']
            needs_search = any(keyword in query_lower for keyword in search_keywords)
            
            return {
                'needs_search': needs_search,
                'max_results': 6 if needs_search else 0,
                'reasoning': f'Heuristic decision - error: {str(e)}'
            }

    def _format_and_display_response(self, response: str):
        """Format and display response with rich formatting and syntax highlighting"""
        if not RICH_AVAILABLE or not console:
            print(response)
            return
        
        try:
            # Check if response contains code blocks
            code_pattern = r'```(\w+)?\n(.*?)\n```'
            
            # Split response into parts (text and code blocks)
            parts = []
            last_end = 0
            
            for match in re.finditer(code_pattern, response, re.DOTALL):
                # Add text before code block
                if match.start() > last_end:
                    text_part = response[last_end:match.start()].strip()
                    if text_part:
                        parts.append(('text', text_part))
                
                # Add code block
                language = match.group(1) or 'text'
                code_content = match.group(2)
                parts.append(('code', code_content, language))
                
                last_end = match.end()
            
            # Add remaining text
            if last_end < len(response):
                remaining_text = response[last_end:].strip()
                if remaining_text:
                    parts.append(('text', remaining_text))
            
            # If no code blocks found, treat entire response as text
            if not parts:
                parts = [('text', response)]
            
            # Display each part
            for part in parts:
                if part[0] == 'text':
                    # Render markdown text
                    try:
                        markdown = Markdown(part[1])
                        console.print(markdown)
                    except:
                        # Fallback to plain text
                        console.print(part[1])
                elif part[0] == 'code':
                    # Render syntax-highlighted code
                    try:
                        syntax = Syntax(part[1], part[2], theme="monokai", line_numbers=True)
                        console.print(Panel(syntax, title=f"[bold cyan]{part[2].title()} Code[/bold cyan]"))
                    except:
                        # Fallback to plain code block
                        console.print(Panel(part[1], title="Code"))
                        
        except Exception as e:
            # Fallback to plain output
            console.print(response)
    
    def _print_colored(self, message: str, style: str = "", end: str = "\n"):
        """Print colored message using rich if available"""
        if RICH_AVAILABLE and console:
            console.print(message, style=style, end=end)
        else:
            print(message, end=end)
    
    async def generate_json_response(self, user_input: str, response_format: dict = None) -> dict:
        """Generate JSON response using AsyncGroq for structured output"""
        if not self.async_groq_client:
            return {"error": "JSON responses require AsyncGroq client"}
        
        try:
            # Default JSON response format if none provided
            if not response_format:
                response_format = {
                    "type": "json_object"
                }
            
            chat_completion = await self.async_groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Always respond with valid JSON format."
                    },
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ],
                model=self.model,
                temperature=0.1,
                response_format=response_format
            )
            
            import json
            json_response = json.loads(chat_completion.choices[0].message.content)
            return json_response
            
        except Exception as e:
            return {"error": f"JSON generation failed: {str(e)}"}
    
    def handle_command(self, user_input: str) -> str:
        """Handle user commands with internet search integration and response timing"""
        start_time = time.time()
        
        try:
            # Check for special commands
            if user_input.lower() in ['exit', 'quit', 'goodbye']:
                return "👋 Goodbye! Thanks for using AI Helper Agent with Internet Access!"
            
            if user_input.lower() in ['help', '?']:
                response = self._get_help_text()
                elapsed_time = time.time() - start_time
                self._format_and_display_response(response)
                self._print_colored(f"⏱️ Response generated in {elapsed_time:.2f} seconds", "dim")
                return ""
            
            # JSON test command
            if user_input.lower().startswith('json:'):
                json_prompt = user_input[5:].strip()
                if json_prompt:
                    self._print_colored("🔧 Testing JSON response with AsyncGroq...", "dim")
                    
                    try:
                        json_result = asyncio.run(self.generate_json_response(json_prompt))
                        elapsed_time = time.time() - start_time
                        
                        import json as json_lib
                        formatted_json = json_lib.dumps(json_result, indent=2)
                        
                        self._print_colored("🤖 JSON Response:", "bold green")
                        self._print_colored(formatted_json, "green")
                        self._print_colored(f"⏱️ Response generated in {elapsed_time:.2f} seconds", "dim")
                        return ""
                    except Exception as e:
                        elapsed_time = time.time() - start_time
                        error_msg = f"❌ JSON Error: {str(e)}"
                        self._print_colored(error_msg, "red")
                        self._print_colored(f"⏱️ Error occurred in {elapsed_time:.2f} seconds", "dim")
                        return ""
                else:
                    self._print_colored("Usage: json: <your prompt>", "yellow")
                    return ""
            
            if user_input.lower().startswith('internet'):
                response = self._handle_internet_commands(user_input)
                elapsed_time = time.time() - start_time
                self._format_and_display_response(response)
                self._print_colored(f"⏱️ Response generated in {elapsed_time:.2f} seconds", "dim")
                return ""
            
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
                # Don't print the message here as it's already printed in _search_and_enhance_response
            
            # Handle streaming response
            if self.streaming_enabled:
                self._print_colored("🤖 AI Helper: ", "bold green", end="")
                
                # Stream response in real-time
                full_response = ""
                try:
                    for chunk in self.conversation_chain.stream(
                        {
                            "input": enhanced_input,
                            "workspace_path": str(self.workspace_path),
                            "model": self.model
                        },
                        config={"configurable": {"session_id": self.session_id}}
                    ):
                        if chunk:
                            print(chunk, end='', flush=True)
                            full_response += chunk
                except Exception as e:
                    # Fallback to non-streaming if streaming fails
                    response = self.conversation_chain.invoke(
                        {
                            "input": enhanced_input,
                            "workspace_path": str(self.workspace_path),
                            "model": self.model
                        },
                        config={"configurable": {"session_id": self.session_id}}
                    )
                    print(response, end='', flush=True)
                    full_response = response
                
                print()  # New line after streaming
                elapsed_time = time.time() - start_time
                self._print_colored(f"⏱️ Response generated in {elapsed_time:.2f} seconds", "dim")
                return ""  # Response already displayed
            else:
                # Non-streaming response
                response = self.conversation_chain.invoke(
                    {
                        "input": enhanced_input,
                        "workspace_path": str(self.workspace_path),
                        "model": self.model
                    },
                    config={"configurable": {"session_id": self.session_id}}
                )
                elapsed_time = time.time() - start_time
                
                # Format and display the response with rich formatting
                self._print_colored("🤖 AI Helper:", "bold green")
                self._format_and_display_response(response)
                self._print_colored(f"⏱️ Response generated in {elapsed_time:.2f} seconds", "dim")
                return ""  # Response already displayed
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"❌ Error processing request: {e}"
            self._print_colored(error_msg, "red")
            self._print_colored(f"⏱️ Error occurred after {elapsed_time:.2f} seconds", "dim")
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
                        query, user="user", session_id=self.session_id, max_results=6
                    )
                    if results and len(results) > 0:
                        # Get current date and time
                        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
                        
                        response = f"🔍 **SEARCH RESULTS FOR:** {query}\n"
                        response += f"**Search performed on:** {current_datetime}\n\n"
                        
                        for i, result in enumerate(results[:6]):
                            response += f"**{i+1}. {result.title}**\n"
                            response += f"URL: {result.url}\n"
                            response += f"Summary: {result.snippet}\n"
                            response += f"Provider: {result.provider.title()}\n\n"
                        
                        # Add citations
                        response += "---\n**References:**\n"
                        for i, result in enumerate(results[:6]):
                            response += f"{i+1}. [{result.title}]({result.url})\n"
                        
                        return response
                    else:
                        return "❌ No search results found."
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
- `json: <prompt>` - Test structured JSON responses
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
        if RICH_AVAILABLE and console:
            console.print(f"\n🌐 [bold cyan]AI Helper Agent - Internet Enabled CLI[/bold cyan]")
            console.print(f"⚡ Model: [yellow]{self.model}[/yellow] (GROQ)")
            console.print(f"🔍 Internet Access: {'[green]✅ Enabled[/green]' if self.internet_manager else '[red]❌ Disabled[/red]'}")
            console.print(f"💾 Session: [blue]{self.session_id}[/blue]")
            console.print(f"📁 Workspace: [magenta]{self.workspace_path}[/magenta]")
            console.print()
            console.print("💡 [bold]Type 'help' for available commands, or just start chatting![/bold]")
            console.print("🌐 AI will automatically search the web when helpful information is needed")
            console.print("⚡ Ultra-fast streaming responses with [bold]syntax highlighting[/bold] enabled")
            console.print()
        else:
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
                if RICH_AVAILABLE and console:
                    user_input = console.input("[bold blue]👤 You:[/bold blue] ").strip()
                else:
                    user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                response = self.handle_command(user_input)
                
                if response:
                    if user_input.lower() not in ['exit', 'quit', 'goodbye']:
                        if not self.streaming_enabled:
                            self._format_and_display_response(response)
                    else:
                        self._print_colored(response, "yellow")
                        break
                        
            except KeyboardInterrupt:
                self._print_colored("\n👋 Goodbye!", "yellow")
                break
            except Exception as e:
                self._print_colored(f"❌ Error: {e}", "red")


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
            rich_formatter.print_status(f"⚠️ Workspace path doesn't exist: {workspace_path}", "warning")
            cli.workspace_path = Path.cwd()
        
        # Setup user session with internet access
        if not cli.setup_user_session():
            rich_formatter.print_status("❌ Failed to setup CLI. Exiting...", "error")
            sys.exit(1)
        
        # Setup LLM chain
        if not cli.setup_llm_and_chain():
            rich_formatter.print_status("❌ Failed to setup LLM chain. Exiting...", "error")
            sys.exit(1)
        
        # Start the application
        cli.start()
        
    except KeyboardInterrupt:
        rich_formatter.print_goodbye()
        sys.exit(0)
    except Exception as e:
        rich_formatter.print_status(f"❌ Error: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
