"""
AI Helper Agent - Prebuilt Templates System
Requirement #8: Comprehensive template system with grade-wise categorization,
custom prompt support, LangChain validation, and cross-session persistence
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import uuid
import sqlite3
from jinja2 import Environment, BaseLoader, Template, TemplateSyntaxError, meta
import threading

import structlog

logger = structlog.get_logger()


class GradeLevel(Enum):
    """Grade level categories for templates"""
    ELEMENTARY = "1-6"
    MIDDLE_HIGH = "6-12"
    COLLEGE = "college"
    POST_COLLEGE = "post-college"
    PROFESSIONAL = "professional"
    ALL_LEVELS = "all"


class TemplateCategory(Enum):
    """Template categories"""
    PYTHON_AGENT = "python"
    STUDY_AGENT = "study"
    DEVELOPER_AGENT = "developer"
    RESEARCH_AGENT = "research"
    CODING_AGENT = "coding"
    DEBUGGING_AGENT = "debugging"
    ANALYSIS_AGENT = "analysis"
    CUSTOM = "custom"


@dataclass
class TemplateMetadata:
    """Template metadata structure"""
    id: str
    name: str
    description: str
    category: str
    grade_level: str
    author: str
    version: str
    created_at: str
    updated_at: str
    usage_count: int = 0
    rating: float = 0.0
    tags: List[str] = None
    langchain_compatible: bool = True
    has_variables: bool = False
    required_variables: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.required_variables is None:
            self.required_variables = []


@dataclass
class Template:
    """Complete template structure"""
    metadata: TemplateMetadata
    system_prompt: str
    user_prompt_template: str
    example_usage: str
    validation_rules: Dict[str, Any] = None
    custom_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = {}
        if self.custom_parameters is None:
            self.custom_parameters = {}


class PromptValidator:
    """Validates prompts for LangChain compatibility and security"""
    
    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())
        self.forbidden_patterns = [
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
        ]
        self.safe_variables = [
            'user_input', 'context', 'query', 'code', 'filename', 'workspace',
            'session_id', 'username', 'timestamp', 'task', 'description',
            'language', 'framework', 'level', 'topic', 'subject'
        ]
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Comprehensive prompt validation"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'langchain_compatible': True,
            'has_variables': False,
            'variables': [],
            'security_issues': [],
            'suggestions': []
        }
        
        try:
            # Check for basic security issues
            security_issues = self._check_security(prompt)
            if security_issues:
                validation_result['security_issues'] = security_issues
                validation_result['is_valid'] = False
                validation_result['errors'].extend([f"Security issue: {issue}" for issue in security_issues])
            
            # Check Jinja2 syntax
            try:
                template = self.jinja_env.from_string(prompt)
                validation_result['langchain_compatible'] = True
            except TemplateSyntaxError as e:
                validation_result['is_valid'] = False
                validation_result['langchain_compatible'] = False
                validation_result['errors'].append(f"Jinja2 syntax error: {e}")
                return validation_result
            
            # Extract variables
            ast = self.jinja_env.parse(prompt)
            variables = meta.find_undeclared_variables(ast)
            validation_result['variables'] = list(variables)
            validation_result['has_variables'] = len(variables) > 0
            
            # Check variable safety
            unsafe_variables = [var for var in variables if not self._is_safe_variable(var)]
            if unsafe_variables:
                validation_result['warnings'].append(f"Potentially unsafe variables: {unsafe_variables}")
            
            # Check for proper LangChain structure
            langchain_issues = self._check_langchain_compatibility(prompt)
            if langchain_issues:
                validation_result['warnings'].extend(langchain_issues)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(prompt, variables)
            validation_result['suggestions'] = suggestions
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation error: {e}")
        
        return validation_result
    
    def _check_security(self, prompt: str) -> List[str]:
        """Check for security issues in prompt"""
        issues = []
        
        for pattern in self.forbidden_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                issues.append(f"Potentially dangerous pattern found: {pattern}")
        
        # Check for suspicious file operations
        if re.search(r'\.\./', prompt) or re.search(r'\.\.\\', prompt):
            issues.append("Path traversal attempt detected")
        
        return issues
    
    def _is_safe_variable(self, variable: str) -> bool:
        """Check if variable name is safe"""
        return (variable.lower() in self.safe_variables or 
                variable.startswith('user_') or 
                variable.startswith('custom_') or
                re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', variable))
    
    def _check_langchain_compatibility(self, prompt: str) -> List[str]:
        """Check LangChain-specific compatibility"""
        issues = []
        
        # Check for proper variable formatting
        if '{' in prompt and '}' in prompt and '{{' not in prompt:
            issues.append("Use {{ }} for variables instead of { } for Jinja2 compatibility")
        
        # Check for message structure recommendations
        if 'system:' not in prompt.lower() and 'user:' not in prompt.lower():
            issues.append("Consider adding role-based structure (system/user messages)")
        
        return issues
    
    def _generate_suggestions(self, prompt: str, variables: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if len(prompt) < 50:
            suggestions.append("Prompt might be too short for effective LLM guidance")
        
        if len(prompt) > 4000:
            suggestions.append("Prompt might be too long, consider breaking into sections")
        
        if not variables:
            suggestions.append("Consider adding variables for dynamic content")
        
        if 'example' not in prompt.lower() and 'format' not in prompt.lower():
            suggestions.append("Consider adding examples or output format specifications")
        
        return suggestions


class TemplateManager:
    """Manages prebuilt and custom templates with database persistence"""
    
    def __init__(self, user_dir: Path):
        self.user_dir = user_dir
        self.templates_dir = user_dir / "templates"
        self.db_path = user_dir / "templates.db"
        
        self.templates_dir.mkdir(exist_ok=True)
        
        self.validator = PromptValidator()
        self.jinja_env = Environment(loader=BaseLoader())
        
        # Thread safety
        self._lock = threading.Lock()
        
        self._init_database()
        self._load_prebuilt_templates()
    
    def _init_database(self):
        """Initialize templates database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                grade_level TEXT,
                author TEXT,
                version TEXT,
                created_at TEXT,
                updated_at TEXT,
                usage_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                tags TEXT,  -- JSON array
                system_prompt TEXT,
                user_prompt_template TEXT,
                example_usage TEXT,
                validation_rules TEXT,  -- JSON
                custom_parameters TEXT,  -- JSON
                langchain_compatible BOOLEAN DEFAULT 1,
                has_variables BOOLEAN DEFAULT 0,
                required_variables TEXT,  -- JSON array
                is_custom BOOLEAN DEFAULT 0
            )
        ''')
        
        # Template usage history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT,
                user_session TEXT,
                used_at TEXT,
                variables_used TEXT,  -- JSON
                success BOOLEAN,
                feedback TEXT,
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        ''')
        
        # Template ratings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT,
                user_session TEXT,
                rating INTEGER,
                review TEXT,
                created_at TEXT,
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_prebuilt_templates(self):
        """Load prebuilt templates into database"""
        prebuilt_templates = self._get_prebuilt_templates()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for template in prebuilt_templates:
                # Check if template already exists
                cursor.execute('SELECT id FROM templates WHERE id = ?', (template.metadata.id,))
                if cursor.fetchone() is None:
                    self._save_template_to_db(cursor, template)
            
            conn.commit()
            conn.close()
        
        logger.info("Prebuilt templates loaded", count=len(prebuilt_templates))
    
    def _get_prebuilt_templates(self) -> List[Template]:
        """Define prebuilt templates"""
        templates = []
        
        # Python Agent Templates
        templates.extend([
            # Elementary Python Agent
            Template(
                metadata=TemplateMetadata(
                    id="python_elementary_v1",
                    name="Elementary Python Tutor",
                    description="Friendly Python tutor for young learners with simple examples",
                    category=TemplateCategory.PYTHON_AGENT.value,
                    grade_level=GradeLevel.ELEMENTARY.value,
                    author="AI Helper Team",
                    version="1.0",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    tags=["python", "beginner", "kids", "friendly"],
                    required_variables=["topic", "level"]
                ),
                system_prompt="""You are a friendly Python teacher for kids aged 6-12. Your job is to make coding fun and easy to understand!

🐍 TEACHING STYLE:
- Use simple words and fun examples
- Include emojis and visual analogies
- Break complex concepts into small steps
- Always encourage and be positive
- Use games, stories, and relatable examples

🎯 FOCUS AREAS:
- Basic Python concepts (variables, print, input)
- Simple calculations and math
- Fun projects like calculators and games
- Problem-solving with coding
- Building confidence in programming

Remember to keep everything age-appropriate and exciting!""",
                user_prompt_template="""Hi there! 🌟 Let's learn about {{ topic }} in Python!

Current level: {{ level }}
What would you like to explore: {{ user_input }}

Let me explain this in a fun and easy way with examples you can try! 🚀""",
                example_usage="topic='variables', level='beginner', user_input='how to store my name in code'"
            ),
            
            # College Python Agent
            Template(
                metadata=TemplateMetadata(
                    id="python_college_v1",
                    name="Advanced Python Developer",
                    description="Comprehensive Python assistance for college-level programming",
                    category=TemplateCategory.PYTHON_AGENT.value,
                    grade_level=GradeLevel.COLLEGE.value,
                    author="AI Helper Team",
                    version="1.0",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    tags=["python", "advanced", "algorithms", "data-structures"],
                    required_variables=["context", "task_type"]
                ),
                system_prompt="""You are an expert Python developer and computer science instructor. You provide comprehensive, professional-level assistance with Python programming.

🎓 EXPERTISE AREAS:
- Advanced Python concepts (OOP, decorators, metaclasses)
- Data structures and algorithms
- Software design patterns
- Performance optimization
- Testing and debugging
- Framework integration (Django, Flask, FastAPI)
- Async programming and concurrency
- Database integration and ORMs

📚 TEACHING APPROACH:
- Provide detailed explanations with code examples
- Discuss best practices and industry standards
- Include performance considerations
- Show multiple solution approaches
- Explain trade-offs and design decisions
- Include relevant documentation references

💡 CODE QUALITY:
- Write clean, readable, and maintainable code
- Follow PEP 8 and Python conventions
- Include proper error handling
- Add meaningful comments and docstrings
- Suggest testing strategies""",
                user_prompt_template="""Context: {{ context }}
Task Type: {{ task_type }}
Request: {{ user_input }}

Please provide a comprehensive solution with:
1. Detailed explanation of the approach
2. Complete, working code with comments
3. Best practices and optimizations
4. Testing considerations
5. Alternative approaches if applicable""",
                example_usage="context='web development project', task_type='API design', user_input='create REST API with authentication'"
            )
        ])
        
        # Study Agent Templates
        templates.extend([
            # General Study Agent
            Template(
                metadata=TemplateMetadata(
                    id="study_general_v1",
                    name="Comprehensive Study Assistant",
                    description="Multi-subject study helper with personalized learning approaches",
                    category=TemplateCategory.STUDY_AGENT.value,
                    grade_level=GradeLevel.ALL_LEVELS.value,
                    author="AI Helper Team",
                    version="1.0",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    tags=["study", "learning", "education", "multi-subject"],
                    required_variables=["subject", "grade_level", "learning_style"]
                ),
                system_prompt="""You are an expert educational assistant specializing in personalized learning across all subjects and grade levels.

📚 CORE CAPABILITIES:
- Adaptive explanations based on grade level and learning style
- Multi-modal learning support (visual, auditory, kinesthetic)
- Subject-specific pedagogical approaches
- Progress tracking and assessment guidance
- Study strategy recommendations

🎯 SUBJECT EXPERTISE:
- Mathematics (algebra, geometry, calculus, statistics)
- Sciences (physics, chemistry, biology, earth science)
- Language Arts (reading, writing, grammar, literature)
- Social Studies (history, geography, civics)
- Computer Science and Technology
- Foreign Languages
- Test Preparation (SAT, ACT, AP, etc.)

🧠 LEARNING STRATEGIES:
- Break complex topics into manageable chunks
- Use analogies and real-world examples
- Provide multiple practice exercises
- Offer different explanation approaches
- Include memory aids and study tips
- Suggest review schedules and techniques""",
                user_prompt_template="""Subject: {{ subject }}
Grade Level: {{ grade_level }}
Learning Style: {{ learning_style }}
Question/Topic: {{ user_input }}

Please provide a comprehensive explanation that:
1. Matches the appropriate grade level
2. Uses the preferred learning style
3. Includes examples and practice opportunities
4. Suggests additional resources or study methods
5. Connects to broader concepts when relevant""",
                example_usage="subject='Biology', grade_level='high school', learning_style='visual', user_input='explain photosynthesis process'"
            )
        ])
        
        # Developer Agent Templates
        templates.extend([
            # Full-Stack Developer Agent
            Template(
                metadata=TemplateMetadata(
                    id="developer_fullstack_v1",
                    name="Full-Stack Development Expert",
                    description="Comprehensive web development assistance for modern tech stacks",
                    category=TemplateCategory.DEVELOPER_AGENT.value,
                    grade_level=GradeLevel.PROFESSIONAL.value,
                    author="AI Helper Team",
                    version="1.0",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    tags=["fullstack", "web-development", "react", "node", "database"],
                    required_variables=["tech_stack", "project_type"]
                ),
                system_prompt="""You are a senior full-stack developer with expertise in modern web technologies and best practices.

🔧 TECHNICAL EXPERTISE:
- Frontend: React, Vue, Angular, TypeScript, Next.js, Svelte
- Backend: Node.js, Python (Django/Flask), Java (Spring), Go, Rust
- Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
- Cloud: AWS, Google Cloud, Azure, Docker, Kubernetes
- DevOps: CI/CD, monitoring, security, performance optimization

🏗️ ARCHITECTURE SKILLS:
- Microservices and distributed systems
- RESTful and GraphQL APIs
- Database design and optimization
- Security implementation
- Scalability planning
- Code organization and patterns

💼 DEVELOPMENT PRACTICES:
- Agile methodologies and best practices
- Test-driven development (TDD)
- Code review and quality assurance
- Performance monitoring and optimization
- Documentation and maintainability
- Industry standards and compliance""",
                user_prompt_template="""Tech Stack: {{ tech_stack }}
Project Type: {{ project_type }}
Development Challenge: {{ user_input }}

Please provide:
1. Detailed technical solution with code examples
2. Architecture considerations and trade-offs
3. Best practices and security considerations
4. Testing and deployment strategies
5. Performance optimization recommendations
6. Maintenance and scalability planning""",
                example_usage="tech_stack='React, Node.js, PostgreSQL', project_type='e-commerce platform', user_input='implement user authentication system'"
            )
        ])
        
        return templates
    
    def create_custom_template(self, name: str, description: str, category: str, 
                             grade_level: str, system_prompt: str, user_prompt_template: str,
                             author: str = "User", tags: List[str] = None) -> Dict[str, Any]:
        """Create a new custom template"""
        try:
            # Validate prompts
            system_validation = self.validator.validate_prompt(system_prompt)
            user_validation = self.validator.validate_prompt(user_prompt_template)
            
            if not system_validation['is_valid'] or not user_validation['is_valid']:
                return {
                    'success': False,
                    'errors': system_validation['errors'] + user_validation['errors']
                }
            
            # Create template
            template_id = f"custom_{uuid.uuid4().hex[:8]}"
            metadata = TemplateMetadata(
                id=template_id,
                name=name,
                description=description,
                category=category,
                grade_level=grade_level,
                author=author,
                version="1.0",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=tags or [],
                langchain_compatible=system_validation['langchain_compatible'] and user_validation['langchain_compatible'],
                has_variables=user_validation['has_variables'],
                required_variables=user_validation['variables']
            )
            
            template = Template(
                metadata=metadata,
                system_prompt=system_prompt,
                user_prompt_template=user_prompt_template,
                example_usage="Custom template - provide your own variables",
                validation_rules={
                    'system_validation': system_validation,
                    'user_validation': user_validation
                }
            )
            
            # Save to database
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                self._save_template_to_db(cursor, template, is_custom=True)
                conn.commit()
                conn.close()
            
            logger.info("Custom template created", template_id=template_id, name=name)
            
            return {
                'success': True,
                'template_id': template_id,
                'validation': {
                    'system': system_validation,
                    'user': user_validation
                }
            }
            
        except Exception as e:
            logger.error("Failed to create custom template", error=str(e))
            return {'success': False, 'error': str(e)}
    
    def get_templates(self, category: Optional[str] = None, grade_level: Optional[str] = None,
                     include_custom: bool = True) -> List[Dict[str, Any]]:
        """Get templates with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM templates WHERE 1=1'
            params = []
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            if grade_level:
                query += ' AND (grade_level = ? OR grade_level = "all")'
                params.append(grade_level)
            
            if not include_custom:
                query += ' AND is_custom = 0'
            
            query += ' ORDER BY usage_count DESC, rating DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            templates = []
            for row in rows:
                template_dict = self._row_to_dict(row)
                templates.append(template_dict)
            
            return templates
            
        except Exception as e:
            logger.error("Failed to get templates", error=str(e))
            return []
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get specific template by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_template(row)
            return None
            
        except Exception as e:
            logger.error("Failed to get template", template_id=template_id, error=str(e))
            return None
    
    def render_template(self, template_id: str, variables: Dict[str, Any],
                       user_input: str = "") -> Dict[str, Any]:
        """Render template with provided variables"""
        try:
            template = self.get_template(template_id)
            if not template:
                return {'success': False, 'error': 'Template not found'}
            
            # Add user_input to variables
            render_vars = variables.copy()
            render_vars['user_input'] = user_input
            
            # Validate required variables
            missing_vars = [var for var in template.metadata.required_variables 
                          if var not in render_vars]
            if missing_vars:
                return {
                    'success': False,
                    'error': f'Missing required variables: {missing_vars}',
                    'required_variables': template.metadata.required_variables
                }
            
            # Render templates
            system_template = self.jinja_env.from_string(template.system_prompt)
            user_template = self.jinja_env.from_string(template.user_prompt_template)
            
            rendered_system = system_template.render(**render_vars)
            rendered_user = user_template.render(**render_vars)
            
            # Log usage
            self._log_template_usage(template_id, variables, True)
            
            return {
                'success': True,
                'system_prompt': rendered_system,
                'user_prompt': rendered_user,
                'template_info': {
                    'name': template.metadata.name,
                    'category': template.metadata.category,
                    'grade_level': template.metadata.grade_level
                }
            }
            
        except Exception as e:
            self._log_template_usage(template_id, variables, False, str(e))
            logger.error("Failed to render template", template_id=template_id, error=str(e))
            return {'success': False, 'error': str(e)}
    
    def validate_custom_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a custom prompt for LangChain compatibility"""
        return self.validator.validate_prompt(prompt)
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get template usage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total templates
            cursor.execute('SELECT COUNT(*) FROM templates')
            total_templates = cursor.fetchone()[0]
            
            # Templates by category
            cursor.execute('SELECT category, COUNT(*) FROM templates GROUP BY category')
            by_category = dict(cursor.fetchall())
            
            # Templates by grade level
            cursor.execute('SELECT grade_level, COUNT(*) FROM templates GROUP BY grade_level')
            by_grade = dict(cursor.fetchall())
            
            # Most used templates
            cursor.execute('SELECT id, name, usage_count FROM templates ORDER BY usage_count DESC LIMIT 5')
            most_used = [{'id': row[0], 'name': row[1], 'usage_count': row[2]} for row in cursor.fetchall()]
            
            # Usage statistics
            cursor.execute('SELECT COUNT(*), AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) FROM template_usage')
            total_usage, success_rate = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_templates': total_templates,
                'by_category': by_category,
                'by_grade_level': by_grade,
                'most_used_templates': most_used,
                'total_usage': total_usage or 0,
                'success_rate': round((success_rate or 0) * 100, 1)
            }
            
        except Exception as e:
            logger.error("Failed to get template statistics", error=str(e))
            return {}
    
    def _save_template_to_db(self, cursor, template: Template, is_custom: bool = False):
        """Save template to database"""
        cursor.execute('''
            INSERT OR REPLACE INTO templates 
            (id, name, description, category, grade_level, author, version, 
             created_at, updated_at, usage_count, rating, tags, 
             system_prompt, user_prompt_template, example_usage,
             validation_rules, custom_parameters, langchain_compatible,
             has_variables, required_variables, is_custom)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            template.metadata.id,
            template.metadata.name,
            template.metadata.description,
            template.metadata.category,
            template.metadata.grade_level,
            template.metadata.author,
            template.metadata.version,
            template.metadata.created_at,
            template.metadata.updated_at,
            template.metadata.usage_count,
            template.metadata.rating,
            json.dumps(template.metadata.tags),
            template.system_prompt,
            template.user_prompt_template,
            template.example_usage,
            json.dumps(template.validation_rules),
            json.dumps(template.custom_parameters),
            template.metadata.langchain_compatible,
            template.metadata.has_variables,
            json.dumps(template.metadata.required_variables),
            is_custom
        ))
    
    def _row_to_template(self, row) -> Template:
        """Convert database row to Template object"""
        metadata = TemplateMetadata(
            id=row[0],
            name=row[1],
            description=row[2],
            category=row[3],
            grade_level=row[4],
            author=row[5],
            version=row[6],
            created_at=row[7],
            updated_at=row[8],
            usage_count=row[9],
            rating=row[10],
            tags=json.loads(row[11]) if row[11] else [],
            langchain_compatible=bool(row[17]),
            has_variables=bool(row[18]),
            required_variables=json.loads(row[19]) if row[19] else []
        )
        
        return Template(
            metadata=metadata,
            system_prompt=row[12],
            user_prompt_template=row[13],
            example_usage=row[14],
            validation_rules=json.loads(row[15]) if row[15] else {},
            custom_parameters=json.loads(row[16]) if row[16] else {}
        )
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        return {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'category': row[3],
            'grade_level': row[4],
            'author': row[5],
            'version': row[6],
            'created_at': row[7],
            'updated_at': row[8],
            'usage_count': row[9],
            'rating': row[10],
            'tags': json.loads(row[11]) if row[11] else [],
            'langchain_compatible': bool(row[17]),
            'has_variables': bool(row[18]),
            'required_variables': json.loads(row[19]) if row[19] else [],
            'is_custom': bool(row[20])
        }
    
    def _log_template_usage(self, template_id: str, variables: Dict[str, Any], 
                           success: bool, feedback: str = ""):
        """Log template usage for analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO template_usage 
                (template_id, user_session, used_at, variables_used, success, feedback)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                template_id,
                "current_session",  # Could be enhanced with actual session ID
                datetime.now().isoformat(),
                json.dumps(variables),
                success,
                feedback
            ))
            
            # Update usage count
            cursor.execute('''
                UPDATE templates SET usage_count = usage_count + 1 
                WHERE id = ?
            ''', (template_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error("Failed to log template usage", error=str(e))


# Factory function for easy integration
def create_template_manager(user_dir: Union[str, Path]) -> TemplateManager:
    """Create template manager for a user"""
    if isinstance(user_dir, str):
        user_dir = Path(user_dir)
    
    return TemplateManager(user_dir)
