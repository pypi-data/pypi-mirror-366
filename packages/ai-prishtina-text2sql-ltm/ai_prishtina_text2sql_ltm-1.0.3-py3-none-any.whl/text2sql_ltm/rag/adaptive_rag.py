"""
Adaptive RAG - Self-improving RAG system with learning capabilities.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

import numpy as np

from .retriever import RAGRetriever
from ..types import UserID, Score
from ..exceptions import RAGError

logger = logging.getLogger(__name__)


@dataclass
class RetrievalFeedback:
    """Feedback for retrieval quality."""
    query: str
    retrieved_docs: List[str]
    user_satisfaction: float
    query_success: bool
    execution_time: float
    timestamp: datetime


@dataclass
class UserProfile:
    """User profile for adaptive retrieval."""
    user_id: UserID
    query_patterns: Dict[str, float]
    preferred_complexity: str
    domain_expertise: Dict[str, float]
    response_preferences: Dict[str, Any]
    success_rate: float
    total_queries: int


class RetrievalOptimizer:
    """Optimizer for retrieval strategies."""
    
    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate
        self.strategy_performance: Dict[str, float] = defaultdict(float)
        self.strategy_usage: Dict[str, int] = defaultdict(int)
    
    def update_strategy_performance(
        self,
        strategy: str,
        performance_score: float
    ) -> None:
        """Update performance score for a retrieval strategy."""
        current_score = self.strategy_performance[strategy]
        usage_count = self.strategy_usage[strategy]
        
        # Exponential moving average
        if usage_count == 0:
            self.strategy_performance[strategy] = performance_score
        else:
            self.strategy_performance[strategy] = (
                (1 - self.learning_rate) * current_score +
                self.learning_rate * performance_score
            )
        
        self.strategy_usage[strategy] += 1
    
    def get_best_strategy(self) -> str:
        """Get the best performing strategy."""
        if not self.strategy_performance:
            return "semantic"  # Default
        
        return max(self.strategy_performance.items(), key=lambda x: x[1])[0]
    
    def get_strategy_scores(self) -> Dict[str, float]:
        """Get all strategy performance scores."""
        return dict(self.strategy_performance)


class AdaptiveRAG:
    """
    Adaptive RAG system that learns and improves over time.
    
    This component provides:
    - User-specific adaptation
    - Strategy optimization
    - Performance learning
    - Context personalization
    """
    
    def __init__(
        self,
        retriever: RAGRetriever,
        learning_rate: float = 0.01,
        adaptation_window: int = 100
    ):
        self.retriever = retriever
        self.learning_rate = learning_rate
        self.adaptation_window = adaptation_window
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # User profiles
        self.user_profiles: Dict[UserID, UserProfile] = {}
        
        # Feedback storage
        self.feedback_history: List[RetrievalFeedback] = []
        
        # Optimizers
        self.retrieval_optimizer = RetrievalOptimizer(learning_rate)
        
        # Adaptation state
        self._adaptation_enabled = True
        self._last_optimization = datetime.utcnow()
        
        # Metrics
        self._metrics = {
            "adaptations_performed": 0,
            "user_profiles_created": 0,
            "feedback_received": 0,
            "optimization_runs": 0,
            "average_improvement": 0.0
        }
    
    async def initialize(self) -> None:
        """Initialize adaptive RAG component."""
        self.logger.info("Adaptive RAG initialized")
    
    async def close(self) -> None:
        """Close adaptive RAG component."""
        self.logger.info("Adaptive RAG closed")
    
    async def get_adaptive_suggestions(
        self,
        query: str,
        user_id: Optional[UserID] = None
    ) -> Dict[str, Any]:
        """
        Get adaptive suggestions for query processing.
        
        Args:
            query: Natural language query
            user_id: Optional user ID
            
        Returns:
            Adaptive suggestions including strategy, parameters, and hints
        """
        try:
            suggestions = {
                "recommended_strategy": "semantic",
                "retrieval_parameters": {},
                "context_hints": [],
                "personalization": {},
                "confidence": 0.5
            }
            
            # Get user profile if available
            user_profile = None
            if user_id:
                user_profile = await self._get_or_create_user_profile(user_id)
                suggestions["personalization"] = self._get_personalization_hints(user_profile, query)
            
            # Get optimal retrieval strategy
            optimal_strategy = self.retrieval_optimizer.get_best_strategy()
            suggestions["recommended_strategy"] = optimal_strategy
            
            # Adapt retrieval parameters
            suggestions["retrieval_parameters"] = self._adapt_retrieval_parameters(
                query, user_profile
            )
            
            # Generate context hints
            suggestions["context_hints"] = self._generate_context_hints(query, user_profile)
            
            # Calculate confidence
            suggestions["confidence"] = self._calculate_suggestion_confidence(
                query, user_profile
            )
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get adaptive suggestions: {str(e)}")
            return {"recommended_strategy": "semantic", "confidence": 0.1}
    
    async def _get_or_create_user_profile(self, user_id: UserID) -> UserProfile:
        """Get or create user profile."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                query_patterns={},
                preferred_complexity="moderate",
                domain_expertise={},
                response_preferences={},
                success_rate=0.5,
                total_queries=0
            )
            self._metrics["user_profiles_created"] += 1
        
        return self.user_profiles[user_id]
    
    def _get_personalization_hints(
        self,
        user_profile: UserProfile,
        query: str
    ) -> Dict[str, Any]:
        """Get personalization hints based on user profile."""
        hints = {
            "preferred_complexity": user_profile.preferred_complexity,
            "domain_focus": [],
            "response_style": user_profile.response_preferences.get("style", "balanced"),
            "detail_level": user_profile.response_preferences.get("detail", "medium")
        }
        
        # Add domain focus based on expertise
        for domain, expertise in user_profile.domain_expertise.items():
            if expertise > 0.7:  # High expertise
                hints["domain_focus"].append(domain)
        
        return hints
    
    def _adapt_retrieval_parameters(
        self,
        query: str,
        user_profile: Optional[UserProfile]
    ) -> Dict[str, Any]:
        """Adapt retrieval parameters based on query and user profile."""
        params = {
            "similarity_threshold": 0.7,
            "max_results": 10,
            "enable_reranking": True,
            "diversity_threshold": 0.8
        }
        
        if user_profile:
            # Adjust based on user success rate
            if user_profile.success_rate > 0.8:
                # High success rate - can be more selective
                params["similarity_threshold"] = 0.75
                params["max_results"] = 8
            elif user_profile.success_rate < 0.5:
                # Low success rate - be more inclusive
                params["similarity_threshold"] = 0.6
                params["max_results"] = 12
            
            # Adjust based on preferred complexity
            if user_profile.preferred_complexity == "simple":
                params["diversity_threshold"] = 0.9  # More diversity for simple queries
            elif user_profile.preferred_complexity == "complex":
                params["enable_reranking"] = True  # Always rerank for complex queries
        
        return params
    
    def _generate_context_hints(
        self,
        query: str,
        user_profile: Optional[UserProfile]
    ) -> List[str]:
        """Generate context hints for query processing."""
        hints = []
        
        # Query-based hints
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["count", "total", "sum"]):
            hints.append("Focus on aggregation functions and GROUP BY clauses")
        
        if any(word in query_lower for word in ["recent", "latest", "last"]):
            hints.append("Prioritize date/time filtering and ORDER BY clauses")
        
        if any(word in query_lower for word in ["compare", "vs", "versus"]):
            hints.append("Consider JOIN operations and comparative analysis")
        
        # User profile-based hints
        if user_profile:
            # Add hints based on user's query patterns
            for pattern, frequency in user_profile.query_patterns.items():
                if frequency > 0.3 and pattern in query_lower:
                    hints.append(f"User frequently queries {pattern} - prioritize related context")
            
            # Add domain-specific hints
            for domain, expertise in user_profile.domain_expertise.items():
                if expertise > 0.6:
                    hints.append(f"User has {domain} expertise - include advanced concepts")
        
        return hints
    
    def _calculate_suggestion_confidence(
        self,
        query: str,
        user_profile: Optional[UserProfile]
    ) -> float:
        """Calculate confidence in adaptive suggestions."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on strategy performance data
        strategy_scores = self.retrieval_optimizer.get_strategy_scores()
        if strategy_scores:
            max_score = max(strategy_scores.values())
            confidence += min(max_score * 0.3, 0.3)
        
        # Increase confidence based on user profile completeness
        if user_profile:
            profile_completeness = min(user_profile.total_queries / 50.0, 1.0)
            confidence += profile_completeness * 0.2
        
        # Increase confidence based on feedback history
        if len(self.feedback_history) > 10:
            recent_feedback = self.feedback_history[-10:]
            avg_satisfaction = sum(f.user_satisfaction for f in recent_feedback) / len(recent_feedback)
            confidence += (avg_satisfaction - 0.5) * 0.2
        
        return min(confidence, 1.0)
    
    async def provide_feedback(
        self,
        query: str,
        retrieved_docs: List[str],
        user_satisfaction: float,
        query_success: bool,
        execution_time: float,
        user_id: Optional[UserID] = None,
        strategy_used: Optional[str] = None
    ) -> None:
        """
        Provide feedback for adaptive learning.
        
        Args:
            query: Original query
            retrieved_docs: List of retrieved document IDs
            user_satisfaction: User satisfaction score (0-1)
            query_success: Whether the query was successful
            execution_time: Query execution time
            user_id: Optional user ID
            strategy_used: Strategy that was used
        """
        try:
            # Create feedback record
            feedback = RetrievalFeedback(
                query=query,
                retrieved_docs=retrieved_docs,
                user_satisfaction=user_satisfaction,
                query_success=query_success,
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )
            
            # Store feedback
            self.feedback_history.append(feedback)
            self._metrics["feedback_received"] += 1
            
            # Update strategy performance
            if strategy_used:
                performance_score = (user_satisfaction + (1.0 if query_success else 0.0)) / 2.0
                self.retrieval_optimizer.update_strategy_performance(strategy_used, performance_score)
            
            # Update user profile
            if user_id:
                await self._update_user_profile(user_id, query, feedback)
            
            # Trigger adaptation if needed
            if len(self.feedback_history) % self.adaptation_window == 0:
                await self._trigger_adaptation()
            
            # Cleanup old feedback
            if len(self.feedback_history) > 1000:
                self.feedback_history = self.feedback_history[-500:]
            
        except Exception as e:
            self.logger.error(f"Failed to process feedback: {str(e)}")
    
    async def _update_user_profile(
        self,
        user_id: UserID,
        query: str,
        feedback: RetrievalFeedback
    ) -> None:
        """Update user profile based on feedback."""
        profile = await self._get_or_create_user_profile(user_id)
        
        # Update query patterns
        query_words = set(query.lower().split())
        for word in query_words:
            if len(word) > 3:  # Skip short words
                current_freq = profile.query_patterns.get(word, 0.0)
                profile.query_patterns[word] = min(current_freq + 0.1, 1.0)
        
        # Update success rate
        profile.total_queries += 1
        current_success = profile.success_rate * (profile.total_queries - 1)
        new_success = current_success + (1.0 if feedback.query_success else 0.0)
        profile.success_rate = new_success / profile.total_queries
        
        # Update complexity preference based on satisfaction
        if feedback.user_satisfaction > 0.8:
            query_complexity = self._estimate_query_complexity(query)
            if query_complexity != profile.preferred_complexity:
                # Gradually shift preference
                complexity_scores = {"simple": 1, "moderate": 2, "complex": 3}
                current_score = complexity_scores.get(profile.preferred_complexity, 2)
                new_score = complexity_scores.get(query_complexity, 2)
                
                # Move towards the successful complexity
                if abs(new_score - current_score) == 1:
                    if new_score > current_score:
                        profile.preferred_complexity = query_complexity
                    else:
                        profile.preferred_complexity = query_complexity
        
        # Update response preferences
        if feedback.user_satisfaction > 0.7:
            if feedback.execution_time < 1.0:
                profile.response_preferences["speed"] = "fast"
            elif feedback.execution_time > 3.0:
                profile.response_preferences["speed"] = "thorough"
    
    def _estimate_query_complexity(self, query: str) -> str:
        """Estimate query complexity from natural language."""
        query_lower = query.lower()
        complexity_indicators = 0
        
        # Count complexity indicators
        if any(word in query_lower for word in ["join", "combine", "merge"]):
            complexity_indicators += 2
        
        if any(word in query_lower for word in ["group", "aggregate", "sum", "count", "average"]):
            complexity_indicators += 1
        
        if any(word in query_lower for word in ["compare", "analyze", "trend", "pattern"]):
            complexity_indicators += 2
        
        if len(query.split()) > 15:
            complexity_indicators += 1
        
        if complexity_indicators <= 1:
            return "simple"
        elif complexity_indicators <= 3:
            return "moderate"
        else:
            return "complex"
    
    async def _trigger_adaptation(self) -> None:
        """Trigger system adaptation based on accumulated feedback."""
        try:
            self.logger.info("Triggering adaptive optimization...")
            
            # Analyze recent feedback
            recent_feedback = self.feedback_history[-self.adaptation_window:]
            
            # Calculate performance metrics
            avg_satisfaction = sum(f.user_satisfaction for f in recent_feedback) / len(recent_feedback)
            success_rate = sum(1 for f in recent_feedback if f.query_success) / len(recent_feedback)
            avg_execution_time = sum(f.execution_time for f in recent_feedback) / len(recent_feedback)
            
            # Adapt retrieval parameters
            if avg_satisfaction < 0.6:
                # Low satisfaction - adjust parameters
                self.logger.info("Low satisfaction detected, adjusting parameters")
                # Implementation would adjust global parameters
            
            if success_rate < 0.7:
                # Low success rate - be more inclusive
                self.logger.info("Low success rate detected, increasing inclusivity")
            
            # Update metrics
            self._metrics["adaptations_performed"] += 1
            self._metrics["optimization_runs"] += 1
            self._last_optimization = datetime.utcnow()
            
            # Calculate improvement
            if len(self.feedback_history) >= self.adaptation_window * 2:
                old_feedback = self.feedback_history[-self.adaptation_window*2:-self.adaptation_window]
                old_satisfaction = sum(f.user_satisfaction for f in old_feedback) / len(old_feedback)
                improvement = avg_satisfaction - old_satisfaction
                self._metrics["average_improvement"] = improvement
            
        except Exception as e:
            self.logger.error(f"Adaptation failed: {str(e)}")
    
    async def optimize(self) -> Dict[str, Any]:
        """Run optimization and return results."""
        try:
            optimization_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "feedback_analyzed": len(self.feedback_history),
                "user_profiles": len(self.user_profiles),
                "strategy_performance": self.retrieval_optimizer.get_strategy_scores(),
                "recommendations": []
            }
            
            # Analyze feedback patterns
            if self.feedback_history:
                recent_feedback = self.feedback_history[-100:]  # Last 100 queries
                
                avg_satisfaction = sum(f.user_satisfaction for f in recent_feedback) / len(recent_feedback)
                success_rate = sum(1 for f in recent_feedback if f.query_success) / len(recent_feedback)
                
                optimization_results["current_performance"] = {
                    "average_satisfaction": avg_satisfaction,
                    "success_rate": success_rate,
                    "total_feedback": len(recent_feedback)
                }
                
                # Generate recommendations
                if avg_satisfaction < 0.7:
                    optimization_results["recommendations"].append(
                        "Consider adjusting similarity thresholds for better relevance"
                    )
                
                if success_rate < 0.8:
                    optimization_results["recommendations"].append(
                        "Increase context diversity to improve query success rate"
                    )
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Optimization failed: {str(e)}")
            return {"error": str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get adaptive RAG metrics."""
        metrics = self._metrics.copy()
        
        # Add current state metrics
        metrics["user_profiles_count"] = len(self.user_profiles)
        metrics["feedback_history_size"] = len(self.feedback_history)
        metrics["strategy_performance"] = self.retrieval_optimizer.get_strategy_scores()
        
        # Add recent performance
        if self.feedback_history:
            recent_feedback = self.feedback_history[-50:]  # Last 50 queries
            metrics["recent_satisfaction"] = sum(f.user_satisfaction for f in recent_feedback) / len(recent_feedback)
            metrics["recent_success_rate"] = sum(1 for f in recent_feedback if f.query_success) / len(recent_feedback)
        
        return metrics
