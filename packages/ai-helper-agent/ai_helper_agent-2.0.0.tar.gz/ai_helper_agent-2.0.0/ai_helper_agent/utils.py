"""
Utility functions for AI Helper Agent v1
"""

import pathlib
import subprocess
import json
import structlog
from typing import Dict, Any, List, Optional

logger = structlog.get_logger()


def validate_python_code(code: str) -> Dict[str, Any]:
    """Validate Python code syntax"""
    try:
        compile(code, '<string>', 'exec')
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax error at line {e.lineno}: {e.msg}",
            "line": e.lineno,
            "offset": e.offset
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


def run_python_code(code: str, timeout: int = 10) -> Dict[str, Any]:
    """Run Python code and capture output with basic security measures"""
    import tempfile
    import os
    
    # Basic security checks
    dangerous_patterns = [
        "import os", "os.", "__import__", "exec(", "eval(", 
        "open(", "file(", "subprocess", "system", "popen",
        "shutil", "rmtree", "remove", "delete", "rm "
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code.lower():
            logger.warning("Potentially dangerous code detected", pattern=pattern)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Security: Code contains potentially dangerous pattern: {pattern}",
                "returncode": -1
            }
    
    try:
        # Use temporary directory for better isolation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = pathlib.Path(temp_dir) / "temp_code_test.py"
            
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Run the code with restricted environment
            env = os.environ.copy()
            env["PYTHONPATH"] = ""  # Clear Python path for security
            
            result = subprocess.run(
                ["python", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=temp_dir  # Run in isolated directory
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        
    except subprocess.TimeoutExpired:
        logger.warning("Code execution timed out", timeout=timeout)
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Code execution timed out after {timeout} seconds",
            "returncode": -1
        }
    except Exception as e:
        logger.error("Error executing code", error=str(e))
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }


def find_python_files(directory: str = ".") -> List[str]:
    """Find all Python files in directory"""
    path = pathlib.Path(directory)
    python_files = []
    
    for file_path in path.rglob("*.py"):
        if file_path.is_file():
            relative_path = file_path.relative_to(path)
            python_files.append(str(relative_path))
    
    return sorted(python_files)


def count_code_lines(code: str) -> Dict[str, int]:
    """Count different types of lines in code"""
    lines = code.splitlines()
    
    counts = {
        "total": len(lines),
        "empty": 0,
        "comments": 0,
        "code": 0
    }
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            counts["empty"] += 1
        elif stripped.startswith("#"):
            counts["comments"] += 1
        else:
            counts["code"] += 1
    
    return counts


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def create_backup(filepath: str) -> Optional[str]:
    """Create a backup of a file"""
    try:
        original = pathlib.Path(filepath)
        if not original.exists():
            return None
        
        backup_path = original.with_suffix(f"{original.suffix}.backup")
        
        # If backup already exists, add number
        counter = 1
        while backup_path.exists():
            backup_path = original.with_suffix(f"{original.suffix}.backup.{counter}")
            counter += 1
        
        # Copy the file
        import shutil
        shutil.copy2(original, backup_path)
        
        return str(backup_path)
        
    except Exception as e:
        logger.error("Error creating backup", error=str(e), filepath=filepath)
        return None


def extract_functions(code: str) -> List[Dict[str, Any]]:
    """Extract function definitions from Python code"""
    import ast
    
    try:
        tree = ast.parse(code)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node)
                })
        
        return functions
        
    except Exception as e:
        logger.error("Error extracting functions", error=str(e))
        return []


def extract_imports(code: str) -> List[str]:
    """Extract import statements from Python code"""
    import ast
    
    try:
        tree = ast.parse(code)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        return sorted(set(imports))
        
    except Exception as e:
        logger.error("Error extracting imports", error=str(e))
        return []


def get_user_data_dir() -> pathlib.Path:
    """Get user data directory for AI Helper Agent"""
    import os
    
    # Use Windows user directory
    if os.name == 'nt':
        base_dir = pathlib.Path.home()
    else:
        base_dir = pathlib.Path.home()
    
    user_data_dir = base_dir / ".ai_helper_agent"
    user_data_dir.mkdir(exist_ok=True)
    return user_data_dir


def format_code_output(result: Dict[str, Any]) -> str:
    """Format code execution output for display"""
    if result["success"]:
        output = "✅ Success\n"
        if result["stdout"]:
            output += f"Output:\n{result['stdout']}"
        return output
    else:
        output = "❌ Error\n"
        if result["stderr"]:
            output += f"Error:\n{result['stderr']}"
        return output
