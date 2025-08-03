"""
AI Helper Agent - API Key Setup Helper
Provides user-friendly API key setup integration for CLI tools
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

def prompt_api_key_setup(provider: str, required: bool = True) -> bool:
    """
    Prompt user to set up API key when missing
    Returns True if key was set up successfully, False otherwise
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.prompt import Confirm
        console = Console()
        
        # Provider information
        provider_info = {
            'groq': {
                'name': 'Groq',
                'description': 'Ultra-fast LLM inference with Llama models',
                'url': 'https://console.groq.com/keys',
                'required': True
            },
            'openai': {
                'name': 'OpenAI',
                'description': 'GPT models (GPT-4, GPT-3.5-turbo)',
                'url': 'https://platform.openai.com/api-keys',
                'required': False
            },
            'anthropic': {
                'name': 'Anthropic',
                'description': 'Claude models (Claude-3, Claude-2)',
                'url': 'https://console.anthropic.com/',
                'required': False
            },
            'google': {
                'name': 'Google',
                'description': 'Gemini models (Gemini Pro, Flash)',
                'url': 'https://makersuite.google.com/app/apikey',
                'required': False
            }
        }
        
        info = provider_info.get(provider.lower(), {
            'name': provider.title(),
            'description': f'{provider.title()} AI models',
            'url': f'https://{provider.lower()}.com',
            'required': required
        })
        
        # Create warning panel
        urgency = "🔴 REQUIRED" if info['required'] else "🟡 OPTIONAL"
        panel_content = f"""[bold red]API Key Missing: {info['name']} ({urgency})[/bold red]

[white]📝 Description:[/white] {info['description']}
[white]🔗 Get your API key:[/white] {info['url']}

[yellow]⚡ Quick Setup Options:[/yellow]
[white]1.[/white] Run the API key setup tool: [cyan]python api_key_setup.py add[/cyan]
[white]2.[/white] Set environment variable: [cyan]export {provider.upper()}_API_KEY='your-key-here'[/cyan]
[white]3.[/white] Continue without this provider (if optional)"""
        
        console.print(Panel(panel_content, title="[bold yellow]🔑 API Key Setup Required[/bold yellow]", border_style="yellow"))
        
        if info['required']:
            # Required key - must set up
            console.print("\n[bold red]This API key is required to continue.[/bold red]")
            
            setup_now = Confirm.ask("🔧 Would you like to set up the API key now?", default=True)
            
            if setup_now:
                return run_api_key_setup_tool(provider)
            else:
                console.print("[red]❌ Cannot continue without required API key.[/red]")
                return False
        else:
            # Optional key - can skip
            console.print(f"\n[yellow]This API key is optional. You can continue without {info['name']} support.[/yellow]")
            
            setup_now = Confirm.ask("🔧 Would you like to set up the API key now?", default=False)
            
            if setup_now:
                return run_api_key_setup_tool(provider)
            else:
                console.print(f"[dim]⏭️ Skipping {info['name']} setup. You can add it later with:[/dim]")
                console.print(f"[dim]   python api_key_setup.py add[/dim]")
                return True  # Continue without this optional key
    
    except ImportError:
        # Fallback for non-Rich environments
        return prompt_api_key_setup_simple(provider, required)

def prompt_api_key_setup_simple(provider: str, required: bool = True) -> bool:
    """Simple text-based API key setup prompt"""
    
    provider_info = {
        'groq': ('Groq', 'https://console.groq.com/keys'),
        'openai': ('OpenAI', 'https://platform.openai.com/api-keys'),
        'anthropic': ('Anthropic', 'https://console.anthropic.com/'),
        'google': ('Google', 'https://makersuite.google.com/app/apikey')
    }
    
    name, url = provider_info.get(provider.lower(), (provider.title(), f'https://{provider.lower()}.com'))
    urgency = "REQUIRED" if required else "OPTIONAL"
    
    print("\n" + "=" * 60)
    print(f"🔑 API KEY MISSING: {name} ({urgency})")
    print("=" * 60)
    print(f"📝 Get your API key from: {url}")
    print(f"⚡ Quick setup: python api_key_setup.py add")
    print(f"🌍 Or set environment: export {provider.upper()}_API_KEY='your-key'")
    
    if required:
        print("\n🔴 This API key is REQUIRED to continue.")
        response = input("🔧 Set up API key now? (y/N): ").strip().lower()
        
        if response == 'y':
            return run_api_key_setup_tool(provider)
        else:
            print("❌ Cannot continue without required API key.")
            return False
    else:
        print(f"\n🟡 This API key is OPTIONAL. You can continue without {name}.")
        response = input("🔧 Set up API key now? (y/N): ").strip().lower()
        
        if response == 'y':
            return run_api_key_setup_tool(provider)
        else:
            print(f"⏭️ Skipping {name} setup.")
            return True

def run_api_key_setup_tool(provider: str) -> bool:
    """Run the API key setup tool for a specific provider"""
    try:
        # Get the path to the API key setup script
        setup_script = Path(__file__).parent.parent / "api_key_setup.py"
        
        if not setup_script.exists():
            print(f"❌ API key setup tool not found: {setup_script}")
            return False
        
        # Run the setup tool
        print(f"🔧 Launching API key setup for {provider}...")
        
        result = subprocess.run([
            sys.executable, str(setup_script), "add"
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run API key setup tool: {e}")
        return False

def check_and_prompt_missing_keys() -> bool:
    """
    Check for missing required keys and prompt setup
    Returns True if all required keys are available, False otherwise
    """
    try:
        from ai_helper_agent.managers.api_key_manager import api_key_manager
        
        # Check for Groq key (required)
        groq_key = api_key_manager.get_api_key('groq')
        if not groq_key:
            if not prompt_api_key_setup('groq', required=True):
                return False
        
        return True
        
    except ImportError:
        print("⚠️ API key manager not available")
        return True  # Continue anyway

def show_api_key_status():
    """Show current API key status in a user-friendly way"""
    try:
        from rich.console import Console
        from rich.table import Table
        console = Console()
        
        from ai_helper_agent.managers.api_key_manager import api_key_manager
        stored_keys = api_key_manager.list_stored_keys()
        
        table = Table(title="🔑 API Key Status", show_header=True, header_style="bold blue")
        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Required", justify="center")
        table.add_column("Description", style="dim")
        
        providers = [
            ("GROQ_API_KEY", "Groq", True, "Ultra-fast LLM inference"),
            ("OPENAI_API_KEY", "OpenAI", False, "GPT models"),
            ("ANTHROPIC_API_KEY", "Anthropic", False, "Claude models"),
            ("GOOGLE_API_KEY", "Google", False, "Gemini models")
        ]
        
        for key_name, name, required, desc in providers:
            status = stored_keys.get(key_name, False)
            status_icon = "✅ Configured" if status else "❌ Missing"
            required_icon = "🔴 Yes" if required else "🟡 No"
            
            table.add_row(name, status_icon, required_icon, desc)
        
        console.print(table)
        console.print("\n💡 [dim]Use 'python api_key_setup.py' to manage API keys[/dim]")
        
    except ImportError:
        # Simple fallback
        print("🔑 API Key Status:")
        print("  Run 'python api_key_setup.py status' for detailed status")

if __name__ == "__main__":
    # Test the helper functions
    show_api_key_status()
