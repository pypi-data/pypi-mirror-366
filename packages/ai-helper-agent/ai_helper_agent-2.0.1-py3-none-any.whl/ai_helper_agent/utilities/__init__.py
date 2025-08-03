"""
AI Helper Agent - Utilities Module
Enhanced utility modules with Rich UI support

This module contains utility tools and helpers for the AI Helper Agent,
including the enhanced API key management system and centralized logo system with Rich UI.
"""

__version__ = "2.0.1"
__author__ = "AI Helper Agent Team"

# Import key utilities for easy access
try:
    from .api_key_setup import (
        show_banner,
        show_provider_info,
        check_current_keys,
        interactive_setup,
        quick_add_key,
        show_stored_keys,
        show_full_keys,
        edit_existing_key,
        validate_api_key,
        manage_keys_menu,
        remove_key,
        show_help,
        mask_api_key
    )
    
    from .simple_logo import (
        get_simple_logo,
        get_enhanced_logo,
        display_cli_header,
        display_simple_header,
        get_terminal_size
    )
    
    __all__ = [
        # API Key Management
        'show_banner',
        'show_provider_info', 
        'check_current_keys',
        'interactive_setup',
        'quick_add_key',
        'show_stored_keys',
        'show_full_keys',
        'edit_existing_key',
        'validate_api_key',
        'manage_keys_menu',
        'remove_key',
        'show_help',
        'mask_api_key',
        
        # Logo System
        'get_simple_logo',
        'get_enhanced_logo',
        'display_cli_header',
        'display_simple_header',
        'get_terminal_size'
    ]
    
except ImportError as e:
    # Graceful fallback if dependencies are not available
    __all__ = []
    print(f"Warning: Some utilities not available due to missing dependencies: {e}")
