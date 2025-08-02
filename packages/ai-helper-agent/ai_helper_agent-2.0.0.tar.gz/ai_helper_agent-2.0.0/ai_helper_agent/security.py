"""
Security manager for AI Helper Agent
Enhanced with search functionality and improved file creation
"""

import os
import pathlib
import glob
import re
from typing import List, Dict, Any, Set
import structlog

logger = structlog.get_logger()


class SecurityManager:
    """Manages security policies and access control"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = pathlib.Path(workspace_path).resolve()
        self.allowed_extensions = {
            ".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml",
            ".js", ".ts", ".html", ".css", ".xml", ".csv", ".log",
            ".ini", ".conf", ".sh", ".bat", ".ps1", ".dockerfile",
            ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php"
        }
        self.blocked_paths = {
            "/etc", "/bin", "/usr/bin", "/sbin", "/usr/sbin",
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
            "/System", "/usr/system"
        }
        self.blocked_patterns = {
            "password", "secret", "token", "key", "credential",
            ".ssh", ".git/config", "database.yml", ".env"
        }
        # Safe write directories
        self.safe_write_dirs = {
            str(self.workspace_path),
            str(self.workspace_path / "output"),
            str(self.workspace_path / "generated"),
            str(self.workspace_path / "temp")
        }
        
        # Ensure generated directory exists
        self.generated_dir = self.workspace_path / "generated"
        self.generated_dir.mkdir(exist_ok=True)
    
    def is_file_accessible(self, filepath: str) -> bool:
        """Check if file is accessible for read/write operations"""
        try:
            file_path = pathlib.Path(filepath).resolve()
            
            # Check if file is within workspace
            try:
                file_path.relative_to(self.workspace_path)
            except ValueError:
                logger.warning("File access denied: outside workspace", 
                             file=str(file_path), workspace=str(self.workspace_path))
                return False
            
            # Check blocked paths
            file_str = str(file_path).lower()
            for blocked in self.blocked_paths:
                if file_str.startswith(blocked.lower()):
                    logger.warning("File access denied: blocked path", file=str(file_path))
                    return False
            
            # Check blocked patterns
            for pattern in self.blocked_patterns:
                if pattern.lower() in file_str:
                    logger.warning("File access denied: contains blocked pattern", 
                                 file=str(file_path), pattern=pattern)
                    return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                logger.warning("File access denied: unsupported extension", 
                             file=str(file_path), extension=file_path.suffix)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Error checking file access", error=str(e), file=filepath)
            return False
    
    def validate_command(self, command: str) -> bool:
        """Validate if a command is safe to execute"""
        dangerous_commands = {
            "rm", "del", "rmdir", "format", "fdisk", "mkfs",
            "sudo", "su", "chmod", "chown", "passwd",
            "wget", "curl", "nc", "netcat", "telnet",
            "python -c", "exec", "eval"
        }
        
        command_lower = command.lower().strip()
        
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                logger.warning("Command blocked: contains dangerous pattern", 
                             command=command, pattern=dangerous)
                return False
        
        return True
    
    def authorize_task(self, task_description: str) -> bool:
        """Authorize a task based on its description"""
        # Simple authorization - can be extended
        sensitive_operations = [
            "delete", "remove", "format", "install", "uninstall",
            "network", "internet", "download", "upload", "send"
        ]
        
        desc_lower = task_description.lower()
        for operation in sensitive_operations:
            if operation in desc_lower:
                logger.info("Sensitive operation detected, requiring approval", 
                          task=task_description, operation=operation)
                return self._request_user_approval(task_description)
        
        return True
    
    def _request_user_approval(self, task: str) -> bool:
        """Request user approval for sensitive operations"""
        try:
            response = input(f"\n⚠️  The agent wants to perform: {task}\nDo you approve? (y/N): ")
            approved = response.lower().strip() == 'y'
            logger.info("User approval requested", task=task, approved=approved)
            return approved
        except (KeyboardInterrupt, EOFError):
            logger.info("User approval cancelled")
            return False
    
    def is_file_writable(self, filepath: str) -> bool:
        """Check if file is writable (for creating/modifying files)"""
        try:
            file_path = pathlib.Path(filepath).resolve()
            parent_dir = file_path.parent
            
            # Check if parent directory is in safe write areas
            parent_str = str(parent_dir)
            for safe_dir in self.safe_write_dirs:
                if parent_str.startswith(safe_dir):
                    # Ensure parent directory exists or can be created
                    try:
                        parent_dir.mkdir(parents=True, exist_ok=True)
                        return True
                    except PermissionError:
                        logger.warning("Permission denied creating directory", 
                                     directory=str(parent_dir))
                        return False
            
            # Check if within workspace (fallback)
            try:
                file_path.relative_to(self.workspace_path)
                return True
            except ValueError:
                logger.warning("File write denied: outside safe areas", 
                             file=str(file_path))
                return False
                
        except Exception as e:
            logger.error("Error checking file write permissions", error=str(e), file=filepath)
            return False
    
    def create_safe_file(self, filename: str, content: str, subdir: str = "generated") -> bool:
        """Safely create a file in a designated safe directory"""
        try:
            # Create safe directory
            safe_dir = self.workspace_path / subdir
            safe_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file path
            file_path = safe_dir / filename
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("File created successfully", file=str(file_path))
            return True
            
        except PermissionError as e:
            logger.error("Permission denied creating file", error=str(e), file=filename)
            return False
        except Exception as e:
            logger.error("Error creating file", error=str(e), file=filename)
            return False
    
    def search_files(self, pattern: str, file_types: List[str] = None) -> List[str]:
        """Search for files matching pattern within workspace"""
        try:
            import glob
            import fnmatch
            
            if file_types is None:
                file_types = [ext[1:] for ext in self.allowed_extensions]  # Remove dot
            
            results = []
            
            # Search in workspace directory
            for file_type in file_types:
                search_pattern = f"**/*.{file_type}"
                for file_path in self.workspace_path.glob(search_pattern):
                    if self.is_file_accessible(str(file_path)):
                        # Check if filename or content matches pattern
                        if fnmatch.fnmatch(file_path.name.lower(), f"*{pattern.lower()}*"):
                            results.append(str(file_path.relative_to(self.workspace_path)))
            
            return sorted(results)
            
        except Exception as e:
            logger.error("Error searching files", error=str(e), pattern=pattern)
            return []
    
    def search_in_files(self, search_text: str, file_types: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search for text content within files"""
        try:
            if file_types is None:
                file_types = [ext[1:] for ext in self.allowed_extensions if ext in {".py", ".txt", ".md", ".js", ".ts"}]
            
            results = {}
            
            for file_type in file_types:
                search_pattern = f"**/*.{file_type}"
                for file_path in self.workspace_path.glob(search_pattern):
                    if self.is_file_accessible(str(file_path)):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                matches = []
                                
                                for line_num, line in enumerate(lines, 1):
                                    if search_text.lower() in line.lower():
                                        matches.append({
                                            "line_number": line_num,
                                            "line_content": line.strip(),
                                            "context": self._get_line_context(lines, line_num - 1)
                                        })
                                
                                if matches:
                                    rel_path = str(file_path.relative_to(self.workspace_path))
                                    results[rel_path] = matches
                                    
                        except Exception as e:
                            logger.debug("Error reading file for search", file=str(file_path), error=str(e))
                            continue
            
            return results
            
        except Exception as e:
            logger.error("Error searching in files", error=str(e), search_text=search_text)
            return {}
    
    def _get_line_context(self, lines: List[str], line_index: int, context_size: int = 2) -> Dict[str, Any]:
        """Get context around a specific line"""
        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)
        
        context_lines = []
        for i in range(start, end):
            context_lines.append({
                "line_number": i + 1,
                "content": lines[i].strip(),
                "is_match": i == line_index
            })
        
        return {
            "before": context_lines[:context_size],
            "match": context_lines[context_size] if len(context_lines) > context_size else None,
            "after": context_lines[context_size + 1:] if len(context_lines) > context_size else []
        }


# Create global security manager instance
security_manager = SecurityManager()
