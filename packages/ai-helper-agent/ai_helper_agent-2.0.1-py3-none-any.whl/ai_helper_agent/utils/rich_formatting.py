"""
Rich Formatting Utilities
Reusable Rich markdown and streaming functionality for all CLI tools
"""

import re
import time
import warnings
from typing import Optional, Iterator, Any

# Filter out warnings to keep CLI clean
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
warnings.filterwarnings("ignore", message=".*avconv.*")
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*")
warnings.filterwarnings("ignore", module="pydub")

# Rich imports for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel  
    from rich.table import Table
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.live import Live
    from rich.syntax import Syntax
    from rich.console import Group
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class RichFormattingManager:
    """Manages Rich console formatting and streaming for CLI applications"""
    
    def __init__(self):
        self.console = console if RICH_AVAILABLE else None
    
    def is_available(self) -> bool:
        """Check if Rich is available"""
        return RICH_AVAILABLE
    
    def stream_with_rich_formatting(self, text_chunks: Iterator[str], provider_name: str = "AI") -> str:
        """Stream text with REAL-TIME Rich markdown formatting using Live Display"""
        if not RICH_AVAILABLE:
            # Fallback for non-Rich environments
            print(f"\n🤖 {provider_name}:")
            full_response = ""
            for chunk in text_chunks:
                if chunk and isinstance(chunk, str):
                    print(chunk, end="", flush=True)
                    full_response += chunk
            print()  # Final newline
            return full_response
        
        # Initialize for real-time streaming
        console.print(f"\n[bold blue]🤖 {provider_name}:[/bold blue]")
        console.print("[bold cyan]══════ Live Streaming View ══════[/bold cyan]")
        
        accumulated_text = ""
        
        # Use Rich Live Display for real-time updates
        with Live(console=console, refresh_per_second=8, transient=False) as live:
            for chunk in text_chunks:
                if chunk and isinstance(chunk, str):
                    accumulated_text += chunk
                    
                    # Real-time rendering with enhanced markdown processing
                    try:
                        # Always use manual formatting for better control during streaming
                        renderable = self._create_enhanced_streaming_renderable(accumulated_text)
                        live.update(renderable)
                        
                        # Small delay for smooth streaming effect
                        time.sleep(0.05)
                        
                    except Exception as e:
                        # Fallback to plain text if formatting fails
                        live.update(Text(accumulated_text))
        
        # Show final enhanced view after streaming completes
        console.print("[bold cyan]═══════════════════════════[/bold cyan]")
        console.print("[dim]✅ Streaming complete[/dim]")
        
        return accumulated_text
    
    def display_enhanced_rich_markdown(self, text: str):
        """Display text with robust Rich markdown formatting"""
        if not RICH_AVAILABLE:
            print(text)
            return
            
        try:
            console.print("\n[bold cyan]══════ Enhanced View ══════[/bold cyan]")
            
            # Preprocess the text for better markdown handling
            processed_text = self._preprocess_markdown_text(text)
            
            # Create Rich Markdown with optimal settings
            markdown_obj = Markdown(
                processed_text,
                code_theme="github-dark",
                inline_code_theme="github-dark",
                hyperlinks=True,
                justify="left"
            )
            
            console.print(markdown_obj)
            console.print("[bold cyan]═══════════════════════════[/bold cyan]")
            
        except Exception as e:
            # Robust fallback formatting
            console.print(f"[yellow]⚠️ Rich Markdown failed: {e}[/yellow]")
            self._display_manual_formatted_text(text)
    
    def _create_enhanced_streaming_renderable(self, text: str):
        """Create enhanced Rich renderable with proper code block and markdown handling for streaming"""
        if not RICH_AVAILABLE:
            return text
            
        renderables = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Handle code blocks
            if line.startswith('```'):
                # Start of code block
                language = line[3:].strip() or "text"
                code_lines = []
                i += 1
                
                # Collect code lines until we find closing ``` or end of text
                while i < len(lines):
                    if lines[i].rstrip().startswith('```'):
                        # End of code block found
                        i += 1
                        break
                    code_lines.append(lines[i])
                    i += 1
                
                # Create syntax-highlighted code block
                if code_lines:
                    code_content = '\n'.join(code_lines)
                    try:
                        # Map language names
                        lang_map = {
                            'python': 'python',
                            'javascript': 'javascript', 
                            'js': 'javascript',
                            'bash': 'bash',
                            'shell': 'bash',
                            'sh': 'bash'
                        }
                        mapped_lang = lang_map.get(language.lower(), language.lower())
                        
                        syntax = Syntax(
                            code_content, 
                            mapped_lang,
                            theme="github-dark",
                            line_numbers=False,
                            word_wrap=True,
                            background_color="default"
                        )
                        renderables.append(syntax)
                    except:
                        # Fallback to colored text
                        code_text = Text()
                        for code_line in code_lines:
                            if language.lower() in ['python', 'py']:
                                code_text.append(code_line + '\n', style="green")
                            elif language.lower() in ['javascript', 'js']:
                                code_text.append(code_line + '\n', style="yellow")
                            elif language.lower() in ['bash', 'shell', 'sh']:
                                code_text.append(code_line + '\n', style="cyan")
                            else:
                                code_text.append(code_line + '\n', style="white")
                        renderables.append(code_text)
                continue
            
            # Handle regular text with inline formatting
            formatted_text = self._format_streaming_line(line)
            if formatted_text.plain:  # Only add non-empty lines
                renderables.append(formatted_text)
            else:
                # Add empty line
                renderables.append(Text(""))
            
            i += 1
        
        return Group(*renderables) if renderables else Text(text)
    
    def _format_streaming_line(self, line: str) -> Text:
        """Format a single line with inline markdown during streaming"""
        if not RICH_AVAILABLE:
            return line
            
        formatted_text = Text()
        
        # Handle headers first
        if line.strip().startswith('### '):
            formatted_text.append(line[4:], style="bold blue")
            return formatted_text
        elif line.strip().startswith('## '):
            formatted_text.append(line[3:], style="bold yellow")  
            return formatted_text
        elif line.strip().startswith('# '):
            formatted_text.append(line[2:], style="bold green")
            return formatted_text
        
        # Handle bullet points
        if re.match(r'^(\s*)[-*+]\s+', line):
            indent = re.match(r'^(\s*)', line).group(1)
            content = re.sub(r'^(\s*)[-*+]\s+', '', line)
            formatted_text.append(indent + "• ", style="bright_blue")
            # Process the rest of the line for inline formatting
            self._apply_inline_formatting(formatted_text, content)
            return formatted_text
        
        # Handle numbered lists
        if re.match(r'^(\s*)\d+\.\s+', line):
            match = re.match(r'^(\s*)(\d+\.\s+)(.*)', line)
            if match:
                indent, number, content = match.groups()
                formatted_text.append(indent, style="white")
                formatted_text.append(number, style="bright_blue bold")
                self._apply_inline_formatting(formatted_text, content)
                return formatted_text
        
        # Regular text with inline formatting
        self._apply_inline_formatting(formatted_text, line)
        return formatted_text
    
    def _apply_inline_formatting(self, text_obj: Text, content: str):
        """Apply inline formatting (bold, italic, code) to text content"""
        
        if not content:
            return
        
        current_pos = 0
        
        # Find all formatting markers
        markers = []
        
        # Bold text
        for match in re.finditer(r'\*\*([^*\n]+?)\*\*', content):
            markers.append((match.start(), match.end(), 'bold', match.group(1)))
        
        # Italic text (avoid conflicts with bold)
        for match in re.finditer(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', content):
            # Check if this overlaps with bold markers
            overlaps = any(match.start() >= m[0] and match.end() <= m[1] for m in markers if m[2] == 'bold')
            if not overlaps:
                markers.append((match.start(), match.end(), 'italic', match.group(1)))
        
        # Inline code
        for match in re.finditer(r'`([^`]+)`', content):
            markers.append((match.start(), match.end(), 'code', match.group(1)))
        
        # Sort markers by position
        markers.sort(key=lambda x: x[0])
        
        # Apply formatting
        for start, end, style, formatted_content in markers:
            # Add text before marker
            if current_pos < start:
                text_obj.append(content[current_pos:start])
            
            # Add formatted content
            if style == 'bold':
                text_obj.append(formatted_content, style="bold")
            elif style == 'italic':
                text_obj.append(formatted_content, style="italic")
            elif style == 'code':
                text_obj.append(formatted_content, style="cyan on grey23")
            
            current_pos = end
        
        # Add remaining text
        if current_pos < len(content):
            text_obj.append(content[current_pos:])
    
    def _preprocess_markdown_text(self, text: str) -> str:
        """Preprocess text for optimal Rich markdown parsing"""
        
        # Clean up the text
        text = text.strip()
        
        # Fix code blocks - add proper language detection
        # Python code blocks
        text = re.sub(
            r'```\s*\n?(import\s|from\s|def\s|class\s|if\s|for\s|while\s|pip\sinstall)',
            r'```python\n\1', text
        )
        
        # JavaScript/Node.js code blocks
        text = re.sub(
            r'```\s*\n?(const\s|let\s|var\s|function\s|require\(|import.*from|npm\sinstall)',
            r'```javascript\n\1', text
        )
        
        # Shell/Bash code blocks
        text = re.sub(
            r'```\s*\n?(pip\sinstall|npm\sinstall|yarn\s|git\s|cd\s|mkdir\s|ls\s)',
            r'```bash\n\1', text
        )
        
        # Fix code block spacing
        text = re.sub(r'([^\n])\n```', r'\1\n\n```', text)  # Space before code blocks
        text = re.sub(r'```([^\n])', r'```\n\1', text)      # Space after opening ```
        
        # FIXED: Proper bold and italic formatting without regex issues
        # Bold formatting - ensure proper word boundaries
        text = re.sub(r'\*\*([^*\n]+?)\*\*', r'**\1**', text)
        
        # Italic formatting - avoid conflicts with bold, use word boundaries  
        text = re.sub(r'(?<!\*)\*([^*\n\*]+?)\*(?!\*)', r'*\1*', text)
        
        # Fix list formatting
        text = re.sub(r'^(\s*)[-*+]\s+', r'\1- ', text, flags=re.MULTILINE)
        
        # Ensure proper paragraph spacing
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _display_manual_formatted_text(self, text: str):
        """Manual formatting fallback when Rich Markdown fails"""
        
        if not RICH_AVAILABLE:
            print(text)
            return
            
        console.print("\n[bold cyan]══════ Manual Format View ══════[/bold cyan]")
        
        lines = text.split('\n')
        in_code_block = False
        code_language = ""
        
        for line in lines:
            line = line.rstrip()
            
            # Handle code blocks
            if line.startswith('```'):
                if not in_code_block:
                    # Start of code block
                    code_language = line[3:].strip() or "text"
                    in_code_block = True
                    console.print(f"[dim white on blue] {code_language.upper()} CODE [/dim white on blue]")
                else:
                    # End of code block
                    in_code_block = False
                    console.print(f"[dim blue]{'─' * 40}[/dim blue]")
                continue
            
            if in_code_block:
                # Display code with appropriate syntax coloring
                if code_language.lower() in ['python', 'py']:
                    console.print(f"[green]{line}[/green]")
                elif code_language.lower() in ['javascript', 'js', 'node']:
                    console.print(f"[yellow]{line}[/yellow]")
                elif code_language.lower() in ['bash', 'shell', 'sh']:
                    console.print(f"[cyan]{line}[/cyan]")
                else:
                    console.print(f"[white]{line}[/white]")
            else:
                # Handle regular text formatting
                formatted_line = line
                
                # Handle headers
                if formatted_line.startswith('### '):
                    console.print(f"[bold blue]{formatted_line[4:]}[/bold blue]")
                elif formatted_line.startswith('## '):
                    console.print(f"[bold yellow]{formatted_line[3:]}[/bold yellow]")
                elif formatted_line.startswith('# '):
                    console.print(f"[bold green]{formatted_line[2:]}[/bold green]")
                else:
                    # Handle inline formatting with simpler regex patterns
                    formatted_line = line
                    
                    # Handle bold text with simpler pattern
                    formatted_line = re.sub(r'\*\*([^*\n]+?)\*\*', r'[bold]\1[/bold]', formatted_line)
                    
                    # Handle italic text - avoid conflicts with bold
                    formatted_line = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'[italic]\1[/italic]', formatted_line)
                    
                    # Handle inline code
                    formatted_line = re.sub(r'`([^`]+)`', r'[cyan]\1[/cyan]', formatted_line)
                    
                    # Handle bullet points
                    if re.match(r'^(\s*)[-*+]\s+', formatted_line):
                        formatted_line = re.sub(r'^(\s*)[-*+]\s+', r'\1• ', formatted_line)
                        console.print(f"[white]{formatted_line}[/white]")
                    else:
                        console.print(formatted_line)
        
        console.print("[bold cyan]═══════════════════════════[/bold cyan]")
    
    def show_banner(self, title: str, subtitle: str = None):
        """Show application banner with Rich formatting"""
        if not RICH_AVAILABLE:
            print(f"🤖 {title}")
            if subtitle:
                print(subtitle)
            return
            
        banner_text = f"""
╔═══════════════════════════════════════════════════════╗
║                🤖 {title} 🤖                ║
"""
        if subtitle:
            banner_text += f"║           {subtitle}         ║\n"
        
        banner_text += """╚═══════════════════════════════════════════════════════╝

🌐 INTERNET ACCESS ENABLED
🔍 AI will automatically search when needed
⚡ Multiple AI providers available
"""
        console.print(Panel(banner_text, style="bold blue"))
    
    def show_table(self, title: str, headers: list, rows: list, styles: Optional[list] = None):
        """Show a formatted table with Rich"""
        if not RICH_AVAILABLE:
            print(f"{title}")
            print(" | ".join(headers))
            print("-" * 50)
            for row in rows:
                print(" | ".join(str(cell) for cell in row))
            return None
            
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        # Add columns with optional styles
        for i, header in enumerate(headers):
            style = styles[i] if styles and i < len(styles) else "white"
            table.add_column(header, style=style)
        
        # Add rows
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        
        console.print(table)
        return table
    
    def print_status(self, message: str, status: str = "info"):
        """Print status message with appropriate coloring"""
        if not RICH_AVAILABLE:
            print(message)
            return
            
        if status == "success":
            console.print(f"[green]{message}[/green]")
        elif status == "error":
            console.print(f"[red]{message}[/red]")
        elif status == "warning":
            console.print(f"[yellow]{message}[/yellow]")
        elif status == "info":
            console.print(f"[blue]{message}[/blue]")
        else:
            console.print(message)
    
    def print_goodbye(self):
        """Print goodbye message"""
        if RICH_AVAILABLE:
            console.print("[yellow]👋 Thanks for using AI Helper Agent! Goodbye![/yellow]")
        else:
            print("👋 Thanks for using AI Helper Agent! Goodbye!")


# Create a global instance for easy importing
rich_formatter = RichFormattingManager()
