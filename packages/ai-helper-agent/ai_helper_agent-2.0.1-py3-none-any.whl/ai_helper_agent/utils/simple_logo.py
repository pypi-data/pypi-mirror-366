"""
AI Helper Agent - Simple Logo System (Compatibility Layer)
This module provides backward compatibility by redirecting to the enhanced
logo system in the utilities directory.

DEPRECATED: Please use ai_helper_agent.utilities.simple_logo instead.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "ai_helper_agent.utils.simple_logo is deprecated. "
    "Use ai_helper_agent.utilities.simple_logo instead.",
    DeprecationWarning,
    stacklevel=2
)

try:
    # Import everything from the new utilities location
    from ai_helper_agent.utilities.simple_logo import *
    
    # Maintain backward compatibility
    __all__ = [
        'get_terminal_size',
        'get_simple_logo', 
        'get_enhanced_logo',
        'display_cli_header',
        'display_simple_header',
        'simple_logo',  # Legacy function
        'display_logo'  # Legacy function
    ]
    
except ImportError as e:
    # Fallback implementation if utilities are not available
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
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🤖 AI HELPER AGENT 🤖                              ║  
║                        Your Intelligent Assistant                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
            """.strip()
        elif columns >= 60:
            return """
╔════════════════════════════════════════════════════════════════════════════════════╗
║                🤖 AI HELPER AGENT 🤖                       ║
║               Your Intelligent Assistant                   ║
╚════════════════════════════════════════════════════════════════════════════════════╝
            """.strip()
        else:
            return """
┌─────────────────────────────────────┐
│     🤖 AI HELPER AGENT 🤖          │
│    Your Intelligent Assistant      │
└─────────────────────────────────────┘
            """.strip()
    
    def display_cli_header(cli_name=None, enhanced=False):
        """Display CLI header with responsive logo"""
        print()
        print(get_simple_logo())
        if cli_name:
            columns, _ = get_terminal_size()
            if columns >= 60:
                print(f"\n🛠️  {cli_name.upper()}  🛠️".center(columns))
            else:
                print(f"🛠️ {cli_name.upper()} 🛠️")
        print()
    
    def display_simple_header(title):
        """Display a simple header without the full logo"""
        columns, _ = get_terminal_size()
        print()
        if columns >= 40:
            print(f"🔧 {title.upper()} 🔧".center(columns))
        else:
            print(f"🔧 {title.upper()} 🔧")
        print("=" * min(len(title) + 8, columns))
        print()
    
    # Legacy functions for backward compatibility
    def simple_logo():
        return get_simple_logo()
    
    def display_logo():
        display_cli_header()
    
    def get_enhanced_logo():
        return None
    
    __all__ = [
        'get_terminal_size',
        'get_simple_logo', 
        'get_enhanced_logo',
        'display_cli_header',
        'display_simple_header',
        'simple_logo',
        'display_logo'
    ]
    
    print(f"Warning: Enhanced utilities not available, using fallback: {e}")
