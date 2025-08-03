#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Helper Agent - Fast CLI Selector
Lightweight entry point to choose and launch CLI tools with minimal startup time
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class FastCLISelector:
    """Lightweight CLI selector with minimal startup overhead"""
    
    def __init__(self, skip_startup=False):
        self.skip_startup = skip_startup
        # Only store minimal data needed for selection
        self.cli_commands = {
            "1": ("ai-fast-chat", "Single Provider CLI - Ultra Fast Groq AI"),
            "2": ("ai-web-chat", "Internet Single CLI - Groq with Web Search"),
            "3": ("ai-advanced", "Enhanced CLI - Advanced Features"),
            "4": ("ai-super-chat", "Enhanced Internet CLI - Most Powerful"),
            "5": ("ai-smart-chat", "Multi Provider CLI - All AI Providers"),
            "6": ("ai-menu", "Full CLI Selector - Complete Options")
        }
    
    def show_quick_menu(self):
        """Show a fast, simple menu without Rich formatting"""
        print("⚡ AI Helper Agent - Quick CLI Selector")
        print("=" * 50)
        print("Choose your AI interface:")
        print()
        
        for key, (command, description) in self.cli_commands.items():
            print(f"  {key}. {description}")
            print(f"     Command: {command}")
        
        print()
        print("  q. Quit")
        print("=" * 50)
    
    def get_user_choice(self) -> Optional[str]:
        """Get user choice with simple input"""
        try:
            choice = input("\nEnter your choice (1-6, q): ").strip().lower()
            return choice
        except (KeyboardInterrupt, EOFError):
            return "q"
    
    def launch_cli(self, command: str) -> bool:
        """Launch the selected CLI command"""
        try:
            print(f"\n🚀 Launching {command}...")
            print("=" * 50)
            
            # Launch the CLI command
            subprocess.run([command], check=False)
            return True
            
        except FileNotFoundError:
            print(f"❌ Command '{command}' not found!")
            print("   Make sure AI Helper Agent is properly installed.")
            return False
        except Exception as e:
            print(f"❌ Error launching {command}: {e}")
            return False
    
    def run(self):
        """Run the fast CLI selector"""
        if self.skip_startup:
            return  # Just initialize for testing
            
        while True:
            try:
                self.show_quick_menu()
                choice = self.get_user_choice()
                
                if choice == "q":
                    print("\n👋 Goodbye!")
                    break
                elif choice in self.cli_commands:
                    command, _ = self.cli_commands[choice]
                    if self.launch_cli(command):
                        break  # Exit after launching
                else:
                    print(f"\n❌ Invalid choice: {choice}")
                    print("Please enter 1-6 or 'q' to quit.")
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                break

def main():
    """Main entry point for fast CLI selector"""
    selector = FastCLISelector()
    selector.run()

if __name__ == "__main__":
    main()
