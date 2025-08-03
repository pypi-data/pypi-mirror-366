"""
AI Helper Agent - Simple Logo System
Provides clean, responsive logos for CLI interfaces
"""

import shutil

def get_terminal_size():
    """Get terminal dimensions safely"""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24

def get_simple_logo():
    """Get a simple, responsive logo that works in all terminals"""
    columns, _ = get_terminal_size()
    
    if columns >= 80:
        return """
╔══════════════════════════════════════════════════════════════════╗
║                🤖 AI HELPER AGENT - v2.0.1 🤖                   ║
║                   Your AI Programming Assistant                  ║
╚══════════════════════════════════════════════════════════════════╝
        """.strip()
    elif columns >= 60:
        return """
┌─────────────────────────────────────────────────────────┐
│          🤖 AI HELPER AGENT v2.0.1 🤖             │
│           Your AI Programming Assistant             │
└─────────────────────────────────────────────────────────┘
        """.strip()
    else:
        return """
🤖 AI HELPER AGENT v2.0.1 🤖
  Your AI Programming Assistant
        """.strip()

def get_enhanced_logo():
    """Get an enhanced logo with more details"""
    return get_simple_logo()

def display_cli_header(title="AI Helper Agent", version="2.0.1"):
    """Display a CLI header with title and version"""
    columns, _ = get_terminal_size()
    
    if columns >= 80:
        border = "=" * min(70, columns - 10)
        title_line = f" 🤖 {title.upper()} - v{version} 🤖 "
        subtitle_line = " Your AI Programming Assistant "
        
        return f"""
╔{border}╗
║{title_line.center(len(border))}║
║{subtitle_line.center(len(border))}║
╚{border}╝
        """.strip()
    else:
        return f"🤖 {title} v{version} 🤖"

def display_simple_header(title="AI Helper Agent"):
    """Display a simple header"""
    return f"🤖 {title} 🤖"

# Legacy compatibility functions
def simple_logo():
    """Legacy function - use get_simple_logo() instead"""
    return get_simple_logo()

def display_logo():
    """Legacy function - use display_cli_header() instead"""
    return display_cli_header()

# Export all functions
__all__ = [
    'get_terminal_size',
    'get_simple_logo', 
    'get_enhanced_logo',
    'display_cli_header',
    'display_simple_header',
    'simple_logo',  # Legacy function
    'display_logo'  # Legacy function
]