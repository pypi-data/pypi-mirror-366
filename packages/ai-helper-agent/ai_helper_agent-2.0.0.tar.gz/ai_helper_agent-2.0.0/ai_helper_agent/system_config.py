"""
System Configuration Module for AI Helper Agent
Handles workspace structure visualization, shell command execution, and system querying
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import psutil
import shutil


class SystemConfigurationManager:
    """Manages system configuration and workspace analysis"""
    
    def __init__(self, workspace_path: Path = None):
        self.workspace_path = workspace_path or Path.cwd()
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total,
            'current_user': os.getenv('USER') or os.getenv('USERNAME'),
            'shell': os.getenv('SHELL') or os.getenv('ComSpec'),
            'env_vars': dict(os.environ)
        }
    
    def get_workspace_structure(self, max_depth: int = 3, max_items: int = 100) -> Dict[str, Any]:
        """Get detailed workspace structure with file analysis"""
        structure = {
            'root': str(self.workspace_path),
            'total_files': 0,
            'total_dirs': 0,
            'file_types': {},
            'languages': {},
            'frameworks': [],
            'tree': {},
            'git_info': None,
            'package_files': []
        }
        
        try:
            # Build file tree
            structure['tree'] = self._build_file_tree(self.workspace_path, max_depth, max_items)
            
            # Analyze workspace contents
            self._analyze_workspace_contents(structure)
            
            # Detect frameworks and tools
            structure['frameworks'] = self._detect_frameworks()
            
            # Get git information
            structure['git_info'] = self._get_git_info()
            
        except Exception as e:
            structure['error'] = str(e)
            
        return structure
    
    def _build_file_tree(self, path: Path, max_depth: int, max_items: int, current_depth: int = 0) -> Dict:
        """Recursively build file tree structure"""
        if current_depth >= max_depth:
            return {'...': 'max_depth_reached'}
        
        tree = {}
        items_counted = 0
        
        try:
            # Sort items: directories first, then files
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if items_counted >= max_items:
                    tree['...'] = f'and {len(list(path.iterdir())) - max_items} more items'
                    break
                
                # Skip hidden files and common ignore patterns
                if item.name.startswith('.') and item.name not in ['.gitignore', '.env', '.vscode']:
                    continue
                
                if item.name in ['node_modules', '__pycache__', '.git', 'build', 'dist', 'target']:
                    tree[f"{item.name}/"] = "ignored"
                    continue
                
                if item.is_dir():
                    tree[f"{item.name}/"] = self._build_file_tree(item, max_depth, max_items, current_depth + 1)
                else:
                    # Add file with metadata
                    try:
                        size = item.stat().st_size
                        tree[item.name] = {
                            'size': size,
                            'type': item.suffix,
                            'size_human': self._format_size(size)
                        }
                    except:
                        tree[item.name] = {'error': 'access_denied'}
                
                items_counted += 1
                
        except PermissionError:
            return {'error': 'permission_denied'}
        except Exception as e:
            return {'error': str(e)}
        
        return tree
    
    def _analyze_workspace_contents(self, structure: Dict):
        """Analyze workspace contents for file types and languages"""
        try:
            for file_path in self.workspace_path.rglob('*'):
                if file_path.is_file():
                    structure['total_files'] += 1
                    
                    # File extension analysis
                    ext = file_path.suffix.lower()
                    if ext:
                        structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                    
                    # Language detection
                    lang = self._detect_language(file_path)
                    if lang:
                        structure['languages'][lang] = structure['languages'].get(lang, 0) + 1
                    
                    # Package files
                    if file_path.name in ['package.json', 'requirements.txt', 'pyproject.toml', 'Cargo.toml', 'go.mod', 'pom.xml']:
                        structure['package_files'].append(str(file_path.relative_to(self.workspace_path)))
                        
                elif file_path.is_dir():
                    structure['total_dirs'] += 1
                    
        except Exception as e:
            structure['analysis_error'] = str(e)
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file"""
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown'
        }
        
        return ext_map.get(file_path.suffix.lower())
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks and tools in workspace"""
        frameworks = []
        
        # Check for common framework indicators
        indicators = {
            'React': ['package.json', 'src/App.js', 'src/App.tsx'],
            'Vue.js': ['package.json', 'src/App.vue'],
            'Angular': ['angular.json', 'src/app/app.module.ts'],
            'Django': ['manage.py', 'settings.py'],
            'Flask': ['app.py', 'requirements.txt'],
            'FastAPI': ['main.py', 'requirements.txt'],
            'Spring Boot': ['pom.xml', 'src/main/java'],
            'Express.js': ['package.json', 'server.js'],
            'Next.js': ['next.config.js', 'pages/'],
            'Rust/Cargo': ['Cargo.toml'],
            'Go Modules': ['go.mod'],
            'Docker': ['Dockerfile', 'docker-compose.yml']
        }
        
        for framework, files in indicators.items():
            if any((self.workspace_path / file).exists() for file in files):
                frameworks.append(framework)
        
        return frameworks
    
    def _get_git_info(self) -> Optional[Dict]:
        """Get Git repository information"""
        try:
            git_dir = self.workspace_path / '.git'
            if not git_dir.exists():
                return None
            
            # Run git commands to get info
            git_info = {}
            
            # Current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=self.workspace_path)
            if result.returncode == 0:
                git_info['current_branch'] = result.stdout.strip()
            
            # Remote URL
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, cwd=self.workspace_path)
            if result.returncode == 0:
                git_info['remote_url'] = result.stdout.strip()
            
            # Last commit
            result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                  capture_output=True, text=True, cwd=self.workspace_path)
            if result.returncode == 0:
                git_info['last_commit'] = result.stdout.strip()
            
            # Status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.workspace_path)
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                git_info['changes'] = len(changes)
                git_info['has_changes'] = len(changes) > 0
            
            return git_info
            
        except Exception:
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def execute_shell_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute shell command with safety checks"""
        # Security check: disallow dangerous commands
        dangerous_commands = [
            'rm -rf', 'del /f', 'format', 'fdisk', 'mkfs',
            'shutdown', 'reboot', 'halt', 'poweroff',
            'dd if=', 'wget', 'curl -O', 'chmod 777'
        ]
        
        if any(dangerous in command.lower() for dangerous in dangerous_commands):
            return {
                'success': False,
                'error': 'Command blocked for security reasons',
                'stdout': '',
                'stderr': 'Dangerous command detected'
            }
        
        try:
            # Determine shell based on OS
            if os.name == 'nt':
                shell_cmd = ['cmd', '/c', command]
            else:
                shell_cmd = ['bash', '-c', command]
            
            result = subprocess.run(
                shell_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace_path
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': command
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds',
                'stdout': '',
                'stderr': 'Timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': str(e)
            }
    
    def get_system_configuration(self) -> Dict[str, Any]:
        """Get comprehensive system configuration"""
        config = {
            'system_info': self.system_info,
            'workspace_info': {
                'path': str(self.workspace_path),
                'exists': self.workspace_path.exists(),
                'is_dir': self.workspace_path.is_dir(),
                'permissions': self._check_permissions()
            },
            'environment': {
                'path_dirs': os.environ.get('PATH', '').split(os.pathsep),
                'python_path': sys.path,
                'current_directory': os.getcwd(),
                'home_directory': str(Path.home())
            },
            'tools': self._detect_installed_tools(),
            'network': self._get_network_info()
        }
        
        return config
    
    def _check_permissions(self) -> Dict[str, bool]:
        """Check workspace permissions"""
        try:
            return {
                'readable': os.access(self.workspace_path, os.R_OK),
                'writable': os.access(self.workspace_path, os.W_OK),
                'executable': os.access(self.workspace_path, os.X_OK)
            }
        except:
            return {'readable': False, 'writable': False, 'executable': False}
    
    def _detect_installed_tools(self) -> Dict[str, bool]:
        """Detect commonly used development tools"""
        tools = ['git', 'node', 'npm', 'python', 'pip', 'docker', 'code', 'vim']
        
        detected = {}
        for tool in tools:
            detected[tool] = shutil.which(tool) is not None
        
        return detected
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network configuration info"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            return {
                'hostname': hostname,
                'local_ip': local_ip,
                'has_internet': self._check_internet_connection()
            }
        except:
            return {'error': 'Network info unavailable'}
    
    def _check_internet_connection(self) -> bool:
        """Check if internet connection is available"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    def render_tree_structure(self, tree: Dict, prefix: str = "", is_last: bool = True) -> str:
        """Render tree structure as ASCII art"""
        lines = []
        items = list(tree.items())
        
        for i, (name, content) in enumerate(items):
            is_last_item = i == len(items) - 1
            current_prefix = "└── " if is_last_item else "├── "
            
            if isinstance(content, dict) and 'size' in content:
                # File with metadata
                lines.append(f"{prefix}{current_prefix}{name} ({content.get('size_human', '')})")
            elif isinstance(content, dict) and content != {'...': 'max_depth_reached'}:
                # Directory
                lines.append(f"{prefix}{current_prefix}{name}")
                if content:
                    next_prefix = prefix + ("    " if is_last_item else "│   ")
                    lines.append(self.render_tree_structure(content, next_prefix, is_last_item))
            else:
                # Simple item or max depth indicator
                lines.append(f"{prefix}{current_prefix}{name}")
        
        return "\n".join(filter(None, lines))


# Global system configuration manager
system_config = SystemConfigurationManager()
