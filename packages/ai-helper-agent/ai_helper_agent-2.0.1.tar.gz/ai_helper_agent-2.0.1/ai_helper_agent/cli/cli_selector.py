#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Helper Agent - CLI Selector
Main entry point to choose and launch any available CLI tool
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Lazy Rich imports - only load when needed
def _lazy_import_rich():
    """Lazy import Rich components only when needed"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.prompt import Prompt
        from rich.text import Text
        from rich import print as rich_print
        from rich.columns import Columns
        from rich.align import Align
        return {
            'Console': Console,
            'Panel': Panel,
            'Table': Table,
            'Prompt': Prompt,
            'Text': Text,
            'rich_print': rich_print,
            'Columns': Columns,
            'Align': Align,
            'available': True
        }
    except ImportError:
        return {
            'available': False,
            'Console': None,
            'Panel': None,
            'Table': None,
            'Prompt': None,
            'Text': None,
            'rich_print': print,
            'Columns': None,
            'Align': None
        }

# Global variables for lazy initialization
_rich_components = None
_console = None


class CLISelector:
    """Main CLI selector to choose and launch specific CLI tools"""
    
    def __init__(self, skip_startup=False):
        self.skip_startup = skip_startup
        # Minimize initialization - only set basic properties
        self._cli_tools = None  # Lazy load CLI tools
        self._rich_components = None
        self._console = None
        
        # If skip_startup is True, don't initialize anything heavy
        if skip_startup:
            return
    
    @property
    def rich_components(self):
        """Lazy load Rich components"""
        if self._rich_components is None:
            self._rich_components = _lazy_import_rich()
        return self._rich_components
    
    @property
    def console(self):
        """Lazy load Rich console"""
        if self._console is None and self.rich_components['available']:
            self._console = self.rich_components['Console']()
        return self._console
    
    @property
    def cli_tools(self):
        """Lazy load CLI tools only when needed"""
        if self._cli_tools is None:
            self._cli_tools = self._get_available_cli_tools()
        return self._cli_tools
    
    def _get_available_cli_tools(self) -> Dict[str, Dict]:
        """Get all available CLI tools with their information"""
        return {
            "1": {
                "name": "🌟 AI Super Chat",
                "command": "ai-super-chat",
                "aliases": ["ai-smart", "ai-genius"],
                "module": "ai_helper_agent.cli.enhanced_internet_cli",
                "description": "Most Powerful - G4F + Groq with Internet Search",
                "features": ["G4F (GPT4Free)", "Groq Lightning Fast", "Internet Search", "Rich Formatting"],
                "use_case": "Free AI access with web search capabilities",
                "status": "🌟 FLAGSHIP - Production Ready"
            },
            "2": {
                "name": "⚡ AI Fast Chat",
                "command": "ai-fast-chat",
                "aliases": ["ai-quick", "ai-turbo"],
                "module": "ai_helper_agent.cli.cli_single",
                "description": "Lightning Fast - Basic Groq AI Chat",
                "features": ["Groq Only", "Ultra Fast", "Rich Formatting", "Conversation History"],
                "use_case": "Lightning-fast responses for quick tasks",
                "status": "✅ Production Ready"
            },
            "3": {
                "name": "🌐 AI Web Chat",
                "command": "ai-web-chat",
                "aliases": ["ai-search", "ai-internet"],
                "module": "ai_helper_agent.cli.cli_internet_single",
                "description": "Smart Search - Groq with Internet Access",
                "features": ["Groq Models", "Web Search", "Rich Formatting", "Internet Access"],
                "use_case": "Groq with real-time web information",
                "status": "✅ Production Ready"
            },
            "4": {
                "name": "🤖 AI Smart Chat",
                "command": "ai-smart-chat",
                "aliases": ["ai-multi", "ai-pro"],
                "module": "ai_helper_agent.cli.multi_provider_cli",
                "description": "Multi-Provider - Choose Any AI Provider",
                "features": ["Groq", "OpenAI", "Anthropic", "Google"],
                "use_case": "Access to all major AI providers",
                "status": "✅ Production Ready"
            },
            "5": {
                "name": "🔧 AI Advanced",
                "command": "ai-advanced",
                "aliases": ["ai-dev", "ai-expert"],
                "module": "ai_helper_agent.cli.enhanced_cli",
                "description": "Developer Pro - Advanced Features + File Processing",
                "features": ["All Providers", "File Analysis", "Code Review", "Workspace Management"],
                "use_case": "Development work with file processing",
                "status": "✅ Production Ready"
            },
            "6": {
                "name": "📜 Legacy Multi-Chat",
                "command": "ai-helper-agent",
                "aliases": ["ai-helper"],
                "module": "ai_helper_agent.cli.cli",
                "description": "Legacy Multi-Provider - Original Version",
                "features": ["Legacy Support", "Basic Features", "Multi-Provider"],
                "use_case": "Compatibility and legacy features",
                "status": "⚠️ Legacy"
            }
        }
    
    def show_banner(self):
        """Show the main CLI selector banner"""
        if not self.rich_components['available']:
            print("🤖 AI HELPER AGENT - CLI SELECTOR 🤖")
            print("Choose your preferred CLI interface")
            return
        
        banner = """
╔════════════════════════════════════════════════════════╗
║         🤖 AI HELPER AGENT - CLI SELECTOR 🤖          ║
║              Choose Your Preferred Interface           ║
╚════════════════════════════════════════════════════════╝

🚀 Select from our production-ready CLI tools below
⚡ Each tool is optimized for specific use cases
🎯 All tools feature Rich formatting and conversation history
        """
        
        self.console.print(self.rich_components['Panel'](
            self.rich_components['Align'].center(banner.strip()),
            border_style="cyan",
            padding=(1, 2)
        ))
    
    def show_cli_options(self):
        """Display available CLI options in a beautiful table"""
        if not self.rich_components['available']:
            print("\nAvailable CLI Tools:")
            for key, cli in self.cli_tools.items():
                print(f"{key}. {cli['name']}")
                print(f"   {cli['description']}")
                print(f"   Status: {cli['status']}")
                print()
            return
        
        # Create main table with row separators - optimized for terminal width
        table = self.rich_components['Table'](
            title="🎯 Available CLI Tools",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
            row_styles=["", "dim"],  # Alternating row styles
            show_lines=True,  # This adds lines between rows
            width=120,  # Set max width to fit most terminals
            expand=False  # Don't expand to full terminal width
        )
        
        table.add_column("ID", style="bold green", width=3, justify="center")
        table.add_column("CLI Tool", style="bold white", width=25, no_wrap=False)
        table.add_column("Command", style="bold cyan", width=15, no_wrap=False)
        table.add_column("Description", style="white", width=35, no_wrap=False)
        table.add_column("Status", style="bold", width=18, justify="center")
        
        for key, cli in self.cli_tools.items():
            # Color code status
            if "FLAGSHIP" in cli['status']:
                status_style = "[bold gold1]" + cli['status'] + "[/bold gold1]"
            elif "Production Ready" in cli['status']:
                status_style = "[bold green]" + cli['status'] + "[/bold green]"
            else:
                status_style = "[bold yellow]" + cli['status'] + "[/bold yellow]"
            
            table.add_row(
                key,
                cli['name'],
                cli['command'],
                cli['description'],
                status_style
            )
        
        self.console.print(table)
        
        # Show command aliases table for easy remembering
        self.show_command_aliases()
        
        # Show detailed features for flagship tool
        self.show_flagship_features()
    
    def show_command_aliases(self):
        """Show command aliases table for easy remembering"""
        if not self.rich_components['available']:
            return
        
        aliases_table = self.rich_components['Table'](
            title="🎯 Easy-to-Remember Commands",
            show_header=True,
            header_style="bold yellow",
            border_style="yellow",
            row_styles=["", "dim"],
            show_lines=True,
            width=100,
            expand=False
        )
        
        aliases_table.add_column("Type", style="bold white", width=15)
        aliases_table.add_column("Main Command", style="bold cyan", width=18)
        aliases_table.add_column("Alternative Names", style="green", width=25)
        aliases_table.add_column("Quick Description", style="white", width=30)
        
        alias_info = [
            ("🌟 Flagship", "ai-super-chat", "ai-smart, ai-genius", "Most powerful with internet"),
            ("⚡ Fastest", "ai-fast-chat", "ai-quick, ai-turbo", "Lightning fast Groq only"),
            ("🌐 Web Search", "ai-web-chat", "ai-search, ai-internet", "Groq with web access"),
            ("🤖 Multi-AI", "ai-smart-chat", "ai-multi, ai-pro", "All AI providers"),
            ("🔧 Developer", "ai-advanced", "ai-dev, ai-expert", "File processing + coding"),
        ]
        
        for type_name, main_cmd, alternatives, desc in alias_info:
            aliases_table.add_row(type_name, main_cmd, alternatives, desc)
        
        self.console.print(aliases_table)
    
    def show_flagship_features(self):
        """Show detailed features of the flagship CLI"""
        if not self.rich_components['available']:
            return
        
        flagship = self.cli_tools["1"]  # Enhanced Internet CLI
        
        features_text = self.rich_components['Text']()
        features_text.append("🌟 FLAGSHIP FEATURES:\n", style="bold gold1")
        for feature in flagship['features']:
            features_text.append(f"  ✅ {feature}\n", style="green")
        
        features_text.append(f"\n🎯 USE CASE: {flagship['use_case']}", style="bold cyan")
        
        self.console.print(self.rich_components['Panel'](
            features_text,
            title="⭐ Enhanced Internet CLI (Recommended)",
            border_style="gold1",
            padding=(1, 2)
        ))
    
    def show_detailed_comparison(self):
        """Show detailed comparison of CLI tools"""
        if not self.rich_components['available']:
            print("\nDetailed CLI Comparison:")
            print("1. Enhanced Internet CLI: G4F + Groq + Internet (FLAGSHIP)")
            print("2. Single CLI: Groq only (Fastest)")
            print("3. Internet Single: Groq + Internet")
            print("4. Multi-Provider: All providers")
            print("5. Enhanced Multi: All providers + File processing")
            print("6. Legacy CLI: Original implementation")
            return
        
        comparison_table = self.rich_components['Table'](
            title="🔍 Detailed CLI Comparison",
            show_header=True,
            header_style="bold magenta",
            border_style="magenta",
            width=110,  # Set max width to fit terminals
            expand=False,
            show_lines=True  # Add lines between rows for better readability
        )
        
        comparison_table.add_column("Feature", style="bold white", width=18)
        comparison_table.add_column("Enhanced Internet", style="gold1", width=12)
        comparison_table.add_column("Single", style="green", width=8)
        comparison_table.add_column("Internet Single", style="blue", width=12)
        comparison_table.add_column("Multi-Provider", style="cyan", width=12)
        comparison_table.add_column("Enhanced Multi", style="purple", width=12)
        
        features_comparison = [
            ("G4F Support", "✅", "❌", "❌", "❌", "❌"),
            ("Groq Support", "✅", "✅", "✅", "✅", "✅"),
            ("Internet Search", "✅", "❌", "✅", "❌", "❌"),
            ("Multi-Provider", "✅", "❌", "❌", "✅", "✅"),
            ("File Processing", "❌", "❌", "❌", "❌", "✅"),
            ("Rich Formatting", "✅", "✅", "✅", "✅", "✅"),
            ("Speed", "Fast", "Fastest", "Fast", "Medium", "Medium"),
            ("Free Access", "✅", "Need API", "Need API", "Need APIs", "Need APIs")
        ]
        
        for feature_row in features_comparison:
            comparison_table.add_row(*feature_row)
        
        self.console.print(comparison_table)
    
    def get_user_choice(self) -> str:
        """Get user's CLI choice"""
        if self.rich_components['available']:
            try:
                choice = self.rich_components['Prompt'].ask(
                    "\n🚀 [bold cyan]Select CLI tool[/bold cyan]",
                    choices=list(self.cli_tools.keys()) + ["help", "compare", "quit"],
                    default="1"
                )
                return choice
            except (EOFError, KeyboardInterrupt):
                if self.rich_components['available']:
                    self.console.print("\n👋 [yellow]Goodbye![/yellow]")
                else:
                    print("\n👋 Goodbye!")
                sys.exit(0)
        else:
            print(f"\nChoices: {', '.join(self.cli_tools.keys())}, help, compare, quit")
            try:
                choice = input("🚀 Select CLI tool (1): ").strip() or "1"
                return choice
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                sys.exit(0)
    
    def launch_cli(self, choice: str):
        """Launch the selected CLI tool"""
        if choice not in self.cli_tools:
            if self.rich_components['available']:
                self.console.print("[red]❌ Invalid choice[/red]")
            else:
                print("❌ Invalid choice")
            return False
        
        cli_info = self.cli_tools[choice]
        
        if self.rich_components['available']:
            self.console.print(f"\n🚀 [bold green]Launching {cli_info['name']}...[/bold green]")
            self.console.print(f"📝 [dim]{cli_info['description']}[/dim]")
        else:
            print(f"\n🚀 Launching {cli_info['name']}...")
            print(f"📝 {cli_info['description']}")
        
        try:
            # Import and run the module directly with improved error handling
            module_name = cli_info['module'].split('.')[-1]  # Get the module name
            
            # Show loading message
            if self.rich_components['available']:
                self.console.print(f"[cyan]⏳ Loading {module_name}...[/cyan]")
            else:
                print(f"⏳ Loading {module_name}...")
            
            # Use subprocess to avoid nested event loop issues
            if self.rich_components['available']:
                self.console.print(f"[cyan]🚀 Starting {module_name} in new process...[/cyan]")
            else:
                print(f"🚀 Starting {module_name} in new process...")
            
            import subprocess
            import sys
            cmd = [sys.executable, "-m", cli_info['module']]
            result = subprocess.run(cmd, cwd=Path.cwd())
            
            return True
            
        except KeyboardInterrupt:
            if self.rich_components['available']:
                self.console.print("\n[yellow]👋 Returning to CLI selector...[/yellow]")
            else:
                print("\n👋 Returning to CLI selector...")
            return True
        except ImportError as e:
            error_msg = f"❌ Module not found: {cli_info['module']} - {str(e)}"
            if self.rich_components['available']:
                self.console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            return False
        except Exception as e:
            error_msg = f"❌ Error launching CLI: {str(e)}"
            if self.rich_components['available']:
                self.console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            return False
    
    def show_help(self):
        """Show help information"""
        help_text = """
🤖 AI HELPER AGENT CLI SELECTOR - HELP

COMMANDS:
• 1-6: Select and launch specific CLI tool
• help: Show this help message
• compare: Show detailed comparison table
• quit: Exit the selector

CLI TOOLS OVERVIEW:

🌟 ENHANCED INTERNET CLI (Recommended)
   • Free access via G4F (GPT4Free)
   • Lightning-fast Groq models
   • Internet search capabilities
   • No API keys required for G4F

⚡ SINGLE PROVIDER CLI
   • Groq-only for maximum speed
   • Optimized for quick tasks
   • Requires Groq API key

🌐 INTERNET SINGLE CLI
   • Groq with web search
   • Real-time information access
   • Requires Groq API key

🤖 MULTI-PROVIDER CLI
   • All major providers supported
   • Provider switching
   • Requires respective API keys

🔧 ENHANCED MULTI-PROVIDER CLI
   • All providers + file processing
   • Code analysis capabilities
   • Development-focused features

TIPS:
• Try Enhanced Internet CLI first (free G4F access)
• Use Single CLI for fastest responses
• Use Enhanced Multi for file analysis
• All tools support Rich formatting and conversation history
        """
        
        if self.rich_components['available']:
            self.console.print(self.rich_components['Panel'](
                help_text.strip(),
                title="📚 Help & Guide",
                border_style="blue",
                padding=(1, 2)
            ))
        else:
            print(help_text)
    
    def run(self):
        """Main CLI selector loop"""
        if self.rich_components['available']:
            self.console.print("\n[bold green]🚀 Welcome to AI Helper Agent![/bold green]")
        else:
            print("\n🚀 Welcome to AI Helper Agent!")
        
        while True:
            try:
                # Show banner and options
                self.show_banner()
                self.show_cli_options()
                
                # Get user choice
                choice = self.get_user_choice()
                
                if choice.lower() == "quit":
                    if self.rich_components['available']:
                        self.console.print("\n[yellow]👋 Thank you for using AI Helper Agent! Goodbye![/yellow]")
                    else:
                        print("\n👋 Thank you for using AI Helper Agent! Goodbye!")
                    break
                
                elif choice.lower() == "help":
                    self.show_help()
                    try:
                        input("\nPress Enter to continue...")
                    except (EOFError, KeyboardInterrupt):
                        print("\n👋 Goodbye!")
                        sys.exit(0)
                    continue
                
                elif choice.lower() == "compare":
                    self.show_detailed_comparison()
                    try:
                        input("\nPress Enter to continue...")
                    except (EOFError, KeyboardInterrupt):
                        print("\n👋 Goodbye!")
                        sys.exit(0)
                    continue
                
                elif choice in self.cli_tools:
                    # Launch selected CLI
                    success = self.launch_cli(choice)
                    if not success:
                        try:
                            input("\nPress Enter to continue...")
                        except (EOFError, KeyboardInterrupt):
                            print("\n👋 Goodbye!")
                            sys.exit(0)
                    # Return to selector after CLI exits
                    continue
                
                else:
                    if self.rich_components['available']:
                        self.console.print("[red]❌ Invalid choice. Try again.[/red]")
                    else:
                        print("❌ Invalid choice. Try again.")
                    continue
                    
            except KeyboardInterrupt:
                if self.rich_components['available']:
                    self.console.print("\n[yellow]👋 Thank you for using AI Helper Agent! Goodbye![/yellow]")
                else:
                    print("\n👋 Thank you for using AI Helper Agent! Goodbye!")
                break
            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                if self.rich_components['available']:
                    self.console.print(f"[red]{error_msg}[/red]")
                else:
                    print(error_msg)
                try:
                    input("\nPress Enter to continue...")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Goodbye!")
                    sys.exit(0)


def show_rich_help():
    """Show Rich-formatted help for CLI selector"""
    # Try to get Rich components
    rich_components = _lazy_import_rich()
    
    if not rich_components['available']:
        # Fallback to plain text
        print("AI Helper Agent - CLI Selector")
        print("\nUsage: ai-helper-selector [options]")
        print("\nOptions:")
        print("  -h, --help            Show this help message")
        print("  --list                List all available CLI tools")
        print("  --launch {1-6}        Directly launch CLI tool")
        print("  --version, -v         Show version")
        print("\nExamples:")
        print("  ai-helper-selector           # Interactive selection")
        print("  ai-helper-selector --list    # List all CLIs")
        print("  ai-helper-selector --launch 1  # Launch AI Super Chat")
        return
    
    console = rich_components['Console']()
    Panel = rich_components['Panel']
    Table = rich_components['Table']
    
    # Main title
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]AI Helper Agent - CLI Selector[/bold blue]\n"
        "[dim]Choose and launch AI CLI tools with ease[/dim]",
        border_style="blue"
    ))
    
    # Usage section
    console.print("\n[bold green]USAGE:[/bold green]")
    console.print("  [cyan]ai-helper-selector[/cyan] [dim][options][/dim]")
    
    # Options table
    options_table = Table(
        show_header=True, 
        header_style="bold magenta",
        width=80,  # Fit standard terminal width
        expand=False,
        show_lines=True
    )
    options_table.add_column("Option", style="cyan", width=18)
    options_table.add_column("Description", style="white", width=50)
    
    options_table.add_row("-h, --help", "Show this help message and exit")
    options_table.add_row("--list", "List all available CLI tools and exit")
    options_table.add_row("--launch {1-6}", "Directly launch specific CLI tool (1-6)")
    options_table.add_row("--version, -v", "Show program's version number and exit")
    
    console.print("\n[bold green]OPTIONS:[/bold green]")
    console.print(options_table)
    
    # Examples section
    console.print("\n[bold green]EXAMPLES:[/bold green]")
    examples = [
        ("ai-helper-selector", "Interactive CLI selection"),
        ("ai-helper-selector --list", "List all available CLIs"),  
        ("ai-helper-selector --launch 1", "Directly launch AI Super Chat (G4F)"),
        ("ai-helper-selector --launch 2", "Directly launch AI Chat (Groq)"),
    ]
    
    for cmd, desc in examples:
        console.print(f"  [cyan]{cmd}[/cyan]  [dim]# {desc}[/dim]")
    
    # Available CLIs
    console.print("\n[bold green]AVAILABLE CLI TOOLS:[/bold green]")
    cli_table = Table(
        show_header=True, 
        header_style="bold magenta",
        width=100,  # Fit standard terminal width
        expand=False,
        show_lines=True
    )
    cli_table.add_column("#", style="yellow", width=3)
    cli_table.add_column("CLI Tool", style="cyan", width=30)
    cli_table.add_column("Description", style="white", width=50)
    
    cli_selector = CLISelector(skip_startup=True)
    for key, cli in cli_selector.cli_tools.items():
        status_icon = "🌟" if cli.get("flagship", False) else "✅"
        cli_table.add_row(key, f"{status_icon} {cli['name']}", cli['description'])
    
    console.print(cli_table)
    console.print("")


def main():
    """Main entry point for CLI selector"""
    # Show Rich help if no arguments or help requested
    if '--help' in sys.argv or '-h' in sys.argv:
        show_rich_help()
        return
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Helper Agent - CLI Selector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-helper-selector           # Interactive CLI selection
  ai-helper-selector --list    # List all available CLIs
  ai-helper-selector --launch 1  # Directly launch AI Super Chat (G4F)
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available CLI tools and exit"
    )
    
    parser.add_argument(
        "--launch",
        type=str,
        choices=["1", "2", "3", "4", "5", "6"],
        help="Directly launch specific CLI tool (1-6)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="AI Helper Agent CLI Selector v2.0.1"
    )
    
    args = parser.parse_args()
    
    try:
        # Use skip_startup for faster initialization where possible
        if args.list or args.launch:
            selector = CLISelector(skip_startup=True)
        else:
            selector = CLISelector()
        
        if args.list:
            # Just list CLIs and exit
            selector.show_cli_options()
            return
        
        if args.launch:
            # Direct launch
            success = selector.launch_cli(args.launch)
            if not success:
                sys.exit(1)
            return
        
        # Interactive mode
        selector.run()
        
    except KeyboardInterrupt:
        try:
            print("\n👋 Goodbye!")
        except UnicodeEncodeError:
            print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        try:
            print(f"❌ Error: {e}")
        except UnicodeEncodeError:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
