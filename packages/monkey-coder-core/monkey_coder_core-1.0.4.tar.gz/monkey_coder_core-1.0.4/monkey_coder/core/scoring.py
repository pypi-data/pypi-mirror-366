"""
Modular scoring strategies for the Advanced Router.

This module implements pluggable scoring components to replace the monolithic
routing logic, making the system more maintainable and extensible.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from enum import Enum

from ..models import ExecuteRequest


class ComplexityLevel(str, Enum):
    """Task complexity levels for routing decisions."""
    TRIVIAL = "trivial"        # Simple queries, basic info retrieval
    SIMPLE = "simple"          # Straightforward coding tasks
    MODERATE = "moderate"      # Multi-step processes, standard algorithms
    COMPLEX = "complex"        # Architecture decisions, complex logic
    CRITICAL = "critical"      # Mission-critical, high-stakes tasks


class ContextType(str, Enum):
    """Context types for routing analysis."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review" 
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REFACTORING = "refactoring"


class ScoringStrategy(ABC):
    """Abstract base class for scoring strategies."""
    
    @abstractmethod
    def score(self, request: ExecuteRequest) -> float:
        """Calculate a score for the given request.
        
        Args:
            request: The execution request to score
            
        Returns:
            A score between 0.0 and 1.0
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this scoring strategy."""
        pass


class ComplexityScorer(ScoringStrategy):
    """Scores task complexity based on various indicators."""
    
    def __init__(self):
        self.base_indicators = ['function', 'class', 'method', 'code', 'implement', 'create']
        self.complex_keywords = [
            'architecture', 'design pattern', 'scalability', 'performance',
            'optimization', 'algorithm', 'data structure', 'system design',
            'distributed', 'microservices', 'database', 'security', 'concurrent',
            'async', 'threading', 'machine learning', 'ai', 'neural network',
            'authentication', 'session', 'validation', 'comprehensive', 'pipeline',
            'fault tolerance', 'auto-scaling', 'real-time', 'serving'
        ]
        self.step_indicators = ['step', 'phase', 'first', 'then', 'next', 'finally', 'multi-step', 'multi-phase']
        self.complex_phrases = [
            'requiring deep technical expertise',
            'with methods for',
            'include detailed',
            'comprehensive',
            'e-commerce platform'
        ]
    
    def score(self, request: ExecuteRequest) -> float:
        """Calculate complexity score from 0.0 (trivial) to 1.0 (critical)."""
        score = 0.0
        prompt = request.prompt.lower()
        
        # Base score for any coding task - use word boundaries for accurate matching
        if any(re.search(r'\b' + re.escape(indicator) + r'\b', prompt) for indicator in self.base_indicators):
            score += 0.2
        
        # Text length indicators - adjusted for better distribution
        word_count = len(prompt.split())
        if word_count > 100:
            score += 0.3
        elif word_count > 50:
            score += 0.2
        elif word_count > 20:
            score += 0.1
        elif word_count > 10:
            score += 0.05
            
        # Technical complexity keywords - expanded and weighted
        keyword_matches = sum(1 for kw in self.complex_keywords if re.search(r'\b' + re.escape(kw) + r'\b', prompt))
        # Adjusted weighting for better balance
        score += min(keyword_matches * 0.08, 0.3)
        
        # Multi-step process indicators - use word boundaries to avoid false matches
        step_count = sum(1 for ind in self.step_indicators if re.search(r'\b' + re.escape(ind) + r'\b', prompt))
        if step_count >= 2:
            score += 0.2
        elif step_count >= 1:
            score += 0.1
            
        # File count complexity
        if request.files and len(request.files) > 8:
            score += 0.3
        elif request.files and len(request.files) > 5:
            score += 0.2
        elif request.files and len(request.files) > 1:
            score += 0.1
        
        # Specific complexity phrases
        phrase_matches = sum(1 for phrase in self.complex_phrases if phrase in prompt)
        score += min(phrase_matches * 0.1, 0.2)
            
        return min(score, 1.0)
    
    def classify_complexity(self, score: float) -> ComplexityLevel:
        """Classify numeric complexity score into levels."""
        if score >= 0.8:
            return ComplexityLevel.CRITICAL
        elif score >= 0.6:
            return ComplexityLevel.COMPLEX
        elif score >= 0.4:
            return ComplexityLevel.MODERATE
        elif score >= 0.2:
            return ComplexityLevel.SIMPLE
        else:
            return ComplexityLevel.TRIVIAL
    
    @property
    def name(self) -> str:
        return "complexity_scorer"


class ContextClassifier(ScoringStrategy):
    """Classifies the context type of a request."""
    
    def __init__(self):
        self.context_keywords = {
            ContextType.CODE_GENERATION: {
                'primary': ['generate', 'create', 'write', 'implement', 'build', 'function', 'class'],
                'secondary': ['code', 'develop', 'program', 'script']
            },
            ContextType.CODE_REVIEW: {
                'primary': ['review', 'analyze', 'check', 'evaluate', 'assess', 'examine'],
                'secondary': ['bugs', 'issues', 'quality']
            },
            ContextType.DEBUGGING: {
                'primary': ['debug', 'fix', 'error', 'bug', 'issue', 'problem', 'traceback'],
                'secondary': ['exception', 'crash', 'fault']
            },
            ContextType.ARCHITECTURE: {
                'primary': ['architecture', 'design', 'structure', 'pattern', 'overall'],
                'secondary': ['system', 'component', 'framework', 'blueprint']
            },
            ContextType.SECURITY: {
                'primary': ['security', 'vulnerability', 'exploit', 'secure', 'auth', 'audit'],
                'secondary': ['authentication', 'authorization', 'encryption', 'attack']
            },
            ContextType.PERFORMANCE: {
                'primary': ['performance', 'optimize', 'speed', 'memory', 'efficient'],
                'secondary': ['fast', 'slow', 'bottleneck', 'scalability']
            },
            ContextType.DOCUMENTATION: {
                'primary': ['document', 'explain', 'describe', 'comment', 'api'],
                'secondary': ['readme', 'guide', 'manual', 'specification']
            },
            ContextType.TESTING: {
                'primary': ['test', 'tests', 'unittest', 'spec', 'verify', 'validate', 'unit test', 'unit tests'],
                'secondary': ['testing', 'assertion', 'mock', 'coverage']
            },
            ContextType.REFACTORING: {
                'primary': ['refactor', 'improve', 'clean', 'restructure'],
                'secondary': ['optimize', 'reorganize', 'simplify']
            },
        }
        
        # Task type mapping - used as fallback
        from ..models import TaskType
        self.task_context_map = {
            TaskType.CODE_GENERATION: ContextType.CODE_GENERATION,
            TaskType.CODE_REVIEW: ContextType.CODE_REVIEW,
            TaskType.DEBUGGING: ContextType.DEBUGGING,
            TaskType.DOCUMENTATION: ContextType.DOCUMENTATION,
            TaskType.TESTING: ContextType.TESTING,
            TaskType.REFACTORING: ContextType.REFACTORING,
        }
    
    def score(self, request: ExecuteRequest) -> float:
        """Score based on context type match confidence."""
        context_type = self.classify_context(request)
        
        # Return a confidence score based on keyword matches
        prompt = request.prompt.lower()
        if context_type in self.context_keywords:
            keyword_groups = self.context_keywords[context_type]
            primary_score = sum(2 for kw in keyword_groups['primary'] 
                              if re.search(r'\b' + re.escape(kw) + r'\b', prompt))
            secondary_score = sum(1 for kw in keyword_groups['secondary'] 
                                if re.search(r'\b' + re.escape(kw) + r'\b', prompt))
            total_score = primary_score + secondary_score
            # Normalize to 0-1 range
            return min(total_score / 10.0, 1.0)
        
        return 0.0
    
    def classify_context(self, request: ExecuteRequest) -> ContextType:
        """Extract primary context type from request."""
        prompt = request.prompt.lower()
        
        # Keyword-based detection with weighted scoring - prioritize this over task type
        best_match = ContextType.CODE_GENERATION
        max_score = 0
        
        for context_type, keyword_groups in self.context_keywords.items():
            # Weighted scoring: primary keywords = 2 points, secondary = 1 point
            primary_score = sum(2 for kw in keyword_groups['primary'] 
                              if re.search(r'\b' + re.escape(kw) + r'\b', prompt))
            secondary_score = sum(1 for kw in keyword_groups['secondary'] 
                                if re.search(r'\b' + re.escape(kw) + r'\b', prompt))
            total_score = primary_score + secondary_score
            
            if total_score > max_score:
                max_score = total_score
                best_match = context_type
        
        # If no keywords matched (max_score == 0), fallback to task type mapping
        if max_score == 0 and request.task_type in self.task_context_map:
            return self.task_context_map[request.task_type]
                
        return best_match
    
    @property
    def name(self) -> str:
        return "context_classifier"


class ScoringManager:
    """Manages multiple scoring strategies and provides aggregated results."""
    
    def __init__(self):
        self.strategies: Dict[str, ScoringStrategy] = {}
        self.complexity_scorer = ComplexityScorer()
        self.context_classifier = ContextClassifier()
        
        # Register default strategies
        self.register_strategy(self.complexity_scorer)
        self.register_strategy(self.context_classifier)
    
    def register_strategy(self, strategy: ScoringStrategy) -> None:
        """Register a new scoring strategy."""
        self.strategies[strategy.name] = strategy
    
    def get_strategy(self, name: str) -> Optional[ScoringStrategy]:
        """Get a scoring strategy by name."""
        return self.strategies.get(name)
    
    def get_complexity_score(self, request: ExecuteRequest) -> Tuple[float, ComplexityLevel]:
        """Get complexity score and classification."""
        score = self.complexity_scorer.score(request)
        level = self.complexity_scorer.classify_complexity(score)
        return score, level
    
    def get_context_classification(self, request: ExecuteRequest) -> Tuple[ContextType, float]:
        """Get context classification and confidence score."""
        context_type = self.context_classifier.classify_context(request)
        confidence = self.context_classifier.score(request)
        return context_type, confidence
    
    def get_scoring_breakdown(self, request: ExecuteRequest) -> Dict[str, float]:
        """Get detailed scoring breakdown from all strategies."""
        breakdown = {}
        for name, strategy in self.strategies.items():
            breakdown[name] = strategy.score(request)
        return breakdown