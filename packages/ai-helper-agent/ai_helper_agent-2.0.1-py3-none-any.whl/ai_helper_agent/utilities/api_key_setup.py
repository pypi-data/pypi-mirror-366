#!/usr/bin/env python3
"""
AI Helper Agent - API Key Setup Tool
Enhanced unified API key management interface with Rich UI
Moved to utilities directory for better organization
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional

# Add the project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Rich UI imports
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.align import Align
    from rich import print as rich_print
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None
    rich_print = print

try:
    from ai_helper_agent.managers.api_key_manager import api_key_manager
    MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import API key manager: {e}")
    MANAGER_AVAILABLE = False

def show_banner():
    """Show the API key setup banner with Rich UI"""
    if RICH_AVAILABLE:
        # Create a beautiful banner with Rich
        banner_text = Text()
        banner_text.append("🔑 AI HELPER AGENT\n", style="bold cyan")
        banner_text.append("API KEY MANAGEMENT SYSTEM", style="bold blue")
        
        subtitle = Text()
        subtitle.append("Enhanced secure storage and management of API keys for all AI providers", style="dim white")
        
        panel = Panel(
            Align.center(banner_text + Text("\n") + subtitle),
            title="[bold green]🛡️  SECURE KEY MANAGEMENT[/bold green]",
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print("\n")
        console.print(panel)
        
        # Show quick stats
        if MANAGER_AVAILABLE:
            try:
                stored_keys = api_key_manager.list_stored_keys()
                configured_count = sum(1 for v in stored_keys.values() if v)
                total_count = len(stored_keys)
                
                stats_text = f"📊 Keys Configured: [bold green]{configured_count}[/bold green]/[bold blue]{total_count}[/bold blue] • [dim cyan]Enhanced Rich UI[/dim cyan]"
                console.print(Align.center(stats_text))
            except:
                pass
        
        console.print()
    else:
        # Fallback for non-Rich environments
        print("=" * 60)
        print("🔑 AI HELPER AGENT - API KEY MANAGEMENT (Enhanced)")
        print("=" * 60)
        print("Enhanced secure storage and management of API keys for all AI providers")
        print()

def show_provider_info():
    """Show information about supported providers with Rich UI"""
    if RICH_AVAILABLE:
        console.print("[bold blue]🤖 SUPPORTED AI PROVIDERS[/bold blue]\n")
        
        # Create a beautiful table
        table = Table(
            title="AI Provider Information",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center", style="bold")
        table.add_column("Description", style="white")
        table.add_column("Get API Key", style="dim blue")
        table.add_column("Env Variable", style="dim yellow")
        
        providers = {
            'Groq': {
                'description': 'Ultra-fast LLM inference (Lightning speed)',
                'url': 'console.groq.com/keys',
                'key_name': 'GROQ_API_KEY',
                'required': True
            },
            'OpenAI': {
                'description': 'GPT models (GPT-4, GPT-3.5-turbo)',
                'url': 'platform.openai.com/api-keys',
                'key_name': 'OPENAI_API_KEY',
                'required': False
            },
            'Anthropic': {
                'description': 'Claude models (Claude-3, Claude-2)',
                'url': 'console.anthropic.com',
                'key_name': 'ANTHROPIC_API_KEY',
                'required': False
            },
            'Google': {
                'description': 'Gemini models (Gemini Pro, Flash)',
                'url': 'makersuite.google.com/app/apikey',
                'key_name': 'GOOGLE_API_KEY',
                'required': False
            }
        }
        
        for name, info in providers.items():
            status = "[bold red]🔴 REQUIRED[/bold red]" if info['required'] else "[bold yellow]🟡 OPTIONAL[/bold yellow]"
            table.add_row(
                f"[bold]{name}[/bold]",
                status,
                info['description'],
                info['url'],
                info['key_name']
            )
        
        console.print(table)
        console.print()
        
        # Add helpful tips
        tips_panel = Panel(
            "[bold yellow]💡 SETUP TIPS[/bold yellow]\n\n"
            "• [green]Groq[/green] is required for fastest performance\n"
            "• [blue]All keys are encrypted[/blue] and stored locally\n"
            "• [cyan]Use 'manage' command[/cyan] for interactive setup\n"
            "• [magenta]Keys can be tested[/magenta] after setup\n"
            "• [yellow]Rich UI provides enhanced experience[/yellow]",
            title="[bold green]🚀 Quick Tips[/bold green]",
            border_style="green"
        )
        console.print(tips_panel)
        
    else:
        # Fallback implementation
        providers = {
            'Groq': {
                'description': 'Ultra-fast LLM inference (Required for best performance)',
                'url': 'https://console.groq.com/keys',
                'key_name': 'GROQ_API_KEY',
                'required': True
            },
            'OpenAI': {
                'description': 'GPT models (GPT-4, GPT-3.5-turbo)',
                'url': 'https://platform.openai.com/api-keys',
                'key_name': 'OPENAI_API_KEY',
                'required': False
            },
            'Anthropic': {
                'description': 'Claude models (Claude-3, Claude-2)',
                'url': 'https://console.anthropic.com/',
                'key_name': 'ANTHROPIC_API_KEY',
                'required': False
            },
            'Google': {
                'description': 'Gemini models (Gemini Pro, Gemini Flash)',
                'url': 'https://makersuite.google.com/app/apikey',
                'key_name': 'GOOGLE_API_KEY',
                'required': False
            }
        }
        
        print("🤖 SUPPORTED AI PROVIDERS:")
        print()
        
        for name, info in providers.items():
            status = "🔴 REQUIRED" if info['required'] else "🟡 OPTIONAL"
            print(f"📍 {name} ({status})")
            print(f"   📝 {info['description']}")
            print(f"   🔗 Get API key: {info['url']}")
            print(f"   🔑 Environment variable: {info['key_name']}")
            print()

def check_current_keys():
    """Check and display current API key status with Rich UI"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return
    
    if RICH_AVAILABLE:
        console.print("[bold blue]📊 CURRENT API KEY STATUS[/bold blue]\n")
        
        try:
            stored_keys = api_key_manager.list_stored_keys()
            
            # Create status table
            table = Table(
                title="API Key Configuration Status",
                show_header=True,
                header_style="bold cyan",
                border_style="blue"
            )
            table.add_column("Provider", style="bold white", no_wrap=True)
            table.add_column("Status", justify="center", style="bold")
            table.add_column("Source", justify="center", style="dim")
            table.add_column("Required", justify="center")
            
            provider_names = {
                'GROQ_API_KEY': ('Groq', True),
                'OPENAI_API_KEY': ('OpenAI', False),
                'ANTHROPIC_API_KEY': ('Anthropic', False),
                'GOOGLE_API_KEY': ('Google', False)
            }
            
            for key_name, (display_name, required) in provider_names.items():
                stored_status = stored_keys.get(key_name, False)
                env_status = bool(os.getenv(key_name))
                
                if stored_status:
                    status = "[bold green]✅ Configured[/bold green]"
                    source = "[blue]Encrypted Storage[/blue]"
                elif env_status:
                    status = "[bold yellow]✅ Available[/bold yellow]"
                    source = "[dim yellow]Environment[/dim yellow]"
                else:
                    status = "[bold red]❌ Missing[/bold red]"
                    source = "[dim red]Not Set[/dim red]"
                
                req_status = "[bold red]🔴 Required[/bold red]" if required else "[dim yellow]🟡 Optional[/dim yellow]"
                
                table.add_row(display_name, status, source, req_status)
            
            console.print(table)
            
            # Show summary
            configured_count = sum(1 for v in stored_keys.values() if v)
            env_count = sum(1 for key in provider_names.keys() if os.getenv(key))
            
            summary_text = Text()
            summary_text.append(f"📋 Summary: ", style="bold")
            summary_text.append(f"{configured_count} stored, ", style="green")
            summary_text.append(f"{env_count} in environment", style="yellow")
            
            console.print(f"\n{summary_text}")
            
            # Show storage location
            config_dir = Path.home() / ".ai_helper_agent"
            console.print(f"[dim]💾 Storage: {config_dir}[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Error checking keys: {e}[/red]")
    else:
        # Fallback implementation
        print("📊 CURRENT API KEY STATUS:")
        print()
        
        try:
            stored_keys = api_key_manager.list_stored_keys()
            
            provider_names = {
                'GROQ_API_KEY': 'Groq (Required)',
                'OPENAI_API_KEY': 'OpenAI',
                'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
                'GOOGLE_API_KEY': 'Google (Gemini)'
            }
            
            for key_name, display_name in provider_names.items():
                status = stored_keys.get(key_name, False)
                icon = "✅" if status else "❌"
                status_text = "Stored securely" if status else "Not configured"
                print(f"  {icon} {display_name}: {status_text}")
            
            print()
            
            # Check environment variables as fallback
            env_keys_found = []
            for key_name in provider_names.keys():
                if os.getenv(key_name):
                    env_keys_found.append(key_name)
            
            if env_keys_found:
                print("🌍 ENVIRONMENT VARIABLES DETECTED:")
                for key in env_keys_found:
                    print(f"  ✅ {key}: Available in environment")
                print("  ℹ️  Environment variables will be used as fallback")
                print()
            
        except Exception as e:
            print(f"❌ Error checking keys: {e}")

def interactive_setup():
    """Run interactive API key setup"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available. Please check installation.[/red]")
        else:
            print("❌ API key manager not available. Please check installation.")
        return False
    
    if RICH_AVAILABLE:
        console.print("[bold green]🔧 INTERACTIVE API KEY SETUP[/bold green]")
        setup_panel = Panel(
            "[white]This will guide you through setting up API keys securely.\n"
            "Keys will be encrypted and stored locally in your home directory.[/white]",
            title="[cyan]🛡️ Secure Setup Process[/cyan]",
            border_style="green"
        )
        console.print(setup_panel)
    else:
        print("🔧 INTERACTIVE API KEY SETUP")
        print("=" * 40)
        print("This will guide you through setting up API keys securely.")
        print("Keys will be encrypted and stored locally in your home directory.")
        print()
    
    try:
        api_key_manager.setup_interactive()
        return True
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]❌ Setup failed: {e}[/red]")
        else:
            print(f"❌ Setup failed: {e}")
        return False

def quick_add_key():
    """Quick add a single API key with Rich UI"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return False
    
    if RICH_AVAILABLE:
        console.print("[bold green]⚡ QUICK ADD API KEY[/bold green]\n")
        
        providers = {
            '1': ('groq', 'Groq'),
            '2': ('openai', 'OpenAI'),
            '3': ('anthropic', 'Anthropic (Claude)'),
            '4': ('google', 'Google (Gemini)')
        }
        
        # Create provider selection table
        table = Table(title="Select Provider", border_style="green")
        table.add_column("Option", style="bold green", no_wrap=True)
        table.add_column("Provider", style="bold white")
        
        for num, (key, name) in providers.items():
            table.add_row(num, name)
        
        console.print(table)
        
        choice = Prompt.ask("\n[bold yellow]Enter choice[/bold yellow]", choices=["1", "2", "3", "4"])
        
        if choice in providers:
            provider_key, provider_name = providers[choice]
            
            console.print(f"\n[bold cyan]🔑 Adding API key for {provider_name}[/bold cyan]")
            
            import getpass
            api_key = getpass.getpass(f"Enter {provider_name} API key: ").strip()
            
            if not api_key:
                console.print("[red]❌ No API key provided[/red]")
                return False
            
            try:
                if api_key_manager.set_api_key(provider_key, api_key):
                    console.print(f"[green]✅ {provider_name} API key saved securely[/green]")
                    return True
                else:
                    console.print(f"[red]❌ Failed to save {provider_name} API key[/red]")
                    return False
            except Exception as e:
                console.print(f"[red]❌ Error saving key: {e}[/red]")
                return False
        else:
            console.print("[red]❌ Invalid choice[/red]")
            return False
    
    else:
        # Fallback implementation
        print("⚡ QUICK ADD API KEY")
        print("=" * 30)
        
        providers = {
            '1': ('groq', 'Groq'),
            '2': ('openai', 'OpenAI'),
            '3': ('anthropic', 'Anthropic (Claude)'),
            '4': ('google', 'Google (Gemini)')
        }
        
        print("Select provider:")
        for num, (key, name) in providers.items():
            print(f"  {num}. {name}")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice not in providers:
            print("❌ Invalid choice")
            return False
        
        provider_key, provider_name = providers[choice]
        
        print(f"\n🔑 Adding API key for {provider_name}")
        
        import getpass
        api_key = getpass.getpass(f"Enter {provider_name} API key: ").strip()
        
        if not api_key:
            print("❌ No API key provided")
            return False
        
        try:
            if api_key_manager.set_api_key(provider_key, api_key):
                print(f"✅ {provider_name} API key saved securely")
                return True
            else:
                print(f"❌ Failed to save {provider_name} API key")
                return False
        except Exception as e:
            print(f"❌ Error saving key: {e}")
            return False

def show_stored_keys():
    """Show all stored API keys with masked values"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return
    
    if RICH_AVAILABLE:
        console.print("[bold green]🔍 STORED API KEYS (MASKED)[/bold green]\n")
        
        try:
            stored_keys = api_key_manager.list_stored_keys()
            
            table = Table(
                title="Stored API Keys",
                show_header=True,
                header_style="bold cyan",
                border_style="green"
            )
            table.add_column("Provider", style="bold white", no_wrap=True)
            table.add_column("Status", justify="center", style="bold")
            table.add_column("Masked Key", style="dim yellow")
            
            provider_names = {
                'GROQ_API_KEY': 'Groq (Required)',
                'OPENAI_API_KEY': 'OpenAI',
                'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
                'GOOGLE_API_KEY': 'Google (Gemini)'
            }
            
            any_keys_found = False
            
            for key_name, display_name in provider_names.items():
                if stored_keys.get(key_name, False):
                    # Get the actual key to show masked version
                    actual_key = api_key_manager.get_api_key(key_name.replace('_API_KEY', '').lower())
                    if actual_key:
                        masked_key = mask_api_key(actual_key)
                        table.add_row(display_name, "[green]✅ Configured[/green]", masked_key)
                        any_keys_found = True
                    else:
                        table.add_row(display_name, "[red]❌ Error[/red]", "Error reading key")
                else:
                    table.add_row(display_name, "[red]❌ Missing[/red]", "Not configured")
            
            console.print(table)
            
            if not any_keys_found:
                console.print("\n[yellow]📭 No API keys are currently stored[/yellow]")
            
        except Exception as e:
            console.print(f"[red]❌ Error retrieving keys: {e}[/red]")
    
    else:
        # Fallback implementation
        print("🔍 STORED API KEYS (MASKED)")
        print("=" * 40)
        
        try:
            stored_keys = api_key_manager.list_stored_keys()
            
            provider_names = {
                'GROQ_API_KEY': 'Groq (Required)',
                'OPENAI_API_KEY': 'OpenAI',
                'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
                'GOOGLE_API_KEY': 'Google (Gemini)'
            }
            
            any_keys_found = False
            
            for key_name, display_name in provider_names.items():
                if stored_keys.get(key_name, False):
                    # Get the actual key to show masked version
                    actual_key = api_key_manager.get_api_key(key_name.replace('_API_KEY', '').lower())
                    if actual_key:
                        masked_key = mask_api_key(actual_key)
                        print(f"  ✅ {display_name}: {masked_key}")
                        any_keys_found = True
                    else:
                        print(f"  ❌ {display_name}: Error reading key")
                else:
                    print(f"  ❌ {display_name}: Not configured")
            
            if not any_keys_found:
                print("  📭 No API keys are currently stored")
            
            print()
            
        except Exception as e:
            print(f"❌ Error retrieving keys: {e}")

def show_full_keys():
    """Show all stored API keys with full values (with warning)"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return
    
    if RICH_AVAILABLE:
        console.print("[bold red]⚠️  SECURITY WARNING: FULL API KEY DISPLAY[/bold red]\n")
        
        warning_panel = Panel(
            "[bold red]🔒 This will display your API keys in plain text!\n"
            "🔒 Make sure no one else can see your screen![/bold red]",
            title="[red]⚠️ Security Warning[/red]",
            border_style="red"
        )
        console.print(warning_panel)
        
        # Security confirmation
        import getpass
        confirmation = getpass.getpass("🔐 Enter 'SHOW' to confirm (case sensitive): ")
        
        if confirmation != "SHOW":
            console.print("[yellow]❌ Confirmation failed. Keys not displayed.[/yellow]")
            return
        
        console.print("\n[bold yellow]🔓 FULL API KEYS:[/bold yellow]")
        
        try:
            provider_names = {
                'GROQ_API_KEY': 'Groq (Required)',
                'OPENAI_API_KEY': 'OpenAI', 
                'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
                'GOOGLE_API_KEY': 'Google (Gemini)'
            }
            
            any_keys_found = False
            
            for key_name, display_name in provider_names.items():
                provider_key = key_name.replace('_API_KEY', '').lower()
                actual_key = api_key_manager.get_api_key(provider_key)
                
                if actual_key:
                    console.print(f"[bold white]📋 {display_name}:[/bold white]")
                    console.print(f"   [yellow]{actual_key}[/yellow]")
                    console.print()
                    any_keys_found = True
            
            if not any_keys_found:
                console.print("[yellow]📭 No API keys are currently stored[/yellow]")
            
            console.print("[red]🔒 Remember to keep these keys secure![/red]")
            
        except Exception as e:
            console.print(f"[red]❌ Error retrieving keys: {e}[/red]")
    
    else:
        # Fallback implementation
        print("⚠️  SECURITY WARNING: FULL API KEY DISPLAY")
        print("=" * 50)
        print("🔒 This will display your API keys in plain text!")
        print("🔒 Make sure no one else can see your screen!")
        print()
        
        # Security confirmation
        import getpass
        confirmation = getpass.getpass("🔐 Enter 'SHOW' to confirm (case sensitive): ")
        
        if confirmation != "SHOW":
            print("❌ Confirmation failed. Keys not displayed.")
            return
        
        print("\n🔓 FULL API KEYS:")
        print("=" * 30)
        
        try:
            provider_names = {
                'GROQ_API_KEY': 'Groq (Required)',
                'OPENAI_API_KEY': 'OpenAI', 
                'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
                'GOOGLE_API_KEY': 'Google (Gemini)'
            }
            
            any_keys_found = False
            
            for key_name, display_name in provider_names.items():
                provider_key = key_name.replace('_API_KEY', '').lower()
                actual_key = api_key_manager.get_api_key(provider_key)
                
                if actual_key:
                    print(f"📋 {display_name}:")
                    print(f"   {actual_key}")
                    print()
                    any_keys_found = True
            
            if not any_keys_found:
                print("📭 No API keys are currently stored")
            
            print("🔒 Remember to keep these keys secure!")
            
        except Exception as e:
            print(f"❌ Error retrieving keys: {e}")

def edit_existing_key():
    """Edit an existing API key with Rich UI"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return False
    
    try:
        stored_keys = api_key_manager.list_stored_keys()
        available_keys = [(k, v) for k, v in stored_keys.items() if v]
        
        if not available_keys:
            if RICH_AVAILABLE:
                console.print("[yellow]📭 No API keys are currently stored to edit[/yellow]")
            else:
                print("📭 No API keys are currently stored to edit")
            return False
        
        if RICH_AVAILABLE:
            # Show available keys with masked values in a table
            table = Table(
                title="Available Keys to Edit",
                show_header=True,
                header_style="bold cyan",
                border_style="blue"
            )
            table.add_column("Option", style="bold green", no_wrap=True)
            table.add_column("Provider", style="bold white")
            table.add_column("Current Key (Masked)", style="dim yellow")
            
            for i, (key_name, _) in enumerate(available_keys, 1):
                provider = key_name.replace('_API_KEY', '').lower()
                actual_key = api_key_manager.get_api_key(provider)
                masked_key = mask_api_key(actual_key) if actual_key else "Error"
                display_name = key_name.replace('_API_KEY', '').title()
                table.add_row(str(i), display_name, masked_key)
            
            console.print(table)
            
            choice = Prompt.ask(
                f"\n[bold yellow]Select key to edit[/bold yellow]",
                choices=[str(i) for i in range(1, len(available_keys) + 1)]
            )
            
            idx = int(choice) - 1
            key_name, _ = available_keys[idx]
            provider = key_name.replace('_API_KEY', '').lower()
            display_name = provider.title()
            
            # Show current key (masked)
            current_key = api_key_manager.get_api_key(provider)
            if current_key:
                console.print(f"\n[bold white]📋 Current {display_name} key:[/bold white] [dim yellow]{mask_api_key(current_key)}[/dim yellow]")
            
            # Get new key
            import getpass
            new_key = getpass.getpass(f"🔑 Enter new {display_name} API key: ").strip()
            
            if not new_key:
                console.print("[red]❌ No new key provided[/red]")
                return False
            
            # Confirm the change
            console.print(f"\n[bold white]📋 New {display_name} key:[/bold white] [dim yellow]{mask_api_key(new_key)}[/dim yellow]")
            
            if Prompt.ask("[bold green]Save this new key?[/bold green]", choices=["y", "n"], default="n") == 'y':
                if api_key_manager.set_api_key(provider, new_key):
                    console.print(f"[green]✅ {display_name} API key updated successfully[/green]")
                    return True
                else:
                    console.print(f"[red]❌ Failed to update {display_name} API key[/red]")
                    return False
            else:
                console.print("[yellow]❌ Update cancelled[/yellow]")
                return False
        
        else:
            # Fallback implementation
            print("✏️  EDIT EXISTING API KEY")
            print("=" * 30)
            
            # Show available keys with masked values
            print("Available API keys to edit:")
            for i, (key_name, _) in enumerate(available_keys, 1):
                provider = key_name.replace('_API_KEY', '').lower()
                actual_key = api_key_manager.get_api_key(provider)
                masked_key = mask_api_key(actual_key) if actual_key else "Error"
                display_name = key_name.replace('_API_KEY', '').title()
                print(f"  {i}. {display_name}: {masked_key}")
            
            choice = input(f"\nSelect key to edit (1-{len(available_keys)}): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_keys):
                    key_name, _ = available_keys[idx]
                    provider = key_name.replace('_API_KEY', '').lower()
                    display_name = provider.title()
                    
                    # Show current key (masked)
                    current_key = api_key_manager.get_api_key(provider)
                    if current_key:
                        print(f"\n📋 Current {display_name} key: {mask_api_key(current_key)}")
                    
                    # Get new key
                    import getpass
                    new_key = getpass.getpass(f"🔑 Enter new {display_name} API key: ").strip()
                    
                    if not new_key:
                        print("❌ No new key provided")
                        return False
                    
                    # Confirm the change
                    print(f"\n📋 New {display_name} key: {mask_api_key(new_key)}")
                    confirm = input("✅ Save this new key? (y/N): ").strip().lower()
                    
                    if confirm == 'y':
                        if api_key_manager.set_api_key(provider, new_key):
                            print(f"✅ {display_name} API key updated successfully")
                            return True
                        else:
                            print(f"❌ Failed to update {display_name} API key")
                            return False
                    else:
                        print("❌ Update cancelled")
                        return False
                else:
                    print("❌ Invalid choice")
                    return False
            except ValueError:
                print("❌ Invalid input")
                return False
                
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]❌ Error editing key: {e}[/red]")
        else:
            print(f"❌ Error editing key: {e}")
        return False

def validate_api_key():
    """Test API keys to make sure they work with Rich UI"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return
    
    if RICH_AVAILABLE:
        console.print("[bold magenta]🧪 API KEY VALIDATION[/bold magenta]")
        console.print("[dim]Testing stored API keys to verify connectivity...[/dim]\n")
        
        # Create validation results table
        table = Table(
            title="API Key Validation Results",
            show_header=True,
            header_style="bold cyan",
            border_style="magenta"
        )
        table.add_column("Provider", style="bold white", no_wrap=True)
        table.add_column("Status", justify="center", style="bold")
        table.add_column("Test Result", justify="center")
        table.add_column("Response Time", justify="center", style="dim")
        
        providers = [
            ('groq', 'Groq', test_groq_key),
            ('openai', 'OpenAI', test_openai_key),
            ('anthropic', 'Anthropic', test_anthropic_key)
        ]
        
        with console.status("[bold blue]Running API validation tests...") as status:
            for provider_key, display_name, test_func in providers:
                api_key = api_key_manager.get_api_key(provider_key)
                
                if api_key:
                    status.update(f"[bold blue]Testing {display_name} API...")
                    
                    import time
                    start_time = time.time()
                    
                    try:
                        is_valid = test_func(api_key)
                        response_time = f"{(time.time() - start_time):.2f}s"
                        
                        if is_valid:
                            status_icon = "[bold green]✅ Configured[/bold green]"
                            result = "[bold green]✅ Valid[/bold green]"
                        else:
                            status_icon = "[bold red]❌ Configured[/bold red]"
                            result = "[bold red]❌ Failed[/bold red]"
                    except Exception as e:
                        response_time = "Error"
                        status_icon = "[bold red]❌ Configured[/bold red]"
                        result = f"[bold red]❌ Error[/bold red]"
                else:
                    status_icon = "[dim yellow]⚠️ Not Set[/dim yellow]"
                    result = "[dim]Not Tested[/dim]"
                    response_time = "N/A"
                
                table.add_row(display_name, status_icon, result, response_time)
        
        console.print(table)
        
        # Summary information
        configured_keys = sum(1 for provider_key, _, _ in providers if api_key_manager.get_api_key(provider_key))
        console.print(f"\n[bold]📊 Summary:[/bold] {configured_keys}/{len(providers)} API keys configured")
        
        if configured_keys == 0:
            console.print("[yellow]💡 Tip: Use 'add' command to configure API keys[/yellow]")
        elif configured_keys < len(providers):
            console.print("[blue]💡 Tip: Configure additional providers for more options[/blue]")
        else:
            console.print("[green]🎉 All supported API providers are configured![/green]")
    
    else:
        # Fallback implementation
        print("🧪 API KEY VALIDATION")
        print("=" * 25)
        print("Testing stored API keys to verify they work...")
        print()
        
        # Test Groq key
        groq_key = api_key_manager.get_api_key('groq')
        if groq_key:
            print("🧪 Testing Groq API key...")
            if test_groq_key(groq_key):
                print("  ✅ Groq API key is valid and working")
            else:
                print("  ❌ Groq API key test failed")
        else:
            print("  ⚠️  Groq API key not configured")
        
        # Test OpenAI key  
        openai_key = api_key_manager.get_api_key('openai')
        if openai_key:
            print("\n🧪 Testing OpenAI API key...")
            if test_openai_key(openai_key):
                print("  ✅ OpenAI API key is valid and working")
            else:
                print("  ❌ OpenAI API key test failed")
        else:
            print("\n  ⚠️  OpenAI API key not configured")
        
        # Test Anthropic key
        anthropic_key = api_key_manager.get_api_key('anthropic')
        if anthropic_key:
            print("\n🧪 Testing Anthropic API key...")
            if test_anthropic_key(anthropic_key):
                print("  ✅ Anthropic API key is valid and working")
            else:
                print("  ❌ Anthropic API key test failed")
        else:
            print("\n  ⚠️  Anthropic API key not configured")
        
        print("\n✅ API key validation complete")

def mask_api_key(api_key: str) -> str:
    """Mask an API key for display"""
    if not api_key:
        return "Not set"
    
    if len(api_key) <= 8:
        return "*" * len(api_key)
    
    # Show first 4 and last 4 characters
    return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

def test_groq_key(api_key: str) -> bool:
    """Test if Groq API key works"""
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Make a simple test request
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.1-8b-instant",
            max_tokens=5
        )
        return True
    except Exception:
        return False

def test_openai_key(api_key: str) -> bool:
    """Test if OpenAI API key works"""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Make a simple test request
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-3.5-turbo",
            max_tokens=5
        )
        return True
    except Exception:
        return False

def test_anthropic_key(api_key: str) -> bool:
    """Test if Anthropic API key works"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Make a simple test request
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=5,
            messages=[{"role": "user", "content": "Hello"}]
        )
        return True
    except Exception:
        return False

def manage_keys_menu():
    """Enhanced interactive key management menu with Rich UI"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return
    
    if RICH_AVAILABLE:
        while True:
            console.clear()
            
            # Create enhanced management menu
            menu_panel = Panel(
                Text.from_markup("""[bold cyan]🔧 API KEY MANAGEMENT MENU[/bold cyan]

[bold white]Key Display & Information:[/bold white]
[green]1.[/green] [white]👀 View Stored Keys (Masked)[/white]    [dim]- Safe key preview[/dim]
[green]2.[/green] [white]🔍 Show Full Keys[/white]               [dim]- Complete key values[/dim]
[green]7.[/green] [white]📊 Show Current Status[/white]           [dim]- Configuration overview[/dim]

[bold white]Key Management Operations:[/bold white]
[yellow]3.[/yellow] [white]✏️ Edit Existing Key[/white]            [dim]- Modify stored keys[/dim]
[yellow]4.[/yellow] [white]➕ Add New Key[/white]                 [dim]- Store additional keys[/dim]
[yellow]5.[/yellow] [white]🗑️ Remove Key[/white]                  [dim]- Delete stored keys[/dim]

[bold white]Testing & Validation:[/bold white]
[cyan]6.[/cyan] [white]🧪 Validate All Keys[/white]             [dim]- Test API connectivity[/dim]

[bold red]8.[/bold red] [white]🚪 Exit Management[/white]           [dim]- Return to main menu[/dim]"""),
                title="🚀 Interactive API Key Manager (Enhanced)",
                border_style="blue",
                padding=(1, 2)
            )
            
            console.print(menu_panel)
            
            # Get user choice with Rich prompt
            try:
                choice = Prompt.ask(
                    "\n[bold yellow]🔧 Select your option[/bold yellow]",
                    choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                    default="7"
                )
            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Management cancelled[/yellow]")
                break
            
            if choice == "1":
                console.print("\n[bold green]👀 MASKED KEY DISPLAY[/bold green]")
                show_stored_keys()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "2":
                console.print("\n[bold red]🔍 FULL KEY DISPLAY[/bold red]")
                console.print("[yellow]⚠️ Warning: This will show complete API keys[/yellow]")
                if Prompt.ask("\n[bold]Continue?[/bold]", choices=["y", "n"], default="n") == "y":
                    show_full_keys()
                else:
                    console.print("[green]✅ Cancelled for security[/green]")
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "3":
                console.print("\n[bold blue]✏️ EDIT EXISTING KEY[/bold blue]")
                edit_existing_key()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "4":
                console.print("\n[bold green]➕ ADD NEW KEY[/bold green]")
                quick_add_key()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "5":
                console.print("\n[bold red]🗑️ REMOVE KEY[/bold red]")
                remove_key()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "6":
                console.print("\n[bold magenta]🧪 VALIDATION RESULTS[/bold magenta]")
                validate_api_key()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "7":
                console.print("\n")
                check_current_keys()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "8":
                console.print("\n[green]👋 Exiting API key management[/green]")
                break
    
    else:
        # Fallback implementation without Rich
        while True:
            print("\n🔧 API KEY MANAGEMENT MENU (Enhanced)")
            print("=" * 40)
            print("1. 👀 View stored keys (masked)")
            print("2. 🔍 Show full keys (security warning)")
            print("3. ✏️  Edit existing key")
            print("4. ➕ Add new key")
            print("5. 🗑️  Remove key") 
            print("6. 🧪 Validate keys")
            print("7. 📊 Show status")
            print("8. 🚪 Exit")
            
            choice = input("\n🔧 Select option (1-8): ").strip()
            
            if choice == "1":
                show_stored_keys()
            elif choice == "2":
                show_full_keys()
            elif choice == "3":
                edit_existing_key()
            elif choice == "4":
                quick_add_key()
            elif choice == "5":
                remove_key()
            elif choice == "6":
                validate_api_key()
            elif choice == "7":
                check_current_keys()
            elif choice == "8":
                print("👋 Exiting API key management")
                break
            else:
                print("❌ Invalid choice. Please select 1-8.")

def remove_key():
    """Remove an API key with Rich UI"""
    if not MANAGER_AVAILABLE:
        if RICH_AVAILABLE:
            console.print("[red]❌ API key manager not available[/red]")
        else:
            print("❌ API key manager not available")
        return False
    
    try:
        stored_keys = api_key_manager.list_stored_keys()
        available_keys = [k for k, v in stored_keys.items() if v]
        
        if not available_keys:
            if RICH_AVAILABLE:
                console.print("[yellow]📭 No API keys are currently stored[/yellow]")
            else:
                print("📭 No API keys are currently stored")
            return False
        
        if RICH_AVAILABLE:
            # Show available keys in a table
            table = Table(
                title="Keys Available for Removal",
                show_header=True,
                header_style="bold cyan",
                border_style="red"
            )
            table.add_column("Option", style="bold red", no_wrap=True)
            table.add_column("Provider", style="bold white")
            table.add_column("Key Type", style="dim")
            
            for i, key in enumerate(available_keys, 1):
                provider = key.replace('_API_KEY', '').lower()
                display_name = key.replace('_API_KEY', '').title()
                table.add_row(str(i), display_name, provider)
            
            console.print(table)
            
            choice = Prompt.ask(
                f"\n[bold yellow]Select key to remove[/bold yellow]",
                choices=[str(i) for i in range(1, len(available_keys) + 1)]
            )
            
            idx = int(choice) - 1
            key_to_remove = available_keys[idx]
            provider = key_to_remove.replace('_API_KEY', '').lower()
            display_name = provider.title()
            
            console.print(f"\n[bold red]⚠️  WARNING: You are about to remove {display_name} API key[/bold red]")
            
            if Prompt.ask(f"[bold red]Really remove {key_to_remove}?[/bold red]", choices=["y", "n"], default="n") == 'y':
                if api_key_manager.remove_api_key(provider):
                    console.print(f"[green]✅ {key_to_remove} removed successfully[/green]")
                    return True
                else:
                    console.print(f"[red]❌ Failed to remove {key_to_remove}[/red]")
                    return False
            else:
                console.print("[yellow]❌ Removal cancelled[/yellow]")
                return False
        
        else:
            # Fallback implementation
            print("🗑️  REMOVE API KEY")
            print("=" * 20)
            
            print("Stored API keys:")
            for i, key in enumerate(available_keys, 1):
                provider = key.replace('_API_KEY', '').lower()
                print(f"  {i}. {key} ({provider})")
            
            choice = input(f"\nSelect key to remove (1-{len(available_keys)}): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_keys):
                    key_to_remove = available_keys[idx]
                    provider = key_to_remove.replace('_API_KEY', '').lower()
                    
                    confirm = input(f"⚠️  Really remove {key_to_remove}? (y/N): ").strip().lower()
                    if confirm == 'y':
                        if api_key_manager.remove_api_key(provider):
                            print(f"✅ {key_to_remove} removed successfully")
                            return True
                        else:
                            print(f"❌ Failed to remove {key_to_remove}")
                            return False
                    else:
                        print("❌ Cancelled")
                        return False
                else:
                    print("❌ Invalid choice")
                    return False
            except ValueError:
                print("❌ Invalid input")
                return False
                
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[red]❌ Error: {e}[/red]")
        else:
            print(f"❌ Error: {e}")
        return False

def show_help():
    """Show comprehensive help information with Rich UI"""
    if RICH_AVAILABLE:
        console.print("[bold yellow]🆘 HELP - Enhanced API Key Management System[/bold yellow]\n")
        
        # Usage section
        usage_panel = Panel(
            Text.from_markup("""[bold white]python -m ai_helper_agent.utilities.api_key_setup [command][/bold white]
[bold white]python api_key_setup.py [command][/bold white] [dim](if in root directory)[/dim]

[dim]Run without arguments to see current status[/dim]"""),
            title="💻 Usage",
            border_style="green"
        )
        console.print(usage_panel)
        
        # Commands table
        commands_table = Table(
            title="📋 Available Commands",
            show_header=True,
            header_style="bold cyan",
            border_style="blue"
        )
        commands_table.add_column("Command", style="bold green", no_wrap=True)
        commands_table.add_column("Description", style="white")
        commands_table.add_column("Use Case", style="dim")
        
        commands = [
            ("setup", "Interactive setup of all API keys", "First-time configuration"),
            ("status", "Show current API key status", "Quick overview"),
            ("add", "Quick add a single API key", "Add one key fast"),
            ("remove", "Remove an API key", "Delete unwanted keys"),
            ("edit", "Edit an existing API key", "Update key values"),
            ("show", "Show stored keys (masked)", "Safe key preview"),
            ("full", "Show full keys (security warning)", "Complete key values"),
            ("validate", "Test API keys to verify they work", "Connectivity testing"),
            ("manage", "Interactive management menu", "Full feature access"),
            ("info", "Show provider information", "Learn about APIs"),
            ("help", "Show this help message", "Get assistance")
        ]
        
        for cmd, desc, use_case in commands:
            commands_table.add_row(cmd, desc, use_case)
        
        console.print(commands_table)
        
        # Examples section
        examples_panel = Panel(
            Text.from_markup("""[green]python -m ai_helper_agent.utilities.api_key_setup setup[/green]     [dim]# Full interactive setup[/dim]
[green]python -m ai_helper_agent.utilities.api_key_setup status[/green]    [dim]# Check which keys are stored[/dim]
[green]python -m ai_helper_agent.utilities.api_key_setup add[/green]       [dim]# Add a single key quickly[/dim]
[green]python -m ai_helper_agent.utilities.api_key_setup show[/green]      [dim]# View stored keys (masked)[/dim]
[green]python -m ai_helper_agent.utilities.api_key_setup edit[/green]      [dim]# Edit an existing key[/dim]
[green]python -m ai_helper_agent.utilities.api_key_setup manage[/green]    [dim]# Full management interface[/dim]
[green]python -m ai_helper_agent.utilities.api_key_setup validate[/green]  [dim]# Test all configured keys[/dim]"""),
            title="💡 Examples",
            border_style="yellow"
        )
        console.print(examples_panel)
        
        # Security & Files info
        security_panel = Panel(
            Text.from_markup(f"""[bold white]Storage Location:[/bold white]
[cyan]{Path.home() / '.ai_helper_agent'}[/cyan]

[bold white]Enhanced Security Features:[/bold white]
[green]✅[/green] Keys stored with AES encryption
[green]✅[/green] Password-protected key storage
[green]✅[/green] Secure key masking in displays
[green]✅[/green] Environment variable fallback support
[green]✅[/green] Rich UI for better user experience
[green]✅[/green] Organized in utilities directory

[bold white]Supported Providers:[/bold white]
[yellow]🔴[/yellow] Groq (Required for basic functionality)
[blue]🟡[/blue] OpenAI (Optional, GPT models)
[purple]🟡[/purple] Anthropic (Optional, Claude models)
[red]🟡[/red] Google (Optional, Gemini models)"""),
            title="🔒 Security & Configuration",
            border_style="red"
        )
        console.print(security_panel)
        
        # Quick tips
        console.print("""[dim]
💡 [bold]Enhanced Features:[/bold]
• [green]Rich UI[/green] provides beautiful, interactive interface
• [blue]Better organization[/blue] in utilities directory
• [yellow]Improved security[/yellow] with enhanced masking
• [cyan]Interactive prompts[/cyan] for safer operations
• [magenta]Real-time validation[/magenta] with progress indicators
• [red]Environment variables[/red] work as fallback[/dim]""")
    
    else:
        # Fallback implementation
        print("🆘 HELP - Enhanced API Key Management")
        print("=" * 40)
        print()
        print("USAGE:")
        print("  python -m ai_helper_agent.utilities.api_key_setup [command]")
        print("  python api_key_setup.py [command]  (if in root directory)")
        print()
        print("COMMANDS:")
        print("  setup     - Interactive setup of all API keys")
        print("  status    - Show current API key status")
        print("  add       - Quick add a single API key")
        print("  remove    - Remove an API key")
        print("  edit      - Edit an existing API key")
        print("  show      - Show stored keys (masked)")
        print("  full      - Show full keys (security warning)")
        print("  validate  - Test API keys to verify they work")
        print("  manage    - Interactive management menu")
        print("  info      - Show provider information")
        print("  help      - Show this help message")
        print()
        print("EXAMPLES:")
        print("  python -m ai_helper_agent.utilities.api_key_setup setup     # Full interactive setup")
        print("  python -m ai_helper_agent.utilities.api_key_setup status    # Check which keys are stored")
        print("  python -m ai_helper_agent.utilities.api_key_setup add       # Add a single key quickly")
        print("  python -m ai_helper_agent.utilities.api_key_setup show      # View stored keys (masked)")
        print("  python -m ai_helper_agent.utilities.api_key_setup edit      # Edit an existing key")
        print("  python -m ai_helper_agent.utilities.api_key_setup manage    # Full management interface")
        print()
        print("ENHANCED FEATURES:")
        print("  • Rich UI for better user experience")
        print("  • Better organization in utilities directory")
        print("  • Enhanced security with improved masking")
        print("  • Interactive prompts for safer operations")
        print()
        print("FILES:")
        print(f"  Config directory: {Path.home() / '.ai_helper_agent'}")
        print("  Keys are stored encrypted with a password you set")

def main():
    """Enhanced main CLI interface"""
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    show_banner()
    
    if command == "setup":
        show_provider_info()
        interactive_setup()
    elif command == "status":
        check_current_keys()
    elif command == "add":
        quick_add_key()
    elif command == "remove":
        remove_key()
    elif command == "edit":
        edit_existing_key()
    elif command == "show":
        show_stored_keys()
    elif command == "full":
        show_full_keys()
    elif command == "validate":
        validate_api_key()
    elif command == "manage":
        manage_keys_menu()
    elif command == "info":
        show_provider_info()
    elif command == "help":
        show_help()
    else:
        if RICH_AVAILABLE:
            console.print(f"[red]❌ Unknown command: {command}[/red]")
            console.print("[yellow]💡 Use 'help' for available commands[/yellow]")
            console.print("[yellow]💡 Use 'manage' for interactive menu[/yellow]")
        else:
            print(f"❌ Unknown command: {command}")
            print("💡 Use 'help' for available commands")
            print("💡 Use 'manage' for interactive menu")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n[yellow]👋 Cancelled by user[/yellow]")
        else:
            print("\n👋 Cancelled by user")
        sys.exit(0)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        else:
            print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
