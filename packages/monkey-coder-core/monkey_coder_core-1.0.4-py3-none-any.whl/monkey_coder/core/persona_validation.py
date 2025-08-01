"""
Enhanced Persona Validation Module

Provides robust validation for persona routing with graceful handling of edge cases,
including single-word inputs, minimal prompts, and context enrichment.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from ..models import ExecuteRequest, PersonaType, TaskType

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of persona validation with enhancement suggestions."""
    
    is_valid: bool
    enhanced_prompt: str
    suggested_persona: Optional[PersonaType] = None
    confidence_score: float = 0.0
    validation_warnings: List[str] = None
    enrichment_applied: bool = False
    original_length: int = 0
    enhanced_length: int = 0
    
    def __post_init__(self):
        if self.validation_warnings is None:
            self.validation_warnings = []


class PersonaValidator:
    """
    Enhanced persona validation with intelligent prompt enrichment.
    
    Handles edge cases like single-word inputs by providing context-aware 
    prompt enhancement and robust persona routing.
    """
    
    def __init__(self):
        self.single_word_patterns = self._init_single_word_patterns()
        self.context_enrichment_templates = self._init_context_templates()
        self.persona_keywords = self._init_persona_keywords()
        logger.info("PersonaValidator initialized with enhanced validation patterns")
    
    def _init_single_word_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for common single-word inputs."""
        return {
            # Development commands
            "build": {
                "task_type": TaskType.CODE_GENERATION,
                "persona": PersonaType.DEVELOPER,
                "template": "Build a {context} application with proper structure and configuration",
                "confidence": 0.8
            },
            "deploy": {
                "task_type": TaskType.CUSTOM,
                "persona": PersonaType.ARCHITECT,
                "template": "Deploy the application to {context} with proper configuration and monitoring",
                "confidence": 0.8
            },
            "test": {
                "task_type": TaskType.TESTING,
                "persona": PersonaType.TESTER,
                "template": "Create comprehensive tests for {context} with full coverage",
                "confidence": 0.9
            },
            "debug": {
                "task_type": TaskType.CODE_ANALYSIS,
                "persona": PersonaType.REVIEWER,
                "template": "Debug and analyze issues in {context} with detailed troubleshooting",
                "confidence": 0.8
            },
            "optimize": {
                "task_type": TaskType.CODE_ANALYSIS,
                "persona": PersonaType.ARCHITECT,
                "template": "Optimize {context} for performance, scalability, and maintainability",
                "confidence": 0.8
            },
            "refactor": {
                "task_type": TaskType.CODE_GENERATION,
                "persona": PersonaType.DEVELOPER,
                "template": "Refactor {context} to improve code quality and maintainability",
                "confidence": 0.8
            },
            
            # Analysis commands
            "analyze": {
                "task_type": TaskType.CODE_ANALYSIS,
                "persona": PersonaType.REVIEWER,
                "template": "Analyze {context} and provide detailed insights and recommendations",
                "confidence": 0.9
            },
            "review": {
                "task_type": TaskType.CODE_ANALYSIS,
                "persona": PersonaType.REVIEWER,
                "template": "Review {context} for quality, security, and best practices",
                "confidence": 0.9
            },
            "audit": {
                "task_type": TaskType.CODE_ANALYSIS,
                "persona": PersonaType.REVIEWER,
                "template": "Conduct comprehensive audit of {context} for compliance and security",
                "confidence": 0.8
            },
            
            # Creation commands  
            "create": {
                "task_type": TaskType.CODE_GENERATION,
                "persona": PersonaType.DEVELOPER,
                "template": "Create {context} with proper structure and best practices",
                "confidence": 0.7
            },
            "implement": {
                "task_type": TaskType.CODE_GENERATION,
                "persona": PersonaType.DEVELOPER,
                "template": "Implement {context} with robust architecture and error handling",
                "confidence": 0.8
            },
            "generate": {
                "task_type": TaskType.CODE_GENERATION,
                "persona": PersonaType.DEVELOPER,
                "template": "Generate {context} with comprehensive documentation and examples",
                "confidence": 0.7
            },
            
            # Architecture commands
            "design": {
                "task_type": TaskType.CUSTOM,
                "persona": PersonaType.ARCHITECT,
                "template": "Design {context} architecture with scalability and maintainability in mind",
                "confidence": 0.8
            },
            "architect": {
                "task_type": TaskType.CUSTOM,
                "persona": PersonaType.ARCHITECT,
                "template": "Architect {context} system with best practices and design patterns",
                "confidence": 0.9
            },
            "plan": {
                "task_type": TaskType.CUSTOM,
                "persona": PersonaType.ARCHITECT,
                "template": "Plan {context} implementation with detailed roadmap and milestones",
                "confidence": 0.8
            }
        }
    
    def _init_context_templates(self) -> Dict[str, str]:
        """Initialize context enrichment templates."""
        return {
            "generic": "the current project",
            "code": "the codebase",
            "api": "the API endpoints",
            "database": "the database schema",
            "frontend": "the user interface",
            "backend": "the server-side components",
            "tests": "the test suite",
            "deployment": "the deployment pipeline",
            "documentation": "the project documentation"
        }
    
    def _init_persona_keywords(self) -> Dict[PersonaType, List[str]]:
        """Initialize persona-specific keywords for enhanced routing."""
        return {
            PersonaType.DEVELOPER: [
                "code", "function", "class", "method", "variable", "implementation",
                "feature", "bug", "fix", "develop", "write", "program"
            ],
            PersonaType.REVIEWER: [
                "review", "analyze", "check", "audit", "validate", "inspect",
                "quality", "security", "performance", "best practices", "standards"
            ],
            PersonaType.ARCHITECT: [
                "design", "architecture", "system", "structure", "pattern",
                "scalability", "maintainability", "planning", "strategy", "roadmap"
            ],
            PersonaType.TESTER: [
                "test", "testing", "spec", "requirement", "validation",
                "verification", "coverage", "scenario", "case", "automation"
            ]
        }
    
    def validate_and_enhance(
        self, 
        request: ExecuteRequest,
        context_hint: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate and enhance a request with intelligent prompt enrichment.
        
        Args:
            request: The execution request to validate
            context_hint: Optional context hint for enhancement
            
        Returns:
            ValidationResult with enhanced prompt and validation details
        """
        original_prompt = request.prompt.strip()
        original_length = len(original_prompt)
        
        logger.info(f"Validating request with prompt length: {original_length}")
        
        # Handle single-word inputs
        if self._is_single_word_input(original_prompt):
            return self._handle_single_word_input(request, context_hint)
        
        # Handle short prompts (< 10 characters)
        if original_length < 10:
            return self._handle_short_prompt(request, context_hint)
        
        # Handle valid prompts that might need persona enhancement
        enhanced_persona = self._suggest_persona_from_content(original_prompt)
        
        return ValidationResult(
            is_valid=True,
            enhanced_prompt=original_prompt,
            suggested_persona=enhanced_persona,
            confidence_score=0.9,
            original_length=original_length,
            enhanced_length=original_length
        )
    
    def _is_single_word_input(self, prompt: str) -> bool:
        """Check if input is a single word."""
        words = prompt.split()
        return len(words) == 1
    
    def _handle_single_word_input(
        self, 
        request: ExecuteRequest,
        context_hint: Optional[str] = None
    ) -> ValidationResult:
        """Handle single-word inputs with intelligent enhancement."""
        word = request.prompt.strip().lower()
        
        # Check if it's a known command pattern
        if word in self.single_word_patterns:
            pattern = self.single_word_patterns[word]
            context = context_hint or self._infer_context_from_request(request)
            
            enhanced_prompt = pattern["template"].format(context=context)
            
            return ValidationResult(
                is_valid=True,
                enhanced_prompt=enhanced_prompt,
                suggested_persona=pattern["persona"],
                confidence_score=pattern["confidence"],
                enrichment_applied=True,
                original_length=len(request.prompt),
                enhanced_length=len(enhanced_prompt),
                validation_warnings=[
                    f"Single-word input '{word}' enhanced to full prompt",
                    f"Suggested task type: {pattern['task_type'].value}"
                ]
            )
        
        # Handle unknown single words
        return self._handle_unknown_single_word(request, context_hint)
    
    def _handle_unknown_single_word(
        self,
        request: ExecuteRequest,
        context_hint: Optional[str] = None
    ) -> ValidationResult:
        """Handle unknown single-word inputs."""
        word = request.prompt.strip()
        context = context_hint or "the current project"
        
        # Attempt to infer intent from word characteristics
        enhanced_prompt = self._create_generic_enhancement(word, context)
        suggested_persona = self._infer_persona_from_word(word)
        
        return ValidationResult(
            is_valid=True,
            enhanced_prompt=enhanced_prompt,
            suggested_persona=suggested_persona,
            confidence_score=0.6,  # Lower confidence for unknown words
            enrichment_applied=True,
            original_length=len(request.prompt),
            enhanced_length=len(enhanced_prompt),
            validation_warnings=[
                f"Unknown single-word input '{word}' enhanced with generic template",
                "Consider providing more specific instructions for better results"
            ]
        )
    
    def _handle_short_prompt(
        self,
        request: ExecuteRequest,
        context_hint: Optional[str] = None
    ) -> ValidationResult:
        """Handle short prompts (< 10 characters) with context enrichment."""
        original = request.prompt.strip()
        
        # Try to extract key words and enhance
        key_words = self._extract_key_words(original)
        context = context_hint or self._infer_context_from_request(request)
        
        if key_words:
            enhanced_prompt = f"Please {original} for {context} with proper implementation and documentation"
        else:
            enhanced_prompt = f"Please assist with {original} in {context} following best practices"
        
        suggested_persona = self._suggest_persona_from_content(original)
        
        return ValidationResult(
            is_valid=True,
            enhanced_prompt=enhanced_prompt,
            suggested_persona=suggested_persona,
            confidence_score=0.7,
            enrichment_applied=True,
            original_length=len(original),
            enhanced_length=len(enhanced_prompt),
            validation_warnings=[
                f"Short prompt enhanced from {len(original)} to {len(enhanced_prompt)} characters"
            ]
        )
    
    def _create_generic_enhancement(self, word: str, context: str) -> str:
        """Create a generic enhancement for unknown words."""
        # Check if word might be a verb, noun, or adjective
        if self._is_likely_action_word(word):
            return f"Please {word} {context} with proper implementation and best practices"
        elif self._is_likely_noun(word):
            return f"Please work with {word} in {context} following established patterns"
        else:
            return f"Please assist with {word} related tasks in {context}"
    
    def _is_likely_action_word(self, word: str) -> bool:
        """Heuristic to determine if word is likely an action/verb."""
        action_endings = ["e", "ize", "fy", "ate"]
        action_words = ["add", "fix", "run", "set", "get", "put", "use", "make", "do"]
        
        return (
            word in action_words or
            any(word.endswith(ending) for ending in action_endings) or
            word.endswith("ing")
        )
    
    def _is_likely_noun(self, word: str) -> bool:
        """Heuristic to determine if word is likely a noun."""
        noun_endings = ["tion", "sion", "ity", "ness", "ment", "ance", "ence"]
        tech_nouns = ["api", "db", "ui", "app", "web", "data", "user", "auth", "config"]
        
        return (
            word in tech_nouns or
            any(word.endswith(ending) for ending in noun_endings) or
            word.endswith("s")  # Plural nouns
        )
    
    def _extract_key_words(self, prompt: str) -> List[str]:
        """Extract key words from short prompt."""
        # Remove common stop words but keep technical terms
        stop_words = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "being"}
        words = [w.lower() for w in prompt.split() if w.lower() not in stop_words]
        return words
    
    def _infer_context_from_request(self, request: ExecuteRequest) -> str:
        """Infer context from request metadata."""
        # Check if there are files to provide context
        if request.files:
            file_types = []
            for file_info in request.files:
                if isinstance(file_info, dict) and "path" in file_info:
                    path = file_info["path"]
                    if path.endswith((".py", ".js", ".ts")):
                        file_types.append("code files")
                    elif path.endswith((".json", ".yaml", ".yml")):
                        file_types.append("configuration files")
                    elif path.endswith((".md", ".txt")):
                        file_types.append("documentation")
            
            if file_types:
                return f"the project ({', '.join(set(file_types))})"
        
        # Infer from task type
        if request.task_type == TaskType.CODE_GENERATION:
            return "the codebase"
        elif request.task_type == TaskType.CODE_ANALYSIS:
            return "the code analysis"
        elif request.task_type == TaskType.TESTING:
            return "the test suite"
        else:
            return "the current project"
    
    def _suggest_persona_from_content(self, content: str) -> Optional[PersonaType]:
        """Suggest persona based on content analysis."""
        content_lower = content.lower()
        
        # Score each persona based on keyword matches
        persona_scores = {}
        for persona, keywords in self.persona_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                persona_scores[persona] = score
        
        # Return persona with highest score
        if persona_scores:
            return max(persona_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _infer_persona_from_word(self, word: str) -> Optional[PersonaType]:
        """Infer persona from single word."""
        word_lower = word.lower()
        
        # Check direct matches in persona keywords
        for persona, keywords in self.persona_keywords.items():
            if word_lower in keywords:
                return persona
        
        # Check partial matches or related terms
        if any(term in word_lower for term in ["develop", "code", "program", "implement"]):
            return PersonaType.DEVELOPER
        elif any(term in word_lower for term in ["review", "analyze", "check", "audit"]):
            return PersonaType.REVIEWER
        elif any(term in word_lower for term in ["design", "architect", "plan", "structure"]):
            return PersonaType.ARCHITECT
        elif any(term in word_lower for term in ["test", "spec", "validate"]):
            return PersonaType.TESTER
        
        # Default to developer for unknown words
        return PersonaType.DEVELOPER
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics and patterns."""
        return {
            "supported_single_words": list(self.single_word_patterns.keys()),
            "persona_keywords": {
                persona.value: keywords
                for persona, keywords in self.persona_keywords.items()
            },
            "context_templates": self.context_enrichment_templates,
            "validation_features": [
                "Single-word input enhancement",
                "Short prompt enrichment", 
                "Context-aware persona suggestion",
                "Intelligent prompt expansion",
                "Edge case handling"
            ]
        }