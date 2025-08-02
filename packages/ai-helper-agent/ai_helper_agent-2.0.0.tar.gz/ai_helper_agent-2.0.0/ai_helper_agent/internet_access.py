"""
AI Helper Agent - Permission-Based Internet Access System
Requirement #7: CLI-level permission prompting, conditional auto-search, 
LLM-driven search decision making, and smart query analysis
"""

import os
import re
import json
import time
import asyncio
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import threading

# Web search and scraping imports
try:
    from googlesearch import search as google_search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        # Fallback to old package name for backward compatibility
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False

# LangChain for query analysis
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_groq import ChatGroq
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

import structlog

logger = structlog.get_logger()


class PermissionLevel(Enum):
    """Permission levels for internet access"""
    ALWAYS_ALLOW = "always"
    ASK_EACH_TIME = "ask"
    NEVER_ALLOW = "never"
    SMART_ANALYSIS = "smart"


class SearchProvider(Enum):
    """Available search providers"""
    DUCKDUCKGO = "duckduckgo"
    GOOGLE = "google"
    SEARX = "searx"
    AUTO = "auto"


@dataclass
class SearchResult:
    """Search result data structure"""
    title: str
    url: str
    snippet: str
    provider: str
    relevance_score: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PermissionRequest:
    """Permission request data structure"""
    query: str
    context: str
    user: str
    session_id: str
    request_type: str
    timestamp: datetime = None
    approved: Optional[bool] = None
    reasoning: str = ""

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class QueryAnalyzer:
    """LLM-driven query analysis for smart search decisions"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.search_keywords = {
            'technical': ['how to', 'tutorial', 'documentation', 'api', 'guide', 'install', 'setup'],
            'research': ['research', 'study', 'academic', 'paper', 'analysis', 'report'],
            'troubleshooting': ['error', 'bug', 'fix', 'problem', 'issue', 'troubleshoot'],
            'information': ['what is', 'explain', 'definition', 'meaning', 'about'],
            'comparison': ['vs', 'versus', 'compare', 'comparison', 'difference', 'best'],
            'current_events': ['news', 'latest', 'recent', 'today', 'current', '2024', '2025'],
            'programming': ['code', 'python', 'javascript', 'programming', 'development', 'framework']
        }
    
    def analyze_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Analyze query to determine if internet search is beneficial"""
        analysis = {
            'needs_search': False,
            'confidence': 0.0,
            'category': 'unknown',
            'reasoning': '',
            'suggested_providers': [],
            'priority': 'low'
        }
        
        query_lower = query.lower()
        
        # Rule-based analysis
        search_indicators = 0
        total_indicators = 0
        category_scores = {}
        
        # Check for search-indicating keywords
        for category, keywords in self.search_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                category_scores[category] = score
                search_indicators += score
            total_indicators += len(keywords)
        
        # Determine dominant category
        if category_scores:
            analysis['category'] = max(category_scores, key=category_scores.get)
        
        # Calculate base confidence
        if search_indicators > 0:
            analysis['confidence'] = min(search_indicators / 3.0, 1.0)  # Cap at 1.0
            analysis['needs_search'] = analysis['confidence'] > 0.3
        
        # Enhanced analysis with LLM if available
        if self.llm and LANGCHAIN_AVAILABLE:
            try:
                llm_analysis = self._llm_analyze_query(query, context)
                # Combine rule-based and LLM analysis
                analysis['confidence'] = (analysis['confidence'] + llm_analysis.get('confidence', 0)) / 2
                analysis['needs_search'] = analysis['needs_search'] or llm_analysis.get('needs_search', False)
                analysis['reasoning'] = llm_analysis.get('reasoning', analysis['reasoning'])
                if llm_analysis.get('category') != 'unknown':
                    analysis['category'] = llm_analysis['category']
            except Exception as e:
                logger.warning("LLM analysis failed", error=str(e))
        
        # Determine priority and providers
        analysis['priority'] = self._determine_priority(analysis)
        analysis['suggested_providers'] = self._suggest_providers(analysis)
        
        # Generate reasoning if not provided by LLM
        if not analysis['reasoning']:
            analysis['reasoning'] = self._generate_reasoning(query, analysis)
        
        return analysis
    
    def _llm_analyze_query(self, query: str, context: str) -> Dict[str, Any]:
        """Use LLM to analyze query for search necessity"""
        system_prompt = """You are an AI assistant that analyzes user queries to determine if they would benefit from internet search.

Analyze the query and context to determine:
1. Does this query need current/real-time information from the internet?
2. Would search results significantly improve the response quality?
3. What category does this query fall into?
4. How confident are you in this assessment?

Categories: technical, research, troubleshooting, information, comparison, current_events, programming, general

Respond with a JSON object containing:
- needs_search: boolean
- confidence: float (0.0 to 1.0)
- category: string
- reasoning: string explaining your decision

Examples:
- "How to install Python?" -> needs_search: true (technical documentation)
- "What is 2+2?" -> needs_search: false (basic math)
- "Latest news about AI" -> needs_search: true (current events)
- "Explain recursion" -> needs_search: false (conceptual explanation)
"""
        
        try:
            user_message = f"Query: {query}\nContext: {context}"
            
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ])
            
            # Parse JSON response
            content = response.content.strip()
            if not content:
                logger.warning("Empty response from LLM analysis")
                return {
                    'needs_search': True,
                    'confidence': 0.5,
                    'category': 'general',
                    'reasoning': 'Empty LLM response, defaulting to search'
                }
            
            # Try to extract JSON from response if it's wrapped in markdown
            if content.startswith('```'):
                # Extract JSON from code block
                lines = content.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                content = '\n'.join(json_lines)
            
            result = json.loads(content)
            
            # Validate required fields
            required_fields = ['needs_search', 'confidence', 'category', 'reasoning']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field '{field}' in LLM response")
                    result[field] = {
                        'needs_search': True,
                        'confidence': 0.5,
                        'category': 'general',
                        'reasoning': f'Missing {field} in LLM response'
                    }[field]
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM JSON response", error=str(e), content=content[:200])
            return {
                'needs_search': True,
                'confidence': 0.5,
                'category': 'general',
                'reasoning': 'JSON parsing failed, defaulting to search'
            }
        except Exception as e:
            logger.error("LLM query analysis failed", error=str(e))
            return {
                'needs_search': True,
                'confidence': 0.5,
                'category': 'general',
                'reasoning': 'LLM analysis failed, defaulting to search'
            }
    
    def _determine_priority(self, analysis: Dict[str, Any]) -> str:
        """Determine priority level based on analysis"""
        confidence = analysis['confidence']
        category = analysis['category']
        
        if category in ['current_events', 'troubleshooting'] and confidence > 0.7:
            return 'high'
        elif category in ['technical', 'research'] and confidence > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _suggest_providers(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest appropriate search providers based on analysis"""
        category = analysis['category']
        providers = []
        
        if category in ['technical', 'programming']:
            providers = ['duckduckgo', 'google']  # Good for technical content
        elif category in ['current_events', 'news']:
            providers = ['google', 'duckduckgo']  # Better for recent content
        elif category in ['research', 'academic']:
            providers = ['google', 'searx']  # Academic-friendly
        else:
            providers = ['duckduckgo', 'google']  # General purpose
        
        return providers
    
    def _generate_reasoning(self, query: str, analysis: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the decision"""
        if analysis['needs_search']:
            return f"Query appears to be {analysis['category']}-related and would benefit from current web information (confidence: {analysis['confidence']:.1%})"
        else:
            return f"Query can likely be answered without web search (confidence: {(1-analysis['confidence']):.1%})"


class WebSearchManager:
    """Manages multiple search providers with fallback capabilities"""
    
    def __init__(self):
        self.providers = {
            SearchProvider.DUCKDUCKGO: self._search_duckduckgo,
            SearchProvider.GOOGLE: self._search_google,
            SearchProvider.SEARX: self._search_searx,
        }
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search(self, query: str, provider: SearchProvider = SearchProvider.AUTO, 
               max_results: int = 10) -> List[SearchResult]:
        """Search using specified provider with automatic fallback"""
        
        if provider == SearchProvider.AUTO:
            # Try providers in order of preference
            providers_to_try = [SearchProvider.DUCKDUCKGO, SearchProvider.GOOGLE, SearchProvider.SEARX]
        else:
            providers_to_try = [provider]
        
        last_error = None
        
        for search_provider in providers_to_try:
            try:
                if search_provider in self.providers:
                    results = self.providers[search_provider](query, max_results)
                    if results:
                        logger.info("Search completed successfully", 
                                  provider=search_provider.value, 
                                  results_count=len(results))
                        return results
            except Exception as e:
                last_error = e
                logger.warning("Search provider failed", 
                             provider=search_provider.value, 
                             error=str(e))
                continue
        
        logger.error("All search providers failed", last_error=str(last_error) if last_error else "Unknown")
        return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using DuckDuckGo with new ddgs package"""
        if not DDGS_AVAILABLE:
            raise ImportError("DuckDuckGo search not available - install with: pip install ddgs")
        
        results = []
        try:
            ddgs = DDGS()
            ddg_results = ddgs.text(query, max_results=max_results, region="us-en", backend="auto")
            
            # Handle both list and generator results
            if hasattr(ddg_results, '__iter__'):
                for result in ddg_results:
                    if isinstance(result, dict):
                        search_result = SearchResult(
                            title=result.get('title', ''),
                            url=result.get('href', '') or result.get('url', ''),
                            snippet=result.get('body', '') or result.get('description', ''),
                            provider='duckduckgo'
                        )
                        results.append(search_result)
                        
                        # Limit results to max_results
                        if len(results) >= max_results:
                            break
            
            logger.info("Search completed successfully", provider="duckduckgo", results_count=len(results))
        
        except Exception as e:
            logger.error("DuckDuckGo search failed", error=str(e))
            raise
        
        return results
    
    def _search_google(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Google with enhanced googlesearch-python"""
        if not GOOGLE_SEARCH_AVAILABLE:
            raise ImportError("Google search not available - install with: pip install googlesearch-python")
        
        results = []
        try:
            # Use googlesearch-python with advanced features
            search_results = google_search(
                query,
                num_results=max_results,
                advanced=True,  # Get more detailed results
                sleep_interval=1,  # Be respectful to Google
                lang="en"
            )
            
            # Handle both generator and list results
            count = 0
            for result in search_results:
                if count >= max_results:
                    break
                    
                if hasattr(result, 'title'):
                    # Advanced search result object
                    search_result = SearchResult(
                        title=result.title or "",
                        url=result.url or "",
                        snippet=result.description or "",
                        provider='google'
                    )
                else:
                    # Simple URL string result
                    url = str(result)
                    title, snippet = self._get_page_metadata(url)
                    search_result = SearchResult(
                        title=title or url,
                        url=url,
                        snippet=snippet or "",
                        provider='google'
                    )
                
                results.append(search_result)
                count += 1
            
            logger.info("Search completed successfully", provider="google", results_count=len(results))
        
        except Exception as e:
            logger.error("Google search failed", error=str(e))
            raise
        
        return results
    
    def _search_searx(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using SearX instance"""
        if not WEB_SCRAPING_AVAILABLE:
            raise ImportError("Web scraping not available for SearX")
        
        results = []
        searx_instances = [
            "https://searx.be",
            "https://search.sapti.me",
            "https://searx.tiekoetter.com"
        ]
        
        for instance in searx_instances:
            try:
                params = {
                    "q": query,
                    "format": "json",
                    "categories": "general"
                }
                
                response = requests.get(f"{instance}/search", params=params, 
                                      headers=self.default_headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                search_results = data.get("results", [])[:max_results]
                
                for result in search_results:
                    search_result = SearchResult(
                        title=result.get('title', ''),
                        url=result.get('url', ''),
                        snippet=result.get('content', ''),
                        provider='searx'
                    )
                    results.append(search_result)
                
                if results:
                    break  # Success with this instance
                    
            except Exception as e:
                logger.warning("SearX instance failed", instance=instance, error=str(e))
                continue
        
        if not results:
            raise Exception("All SearX instances failed")
        
        return results
    
    def _get_page_metadata(self, url: str) -> Tuple[str, str]:
        """Extract title and description from webpage"""
        if not WEB_SCRAPING_AVAILABLE:
            return url, ""
        
        try:
            response = requests.get(url, headers=self.default_headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else ""
            
            # Get meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if not desc_tag:
                desc_tag = soup.find('meta', attrs={'property': 'og:description'})
            
            description = desc_tag.get('content', '').strip() if desc_tag else ""
            
            # If no description, get first paragraph
            if not description:
                p_tag = soup.find('p')
                if p_tag:
                    description = p_tag.text.strip()[:200] + "..."
            
            return title, description
            
        except Exception as e:
            logger.debug("Failed to get page metadata", url=url, error=str(e))
            return url, ""


class PermissionManager:
    """Manages internet access permissions and user preferences"""
    
    def __init__(self, user_dir: Path):
        self.user_dir = user_dir
        self.db_path = user_dir / "permissions.db"
        self.config_path = user_dir / "internet_config.json"
        self.current_permission = PermissionLevel.ASK_EACH_TIME
        self.auto_approve_categories = set()
        self.query_analyzer = None
        self._init_database()
        self._load_config()
    
    def _init_database(self):
        """Initialize permissions database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permission_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                context TEXT,
                user TEXT,
                session_id TEXT,
                request_type TEXT,
                timestamp TIMESTAMP,
                approved BOOLEAN,
                reasoning TEXT,
                auto_approved BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permission_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT UNIQUE,
                action TEXT,  -- allow, deny, ask
                category TEXT,
                created_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_config(self):
        """Load permission configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.current_permission = PermissionLevel(config.get('permission_level', 'ask'))
                self.auto_approve_categories = set(config.get('auto_approve_categories', []))
                
                logger.info("Permission config loaded", 
                          permission_level=self.current_permission.value,
                          auto_categories=len(self.auto_approve_categories))
        except Exception as e:
            logger.warning("Failed to load permission config", error=str(e))
    
    def _save_config(self):
        """Save permission configuration"""
        try:
            config = {
                'permission_level': self.current_permission.value,
                'auto_approve_categories': list(self.auto_approve_categories),
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info("Permission config saved")
        except Exception as e:
            logger.error("Failed to save permission config", error=str(e))
    
    def set_permission_level(self, level: PermissionLevel):
        """Set global permission level"""
        if isinstance(level, str):
            try:
                level = PermissionLevel(level)
            except ValueError:
                raise ValueError(f"Invalid permission level: {level}. Must be one of: {list(PermissionLevel)}")
        
        self.current_permission = level
        self._save_config()
        logger.info("Permission level updated", level=level.value)
    
    def add_auto_approve_category(self, category: str):
        """Add category to auto-approve list"""
        self.auto_approve_categories.add(category)
        self._save_config()
        logger.info("Auto-approve category added", category=category)
    
    def remove_auto_approve_category(self, category: str):
        """Remove category from auto-approve list"""
        self.auto_approve_categories.discard(category)
        self._save_config()
        logger.info("Auto-approve category removed", category=category)
    
    def request_permission(self, request: PermissionRequest) -> bool:
        """Request permission for internet access"""
        
        # Check global permission level
        if self.current_permission == PermissionLevel.NEVER_ALLOW:
            self._log_request(request, False, auto_approved=True, 
                            reasoning="Global permission set to never allow")
            return False
        
        if self.current_permission == PermissionLevel.ALWAYS_ALLOW:
            self._log_request(request, True, auto_approved=True, 
                            reasoning="Global permission set to always allow")
            return True
        
        # Smart analysis if enabled
        if self.current_permission == PermissionLevel.SMART_ANALYSIS:
            return self._smart_permission_check(request)
        
        # Ask user for permission
        return self._ask_user_permission(request)
    
    def _smart_permission_check(self, request: PermissionRequest) -> bool:
        """Use AI analysis to determine if permission should be granted"""
        if not self.query_analyzer:
            # Fall back to asking user if no analyzer available
            return self._ask_user_permission(request)
        
        try:
            analysis = self.query_analyzer.analyze_query(request.query, request.context)
            
            # Get category safely with default
            category = analysis.get('category', 'unknown')
            needs_search = analysis.get('needs_search', False)
            confidence = analysis.get('confidence', 0.0)
            
            # Auto-approve if category is in auto-approve list
            if category in self.auto_approve_categories:
                self._log_request(request, True, auto_approved=True,
                                reasoning=f"Auto-approved category: {category}")
                return True
            
            # Auto-approve high-confidence technical queries
            if (needs_search and 
                confidence > 0.8 and 
                category in ['technical', 'programming', 'troubleshooting']):
                self._log_request(request, True, auto_approved=True,
                                reasoning=f"High-confidence {category} query")
                return True
            
            # Ask user for medium-confidence queries
            if needs_search and confidence > 0.5:
                reasoning = analysis.get('reasoning', 'Query analysis suggests internet search needed')
                print(f"\n🤖 AI Analysis: {reasoning}")
                return self._ask_user_permission(request)
            
            # Deny low-confidence queries
            self._log_request(request, False, auto_approved=True,
                            reasoning=f"Low-confidence query (score: {confidence:.1%})")
            return False
            
        except Exception as e:
            logger.error("Smart permission analysis failed", error=str(e))
            # Fall back to asking user
            return self._ask_user_permission(request)
    
    def _ask_user_permission(self, request: PermissionRequest) -> bool:
        """Ask user for permission interactively"""
        try:
            print(f"\n🌐 Internet Access Request")
            print(f"📝 Query: {request.query}")
            print(f"📋 Context: {request.context}")
            print(f"🔍 Type: {request.request_type}")
            
            while True:
                response = input("\n🤔 Allow internet access? (y/n/always/never/smart): ").lower().strip()
                
                if response in ['y', 'yes']:
                    approved = True
                    break
                elif response in ['n', 'no']:
                    approved = False
                    break
                elif response == 'always':
                    self.set_permission_level(PermissionLevel.ALWAYS_ALLOW)
                    approved = True
                    break
                elif response == 'never':
                    self.set_permission_level(PermissionLevel.NEVER_ALLOW)
                    approved = False
                    break
                elif response == 'smart':
                    self.set_permission_level(PermissionLevel.SMART_ANALYSIS)
                    approved = self._smart_permission_check(request)
                    break
                else:
                    print("Please answer y/n/always/never/smart")
            
            self._log_request(request, approved, auto_approved=False)
            return approved
            
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Permission denied (user cancelled)")
            self._log_request(request, False, auto_approved=False, 
                            reasoning="User cancelled permission request")
            return False
    
    def _log_request(self, request: PermissionRequest, approved: bool, 
                    auto_approved: bool = False, reasoning: str = ""):
        """Log permission request to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO permission_requests 
                (query, context, user, session_id, request_type, timestamp, 
                 approved, reasoning, auto_approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.query,
                request.context,
                request.user,
                request.session_id,
                request.request_type,
                request.timestamp.isoformat(),
                approved,
                reasoning,
                auto_approved
            ))
            
            conn.commit()
            conn.close()
            
            logger.info("Permission request logged", 
                      approved=approved, auto_approved=auto_approved)
            
        except Exception as e:
            logger.error("Failed to log permission request", error=str(e))
    
    def get_permission_stats(self) -> Dict[str, Any]:
        """Get permission statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total requests
            cursor.execute('SELECT COUNT(*) FROM permission_requests')
            total_requests = cursor.fetchone()[0]
            
            # Get approved requests
            cursor.execute('SELECT COUNT(*) FROM permission_requests WHERE approved = 1')
            approved_requests = cursor.fetchone()[0]
            
            # Get auto-approved requests
            cursor.execute('SELECT COUNT(*) FROM permission_requests WHERE auto_approved = 1')
            auto_approved_requests = cursor.fetchone()[0]
            
            # Get recent requests (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM permission_requests WHERE timestamp > ?', (week_ago,))
            recent_requests = cursor.fetchone()[0]
            
            conn.close()
            
            approval_rate = (approved_requests / total_requests * 100) if total_requests > 0 else 0
            auto_rate = (auto_approved_requests / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'approved_requests': approved_requests,
                'auto_approved_requests': auto_approved_requests,
                'recent_requests': recent_requests,
                'approval_rate': approval_rate,
                'auto_approval_rate': auto_rate,
                'current_permission_level': self.current_permission.value,
                'auto_approve_categories': list(self.auto_approve_categories)
            }
            
        except Exception as e:
            logger.error("Failed to get permission stats", error=str(e))
            return {'error': str(e)}


class InternetAccessManager:
    """Main manager for permission-based internet access"""
    
    def __init__(self, user_dir: Path, llm=None):
        self.user_dir = user_dir
        self.permission_manager = PermissionManager(user_dir)
        self.search_manager = WebSearchManager()
        self.query_analyzer = QueryAnalyzer(llm)
        
        # Connect analyzer to permission manager
        self.permission_manager.query_analyzer = self.query_analyzer
        
        logger.info("Internet access manager initialized", user_dir=str(user_dir))
    
    def search_with_permission(self, query: str, context: str = "", user: str = "user", 
                             session_id: str = "default", max_results: int = 10,
                             provider: SearchProvider = SearchProvider.AUTO) -> Optional[List[SearchResult]]:
        """Search with permission checking"""
        
        # Create permission request
        request = PermissionRequest(
            query=query,
            context=context,
            user=user,
            session_id=session_id,
            request_type="web_search"
        )
        
        # Check permission
        if not self.permission_manager.request_permission(request):
            logger.info("Internet access denied", query=query[:50])
            return None
        
        # Perform search
        try:
            results = self.search_manager.search(query, provider, max_results)
            logger.info("Search completed with permission", 
                      query=query[:50], results_count=len(results))
            return results
            
        except Exception as e:
            logger.error("Search failed after permission granted", error=str(e))
            return None
    
    def analyze_query_for_search(self, query: str, context: str = "") -> Dict[str, Any]:
        """Analyze if query would benefit from search"""
        return self.query_analyzer.analyze_query(query, context)
    
    def configure_permissions(self, level: str = None, auto_categories: List[str] = None):
        """Configure permission settings"""
        if level:
            try:
                permission_level = PermissionLevel(level)
                self.permission_manager.set_permission_level(permission_level)
                print(f"✅ Permission level set to: {level}")
            except ValueError:
                print(f"❌ Invalid permission level: {level}")
                print("Valid options: always, ask, never, smart")
        
        if auto_categories:
            for category in auto_categories:
                self.permission_manager.add_auto_approve_category(category)
            print(f"✅ Auto-approve categories updated: {auto_categories}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        stats = self.permission_manager.get_permission_stats()
        
        # Add provider availability
        stats['available_providers'] = {
            'duckduckgo': DDGS_AVAILABLE,
            'google': GOOGLE_SEARCH_AVAILABLE,
            'web_scraping': WEB_SCRAPING_AVAILABLE,
            'langchain_analysis': LANGCHAIN_AVAILABLE
        }
        
        # Add system capabilities
        stats['capabilities'] = {
            'smart_analysis': LANGCHAIN_AVAILABLE and self.query_analyzer.llm is not None,
            'multiple_providers': DDGS_AVAILABLE or GOOGLE_SEARCH_AVAILABLE,
            'metadata_extraction': WEB_SCRAPING_AVAILABLE
        }
        
        return stats


# Factory function for easy integration
def create_internet_access_manager(user_dir: Union[str, Path], llm=None) -> InternetAccessManager:
    """Create internet access manager for a user"""
    if isinstance(user_dir, str):
        user_dir = Path(user_dir)
    
    return InternetAccessManager(user_dir, llm)
