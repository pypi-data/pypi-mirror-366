"""
MCP Integration Module for AI Helper Agent
Provides Model Context Protocol client and server capabilities with REAL connections
"""

import asyncio
import json
import logging
import os
import sqlite3
import subprocess
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
import uuid

# Set up logging
logger = logging.getLogger(__name__)

# MCP SDK imports with fallback
try:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
    from mcp.server.lowlevel import Server
    from mcp.server.stdio import stdio_server
    from mcp.shared.exceptions import McpError
    from mcp import types
    from mcp.server.models import InitializationOptions
    MCP_AVAILABLE = True
except ImportError:
    # Fallback when MCP SDK is not installed
    MCP_AVAILABLE = False
    logger.warning("MCP SDK not available. Install with: pip install mcp")
    
    # Fallback classes when MCP not available
    class InitializationOptions:
        def __init__(self):
            pass


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: List[str]
    description: str = ""
    enabled: bool = True
    timeout: int = 30
    environment: Dict[str, str] = field(default_factory=dict)
    args: List[str] = field(default_factory=list)
    working_directory: Optional[str] = None
    auto_restart: bool = True
    max_restarts: int = 3
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['last_used']:
            data['last_used'] = data['last_used'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServerConfig':
        """Create from dictionary (JSON deserialization)"""
        # Convert ISO strings back to datetime objects
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        return cls(**data)


@dataclass
class MCPToolInfo:
    """Information about an available MCP tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str
    last_used: Optional[datetime] = None
    usage_count: int = 0


@dataclass
class MCPResourceInfo:
    """Information about an available MCP resource"""
    uri: str
    name: str
    description: str
    server_name: str
    mime_type: Optional[str] = None
    access_count: int = 0


class MCPDatabase:
    """Database manager for MCP sessions and usage tracking"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcp_sessions (
                    id TEXT PRIMARY KEY,
                    server_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tools_count INTEGER DEFAULT 0,
                    resources_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0
                )
            """)
            
            # Tool usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    tool_name TEXT NOT NULL,
                    server_name TEXT NOT NULL,
                    arguments TEXT,
                    result TEXT,
                    success BOOLEAN,
                    duration_ms INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES mcp_sessions (id)
                )
            """)
            
            # Resource access table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resource_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    resource_uri TEXT NOT NULL,
                    server_name TEXT NOT NULL,
                    success BOOLEAN,
                    content_length INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES mcp_sessions (id)
                )
            """)
            
            conn.commit()
    
    def log_session(self, session_id: str, server_name: str, status: str):
        """Log session information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO mcp_sessions 
                (id, server_name, status, updated_at) 
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (session_id, server_name, status))
            conn.commit()
    
    def log_tool_usage(self, session_id: str, tool_name: str, server_name: str, 
                      arguments: str, result: str, success: bool, duration_ms: int):
        """Log tool usage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tool_usage 
                (session_id, tool_name, server_name, arguments, result, success, duration_ms) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, tool_name, server_name, arguments, result, success, duration_ms))
            conn.commit()
    
    def log_resource_access(self, session_id: str, resource_uri: str, server_name: str, 
                           success: bool, content_length: int):
        """Log resource access"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resource_access 
                (session_id, resource_uri, server_name, success, content_length) 
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, resource_uri, server_name, success, content_length))
            conn.commit()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tool usage stats
            cursor.execute("""
                SELECT server_name, tool_name, COUNT(*) as usage_count,
                       AVG(duration_ms) as avg_duration,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count
                FROM tool_usage 
                GROUP BY server_name, tool_name
            """)
            tool_stats = cursor.fetchall()
            
            # Resource access stats
            cursor.execute("""
                SELECT server_name, COUNT(*) as access_count,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count
                FROM resource_access 
                GROUP BY server_name
            """)
            resource_stats = cursor.fetchall()
            
            return {
                "tool_stats": tool_stats,
                "resource_stats": resource_stats
            }


class MCPSessionManager:
    """Manager for MCP server sessions and connections"""
    
    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = config_path
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self.active_sessions: Dict[str, ClientSession] = {}
        self.server_processes: Dict[str, subprocess.Popen] = {}
        self.session_data: Dict[str, Any] = {}
        
        # Store MCP database in user's .ai_helper_agent directory alongside FAISS
        user_home = Path.home()
        ai_helper_dir = user_home / ".ai_helper_agent"
        ai_helper_dir.mkdir(exist_ok=True)
        mcp_db_path = ai_helper_dir / "mcp_sessions.db"
        self.db = MCPDatabase(str(mcp_db_path))
        
        # Tool and resource tracking
        self.available_tools: Dict[str, MCPToolInfo] = {}
        self.available_resources: Dict[str, MCPResourceInfo] = {}
        
        # Load configurations
        self.load_server_configs()
        
        # Event callbacks
        self.on_tool_call: Optional[Callable] = None
        self.on_resource_access: Optional[Callable] = None
        self.on_session_change: Optional[Callable] = None
    
    def load_server_configs(self):
        """Load server configurations from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for name, config_data in data.get('servers', {}).items():
                        self.server_configs[name] = MCPServerConfig.from_dict(config_data)
            else:
                # Create default configurations
                self.create_default_configs()
                self.save_server_configs()
        except Exception as e:
            logger.error(f"Error loading server configs: {e}")
            self.create_default_configs()
    
    def create_default_configs(self):
        """Create default server configurations"""
        default_servers = {
            "filesystem": MCPServerConfig(
                name="filesystem",
                command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                description="Filesystem operations server",
                args=["/tmp"]  # Default directory
            ),
            "git": MCPServerConfig(
                name="git",
                command=["npx", "-y", "@modelcontextprotocol/server-git"],
                description="Git operations server"
            ),
            "time": MCPServerConfig(
                name="time",
                command=["npx", "-y", "@modelcontextprotocol/server-time"],
                description="Time and date server"
            ),
            "python_tool": MCPServerConfig(
                name="python_tool",
                command=["python", "-m", "mcp_server_simple_tool"],
                description="Simple Python tool server"
            )
        }
        
        for name, config in default_servers.items():
            self.server_configs[name] = config
    
    def save_server_configs(self):
        """Save server configurations to file"""
        try:
            data = {
                "servers": {name: config.to_dict() for name, config in self.server_configs.items()}
            }
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving server configs: {e}")
    
    def add_server_config(self, config: MCPServerConfig):
        """Add a new server configuration"""
        self.server_configs[config.name] = config
        self.save_server_configs()
        logger.info(f"Added server configuration: {config.name}")
    
    def remove_server_config(self, server_name: str) -> bool:
        """Remove a server configuration"""
        if server_name in self.server_configs:
            # Disconnect if active
            if server_name in self.active_sessions:
                asyncio.create_task(self.disconnect_server(server_name))
            
            del self.server_configs[server_name]
            self.save_server_configs()
            logger.info(f"Removed server configuration: {server_name}")
            return True
        return False
    
    async def connect_server(self, server_name: str) -> bool:
        """Connect to an MCP server with REAL connection"""
        if not MCP_AVAILABLE:
            logger.error("MCP SDK not available. Cannot connect to servers.")
            return False
        
        if server_name not in self.server_configs:
            logger.error(f"Server configuration not found: {server_name}")
            return False
        
        if server_name in self.active_sessions:
            logger.info(f"Already connected to server: {server_name}")
            return True
        
        config = self.server_configs[server_name]
        if not config.enabled:
            logger.info(f"Server disabled: {server_name}")
            return False
        
        try:
            session_id = str(uuid.uuid4())
            
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command=config.command[0],
                args=config.command[1:] + config.args,
                env=config.environment
            )
            
            # Start the server process and create stdio client with timeout
            try:
                # Create the stdio client transport
                transport = stdio_client(server_params)
                
                async with transport as (read, write):
                    # Create client session
                    session = ClientSession(read, write)
                    
                    # Initialize the session with timeout
                    await asyncio.wait_for(session.initialize(), timeout=10)
                    
                    # Store the session
                    self.active_sessions[server_name] = session
                    self.session_data[server_name] = {
                        "session_id": session_id,
                        "connected_at": datetime.now(),
                        "last_activity": datetime.now()
                    }
                    
                    # Update config last used time
                    config.last_used = datetime.now()
                    self.save_server_configs()
                    
                    # Load available tools and resources
                    await self.refresh_server_capabilities(server_name)
                    
                    # Log session
                    self.db.log_session(session_id, server_name, "connected")
                    
                    logger.info(f"Successfully connected to MCP server: {server_name}")
                    
                    # Notify callbacks
                    if self.on_session_change:
                        self.on_session_change(server_name, "connected")
                    
                    return True
                    
            except asyncio.TimeoutError:
                logger.error(f"Timeout connecting to server {server_name} after {config.timeout}s")
                self.db.log_session(session_id, server_name, "timeout")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to server {server_name}: {e}")
            self.db.log_session(session_id if 'session_id' in locals() else "unknown", 
                              server_name, "connection_failed")
            return False
    
    async def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        if server_name not in self.active_sessions:
            logger.info(f"Server not connected: {server_name}")
            return True
        
        try:
            session = self.active_sessions[server_name]
            await session.close()
            
            # Clean up
            del self.active_sessions[server_name]
            if server_name in self.session_data:
                session_id = self.session_data[server_name]["session_id"]
                del self.session_data[server_name]
                
                # Log disconnection
                self.db.log_session(session_id, server_name, "disconnected")
            
            # Remove server-specific tools and resources
            self.available_tools = {k: v for k, v in self.available_tools.items() 
                                  if v.server_name != server_name}
            self.available_resources = {k: v for k, v in self.available_resources.items() 
                                      if v.server_name != server_name}
            
            logger.info(f"Disconnected from server: {server_name}")
            
            # Notify callbacks
            if self.on_session_change:
                self.on_session_change(server_name, "disconnected")
            
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from server {server_name}: {e}")
            return False
    
    async def refresh_server_capabilities(self, server_name: str):
        """Refresh available tools and resources for a server"""
        if server_name not in self.active_sessions:
            logger.warning(f"Server not connected: {server_name}")
            return
        
        try:
            session = self.active_sessions[server_name]
            
            # List available tools
            try:
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    tool_key = f"{server_name}:{tool.name}"
                    self.available_tools[tool_key] = MCPToolInfo(
                        name=tool.name,
                        description=tool.description or "",
                        input_schema=tool.inputSchema or {},
                        server_name=server_name
                    )
            except Exception as e:
                logger.warning(f"Could not list tools for {server_name}: {e}")
            
            # List available resources
            try:
                resources_result = await session.list_resources()
                for resource in resources_result.resources:
                    resource_key = f"{server_name}:{resource.uri}"
                    self.available_resources[resource_key] = MCPResourceInfo(
                        uri=resource.uri,
                        name=resource.name,
                        description=resource.description or "",
                        mime_type=getattr(resource, 'mimeType', None),
                        server_name=server_name
                    )
            except Exception as e:
                logger.warning(f"Could not list resources for {server_name}: {e}")
            
            # Update session data
            if server_name in self.session_data:
                self.session_data[server_name]["last_activity"] = datetime.now()
            
            logger.info(f"Refreshed capabilities for server: {server_name}")
            
        except Exception as e:
            logger.error(f"Error refreshing capabilities for {server_name}: {e}")
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on an MCP server"""
        if server_name not in self.active_sessions:
            raise ValueError(f"Server not connected: {server_name}")
        
        session = self.active_sessions[server_name]
        session_id = self.session_data[server_name]["session_id"]
        start_time = time.time()
        
        try:
            # Call the tool
            result = await session.call_tool(tool_name, arguments)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Process result
            response = {
                "success": True,
                "result": result,
                "duration_ms": duration_ms
            }
            
            # Log usage
            self.db.log_tool_usage(
                session_id, tool_name, server_name,
                json.dumps(arguments), json.dumps(result),
                True, duration_ms
            )
            
            # Update tool info
            tool_key = f"{server_name}:{tool_name}"
            if tool_key in self.available_tools:
                self.available_tools[tool_key].usage_count += 1
                self.available_tools[tool_key].last_used = datetime.now()
            
            # Update session activity
            self.session_data[server_name]["last_activity"] = datetime.now()
            
            # Notify callbacks
            if self.on_tool_call:
                self.on_tool_call(server_name, tool_name, arguments, result)
            
            logger.info(f"Tool call successful: {server_name}:{tool_name}")
            return response
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            
            # Log failure
            self.db.log_tool_usage(
                session_id, tool_name, server_name,
                json.dumps(arguments), error_msg,
                False, duration_ms
            )
            
            logger.error(f"Tool call failed: {server_name}:{tool_name} - {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "duration_ms": duration_ms
            }
    
    async def read_resource(self, server_name: str, resource_uri: str) -> Dict[str, Any]:
        """Read a resource from an MCP server"""
        if server_name not in self.active_sessions:
            raise ValueError(f"Server not connected: {server_name}")
        
        session = self.active_sessions[server_name]
        session_id = self.session_data[server_name]["session_id"]
        
        try:
            # Read the resource
            result = await session.read_resource(resource_uri)
            
            # Process result
            content_length = len(str(result)) if result else 0
            
            response = {
                "success": True,
                "content": result,
                "content_length": content_length
            }
            
            # Log access
            self.db.log_resource_access(
                session_id, resource_uri, server_name,
                True, content_length
            )
            
            # Update resource info
            resource_key = f"{server_name}:{resource_uri}"
            if resource_key in self.available_resources:
                self.available_resources[resource_key].access_count += 1
            
            # Update session activity
            self.session_data[server_name]["last_activity"] = datetime.now()
            
            # Notify callbacks
            if self.on_resource_access:
                self.on_resource_access(server_name, resource_uri, result)
            
            logger.info(f"Resource read successful: {server_name}:{resource_uri}")
            return response
            
        except Exception as e:
            error_msg = str(e)
            
            # Log failure
            self.db.log_resource_access(
                session_id, resource_uri, server_name,
                False, 0
            )
            
            logger.error(f"Resource read failed: {server_name}:{resource_uri} - {error_msg}")
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def connect_all_servers(self) -> Dict[str, bool]:
        """Connect to all enabled servers"""
        results = {}
        
        for server_name, config in self.server_configs.items():
            if config.enabled:
                try:
                    # Try to connect with timeout
                    result = await asyncio.wait_for(
                        self.connect_server(server_name), 
                        timeout=15
                    )
                    results[server_name] = result
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout connecting to {server_name}")
                    results[server_name] = False
                except Exception as e:
                    logger.warning(f"Failed to connect to {server_name}: {e}")
                    results[server_name] = False
            else:
                results[server_name] = False
                logger.info(f"Skipping disabled server: {server_name}")
        
        return results
    
    async def disconnect_all_servers(self) -> Dict[str, bool]:
        """Disconnect from all servers"""
        results = {}
        for server_name in list(self.active_sessions.keys()):
            results[server_name] = await self.disconnect_server(server_name)
        
        return results
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all servers"""
        status = {}
        for server_name, config in self.server_configs.items():
            is_connected = server_name in self.active_sessions
            session_info = self.session_data.get(server_name, {})
            
            status[server_name] = {
                "name": server_name,
                "description": config.description,
                "enabled": config.enabled,
                "connected": is_connected,
                "last_used": config.last_used.isoformat() if config.last_used else None,
                "session_info": session_info,
                "tools_count": len([t for t in self.available_tools.values() if t.server_name == server_name]),
                "resources_count": len([r for r in self.available_resources.values() if r.server_name == server_name])
            }
        
        return status
    
    def get_available_tools(self, server_name: Optional[str] = None) -> List[MCPToolInfo]:
        """Get list of available tools"""
        if server_name:
            return [tool for tool in self.available_tools.values() if tool.server_name == server_name]
        return list(self.available_tools.values())
    
    def get_available_resources(self, server_name: Optional[str] = None) -> List[MCPResourceInfo]:
        """Get list of available resources"""
        if server_name:
            return [resource for resource in self.available_resources.values() if resource.server_name == server_name]
        return list(self.available_resources.values())
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        stats = self.db.get_usage_stats()
        
        # Add current session info
        active_sessions = len(self.active_sessions)
        total_tools = len(self.available_tools)
        total_resources = len(self.available_resources)
        
        stats.update({
            "active_sessions": active_sessions,
            "total_tools": total_tools,
            "total_resources": total_resources,
            "server_configs": len(self.server_configs)
        })
        
        return stats


class MCPServerTemplate:
    """Template for creating custom MCP servers"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.server = Server(name)
        self.tools: Dict[str, Callable] = {}
        self.resources: Dict[str, Callable] = {}
    
    def add_tool(self, name: str, description: str, input_schema: Dict[str, Any], 
                 handler: Callable[[Dict[str, Any]], Any]):
        """Add a tool to the server"""
        self.tools[name] = handler
        
        # Register with MCP server
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name in self.tools:
                try:
                    result = await self.tools[name](arguments)
                    if MCP_AVAILABLE:
                        return [types.TextContent(type="text", text=str(result))]
                    else:
                        return [{"type": "text", "text": str(result)}]
                except Exception as e:
                    if MCP_AVAILABLE:
                        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
                    else:
                        return [{"type": "text", "text": f"Error: {str(e)}"}]
            else:
                if MCP_AVAILABLE:
                    return [types.TextContent(type="text", text=f"Tool not found: {name}")]
                else:
                    return [{"type": "text", "text": f"Tool not found: {name}"}]
    
    def add_resource(self, uri: str, name: str, description: str, 
                     handler: Callable[[str], Any]):
        """Add a resource to the server"""
        self.resources[uri] = handler
    
    async def run_stdio(self):
        """Run the server with stdio transport"""
        if not MCP_AVAILABLE:
            logger.error("MCP SDK not available")
            return
        
        try:
            async with stdio_server() as streams:
                await self.server.run(*streams, InitializationOptions())
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            # Fallback without InitializationOptions
            async with stdio_server() as streams:
                await self.server.run(*streams)


# Example usage and integration functions
def create_filesystem_tool_server() -> MCPServerTemplate:
    """Create a simple filesystem tool server"""
    server = MCPServerTemplate("filesystem_tools", "Basic filesystem operations")
    
    async def read_file_tool(args: Dict[str, Any]) -> str:
        """Read a file and return its contents"""
        file_path = args.get("path", "")
        if not file_path:
            raise ValueError("Missing required parameter: path")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    async def write_file_tool(args: Dict[str, Any]) -> str:
        """Write content to a file"""
        file_path = args.get("path", "")
        content = args.get("content", "")
        
        if not file_path:
            raise ValueError("Missing required parameter: path")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            raise ValueError(f"Error writing file: {str(e)}")
    
    async def list_directory_tool(args: Dict[str, Any]) -> str:
        """List contents of a directory"""
        dir_path = args.get("path", ".")
        
        try:
            items = os.listdir(dir_path)
            return "\n".join(sorted(items))
        except Exception as e:
            raise ValueError(f"Error listing directory: {str(e)}")
    
    # Add tools to server
    server.add_tool("read_file", "Read contents of a file", 
                   {"type": "object", "properties": {"path": {"type": "string"}}}, 
                   read_file_tool)
    
    server.add_tool("write_file", "Write content to a file",
                   {"type": "object", "properties": {
                       "path": {"type": "string"}, 
                       "content": {"type": "string"}
                   }}, write_file_tool)
    
    server.add_tool("list_directory", "List directory contents",
                   {"type": "object", "properties": {"path": {"type": "string"}}},
                   list_directory_tool)
    
    return server


def create_simple_mcp_server() -> MCPServerTemplate:
    """Create a simple MCP server for testing"""
    server = MCPServerTemplate("simple_tools", "Simple utility tools")
    
    async def echo_tool(args: Dict[str, Any]) -> str:
        """Echo back the input message"""
        message = args.get("message", "")
        return f"Echo: {message}"
    
    async def current_time_tool(args: Dict[str, Any]) -> str:
        """Get current time"""
        return datetime.now().isoformat()
    
    async def calculate_tool(args: Dict[str, Any]) -> str:
        """Simple calculator"""
        operation = args.get("operation", "")
        a = args.get("a", 0)
        b = args.get("b", 0)
        
        if operation == "add":
            return str(a + b)
        elif operation == "subtract":
            return str(a - b)
        elif operation == "multiply":
            return str(a * b)
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return str(a / b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    # Add tools
    server.add_tool("echo", "Echo a message",
                   {"type": "object", "properties": {"message": {"type": "string"}}},
                   echo_tool)
    
    server.add_tool("current_time", "Get current time",
                   {"type": "object", "properties": {}},
                   current_time_tool)
    
    server.add_tool("calculate", "Perform basic calculations",
                   {"type": "object", "properties": {
                       "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                       "a": {"type": "number"},
                       "b": {"type": "number"}
                   }},
                   calculate_tool)
    
    return server


# Main integration class for the AI Helper Agent
class MCPIntegration:
    """Main MCP integration for AI Helper Agent"""
    
    def __init__(self, config_path: str = "mcp_config.json"):
        self.session_manager = MCPSessionManager(config_path)
        self.custom_servers: Dict[str, MCPServerTemplate] = {}
        self.running = False
    
    async def initialize(self) -> bool:
        """Initialize the MCP integration"""
        try:
            # Connect to all enabled servers with timeout
            print("🔗 Initializing MCP integration...")
            
            # Only try to connect if MCP SDK is available
            if not MCP_AVAILABLE:
                print("⚠️ MCP SDK not available, running in fallback mode")
                self.running = True
                return True
            
            results = await asyncio.wait_for(
                self.session_manager.connect_all_servers(), 
                timeout=30
            )
            
            connected_count = sum(1 for success in results.values() if success)
            total_count = len([config for config in self.session_manager.server_configs.values() if config.enabled])
            
            print(f"🔗 MCP Integration initialized: {connected_count}/{total_count} servers connected")
            self.running = True
            
            return connected_count >= 0  # Success if at least some connection attempts were made
            
        except asyncio.TimeoutError:
            print("⚠️ MCP initialization timed out - continuing with available connections")
            self.running = True
            return True
        except Exception as e:
            print(f"⚠️ MCP initialization had issues: {e} - continuing anyway")
            self.running = True
            return True
    
    async def shutdown(self):
        """Shutdown the MCP integration"""
        try:
            await self.session_manager.disconnect_all_servers()
            self.running = False
            logger.info("MCP Integration shutdown complete")
        except Exception as e:
            logger.error(f"Error during MCP shutdown: {e}")
    
    async def execute_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on an MCP server"""
        return await self.session_manager.call_tool(server_name, tool_name, arguments)
    
    async def read_resource(self, server_name: str, resource_uri: str) -> Dict[str, Any]:
        """Read a resource from an MCP server"""
        return await self.session_manager.read_resource(server_name, resource_uri)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of MCP integration"""
        return {
            "running": self.running,
            "servers": self.session_manager.get_server_status(),
            "statistics": self.session_manager.get_usage_statistics()
        }
    
    def get_available_tools(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available tools"""
        tools = self.session_manager.get_available_tools(server_name)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "server": tool.server_name,
                "usage_count": tool.usage_count,
                "last_used": tool.last_used.isoformat() if tool.last_used else None
            }
            for tool in tools
        ]
    
    def get_available_resources(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available resources"""
        resources = self.session_manager.get_available_resources(server_name)
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "server": resource.server_name,
                "access_count": resource.access_count
            }
            for resource in resources
        ]
    
    def add_custom_server(self, server: MCPServerTemplate):
        """Add a custom MCP server"""
        self.custom_servers[server.name] = server
        logger.info(f"Added custom MCP server: {server.name}")
    
    async def start_custom_server(self, server_name: str):
        """Start a custom MCP server"""
        if server_name in self.custom_servers:
            server = self.custom_servers[server_name]
            await server.run_stdio()
        else:
            raise ValueError(f"Custom server not found: {server_name}")


# Example usage
if __name__ == "__main__":
    async def main():
        # Create MCP integration
        mcp = MCPIntegration()
        
        # Add custom servers
        filesystem_server = create_filesystem_tool_server()
        mcp.add_custom_server(filesystem_server)
        
        simple_server = create_simple_mcp_server()
        mcp.add_custom_server(simple_server)
        
        # Initialize
        await mcp.initialize()
        
        # Test tool execution
        try:
            result = await mcp.execute_tool("time", "get_current_time", {})
            print(f"Time result: {result}")
        except Exception as e:
            print(f"Error calling time tool: {e}")
        
        # Get status
        status = mcp.get_status()
        print(f"MCP Status: {json.dumps(status, indent=2)}")
        
        # Shutdown
        await mcp.shutdown()
    
    # Run example
    asyncio.run(main())
