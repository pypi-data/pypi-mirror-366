"""
Interactive AI Helper Agent - Core Module
Provides intelligent code assistance with interactive prompting
"""

import asyncio
import pathlib
import json
import re
from typing import Optional, Dict, Any, List
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from .config import config
from .security import security_manager
from .mcp_integration import MCPIntegration, MCPSessionManager, MCP_AVAILABLE

try:
    from .browser_integration import BrowserManager, create_browser_manager, PLAYWRIGHT_AVAILABLE
    BROWSER_INTEGRATION_AVAILABLE = True
except ImportError:
    BROWSER_INTEGRATION_AVAILABLE = False
    BrowserManager = None
    create_browser_manager = None
    PLAYWRIGHT_AVAILABLE = False

try:
    from .file_operations import enhanced_file_ops, read_file_enhanced, get_file_capabilities, OCR_AVAILABLE
    FILE_OPERATIONS_AVAILABLE = True
except ImportError:
    FILE_OPERATIONS_AVAILABLE = False
    enhanced_file_ops = None
    read_file_enhanced = None
    get_file_capabilities = None
    OCR_AVAILABLE = False


class InteractiveAgent:
    """Interactive AI Assistant for Code Analysis and Bug Fixing"""
    
    def __init__(self, llm: Optional[ChatGroq] = None, workspace_path: str = ".", 
                 api_key: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.1,
                 enable_mcp: bool = True, enable_browser: bool = True):
        """
        Initialize the Interactive Agent
        
        Args:
            llm: Pre-configured LLM instance (optional)
            workspace_path: Path to workspace directory
            api_key: Groq API key (optional, will use env var if not provided)
            model: Model name to use (optional, defaults to llama3-8b-8192)
            temperature: Temperature for AI responses (optional, defaults to 0.1)
            enable_mcp: Enable MCP integration (optional, defaults to True)
            enable_browser: Enable browser integration (optional, defaults to True)
        """
        self.api_key = api_key
        self.model = model or "llama3-8b-8192"
        self.temperature = temperature
        self.llm = llm or self._setup_default_llm()
        self.workspace_path = pathlib.Path(workspace_path)
        self.conversation_history = []
        
        # MCP Integration
        self.enable_mcp = enable_mcp
        self.mcp_integration: Optional[MCPIntegration] = None
        
        if self.enable_mcp:
            self._setup_mcp_integration()
        
        # Browser Integration
        self.enable_browser = enable_browser
        self.browser_manager = None  # Type: Optional[BrowserManager]
        
        if self.enable_browser and BROWSER_INTEGRATION_AVAILABLE:
            self._setup_browser_integration()
        
        # Default system prompt for code assistance
        self.system_prompt = """You are an expert AI programming assistant specializing in:

🔧 CODE ANALYSIS & BUG FIXING
- Analyze Python, JavaScript, TypeScript, and other code
- Identify syntax errors, logic bugs, and performance issues
- Provide complete, working fixes with explanations

📁 ENHANCED FILE OPERATIONS
- Read multiple file formats (.py, .c, .java, .sol, .r, .txt, .docx, .pdf)
- OCR text extraction from images and unreadable files
- Structured data processing (CSV, JSON, XML, YAML)
- Smart file type detection and processing method selection

� MCP INTEGRATION (if enabled)
- Access external MCP tools and resources
- Expose AI capabilities through MCP protocol
- Integrate with MCP-compatible development tools

�🚀 BEST PRACTICES
- Follow language-specific conventions
- Implement proper error handling
- Add meaningful comments and documentation
- Suggest improvements and optimizations

INTERACTION RULES:
1. Always ask for user confirmation before creating/modifying files
2. Provide clear explanations for all changes
3. Show code previews before implementing
4. Ask clarifying questions when requirements are unclear
5. Offer multiple solutions when appropriate

When the user provides input, analyze their request and:
- If it involves file operations, ask for specific file paths and destinations
- If it's code analysis, show your findings and proposed fixes
- If it's code creation, show the structure and ask for approval
- If it's web browsing/search, use browser integration capabilities
- Always be helpful, clear, and interactive

Current workspace: {workspace_path}
MCP Integration: {"Enabled" if enable_mcp else "Disabled"}
Browser Integration: {"Enabled" if enable_browser else "Disabled"}
Enhanced File Operations: {"Enabled" if FILE_OPERATIONS_AVAILABLE else "Disabled"}
OCR Capabilities: {"Available" if OCR_AVAILABLE else "Not Available"}
Ready to assist with your coding needs!"""

    def _setup_default_llm(self) -> ChatGroq:
        """Setup default Groq LLM"""
        # Use provided API key or get from config/environment
        api_key = self.api_key or config.get_api_key("groq")
        
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please either:\n"
                # "1. Set GROQ_API_KEY environment variable, or\n"
                "2. Pass api_key parameter: InteractiveAgent(api_key='your_key')"
            )
        
        return ChatGroq(
            model=self.model,
            temperature=self.temperature,
            api_key=api_key
        )

    def _setup_mcp_integration(self):
        """Setup MCP integration"""
        try:
            # Initialize MCP integration
            user_dir = self.workspace_path / ".ai_helper"
            user_dir.mkdir(exist_ok=True)
            config_path = user_dir / "mcp_config.json"
            self.mcp_integration = MCPIntegration(str(config_path))
            
            print("✅ MCP integration initialized successfully")
            if MCP_AVAILABLE:
                print("✅ MCP SDK available - real connections enabled")
            else:
                print("⚠️ MCP SDK not available - install with: pip install mcp")
                
        except Exception as e:
            print(f"⚠️ MCP integration failed: {e}")
            self.enable_mcp = False

    def _setup_browser_integration(self):
        """Setup browser integration"""
        try:
            # Initialize browser manager
            self.browser_manager = create_browser_manager(headless=True)
            
            print("✅ Browser integration initialized successfully")
            if PLAYWRIGHT_AVAILABLE:
                print("✅ Playwright available - browser automation enabled")
            else:
                print("⚠️ Playwright not available - install with: pip install playwright")
                
        except Exception as e:
            print(f"⚠️ Browser integration failed: {e}")
            self.enable_browser = False

    async def start_mcp_session(self) -> bool:
        """Start MCP integration"""
        if not self.enable_mcp or not self.mcp_integration:
            return False
        
        return await self.mcp_integration.initialize()

    async def stop_mcp_session(self):
        """Stop MCP integration"""
        if self.mcp_integration:
            await self.mcp_integration.shutdown()

    async def run_as_mcp_server(self):
        """Run AI Helper Agent as an MCP server"""
        if not self.enable_mcp or not self.mcp_integration:
            raise RuntimeError("MCP integration not enabled or available")
        
        print("🚀 Starting AI Helper Agent as MCP server...")
        # This would require creating a custom server implementation
        print("Custom MCP server not implemented yet")

    def get_mcp_status(self) -> Dict[str, Any]:
        """Get MCP integration status"""
        if not self.enable_mcp or not self.mcp_integration:
            return {"enabled": False, "reason": "MCP not initialized"}
        
        return {
            "enabled": True,
            **self.mcp_integration.get_status()
        }

    async def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool by name"""
        if not self.enable_mcp or not self.mcp_integration:
            return {"success": False, "error": "MCP not enabled"}
        
        return await self.mcp_integration.execute_tool(tool_name, arguments)

    # Browser Integration Methods

    async def start_browser_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a new browser session"""
        if not self.enable_browser or not self.browser_manager:
            return {"success": False, "error": "Browser integration not enabled"}
        
        try:
            if not session_id:
                session_id = self.browser_manager.create_session()
            else:
                self.browser_manager.create_session(session_id)
            
            success = await self.browser_manager.start_session(session_id)
            
            if success:
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": f"Browser session {session_id} started successfully"
                }
            else:
                return {"success": False, "error": "Failed to start browser session"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def browse_url(self, url: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Navigate to URL in browser session"""
        if not self.enable_browser or not self.browser_manager:
            return {"success": False, "error": "Browser integration not enabled"}
        
        try:
            # Create session if needed
            if not session_id:
                session_id = self.browser_manager.create_session()
                await self.browser_manager.start_session(session_id)
            
            result = await self.browser_manager.navigate(session_id, url)
            
            if result["success"]:
                # Also take a screenshot for documentation
                screenshot_result = await self.browser_manager.screenshot(session_id)
                result["screenshot"] = screenshot_result.get("screenshot_path")
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_web(self, query: str, provider: str = "duckduckgo", session_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform web search"""
        if not self.enable_browser or not self.browser_manager:
            return {"success": False, "error": "Browser integration not enabled"}
        
        try:
            # Create session if needed
            if not session_id:
                session_id = self.browser_manager.create_session()
                await self.browser_manager.start_session(session_id)
            
            result = await self.browser_manager.search_web(session_id, query, provider)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def browser_screenshot(self, session_id: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Take screenshot of browser session"""
        if not self.enable_browser or not self.browser_manager:
            return {"success": False, "error": "Browser integration not enabled"}
        
        return await self.browser_manager.screenshot(session_id, filename)

    async def extract_page_content(self, session_id: str, format: str = "text") -> Dict[str, Any]:
        """Extract content from current page"""
        if not self.enable_browser or not self.browser_manager:
            return {"success": False, "error": "Browser integration not enabled"}
        
        return await self.browser_manager.extract_content(session_id, format)

    async def demo_browser_localhost(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Demonstrate browser integration with localhost"""
        if not self.enable_browser or not self.browser_manager:
            return {"success": False, "error": "Browser integration not enabled"}
        
        return await self.browser_manager.demo_localhost(session_id)

    def get_browser_status(self) -> Dict[str, Any]:
        """Get browser integration status"""
        if not self.enable_browser or not self.browser_manager:
            return {"enabled": False, "reason": "Browser not initialized"}
        
        return {
            "enabled": True,
            **self.browser_manager.get_status()
        }

    async def close_browser_session(self, session_id: str) -> bool:
        """Close browser session"""
        if not self.enable_browser or not self.browser_manager:
            return False
        
        return await self.browser_manager.close_session(session_id)

    # Enhanced File Operations Methods

    def read_file_enhanced(self, file_path: str, force_ocr: bool = False) -> Dict[str, Any]:
        """Enhanced file reading with OCR capabilities"""
        if not FILE_OPERATIONS_AVAILABLE:
            return {"success": False, "error": "Enhanced file operations not available"}
        
        try:
            result = read_file_enhanced(file_path, force_ocr)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_file_capabilities(self) -> Dict[str, Any]:
        """Get file processing capabilities"""
        if not FILE_OPERATIONS_AVAILABLE:
            return {
                "available": False,
                "reason": "Enhanced file operations not available",
                "ocr_available": False,
                "pdf_available": False,
                "docx_available": False
            }
        
        try:
            capabilities = get_file_capabilities()
            capabilities["available"] = True
            return capabilities
        except Exception as e:
            return {"available": False, "error": str(e)}

    def detect_file_type(self, file_path: str) -> Dict[str, Any]:
        """Detect file type and processing method"""
        if not FILE_OPERATIONS_AVAILABLE:
            return {"supported": False, "error": "Enhanced file operations not available"}
        
        try:
            from .file_operations import detect_file_type
            return detect_file_type(file_path)
        except Exception as e:
            return {"supported": False, "error": str(e)}

    def get_file_processing_stats(self) -> Dict[str, Any]:
        """Get file processing statistics"""
        if not FILE_OPERATIONS_AVAILABLE:
            return {"available": False, "error": "Enhanced file operations not available"}
        
        try:
            from .file_operations import get_file_stats
            return get_file_stats()
        except Exception as e:
            return {"available": False, "error": str(e)}

    def read_multiple_files(self, file_paths: List[str], force_ocr: bool = False) -> Dict[str, Any]:
        """Read multiple files with enhanced capabilities"""
        if not FILE_OPERATIONS_AVAILABLE:
            return {"success": False, "error": "Enhanced file operations not available"}
        
        try:
            results = {}
            successful = 0
            failed = 0
            
            for file_path in file_paths:
                result = self.read_file_enhanced(file_path, force_ocr)
                results[file_path] = result
                
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
            
            return {
                "success": True,
                "results": results,
                "summary": {
                    "total_files": len(file_paths),
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (successful / len(file_paths) * 100) if file_paths else 0
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def analyze_code(self, code: str, filename: str = "code") -> Dict[str, Any]:
        """Analyze code for issues and improvements"""
        analysis_prompt = f"""
Analyze this {filename} code for:
1. Syntax errors
2. Logic bugs  
3. Performance issues
4. Best practice violations
5. Missing error handling

Code:
```python
{code}
```

Provide a structured analysis with specific line numbers and suggestions.
"""
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt.format(workspace_path=self.workspace_path)),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "analysis": response.content,
                "filename": filename,
                "code_length": len(code)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }

    async def fix_code(self, code: str, issues: str = "", filename: str = "code") -> Dict[str, Any]:
        """Fix code issues and return corrected version"""
        fix_prompt = f"""
Fix this {filename} code. 

Issues to address: {issues if issues else "All detectable bugs and improvements"}

Original code:
```python
{code}
```

Return ONLY the complete fixed Python code. No explanations, just clean, working code.
"""
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt.format(workspace_path=self.workspace_path)),
                HumanMessage(content=fix_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            fixed_code = response.content.strip()
            
            # Clean up response to extract code
            if "```python" in fixed_code:
                start = fixed_code.find("```python") + 9
                end = fixed_code.find("```", start)
                if end != -1:
                    fixed_code = fixed_code[start:end].strip()
            elif "```" in fixed_code:
                start = fixed_code.find("```") + 3
                end = fixed_code.find("```", start)
                if end != -1:
                    fixed_code = fixed_code[start:end].strip()
            
            return {
                "success": True,
                "fixed_code": fixed_code,
                "original_length": len(code),
                "fixed_length": len(fixed_code),
                "filename": filename
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }

    async def chat(self, user_input: str) -> str:
        """Interactive chat with the AI assistant"""
        try:
            # Check if user is asking for username change
            username_response = self._handle_username_commands(user_input)
            if username_response:
                return username_response
            
            # Check if user is asking for MCP-related operations
            if self.enable_mcp and self.mcp_integration:
                mcp_response = await self._handle_mcp_commands(user_input)
                if mcp_response:
                    return mcp_response
            
            # Check if user is asking for browser-related operations
            if self.enable_browser and self.browser_manager:
                browser_response = await self._handle_browser_commands(user_input)
                if browser_response:
                    return browser_response
            
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Build messages with conversation context
            messages = [
                SystemMessage(content=self.system_prompt.format(workspace_path=self.workspace_path))
            ]
            
            # Add MCP context if available
            if self.enable_mcp and self.mcp_integration:
                mcp_context = self._get_mcp_context()
                if mcp_context:
                    messages.append(SystemMessage(content=mcp_context))
            
            # Add browser context if available
            if self.enable_browser and self.browser_manager:
                browser_context = self._get_browser_context()
                if browser_context:
                    messages.append(SystemMessage(content=browser_context))
            
            # Add recent conversation history (last 10 exchanges)
            for exchange in self.conversation_history[-10:]:
                if exchange["role"] == "user":
                    messages.append(HumanMessage(content=exchange["content"]))
                else:
                    messages.append(SystemMessage(content=f"Assistant: {exchange['content']}"))
            
            response = await self.llm.ainvoke(messages)
            assistant_response = response.content
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
        except Exception as e:
            return f"❌ Error: {str(e)}"

    async def _handle_mcp_commands(self, user_input: str) -> Optional[str]:
        """Handle MCP-specific commands"""
        lower_input = user_input.lower()
        
        if "mcp status" in lower_input:
            status = self.get_mcp_status()
            return self._format_mcp_status(status)
        
        elif "list mcp tools" in lower_input or "mcp tools" in lower_input:
            if not self.mcp_integration:
                return "❌ MCP integration not available"
            tools = self.mcp_integration.get_available_tools()
            return self._format_mcp_tools(tools)
        
        elif "list mcp resources" in lower_input or "mcp resources" in lower_input:
            if not self.mcp_integration:
                return "❌ MCP integration not available"
            resources = self.mcp_integration.get_available_resources()
            return self._format_mcp_resources(resources)
        
        elif "start mcp" in lower_input:
            success = await self.start_mcp_session()
            return f"✅ MCP session started successfully" if success else "❌ Failed to start MCP session"
        
        elif "stop mcp" in lower_input:
            await self.stop_mcp_session()
            return "🛑 MCP session stopped"
        
        # Check for tool execution patterns
        if "use mcp tool" in lower_input or "execute mcp" in lower_input:
            # Extract tool name and arguments (simplified parsing)
            # In a real implementation, you'd use proper NLP/parsing
            parts = user_input.split()
            if len(parts) >= 4:  # "use mcp tool toolname"
                tool_name = parts[3]
                return await self._execute_mcp_tool_from_chat(tool_name, user_input)
        
        return None

    def _get_mcp_context(self) -> str:
        """Get MCP context for AI assistant"""
        if not self.mcp_integration:
            return ""
        
        status = self.mcp_integration.get_status()
        tools = self.mcp_integration.get_available_tools()
        
        if not tools:
            return "MCP Integration: No external tools available."
        
        tool_list = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in tools[:5]])
        
        return f"""
MCP Integration Active:
- {status['available_tools']} tools available from {status['active_sessions']} servers
- Available tools:
{tool_list}
{'...' if len(tools) > 5 else ''}

You can suggest using MCP tools when appropriate for the user's requests.
"""

    def _format_mcp_status(self, status: Dict[str, Any]) -> str:
        """Format MCP status for display"""
        if not status["enabled"]:
            return f"❌ MCP Integration: Disabled ({status.get('reason', 'Unknown reason')})"
        
        return f"""🔌 MCP Integration Status:
✅ Enabled and Active
📊 Active Sessions: {status['active_sessions']}
🔧 Available Tools: {status['available_tools']}
📁 Available Resources: {status['available_resources']}
⚙️ Configured Servers: {status['configured_servers']}
🟢 Enabled Servers: {status['enabled_servers']}
"""

    def _format_mcp_tools(self, tools: List[Dict[str, Any]]) -> str:
        """Format MCP tools for display"""
        if not tools:
            return "🔧 No MCP tools available. Start MCP session first."
        
        formatted = "🔧 Available MCP Tools:\n\n"
        for tool in tools:
            formatted += f"**{tool['name']}** ({tool['server']})\n"
            formatted += f"  📝 {tool['description']}\n"
            formatted += f"  📊 Used {tool['usage_count']} times\n"
            if tool['last_used']:
                formatted += f"  🕒 Last used: {tool['last_used']}\n"
            formatted += "\n"
        
        return formatted

    def _format_mcp_resources(self, resources: List[Dict[str, Any]]) -> str:
        """Format MCP resources for display"""
        if not resources:
            return "📁 No MCP resources available. Start MCP session first."
        
        formatted = "📁 Available MCP Resources:\n\n"
        for resource in resources:
            formatted += f"**{resource['name']}** ({resource['server']})\n"
            formatted += f"  📝 {resource['description']}\n"
            formatted += f"  🔗 URI: {resource['uri']}\n"
            if resource['mime_type']:
                formatted += f"  📄 Type: {resource['mime_type']}\n"
            formatted += f"  📊 Accessed {resource['access_count']} times\n\n"
        
        return formatted

    async def _execute_mcp_tool_from_chat(self, tool_name: str, user_input: str) -> str:
        """Execute MCP tool from chat context"""
        try:
            # For now, execute with empty arguments
            # In a real implementation, you'd parse arguments from user input
            result = await self.execute_mcp_tool(tool_name, {})
            
            if result["success"]:
                content = "\n".join(result["content"]) if isinstance(result["content"], list) else str(result["content"])
                return f"✅ MCP Tool '{tool_name}' executed successfully:\n\n{content}"
            else:
                return f"❌ MCP Tool '{tool_name}' failed: {result['error']}"
                
        except Exception as e:
            return f"❌ Error executing MCP tool '{tool_name}': {e}"

    async def _handle_browser_commands(self, user_input: str) -> Optional[str]:
        """Handle browser-specific commands"""
        lower_input = user_input.lower()
        
        if "browser status" in lower_input:
            status = self.get_browser_status()
            return self._format_browser_status(status)
        
        elif "browse " in lower_input or "navigate to " in lower_input or "go to " in lower_input:
            # Extract URL from input
            url = self._extract_url_from_input(user_input)
            if url:
                result = await self.browse_url(url)
                return self._format_browser_result(result, f"Navigation to {url}")
            else:
                return "❌ Please provide a valid URL to navigate to"
        
        elif "search web" in lower_input or "web search" in lower_input:
            # Extract search query
            query = self._extract_search_query(user_input)
            if query:
                result = await self.search_web(query)
                return self._format_browser_result(result, f"Web search for '{query}'")
            else:
                return "❌ Please provide a search query"
        
        elif "screenshot browser" in lower_input or "browser screenshot" in lower_input:
            # Get active session or create one
            status = self.get_browser_status()
            if status["enabled"] and status["active_sessions"] > 0:
                session_id = status["session_ids"][0]  # Use first active session
                result = await self.browser_screenshot(session_id)
                return self._format_browser_result(result, "Browser screenshot")
            else:
                return "❌ No active browser sessions. Browse to a page first."
        
        elif "demo browser" in lower_input or "browser demo" in lower_input:
            result = await self.demo_browser_localhost()
            return self._format_browser_result(result, "Browser localhost demo")
        
        elif "extract page" in lower_input or "page content" in lower_input:
            # Extract content from current page
            status = self.get_browser_status()
            if status["enabled"] and status["active_sessions"] > 0:
                session_id = status["session_ids"][0]
                format_type = "markdown" if "markdown" in lower_input else "text"
                result = await self.extract_page_content(session_id, format_type)
                return self._format_browser_result(result, f"Page content extraction ({format_type})")
            else:
                return "❌ No active browser sessions. Browse to a page first."
        
        return None

    def _extract_url_from_input(self, user_input: str) -> Optional[str]:
        """Extract URL from user input"""
        import re
        # Look for URLs in the input
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, user_input)
        if urls:
            return urls[0]
        
        # Look for common patterns like "go to example.com"
        words = user_input.split()
        for i, word in enumerate(words):
            if word.lower() in ["to", "browse", "navigate"] and i + 1 < len(words):
                potential_url = words[i + 1]
                if "." in potential_url and not potential_url.startswith("http"):
                    return f"https://{potential_url}"
                elif potential_url.startswith("http"):
                    return potential_url
        
        return None

    def _extract_search_query(self, user_input: str) -> Optional[str]:
        """Extract search query from user input"""
        # Look for patterns like "search web for X" or "web search X"
        lower_input = user_input.lower()
        
        if "search web for " in lower_input:
            return user_input.split("search web for ", 1)[1].strip()
        elif "web search for " in lower_input:
            return user_input.split("web search for ", 1)[1].strip()
        elif "search " in lower_input:
            return user_input.split("search ", 1)[1].strip()
        
        return None

    def _format_browser_status(self, status: Dict[str, Any]) -> str:
        """Format browser status for display"""
        if not status["enabled"]:
            return f"❌ Browser Integration: Disabled ({status.get('reason', 'Unknown reason')})"
        
        return f"""🌐 Browser Integration Status:
✅ Enabled and Active
📊 Active Sessions: {status['active_sessions']}
🔧 Playwright Available: {status['playwright_available']}
📄 Markdownify Available: {status['markdownify_available']}
🌐 Requests Available: {status['requests_available']}
🔗 Localhost Server: {status['localhost_server_url']}
💻 Headless Mode: {status['headless_mode']}
"""

    def _format_browser_result(self, result: Dict[str, Any], operation: str) -> str:
        """Format browser operation result for display"""
        if not result["success"]:
            return f"❌ {operation} failed: {result['error']}"
        
        formatted = f"✅ {operation} successful!\n\n"
        
        if "url" in result:
            formatted += f"🔗 URL: {result['url']}\n"
        if "title" in result:
            formatted += f"📄 Title: {result['title']}\n"
        if "screenshot" in result and result["screenshot"]:
            formatted += f"📸 Screenshot: {result['screenshot']}\n"
        if "session_id" in result:
            formatted += f"🆔 Session: {result['session_id']}\n"
        if "content_preview" in result:
            formatted += f"📋 Content Preview:\n{result['content_preview']}\n"
        if "message" in result:
            formatted += f"💬 {result['message']}\n"
        
        return formatted

    def _get_browser_context(self) -> str:
        """Get browser context for AI assistant"""
        if not self.browser_manager:
            return ""
        
        status = self.browser_manager.get_status()
        
        if status["active_sessions"] == 0:
            return "Browser Integration: Available but no active sessions."
        
        return f"""
Browser Integration Active:
- {status['active_sessions']} active browser sessions
- Playwright browser automation available
- Can navigate, search, screenshot, and extract content

Available browser commands:
- browse <url> - Navigate to a website
- search web <query> - Perform web search
- screenshot browser - Take screenshot of current page
- demo browser - Show localhost demonstration
- extract page - Get page content as text/markdown
"""

    def _handle_username_commands(self, user_input: str) -> Optional[str]:
        """Handle username-related commands"""
        lower_input = user_input.lower().strip()
        
        # Check for change_name command
        if lower_input.startswith('change_name'):
            return self._handle_change_name_command(user_input)
        
        # Check for alternative formats
        if 'change my name to' in lower_input or 'change name to' in lower_input:
            return self._handle_change_name_command(user_input)
        
        return None
    
    def _handle_change_name_command(self, user_input: str) -> str:
        """Handle change_name command"""
        try:
            # Extract new username from various command formats
            new_username = self._extract_new_username(user_input)
            
            if not new_username:
                return "❌ Please provide a new username. Usage: change_name \"new_username\""
            
            # Check if we have a user manager
            if not hasattr(self, 'user_manager') or not self.user_manager:
                return "❌ User management not available. Please initialize user manager first."
            
            # Attempt to change username
            old_username = getattr(self.user_manager, 'current_user', 'Unknown')
            success = self.user_manager.change_username(new_username)
            
            if success:
                return f"✅ Username changed successfully!\n📝 Old username: {old_username}\n📝 New username: {new_username}\n💡 Your session has been migrated to the new username."
            else:
                return f"❌ Failed to change username to '{new_username}'. Please check if the username is valid and try again."
        
        except Exception as e:
            return f"❌ Error changing username: {str(e)}"
    
    def _extract_new_username(self, user_input: str) -> Optional[str]:
        """Extract new username from user input"""
        import re
        
        # Pattern 1: change_name "username"
        pattern1 = r'change_name\s+["\']([^"\']+)["\']'
        match = re.search(pattern1, user_input, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: change_name username (without quotes)
        pattern2 = r'change_name\s+(\w+)'
        match = re.search(pattern2, user_input, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 3: change my name to username
        pattern3 = r'change\s+(?:my\s+)?name\s+to\s+["\']?([^"\']+)["\']?'
        match = re.search(pattern3, user_input, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read a file from the workspace"""
        try:
            file_path = self.workspace_path / filepath
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "filepath": str(file_path),
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, filepath: str, content: str, confirm: bool = True) -> Dict[str, Any]:
        """Write content to a file (with confirmation and security checks)"""
        try:
            # Security check
            if not security_manager.is_file_accessible(filepath):
                return {"success": False, "error": "Access denied: File not accessible"}
            
            file_path = self.workspace_path / filepath
            
            if confirm and file_path.exists():
                response = input(f"⚠️  File {filepath} already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    return {"success": False, "error": "Operation cancelled by user"}
            
            # Additional confirmation for new files if configured
            if confirm and not file_path.exists():
                response = input(f"📝 Create new file {filepath}? (y/N): ")
                if response.lower() != 'y':
                    return {"success": False, "error": "Operation cancelled by user"}
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return {
                "success": True,
                "filepath": str(file_path),
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files(self, pattern: str = "*") -> List[str]:
        """List files in workspace matching pattern"""
        try:
            files = []
            for file_path in self.workspace_path.rglob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.workspace_path)
                    files.append(str(relative_path))
            return sorted(files)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def interactive_session(self):
        """Start an interactive session with the AI assistant"""
        print("🤖 AI Helper Agent v1 - Interactive Session")
        print("=" * 50)
        print(f"📂 Workspace: {self.workspace_path.resolve()}")
        print("\nCommands:")
        print("  📝 'analyze <file>' - Analyze a code file")
        print("  🔧 'fix <file>' - Fix bugs in a file")
        print("  📂 'list [pattern]' - List files (optional pattern)")
        print("  💬 Just type anything else to chat")
        print("  🚪 'quit' or 'exit' to end session")
        print("\n" + "=" * 50)
        
        while True:
            try:
                user_input = input("\n🔵 You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Happy coding!")
                    break
                
                # Handle special commands
                if user_input.startswith('analyze '):
                    filename = user_input[8:].strip()
                    result = self.read_file(filename)
                    if result["success"]:
                        print(f"\n📖 Analyzing {filename}...")
                        analysis = asyncio.run(self.analyze_code(result["content"], filename))
                        if analysis["success"]:
                            print(f"🤖 Assistant:\n{analysis['analysis']}")
                        else:
                            print(f"❌ Analysis failed: {analysis['error']}")
                    else:
                        print(f"❌ {result['error']}")
                    continue
                
                elif user_input.startswith('fix '):
                    filename = user_input[4:].strip()
                    result = self.read_file(filename)
                    if result["success"]:
                        print(f"\n🔧 Fixing {filename}...")
                        fix_result = asyncio.run(self.fix_code(result["content"], filename=filename))
                        if fix_result["success"]:
                            fixed_filename = f"{pathlib.Path(filename).stem}_fixed{pathlib.Path(filename).suffix}"
                            
                            # Show preview
                            print(f"\n📄 Fixed code preview:")
                            lines = fix_result["fixed_code"].split('\n')
                            for i, line in enumerate(lines[:10], 1):
                                print(f"   {i:2d}: {line}")
                            if len(lines) > 10:
                                print(f"   ... ({len(lines) - 10} more lines)")
                            
                            # Ask for confirmation
                            confirm = input(f"\n💾 Save as {fixed_filename}? (Y/n): ")
                            if confirm.lower() != 'n':
                                write_result = self.write_file(fixed_filename, fix_result["fixed_code"], confirm=False)
                                if write_result["success"]:
                                    print(f"✅ Saved fixed code to {fixed_filename}")
                                else:
                                    print(f"❌ {write_result['error']}")
                        else:
                            print(f"❌ Fix failed: {fix_result['error']}")
                    else:
                        print(f"❌ {result['error']}")
                    continue
                
                elif user_input.startswith('list'):
                    pattern = user_input[4:].strip() or "*"
                    files = self.list_files(pattern)
                    print(f"\n📂 Files matching '{pattern}':")
                    for f in files[:20]:  # Show first 20
                        print(f"   📄 {f}")
                    if len(files) > 20:
                        print(f"   ... and {len(files) - 20} more files")
                    continue
                
                # Regular chat
                print(f"\n💭 Processing your request...")
                response = asyncio.run(self.chat(user_input))
                print(f"🤖 Assistant:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def create_agent(llm: Optional[ChatGroq] = None, workspace_path: str = ".", 
                 api_key: Optional[str] = None, model: Optional[str] = None, 
                 temperature: float = 0.1) -> InteractiveAgent:
    """
    Create a new AI Helper Agent instance
    
    Args:
        llm: Pre-configured LLM instance (optional)
        workspace_path: Path to workspace directory
        api_key: Groq API key (optional, will use env var if not provided)
        model: Model name to use (optional, defaults to llama3-8b-8192)
        temperature: Temperature for AI responses (optional, defaults to 0.1)
    
    Returns:
        InteractiveAgent instance
    """
    return InteractiveAgent(llm=llm, workspace_path=workspace_path, api_key=api_key, 
                          model=model, temperature=temperature)


# Quick start function for immediate use
def quick_start():
    """Quick start interactive session"""
    agent = create_agent()
    agent.interactive_session()


def main():
    """Main entry point for CLI usage"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - Interactive code assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper                    # Start interactive session
  ai-helper analyze file.py    # Analyze a specific file
  ai-helper chat "help me"     # Quick chat command
  ai-helper mcp-status         # Show MCP integration status
  ai-helper mcp-start          # Start MCP connections
  ai-helper mcp-tools          # List available MCP tools
  ai-helper mcp-execute tool   # Execute MCP tool
  ai-helper mcp-server         # Run as MCP server
        """
    )
    
    parser.add_argument(
        "command", 
        nargs="?", 
        choices=["analyze", "chat", "interactive", "mcp-status", "mcp-start", "mcp-stop", "mcp-tools", "mcp-execute", "mcp-server"],
        default="interactive",
        help="Command to execute"
    )
    
    parser.add_argument(
        "target",
        nargs="?", 
        help="File to analyze or message to chat"
    )
    
    parser.add_argument(
        "--workspace", "-w",
        default=".",
        help="Workspace directory path"
    )
    
    parser.add_argument(
        "--no-mcp",
        action="store_true",
        help="Disable MCP integration"
    )
    
    parser.add_argument(
        "--tool-args",
        help="JSON arguments for MCP tool execution"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent v1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        agent = create_agent(workspace_path=args.workspace, enable_mcp=not args.no_mcp)
        
        if args.command == "analyze":
            if not args.target:
                print("Error: Please provide a file to analyze")
                sys.exit(1)
            result = agent.analyze_file(args.target)
            print(result)
            
        elif args.command == "chat":
            if not args.target:
                print("Error: Please provide a message")
                sys.exit(1)
            response = agent.chat(args.target)
            print(response)
            
        elif args.command == "mcp-status":
            status = agent.get_mcp_status()
            print(json.dumps(status, indent=2))
            
        elif args.command == "mcp-start":
            print("🔗 Starting MCP connections...")
            success = asyncio.run(agent.start_mcp_session())
            if success:
                print("✅ MCP session started successfully")
            else:
                print("❌ Failed to start MCP session")
                sys.exit(1)
                
        elif args.command == "mcp-stop":
            print("🔌 Stopping MCP connections...")
            asyncio.run(agent.stop_mcp_session())
            print("✅ MCP session stopped")
            
        elif args.command == "mcp-tools":
            if not agent.enable_mcp or not agent.mcp_manager:
                print("❌ MCP not enabled")
                sys.exit(1)
            tools = agent.mcp_manager.get_available_tools()
            if tools:
                print(f"📋 Available MCP Tools ({len(tools)}):")
                for tool in tools:
                    print(f"  • {tool['name']} ({tool['server']}) - {tool['description']}")
            else:
                print("📋 No MCP tools available (connect to servers first)")
                
        elif args.command == "mcp-execute":
            if not args.target:
                print("Error: Please provide a tool name to execute")
                sys.exit(1)
            
            tool_args = {}
            if args.tool_args:
                try:
                    tool_args = json.loads(args.tool_args)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON in --tool-args: {e}")
                    sys.exit(1)
            
            print(f"🔧 Executing MCP tool: {args.target}")
            result = asyncio.run(agent.execute_mcp_tool(args.target, tool_args))
            print(json.dumps(result, indent=2))
            
        elif args.command == "mcp-server":
            print("🚀 Starting AI Helper Agent as MCP server...")
            asyncio.run(agent.run_as_mcp_server())
            
        else:  # interactive
            agent.interactive_session()
            
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
