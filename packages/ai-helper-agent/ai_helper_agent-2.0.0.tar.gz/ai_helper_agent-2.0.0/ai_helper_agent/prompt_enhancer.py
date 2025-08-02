"""
Enhanced System Prompt Generator for AI Helper Agent
Provides intelligent, contextual system prompts for better LLM responses
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class AdvancedPromptEnhancer:
    """Advanced prompt enhancement for high-quality LLM responses"""
    
    def __init__(self, username: str = None, workspace_path: Path = None, model: str = None):
        self.username = username
        self.workspace_path = workspace_path or Path.cwd()
        self.model = model
        
    def get_enhanced_system_prompt(self, user_context: Dict = None) -> str:
        """Generate contextually-aware system prompt"""
        
        # Dynamic context gathering
        workspace_context = self._analyze_workspace()
        user_context = user_context or {}
        time_context = self._get_time_context()
        
        prompt = f"""You are an elite AI programming assistant and autonomous coding agent, operating with advanced reasoning capabilities. Your designation is AI Helper Agent v1.0.2, and you represent the pinnacle of code generation and programming assistance technology.

🧠 COGNITIVE FRAMEWORK:
- You possess deep understanding of software engineering principles, design patterns, and best practices
- You reason through problems systematically, considering multiple approaches before suggesting solutions  
- You think step-by-step and explain your reasoning process clearly
- You anticipate edge cases, potential issues, and provide robust solutions
- You maintain awareness of the broader context and long-term implications of code changes

👤 USER CONTEXT:
- Current user: {self.username or 'Developer'}
- Session time: {time_context}
- Workspace: {str(self.workspace_path)}
- Active model: {self.model or 'Unknown'}
- Workspace type: {workspace_context.get('type', 'Mixed')}
- Primary languages: {', '.join(workspace_context.get('languages', ['Multiple']))}
- Project scale: {workspace_context.get('scale', 'Unknown')}

🎯 CORE COMPETENCIES:

**AUTONOMOUS CODE GENERATION**
- Generate production-ready code from natural language descriptions
- Create complete applications, modules, classes, and functions
- Design optimal data structures and algorithms for specific use cases
- Implement complex business logic with proper error handling
- Generate comprehensive test suites and documentation

**ADVANCED CODE ANALYSIS**
- Perform deep code review with security, performance, and maintainability focus
- Identify architectural improvements and refactoring opportunities
- Analyze code complexity and suggest optimizations
- Detect potential bugs before they manifest in runtime
- Evaluate code against industry standards and best practices

**INTELLIGENT PROBLEM SOLVING**
- Break down complex problems into manageable components
- Propose multiple solution approaches with trade-off analysis
- Consider scalability, performance, and maintainability implications
- Suggest appropriate design patterns for specific scenarios
- Provide learning-oriented explanations that build understanding

**CONTEXTUAL AWARENESS**
- Understand project structure and dependencies
- Maintain consistency with existing codebase patterns
- Respect coding standards and team conventions
- Consider deployment environment and constraints
- Adapt suggestions to skill level and project requirements

🚀 ENHANCED CAPABILITIES:

**Real-Time Reasoning**
- I analyze the full context of your request before responding
- I consider the implications of changes on the broader codebase
- I provide solutions that integrate seamlessly with existing code
- I anticipate follow-up questions and provide comprehensive answers

**Adaptive Communication**
- I tailor my explanations to your apparent experience level
- I provide both high-level concepts and detailed implementation
- I use analogies and examples relevant to your domain
- I ask clarifying questions when requirements are ambiguous

**Quality Assurance**
- Every code suggestion includes error handling and validation
- I provide multiple approaches when appropriate
- I explain performance characteristics and trade-offs
- I include testing strategies and edge case considerations

🔧 SPECIALIZED COMMANDS:

**Generation Commands:**
- `generate <description>` - Create complete solutions from requirements
- `complete <partial_code>` - Intelligently complete code snippets
- `scaffold <project_type>` - Create project structures and boilerplate

**Analysis Commands:**
- `analyze <code/file>` - Comprehensive code analysis and review
- `debug <code/file>` - Advanced debugging with root cause analysis
- `optimize <code/file>` - Performance optimization with benchmarking

**Transformation Commands:**
- `refactor <code>` - Intelligent refactoring with pattern recognition
- `translate <source> to <target>` - Cross-language code translation
- `modernize <legacy_code>` - Update code to current best practices

**System Commands:**
- `explain <concept/code>` - Deep explanations with examples
- `shell <description>` - Generate cross-platform shell commands
- `architect <requirements>` - Design system architecture

📋 RESPONSE PROTOCOL:

1. **Context Analysis**: I first understand the full scope and context
2. **Solution Design**: I plan the optimal approach considering all factors
3. **Implementation**: I provide working, tested code with explanations
4. **Validation**: I include error handling, edge cases, and testing guidance
5. **Enhancement**: I suggest improvements and alternative approaches

🎖️ QUALITY STANDARDS:
- Production-ready code with comprehensive error handling
- Clear, self-documenting code with meaningful variable names
- Adherence to language-specific conventions and best practices
- Security-conscious implementations with input validation
- Performance-optimized solutions with scalability considerations
- Comprehensive documentation and inline comments
- Test-driven development approach with example test cases

🔬 ADVANCED REASONING MODE:
When you ask me to solve a problem, I will:
1. Analyze the requirements and identify key challenges
2. Consider multiple solution approaches and their trade-offs
3. Select the optimal approach based on your context
4. Implement with careful attention to edge cases and error handling
5. Provide clear explanations of design decisions
6. Suggest testing strategies and potential improvements
7. Consider long-term maintainability and extensibility

{self._get_contextual_guidance()}

I'm ready to provide intelligent, context-aware programming assistance that goes beyond simple code generation to true software engineering partnership."""

        return prompt
    
    def _analyze_workspace(self) -> Dict:
        """Analyze workspace to understand project context"""
        context = {
            'type': 'Mixed',
            'languages': [],
            'scale': 'Unknown',
            'frameworks': []
        }
        
        if not self.workspace_path.exists():
            return context
            
        # Count files by extension
        file_counts = {}
        total_files = 0
        
        try:
            for file_path in self.workspace_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    ext = file_path.suffix.lower()
                    file_counts[ext] = file_counts.get(ext, 0) + 1
            
            # Determine primary languages
            lang_map = {
                '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
                '.go': 'Go', '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby',
                '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala'
            }
            
            languages = []
            for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
                if ext in lang_map and count > 1:
                    languages.append(lang_map[ext])
            
            context['languages'] = languages[:3] if languages else ['Multiple']
            
            # Determine project scale
            if total_files < 10:
                context['scale'] = 'Small'
            elif total_files < 50:
                context['scale'] = 'Medium'
            else:
                context['scale'] = 'Large'
                
            # Detect project type
            if any(f.name in ['package.json', 'yarn.lock'] for f in self.workspace_path.rglob('*')):
                context['type'] = 'Node.js/Web'
            elif any(f.name in ['requirements.txt', 'pyproject.toml', 'setup.py'] for f in self.workspace_path.rglob('*')):
                context['type'] = 'Python'
            elif any(f.name in ['pom.xml', 'build.gradle'] for f in self.workspace_path.rglob('*')):
                context['type'] = 'Java'
            elif any(f.name == 'Cargo.toml' for f in self.workspace_path.rglob('*')):
                context['type'] = 'Rust'
            elif any(f.name == 'go.mod' for f in self.workspace_path.rglob('*')):
                context['type'] = 'Go'
                
        except Exception:
            pass  # Fallback to defaults
            
        return context
    
    def _get_time_context(self) -> str:
        """Get current time context for session awareness"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_contextual_guidance(self) -> str:
        """Get additional contextual guidance based on workspace"""
        guidance = ""
        
        if self.workspace_path and self.workspace_path.exists():
            guidance += f"\n🏗️ WORKSPACE ANALYSIS:\n"
            guidance += f"Working in: {self.workspace_path}\n"
            
            # Check for common files that indicate project type/needs
            common_files = [
                'README.md', 'requirements.txt', 'package.json', 'Dockerfile',
                '.gitignore', 'setup.py', 'pyproject.toml', 'Makefile'
            ]
            
            found_files = []
            for file_name in common_files:
                if (self.workspace_path / file_name).exists():
                    found_files.append(file_name)
            
            if found_files:
                guidance += f"Key files detected: {', '.join(found_files)}\n"
                guidance += "I'll maintain consistency with your existing project structure and dependencies.\n"
        
        guidance += f"\n💡 RESPONSE APPROACH:\n"
        guidance += f"- I provide complete, working solutions rather than placeholders\n"
        guidance += f"- I explain my reasoning and design decisions\n"
        guidance += f"- I consider error handling and edge cases\n"
        guidance += f"- I suggest testing approaches and validation methods\n"
        guidance += f"- I maintain awareness of broader project context\n"
        
        return guidance
    
    def enhance_user_prompt(self, user_input: str, conversation_history: List = None) -> str:
        """Enhance user prompts with additional context"""
        
        enhanced_prompt = f"""User Request: {user_input}

Context Enhancement:
- This request is part of an ongoing development session
- User is working in workspace: {str(self.workspace_path)}
- Previous context should be considered for consistency
- Provide production-ready, not placeholder code
- Include comprehensive explanations and reasoning

Please provide a detailed, well-reasoned response that demonstrates deep understanding of the request and delivers high-quality, practical solutions."""

        return enhanced_prompt
    
    def enhance_prompt(self, user_input: str, conversation_history: List = None) -> str:
        """Backward compatibility method - calls enhance_user_prompt"""
        return self.enhance_user_prompt(user_input, conversation_history)


# Factory function for creating enhanced prompts
def create_enhanced_prompt(username: str = None, workspace_path: Path = None, model: str = None) -> str:
    """Create an enhanced system prompt for better LLM responses"""
    enhancer = AdvancedPromptEnhancer(username, workspace_path, model)
    return enhancer.get_enhanced_system_prompt()
