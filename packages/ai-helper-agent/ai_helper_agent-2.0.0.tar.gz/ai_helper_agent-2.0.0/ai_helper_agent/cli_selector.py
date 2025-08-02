#!/usr/bin/env python3
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

# Rich imports for beautiful interface
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.text import Text
    from rich import print as rich_print
    from rich.columns import Columns
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    rich_print = print

# Initialize console
if RICH_AVAILABLE:
    console = Console()
else:
    console = None


class CLISelector:
    """Main CLI selector to choose and launch specific CLI tools"""
    
    def __init__(self):
        self.cli_tools = self._get_available_cli_tools()
    
    def _get_available_cli_tools(self) -> Dict[str, Dict]:
        """Get all available CLI tools with their information"""
        return {
            "1": {
                "name": "🌟 AI Super Chat (G4F)",
                "module": "ai_helper_agent.enhanced_internet_cli",
                "description": "Most Powerful - G4F + Groq with Internet Search",
                "features": ["G4F (GPT4Free)", "Groq Lightning Fast", "Internet Search", "Rich Formatting"],
                "use_case": "Free AI access with web search capabilities",
                "status": "🌟 FLAGSHIP - Production Ready"
            },
            "2": {
                "name": "⚡ AI Chat",
                "module": "ai_helper_agent.cli_single",
                "description": "Simple & Fast - Basic Groq AI Chat",
                "features": ["Groq Only", "Ultra Fast", "Rich Formatting", "Conversation History"],
                "use_case": "Lightning-fast responses for quick tasks",
                "status": "✅ Production Ready"
            },
            "3": {
                "name": "🌐 AI Web Chat",
                "module": "ai_helper_agent.cli_internet_single",
                "description": "Groq with Internet Search - AI with Web Access",
                "features": ["Groq Models", "Web Search", "Rich Formatting", "Internet Access"],
                "use_case": "Groq with real-time web information",
                "status": "✅ Production Ready"
            },
            "4": {
                "name": "🤖 AI Smart Chat",
                "module": "ai_helper_agent.multi_provider_cli",
                "description": "Multi-Provider - Choose Any AI Provider",
                "features": ["Groq", "OpenAI", "Anthropic", "Google"],
                "use_case": "Access to all major AI providers",
                "status": "✅ Production Ready"
            },
            "5": {
                "name": "🔧 AI Advanced Chat",
                "module": "ai_helper_agent.enhanced_cli",
                "description": "Enhanced Multi-Provider - Advanced Features",
                "features": ["All Providers", "File Analysis", "Code Review", "Workspace Management"],
                "use_case": "Development work with file processing",
                "status": "✅ Production Ready"
            },
            "6": {
                "name": "📜 Legacy Multi-Chat",
                "module": "ai_helper_agent.cli",
                "description": "Legacy Multi-Provider - Original Version",
                "features": ["Legacy Support", "Basic Features", "Multi-Provider"],
                "use_case": "Compatibility and legacy features",
                "status": "⚠️ Legacy"
            }
        }
    
    def show_banner(self):
        """Show the main CLI selector banner"""
        if not RICH_AVAILABLE:
            print("🤖 AI HELPER AGENT - CLI SELECTOR 🤖")
            print("Choose your preferred CLI interface")
            return
        
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                🤖 AI HELPER AGENT - CLI SELECTOR 🤖              ║
║                   Choose Your Preferred Interface                ║
╚══════════════════════════════════════════════════════════════════╝

🚀 Select from our production-ready CLI tools below
⚡ Each tool is optimized for specific use cases
🎯 All tools feature Rich formatting and conversation history
        """
        
        console.print(Panel(
            Align.center(banner.strip()),
            border_style="cyan",
            padding=(1, 2)
        ))
    
    def show_cli_options(self):
        """Display available CLI options in a beautiful table"""
        if not RICH_AVAILABLE:
            print("\nAvailable CLI Tools:")
            for key, cli in self.cli_tools.items():
                print(f"{key}. {cli['name']}")
                print(f"   {cli['description']}")
                print(f"   Status: {cli['status']}")
                print()
            return
        
        # Create main table
        table = Table(
            title="🎯 Available CLI Tools",
            show_header=True,
            header_style="bold cyan",
            border_style="blue"
        )
        
        table.add_column("ID", style="bold green", width=4)
        table.add_column("CLI Tool", style="bold white", width=30)
        table.add_column("Description", style="white", width=35)
        table.add_column("Status", style="bold", width=20)
        
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
                cli['description'],
                status_style
            )
        
        console.print(table)
        
        # Show detailed features for flagship tool
        self.show_flagship_features()
    
    def show_flagship_features(self):
        """Show detailed features of the flagship CLI"""
        if not RICH_AVAILABLE:
            return
        
        flagship = self.cli_tools["1"]  # Enhanced Internet CLI
        
        features_text = Text()
        features_text.append("🌟 FLAGSHIP FEATURES:\n", style="bold gold1")
        for feature in flagship['features']:
            features_text.append(f"  ✅ {feature}\n", style="green")
        
        features_text.append(f"\n🎯 USE CASE: {flagship['use_case']}", style="bold cyan")
        
        console.print(Panel(
            features_text,
            title="⭐ Enhanced Internet CLI (Recommended)",
            border_style="gold1",
            padding=(1, 2)
        ))
    
    def show_detailed_comparison(self):
        """Show detailed comparison of CLI tools"""
        if not RICH_AVAILABLE:
            print("\nDetailed CLI Comparison:")
            print("1. Enhanced Internet CLI: G4F + Groq + Internet (FLAGSHIP)")
            print("2. Single CLI: Groq only (Fastest)")
            print("3. Internet Single: Groq + Internet")
            print("4. Multi-Provider: All providers")
            print("5. Enhanced Multi: All providers + File processing")
            print("6. Legacy CLI: Original implementation")
            return
        
        comparison_table = Table(
            title="🔍 Detailed CLI Comparison",
            show_header=True,
            header_style="bold magenta",
            border_style="magenta"
        )
        
        comparison_table.add_column("Feature", style="bold white", width=20)
        comparison_table.add_column("Enhanced Internet", style="gold1", width=15)
        comparison_table.add_column("Single", style="green", width=10)
        comparison_table.add_column("Internet Single", style="blue", width=15)
        comparison_table.add_column("Multi-Provider", style="cyan", width=15)
        comparison_table.add_column("Enhanced Multi", style="purple", width=15)
        
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
        
        console.print(comparison_table)
    
    def get_user_choice(self) -> str:
        """Get user's CLI choice"""
        if RICH_AVAILABLE:
            choice = Prompt.ask(
                "\n🚀 [bold cyan]Select CLI tool[/bold cyan]",
                choices=list(self.cli_tools.keys()) + ["help", "compare", "quit"],
                default="1"
            )
        else:
            print(f"\nChoices: {', '.join(self.cli_tools.keys())}, help, compare, quit")
        try:
            choice = input("🚀 Select CLI tool (1): ").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        return choice
    
    def launch_cli(self, choice: str):
        """Launch the selected CLI tool"""
        if choice not in self.cli_tools:
            if RICH_AVAILABLE:
                console.print("[red]❌ Invalid choice[/red]")
            else:
                print("❌ Invalid choice")
            return False
        
        cli_info = self.cli_tools[choice]
        
        if RICH_AVAILABLE:
            console.print(f"\n🚀 [bold green]Launching {cli_info['name']}...[/bold green]")
            console.print(f"📝 [dim]{cli_info['description']}[/dim]")
        else:
            print(f"\n🚀 Launching {cli_info['name']}...")
            print(f"📝 {cli_info['description']}")
        
        try:
            # Launch the selected CLI module
            import subprocess
            import sys
            
            cmd = [sys.executable, "-m", cli_info['module']]
            
            if RICH_AVAILABLE:
                console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
            
            # Execute the CLI
            result = subprocess.run(cmd, cwd=Path.cwd())
            
            return True
            
        except KeyboardInterrupt:
            if RICH_AVAILABLE:
                console.print("\n[yellow]👋 Returning to CLI selector...[/yellow]")
            else:
                print("\n👋 Returning to CLI selector...")
            return True
        except Exception as e:
            error_msg = f"❌ Error launching CLI: {str(e)}"
            if RICH_AVAILABLE:
                console.print(f"[red]{error_msg}[/red]")
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
        
        if RICH_AVAILABLE:
            console.print(Panel(
                help_text.strip(),
                title="📚 Help & Guide",
                border_style="blue",
                padding=(1, 2)
            ))
        else:
            print(help_text)
    
    def run(self):
        """Main CLI selector loop"""
        if RICH_AVAILABLE:
            console.print("\n[bold green]🚀 Welcome to AI Helper Agent![/bold green]")
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
                    if RICH_AVAILABLE:
                        console.print("\n[yellow]👋 Thank you for using AI Helper Agent! Goodbye![/yellow]")
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
                    if RICH_AVAILABLE:
                        console.print("[red]❌ Invalid choice. Try again.[/red]")
                    else:
                        print("❌ Invalid choice. Try again.")
                    continue
                    
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    console.print("\n[yellow]👋 Thank you for using AI Helper Agent! Goodbye![/yellow]")
                else:
                    print("\n👋 Thank you for using AI Helper Agent! Goodbye!")
                break
            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                if RICH_AVAILABLE:
                    console.print(f"[red]{error_msg}[/red]")
                else:
                    print(error_msg)
                try:
                    input("\nPress Enter to continue...")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Goodbye!")
                    sys.exit(0)


def show_rich_help():
    """Show Rich-formatted help for CLI selector"""
    if not RICH_AVAILABLE:
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
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    
    console = Console()
    
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
    options_table = Table(show_header=True, header_style="bold magenta")
    options_table.add_column("Option", style="cyan", width=20)
    options_table.add_column("Description", style="white")
    
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
    cli_table = Table(show_header=True, header_style="bold magenta")
    cli_table.add_column("#", style="yellow", width=3)
    cli_table.add_column("CLI Tool", style="cyan", width=25)
    cli_table.add_column("Description", style="white")
    
    cli_selector = CLISelector()
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
        version="AI Helper Agent CLI Selector v1.0"
    )
    
    args = parser.parse_args()
    
    try:
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
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
