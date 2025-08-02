"""
Browser Integration with Playwright - Requirement #10
Provides web automation, search functionality, and localhost demonstration
Based on Devika CLI patterns with enhanced localhost integration
"""

import asyncio
import os
import time
import base64
import json
import logging
import threading
import http.server
import socketserver
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from urllib.parse import urlparse, urljoin
import sqlite3
from datetime import datetime

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    PlaywrightTimeoutError = Exception

try:
    from markdownify import markdownify as md
    MARKDOWNIFY_AVAILABLE = True
except ImportError:
    MARKDOWNIFY_AVAILABLE = False
    md = lambda x: x  # Fallback function

try:
    from .utils import get_user_data_dir
except ImportError:
    # Fallback function for when importing as standalone module
    def get_user_data_dir():
        import pathlib
        import os
        if os.name == 'nt':  # Windows
            data_dir = pathlib.Path.home() / "AppData" / "Local" / "ai_helper_agent"
        else:  # Linux/Mac
            data_dir = pathlib.Path.home() / ".ai_helper_agent"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir


class BrowserDatabase:
    """Database manager for browser session data"""
    
    def __init__(self):
        self.user_data_dir = get_user_data_dir()
        self.db_path = self.user_data_dir / "browser_sessions.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize browser database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS browser_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    screenshot_path TEXT,
                    content_html TEXT,
                    content_markdown TEXT,
                    search_query TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS localhost_demos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    demo_name TEXT NOT NULL,
                    localhost_url TEXT NOT NULL,
                    description TEXT,
                    port INTEGER,
                    status TEXT DEFAULT 'created',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    engine TEXT NOT NULL,
                    results_count INTEGER,
                    first_result_url TEXT,
                    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_session(self, session_data: Dict[str, Any]) -> int:
        """Save browser session data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO browser_sessions 
                (session_name, url, title, screenshot_path, content_html, content_markdown, search_query)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data.get('session_name', 'unknown'),
                session_data.get('url', ''),
                session_data.get('title', ''),
                session_data.get('screenshot_path', ''),
                session_data.get('content_html', ''),
                session_data.get('content_markdown', ''),
                session_data.get('search_query', '')
            ))
            return cursor.lastrowid
    
    def save_localhost_demo(self, demo_data: Dict[str, Any]) -> int:
        """Save localhost demonstration data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO localhost_demos (demo_name, localhost_url, description, port, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                demo_data.get('demo_name', 'localhost_demo'),
                demo_data.get('localhost_url', ''),
                demo_data.get('description', ''),
                demo_data.get('port', 8000),
                demo_data.get('status', 'created')
            ))
            return cursor.lastrowid
    
    def get_localhost_demos(self) -> List[Dict[str, Any]]:
        """Get all localhost demonstrations"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM localhost_demos ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]


class LocalhostDemoServer:
    """Simple localhost demonstration server"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.is_running = False
        self.demo_content = self._generate_demo_content()
    
    def _generate_demo_content(self) -> str:
        """Generate demonstration HTML content"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Helper Agent - Browser Integration Demo</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .feature-card {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.3s ease;
        }}
        .feature-card:hover {{
            transform: translateY(-5px);
        }}
        .search-demo {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
        }}
        button {{
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s ease;
        }}
        button:hover {{
            background: #45a049;
        }}
        .status {{
            background: rgba(76, 175, 80, 0.2);
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .timestamp {{
            text-align: center;
            margin-top: 30px;
            opacity: 0.8;
        }}
        #searchResults {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            min-height: 100px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Helper Agent - Browser Integration Demo</h1>
        
        <div class="status">
            <strong>✅ Browser Integration Active</strong><br>
            Server running on localhost:{self.port} | Playwright engine ready
        </div>
        
        <div class="feature-grid">
            <div class="feature-card">
                <h3>🌐 Web Automation</h3>
                <p>Automated web browsing with Playwright engine. Navigate websites, interact with elements, and extract data seamlessly.</p>
            </div>
            
            <div class="feature-card">
                <h3>🔍 Intelligent Search</h3>
                <p>Smart search capabilities with multiple engines. DuckDuckGo, Google, and Bing integration for comprehensive results.</p>
            </div>
            
            <div class="feature-card">
                <h3>📸 Screenshot Capture</h3>
                <p>Full-page screenshots with automatic saving. Visual documentation of browsing sessions and search results.</p>
            </div>
            
            <div class="feature-card">
                <h3>💾 Session Management</h3>
                <p>Persistent session storage with SQLite database. Track browsing history, search queries, and results.</p>
            </div>
        </div>
        
        <div class="search-demo">
            <h3>🔍 Live Search Demonstration</h3>
            <p>Try the integrated search functionality below:</p>
            <input type="text" id="searchQuery" placeholder="Enter your search query..." value="Python programming tutorials">
            <button onclick="performSearch()">Search with AI Helper Agent</button>
            <div id="searchResults">
                <em>Search results will appear here...</em>
            </div>
        </div>
        
        <div class="timestamp">
            <p>Demo server started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Access this demo at: <code>http://localhost:{self.port}</code></p>
        </div>
    </div>

    <script>
        function performSearch() {{
            const query = document.getElementById('searchQuery').value;
            const resultsDiv = document.getElementById('searchResults');
            
            resultsDiv.innerHTML = '<p>🔄 Searching with AI Helper Agent...</p>';
            
            // Simulate search process
            setTimeout(() => {{
                resultsDiv.innerHTML = `
                    <h4>Search Results for: "${{query}}"</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 10px; margin: 5px 0; border-radius: 5px;">
                        <strong>🎯 AI Helper Agent Integration</strong><br>
                        <em>Real search would be performed through the browser integration engine</em><br>
                        <small>localhost:{self.port}/search?q=${{encodeURIComponent(query)}}</small>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); padding: 10px; margin: 5px 0; border-radius: 5px;">
                        <strong>📊 Search Statistics</strong><br>
                        Query: "${{query}}" | Engine: Auto-Selected | Results: Available<br>
                        <small>Timestamp: ${{new Date().toLocaleString()}}</small>
                    </div>
                `;
            }}, 1500);
        }}

        // Auto-update timestamp every minute
        setInterval(() => {{
            const timestampP = document.querySelector('.timestamp p:last-child');
            timestampP.innerHTML = `Current time: <code>${{new Date().toLocaleString()}}</code>`;
        }}, 60000);
    </script>
</body>
</html>
        """
    
    async def start_server(self) -> bool:
        """Start the demonstration server"""
        try:
            import aiohttp
            from aiohttp import web
            
            async def handle_demo(request):
                return web.Response(text=self.demo_content, content_type='text/html')
            
            async def handle_search(request):
                query = request.query.get('q', '')
                search_result = {
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'engine': 'AI Helper Agent Browser Integration',
                    'status': 'demo_mode',
                    'message': f'Search query "{query}" processed through browser integration'
                }
                return web.json_response(search_result)
            
            app = web.Application()
            app.router.add_get('/', handle_demo)
            app.router.add_get('/search', handle_search)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', self.port)
            await site.start()
            
            self.is_running = True
            return True
            
        except ImportError:
            # Fallback to simple HTTP server
            import http.server
            import socketserver
            import threading
            
            class DemoHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/' or self.path == '/index.html':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(self.server.demo_content.encode())
                    else:
                        super().do_GET()
            
            httpd = socketserver.TCPServer(("localhost", self.port), DemoHandler)
            httpd.demo_content = self.demo_content
            
            def run_server():
                httpd.serve_forever()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            self.is_running = True
            return True
            
        except Exception as e:
            logging.error(f"Failed to start localhost demo server: {e}")
            return False


class BrowserIntegration:
    """
    Advanced Browser Integration with Playwright
    Based on Devika CLI patterns with localhost demonstration
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize Browser Integration
        
        Args:
            headless: Run browser in headless mode
            timeout: Default timeout for operations (ms)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required for browser integration. Install with: pip install playwright")
        
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.page = None
        self.current_session = None
        
        # Initialize components
        self.database = BrowserDatabase()
        self.localhost_server = None
        
        # Screenshots directory
        self.screenshots_dir = get_user_data_dir() / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def start(self) -> bool:
        """Start browser integration"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({"width": 1280, "height": 1024})
            
            self.logger.info("Browser integration started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            return False
    
    async def start_localhost_demo(self, port: int = 8080) -> Tuple[bool, str]:
        """
        Start localhost demonstration server
        
        Args:
            port: Port number for localhost server
            
        Returns:
            Tuple of (success, url)
        """
        try:
            self.localhost_server = LocalhostDemoServer(port)
            success = await self.localhost_server.start_server()
            
            if success:
                demo_url = f"http://localhost:{port}"
                
                # Save demo to database
                demo_data = {
                    'demo_name': 'Browser Integration Demo',
                    'localhost_url': demo_url,
                    'description': 'AI Helper Agent browser integration demonstration',
                    'port': port,
                    'status': 'running'
                }
                self.database.save_localhost_demo(demo_data)
                
                self.logger.info(f"Localhost demo started at {demo_url}")
                return True, demo_url
            else:
                return False, ""
                
        except Exception as e:
            self.logger.error(f"Failed to start localhost demo: {e}")
            return False, ""
    
    async def navigate_to(self, url: str) -> bool:
        """
        Navigate to URL
        
        Args:
            url: Target URL
            
        Returns:
            Success status
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started. Call start() first.")
            
            # Handle localhost URLs and relative URLs
            if not url.startswith(('http://', 'https://')):
                if url.startswith('localhost'):
                    url = f"http://{url}"
                elif url.startswith('/'):
                    url = f"http://localhost:8080{url}"
                else:
                    url = f"http://{url}"
            
            await self.page.goto(url, timeout=self.timeout)
            self.logger.info(f"Navigated to: {url}")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout navigating to: {url}")
            return False
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False
    
    async def take_screenshot(self, session_name: str = "browser_session") -> Optional[str]:
        """
        Take full-page screenshot
        
        Args:
            session_name: Name for the session
            
        Returns:
            Screenshot file path
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started. Call start() first.")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{session_name}_{timestamp}.png"
            screenshot_path = self.screenshots_dir / filename
            
            # Take screenshot
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return None
    
    async def get_page_content(self) -> Dict[str, Any]:
        """
        Get page content in multiple formats
        
        Returns:
            Dictionary with content in different formats
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started. Call start() first.")
            
            # Get page metadata
            page_info = await self.page.evaluate("""
                () => ({
                    url: document.location.href,
                    title: document.title,
                    description: document.querySelector('meta[name="description"]')?.content || '',
                    viewport: { width: window.innerWidth, height: window.innerHeight }
                })
            """)
            
            # Get HTML content
            html_content = await self.page.content()
            
            # Get text content
            text_content = await self.page.evaluate("() => document.body.innerText")
            
            # Convert to markdown if available
            markdown_content = ""
            if MARKDOWNIFY_AVAILABLE:
                try:
                    markdown_content = md(html_content)
                except Exception:
                    markdown_content = text_content
            else:
                markdown_content = text_content
            
            return {
                'url': page_info['url'],
                'title': page_info['title'],
                'description': page_info['description'],
                'viewport': page_info['viewport'],
                'html': html_content,
                'text': text_content,
                'markdown': markdown_content
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get page content: {e}")
            return {}
    
    async def search_web(self, query: str, engine: str = "duckduckgo") -> Dict[str, Any]:
        """
        Perform web search using specified engine
        
        Args:
            query: Search query
            engine: Search engine (duckduckgo, google, bing)
            
        Returns:
            Search results and metadata
        """
        try:
            search_urls = {
                "duckduckgo": f"https://duckduckgo.com/?q={query}",
                "google": f"https://www.google.com/search?q={query}",
                "bing": f"https://www.bing.com/search?q={query}"
            }
            
            search_url = search_urls.get(engine.lower(), search_urls["duckduckgo"])
            
            # Navigate to search page
            success = await self.navigate_to(search_url)
            if not success:
                return {"error": "Failed to navigate to search engine"}
            
            # Wait for results to load
            await asyncio.sleep(2)
            
            # Get page content
            content = await self.get_page_content()
            
            # Take screenshot
            screenshot_path = await self.take_screenshot(f"search_{engine}_{query[:20]}")
            
            # Save to database
            search_data = {
                'session_name': f"search_{engine}",
                'url': content.get('url', search_url),
                'title': content.get('title', f"Search: {query}"),
                'screenshot_path': screenshot_path or '',
                'content_html': content.get('html', ''),
                'content_markdown': content.get('markdown', ''),
                'search_query': query
            }
            
            session_id = self.database.save_session(search_data)
            
            return {
                'session_id': session_id,
                'query': query,
                'engine': engine,
                'url': content.get('url'),
                'title': content.get('title'),
                'screenshot_path': screenshot_path,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return {"error": str(e)}
    
    async def interact_with_element(self, selector: str, action: str, value: str = "") -> bool:
        """
        Interact with page elements
        
        Args:
            selector: CSS selector for element
            action: Action type (click, type, scroll)
            value: Value for type actions
            
        Returns:
            Success status
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started. Call start() first.")
            
            if action == "click":
                await self.page.click(selector, timeout=5000)
            elif action == "type":
                await self.page.fill(selector, value)
            elif action == "scroll":
                if value == "up":
                    await self.page.keyboard.press("PageUp")
                elif value == "down":
                    await self.page.keyboard.press("PageDown")
            
            self.logger.info(f"Element interaction: {action} on {selector}")
            return True
            
        except Exception as e:
            self.logger.error(f"Element interaction failed: {e}")
            return False
    
    async def save_current_session(self, session_name: str) -> Optional[int]:
        """
        Save current browser session
        
        Args:
            session_name: Name for the session
            
        Returns:
            Session ID if successful
        """
        try:
            content = await self.get_page_content()
            screenshot_path = await self.take_screenshot(session_name)
            
            session_data = {
                'session_name': session_name,
                'url': content.get('url', ''),
                'title': content.get('title', ''),
                'screenshot_path': screenshot_path or '',
                'content_html': content.get('html', ''),
                'content_markdown': content.get('markdown', ''),
                'search_query': ''
            }
            
            session_id = self.database.save_session(session_data)
            self.current_session = session_id
            
            self.logger.info(f"Session saved: {session_name} (ID: {session_id})")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            return None
    
    def get_localhost_demos(self) -> List[Dict[str, Any]]:
        """Get all localhost demonstrations"""
        return self.database.get_localhost_demos()
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.logger.info("Browser integration closed")
            
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")


class BrowserManager:
    """High-level browser manager for AI Helper Agent"""
    
    def __init__(self, headless: bool = True):
        """Initialize Browser Manager"""
        self.browser_integration = BrowserIntegration(headless=headless)
        self.is_active = False
    
    async def start_browser_integration(self) -> Tuple[bool, str]:
        """
        Start complete browser integration with localhost demo
        
        Returns:
            Tuple of (success, localhost_url)
        """
        try:
            # Start browser
            browser_success = await self.browser_integration.start()
            if not browser_success:
                return False, ""
            
            # Start localhost demo
            demo_success, localhost_url = await self.browser_integration.start_localhost_demo()
            
            if demo_success:
                # Navigate to localhost demo to validate
                await self.browser_integration.navigate_to(localhost_url)
                await asyncio.sleep(1)  # Let page load
                
                # Take initial screenshot
                await self.browser_integration.take_screenshot("localhost_demo_startup")
                
                self.is_active = True
                return True, localhost_url
            else:
                return False, ""
                
        except Exception as e:
            logging.error(f"Failed to start browser integration: {e}")
            return False, ""
    
    async def demonstrate_search(self, query: str = "Python programming tutorials") -> Dict[str, Any]:
        """
        Demonstrate search functionality
        
        Args:
            query: Search query to demonstrate
            
        Returns:
            Search results and demonstration data
        """
        if not self.is_active:
            return {"error": "Browser integration not active"}
        
        # Perform search demonstration
        results = await self.browser_integration.search_web(query, "duckduckgo")
        
        # Add demonstration metadata
        results['demonstration'] = {
            'purpose': 'Browser integration search demonstration',
            'query_used': query,
            'engine_demonstrated': 'DuckDuckGo',
            'features_shown': [
                'Web navigation',
                'Search execution', 
                'Screenshot capture',
                'Content extraction',
                'Session persistence'
            ]
        }
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get browser integration status"""
        localhost_demos = self.browser_integration.get_localhost_demos()
        
        return {
            'browser_active': self.is_active,
            'playwright_available': PLAYWRIGHT_AVAILABLE,
            'markdownify_available': MARKDOWNIFY_AVAILABLE,
            'screenshots_dir': str(self.browser_integration.screenshots_dir),
            'localhost_demos': localhost_demos,
            'database_path': str(self.browser_integration.database.db_path)
        }
    
    async def cleanup(self):
        """Cleanup browser resources"""
        await self.browser_integration.close()
        self.is_active = False


# Factory function for easy integration
def create_browser_manager(headless: bool = True) -> BrowserManager:
    """
    Create a browser manager instance
    
    Args:
        headless: Run browser in headless mode
        
    Returns:
        BrowserManager instance
    """
    return BrowserManager(headless=headless)


# CLI Integration functions
async def start_browser_demo():
    """Start browser integration with localhost demonstration"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available. Install with: pip install playwright")
        return False, ""
    
    print("🚀 Starting Browser Integration with Localhost Demo...")
    
    browser_manager = create_browser_manager(headless=False)  # Show browser for demo
    success, localhost_url = await browser_manager.start_browser_integration()
    
    if success:
        print(f"✅ Browser Integration Active!")
        print(f"🌐 Localhost Demo: {localhost_url}")
        print(f"📸 Screenshots saved to: {browser_manager.browser_integration.screenshots_dir}")
        
        # Demonstrate search
        print("\n🔍 Demonstrating Search Functionality...")
        search_results = await browser_manager.demonstrate_search("AI programming assistant")
        
        if 'error' not in search_results:
            print(f"✅ Search demonstration completed")
            print(f"📄 Session ID: {search_results.get('session_id')}")
            print(f"🖼️ Screenshot: {search_results.get('screenshot_path')}")
        
        return True, localhost_url
    else:
        print("❌ Failed to start browser integration")
        return False, ""


if __name__ == "__main__":
    # Quick test/demo
    asyncio.run(start_browser_demo())
