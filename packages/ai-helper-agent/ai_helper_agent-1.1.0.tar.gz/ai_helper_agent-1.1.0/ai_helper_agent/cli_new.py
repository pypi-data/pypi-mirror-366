"""
AI Helper Agent CLI Module
Interactive command-line interface with conversation history and message trimming
Enhanced with Codex-like capabilities and latest Groq models
"""

import os
import sys
import asyncio
import getpass
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

# Global conversation store
conversation_store: Dict[str, BaseChatMessageHistory] = {}


class AIHelperCLI:
    """Enhanced CLI with LangChain conversation history and Codex-like capabilities"""
    
    # Available Groq models (Production + Preview)
    AVAILABLE_MODELS = {
        # Production Models
        "gemma2-9b-it": "Gemma 2 9B (Google - Chat fine-tuned, Balanced)",
        "llama-3.1-8b-instant": "Llama 3.1 8B (Meta - Instant response, Fast)",
        "llama-3.3-70b-versatile": "Llama 3.3 70B (Meta - General purpose, Large)",
        
        # Legacy Production Models (still supported)
        "llama3-8b-8192": "Llama 3 8B (Legacy - Fast, Good for coding)",
        "llama3-70b-8192": "Llama 3 70B (Legacy - Better reasoning)",
        "mixtral-8x7b-32768": "Mixtral 8x7B (Great for complex tasks)",
        
        # Preview Models (Advanced Features)
        "deepseek-r1-distill-llama-70b": "DeepSeek R1 (Preview - Chat distillation)",
        "meta-llama/llama-4-maverick-17b-128e-instruct": "Llama 4 Maverick (Preview - Instruction-tuned)",
        "meta-llama/llama-4-scout-17b-16e-instruct": "Llama 4 Scout (Preview - Instruction-tuned)",
        "moonshotai/kimi-k2-instruct": "Kimi K2 (Preview - Moonshot AI)",
        "qwen/qwen3-32b": "Qwen 3 32B (Preview - Alibaba Cloud)"
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
        
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for session"""
        if session_id not in conversation_store:
            conversation_store[session_id] = ChatMessageHistory()
        return conversation_store[session_id]
    
    def setup_api_key(self) -> bool:
        """Setup API key with user interaction"""
        print("🤖 AI Helper Agent - Interactive CLI")
        print("=" * 50)
        
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
        """Setup LLM and conversation chain with history"""
        try:
            # Initialize LLM with selected model
            self.llm = ChatGroq(
                model=self.model,
                temperature=0.1,
                api_key=self.api_key
            )
            
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
            
            print("✅ AI Helper Agent initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize AI Helper: {e}")
            return False
        
        return True
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
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

💡 INTELLIGENT ASSISTANCE
- Explain complex programming concepts with examples
- Provide learning resources and tutorials
- Help with algorithm design and data structure selection
- Answer technical questions with detailed explanations

🛠️ SHELL & CLI INTEGRATION
- Generate shell commands from natural language
- Create CLI tools and automation scripts
- Help with system administration tasks
- Provide cross-platform command solutions

SPECIALIZED COMMANDS:
- generate <description> - Generate code from natural language
- complete <partial_code> - Complete partially written code
- translate <from_lang> to <to_lang> - Convert code between languages
- explain <code> - Explain what code does in plain English
- refactor <code> - Improve code structure and efficiency
- debug <code> - Find and fix bugs in code
- shell <description> - Generate shell commands
- optimize <code> - Improve performance and efficiency

RESPONSE GUIDELINES:
1. Always provide working, tested code examples
2. Include comments explaining complex logic
3. Follow language-specific best practices and conventions
4. Provide multiple solutions when appropriate
5. Explain the reasoning behind code choices
6. Include error handling and edge cases
7. Suggest testing strategies

Current workspace: {self.workspace_path}
Current model: {self.model}

I'm ready to help you with any programming task, from simple scripts to complex applications!"""
    
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
            
            # Regular conversation with history
            config = {"configurable": {"session_id": self.session_id}}
            
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
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
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
            
            config = {"configurable": {"session_id": self.session_id}}
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
            
            config = {"configurable": {"session_id": self.session_id}}
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
            
            config = {"configurable": {"session_id": self.session_id}}
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
            
            config = {"configurable": {"session_id": self.session_id}}
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
            
            config = {"configurable": {"session_id": self.session_id}}
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
            
            config = {"configurable": {"session_id": self.session_id}}
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
            
            config = {"configurable": {"session_id": self.session_id}}
            response = await self.conversation_chain.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            
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
    
    def _handle_workspace_command(self, path: str) -> str:
        """Handle workspace change command"""
        try:
            new_path = Path(path).resolve()
            if new_path.exists() and new_path.is_dir():
                self.workspace_path = new_path
                return f"📂 Workspace changed to: {self.workspace_path}"
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
  
💻 SHELL & CLI:
  shell <description>       - Generate shell/terminal commands
  
🛠️ WORKSPACE & MODEL:
  workspace <path>          - Change current workspace directory
  model                     - Show current model and available options
  model <number>            - Change to different Groq model
  
💬 NATURAL CONVERSATION:
  Just describe what you want to build or ask programming questions!
  Examples:
  - "Create a REST API with authentication"
  - "Build a data processing pipeline"
  - "Help me understand decorators in Python"
  - "Optimize this sorting algorithm"
  - "Convert this Python function to JavaScript"
  
📚 ADVANCED FEATURES:
  • Multi-language support (Python, JS, TS, Go, Rust, Java, C++, etc.)
  • Intelligent code completion and generation
  • Cross-language code translation
  • Performance optimization suggestions
  • Security vulnerability detection
  • Best practices enforcement
  • Shell command generation
  
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
                
                # Process the input
                print("🤔 Thinking...")
                response = await self.handle_command(user_input)
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
            # Setup API key
            if not self.setup_api_key():
                return
            
            # Setup LLM and chains
            if not self.setup_llm_and_chain():
                return
            
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
  ai-helper                          # Start interactive session
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
        "--version", "-v",
        action="version",
        version="AI Helper Agent CLI v1.0.1"
    )
    
    args = parser.parse_args()
    
    try:
        # Create CLI instance with model selection
        cli = AIHelperCLI(session_id=args.session, model=args.model)
        
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
