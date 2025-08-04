"""
Context Augmentor - Intelligent context enhancement for SQL generation.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

from ..exceptions import RAGError

logger = logging.getLogger(__name__)


class AugmentationStrategy(str, Enum):
    """Context augmentation strategies."""
    SIMPLE = "simple"
    CONTEXTUAL = "contextual"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"


@dataclass
class AugmentationConfig:
    """Configuration for context augmentation."""
    strategy: AugmentationStrategy = AugmentationStrategy.CONTEXTUAL
    max_context_length: int = 4000
    include_metadata: bool = True
    prioritize_recent: bool = True
    schema_weight: float = 0.4
    pattern_weight: float = 0.3
    document_weight: float = 0.3


class ContextAugmentor:
    """
    Intelligent context augmentor that enhances query context with retrieved information.
    
    This class provides sophisticated context augmentation strategies to improve
    SQL generation by providing relevant background information, schema details,
    and query patterns.
    """
    
    def __init__(
        self,
        strategy: AugmentationStrategy = AugmentationStrategy.CONTEXTUAL,
        max_context_length: int = 4000,
        config: Optional[AugmentationConfig] = None
    ):
        self.strategy = strategy
        self.max_context_length = max_context_length
        self.config = config or AugmentationConfig(
            strategy=strategy,
            max_context_length=max_context_length
        )
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def augment_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Augment context with retrieved information.
        
        Args:
            context: Raw context with retrieved documents, schema, patterns
            
        Returns:
            Enhanced context optimized for SQL generation
        """
        try:
            if self.strategy == AugmentationStrategy.SIMPLE:
                return await self._simple_augmentation(context)
            elif self.strategy == AugmentationStrategy.CONTEXTUAL:
                return await self._contextual_augmentation(context)
            elif self.strategy == AugmentationStrategy.HIERARCHICAL:
                return await self._hierarchical_augmentation(context)
            elif self.strategy == AugmentationStrategy.ADAPTIVE:
                return await self._adaptive_augmentation(context)
            else:
                raise RAGError(f"Unsupported augmentation strategy: {self.strategy}")
                
        except Exception as e:
            self.logger.error(f"Context augmentation failed: {str(e)}")
            raise RAGError(f"Context augmentation failed: {str(e)}") from e
    
    async def _simple_augmentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple context augmentation - just concatenate all information."""
        augmented = context.copy()
        
        # Build simple context string
        context_parts = []
        
        # Add query
        if context.get("query"):
            context_parts.append(f"Query: {context['query']}")
        
        # Add documents
        for doc in context.get("documents", []):
            content = doc.get("content", "")
            if content:
                context_parts.append(f"Document: {content}")
        
        # Add schema context
        schema_context = context.get("schema_context", {})
        if schema_context:
            context_parts.append(f"Schema: {str(schema_context)}")
        
        # Add query patterns
        for pattern in context.get("query_patterns", []):
            if pattern.get("content"):
                context_parts.append(f"Pattern: {pattern['content']}")
        
        # Combine and truncate
        full_context = "\n\n".join(context_parts)
        if len(full_context) > self.max_context_length:
            full_context = full_context[:self.max_context_length] + "..."
        
        augmented["augmented_context"] = full_context
        augmented["augmentation_strategy"] = "simple"
        
        return augmented
    
    async def _contextual_augmentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Contextual augmentation with intelligent prioritization."""
        augmented = context.copy()
        
        # Prioritize and structure context
        structured_context = {
            "query_intent": self._extract_query_intent(context.get("query", "")),
            "relevant_schema": self._prioritize_schema_info(context.get("schema_context", {})),
            "similar_patterns": self._prioritize_patterns(context.get("query_patterns", [])),
            "supporting_documents": self._prioritize_documents(context.get("documents", [])),
            "adaptive_hints": context.get("adaptive_suggestions", {})
        }
        
        # Build contextual prompt
        context_prompt = self._build_contextual_prompt(structured_context)
        
        # Ensure length constraints
        if len(context_prompt) > self.max_context_length:
            context_prompt = self._truncate_intelligently(context_prompt)
        
        augmented["augmented_context"] = context_prompt
        augmented["structured_context"] = structured_context
        augmented["augmentation_strategy"] = "contextual"
        
        return augmented
    
    async def _hierarchical_augmentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hierarchical augmentation with layered context building."""
        augmented = context.copy()
        
        # Build context in layers of importance
        layers = {
            "core": {
                "query": context.get("query", ""),
                "primary_intent": self._extract_query_intent(context.get("query", ""))
            },
            "schema": self._build_schema_layer(context.get("schema_context", {})),
            "patterns": self._build_patterns_layer(context.get("query_patterns", [])),
            "documents": self._build_documents_layer(context.get("documents", [])),
            "adaptive": self._build_adaptive_layer(context.get("adaptive_suggestions", {}))
        }
        
        # Combine layers with weights
        weighted_context = self._combine_layers_with_weights(layers)
        
        augmented["augmented_context"] = weighted_context
        augmented["hierarchical_layers"] = layers
        augmented["augmentation_strategy"] = "hierarchical"
        
        return augmented
    
    async def _adaptive_augmentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptive augmentation that learns from user patterns."""
        augmented = context.copy()
        
        # Analyze user patterns and preferences
        user_profile = self._analyze_user_patterns(context)
        
        # Adapt context based on user profile
        adapted_context = self._adapt_context_to_user(context, user_profile)
        
        # Build personalized context
        personalized_prompt = self._build_personalized_prompt(adapted_context, user_profile)
        
        augmented["augmented_context"] = personalized_prompt
        augmented["user_profile"] = user_profile
        augmented["adapted_context"] = adapted_context
        augmented["augmentation_strategy"] = "adaptive"
        
        return augmented
    
    def _extract_query_intent(self, query: str) -> Dict[str, Any]:
        """Extract intent from natural language query."""
        intent = {
            "type": "unknown",
            "entities": [],
            "operations": [],
            "complexity": "simple"
        }
        
        query_lower = query.lower()
        
        # Determine query type
        if any(word in query_lower for word in ["select", "show", "get", "find", "list"]):
            intent["type"] = "select"
        elif any(word in query_lower for word in ["insert", "add", "create"]):
            intent["type"] = "insert"
        elif any(word in query_lower for word in ["update", "modify", "change"]):
            intent["type"] = "update"
        elif any(word in query_lower for word in ["delete", "remove"]):
            intent["type"] = "delete"
        
        # Extract operations
        if "count" in query_lower:
            intent["operations"].append("count")
        if any(word in query_lower for word in ["sum", "total"]):
            intent["operations"].append("sum")
        if any(word in query_lower for word in ["average", "avg"]):
            intent["operations"].append("average")
        if any(word in query_lower for word in ["group", "grouped"]):
            intent["operations"].append("group_by")
        if any(word in query_lower for word in ["order", "sort"]):
            intent["operations"].append("order_by")
        if "join" in query_lower:
            intent["operations"].append("join")
        
        # Determine complexity
        if len(intent["operations"]) > 2 or "join" in intent["operations"]:
            intent["complexity"] = "complex"
        elif len(intent["operations"]) > 0:
            intent["complexity"] = "moderate"
        
        return intent
    
    def _prioritize_schema_info(self, schema_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize schema information based on relevance."""
        if not schema_context:
            return {}
        
        prioritized = {
            "primary_tables": [],
            "key_relationships": [],
            "relevant_columns": [],
            "constraints": []
        }
        
        # Extract and prioritize schema elements
        # This would be more sophisticated in practice
        for key, value in schema_context.items():
            if "table" in key.lower():
                prioritized["primary_tables"].append({key: value})
            elif "relationship" in key.lower():
                prioritized["key_relationships"].append({key: value})
            elif "column" in key.lower():
                prioritized["relevant_columns"].append({key: value})
        
        return prioritized
    
    def _prioritize_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize query patterns based on relevance and success rate."""
        if not patterns:
            return []
        
        # Sort by score/relevance
        sorted_patterns = sorted(
            patterns,
            key=lambda p: p.get("score", 0.0),
            reverse=True
        )
        
        # Take top patterns and add priority info
        prioritized = []
        for i, pattern in enumerate(sorted_patterns[:5]):  # Top 5 patterns
            pattern_copy = pattern.copy()
            pattern_copy["priority"] = i + 1
            pattern_copy["relevance"] = "high" if i < 2 else "medium"
            prioritized.append(pattern_copy)
        
        return prioritized
    
    def _prioritize_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize documents based on relevance and type."""
        if not documents:
            return []
        
        # Sort by score
        sorted_docs = sorted(
            documents,
            key=lambda d: d.get("score", 0.0),
            reverse=True
        )
        
        # Prioritize by document type and recency
        prioritized = []
        for doc in sorted_docs[:3]:  # Top 3 documents
            doc_copy = doc.copy()
            
            # Add priority based on type
            doc_type = doc.get("metadata", {}).get("document_type", "general")
            if doc_type == "schema":
                doc_copy["priority"] = "high"
            elif doc_type == "query_pattern":
                doc_copy["priority"] = "medium"
            else:
                doc_copy["priority"] = "low"
            
            prioritized.append(doc_copy)
        
        return prioritized
    
    def _build_contextual_prompt(self, structured_context: Dict[str, Any]) -> str:
        """Build a contextual prompt from structured context."""
        prompt_parts = []
        
        # Query intent
        intent = structured_context.get("query_intent", {})
        if intent.get("type") != "unknown":
            prompt_parts.append(f"Query Type: {intent['type']}")
            if intent.get("operations"):
                prompt_parts.append(f"Operations: {', '.join(intent['operations'])}")
        
        # Schema information
        schema = structured_context.get("relevant_schema", {})
        if schema.get("primary_tables"):
            tables_info = []
            for table_info in schema["primary_tables"][:3]:  # Limit tables
                tables_info.append(str(table_info))
            prompt_parts.append(f"Relevant Tables: {'; '.join(tables_info)}")
        
        # Query patterns
        patterns = structured_context.get("similar_patterns", [])
        if patterns:
            pattern_info = []
            for pattern in patterns[:2]:  # Top 2 patterns
                if pattern.get("content"):
                    pattern_info.append(f"Pattern: {pattern['content']}")
            if pattern_info:
                prompt_parts.append("Similar Patterns:\n" + "\n".join(pattern_info))
        
        # Supporting documents
        docs = structured_context.get("supporting_documents", [])
        if docs:
            doc_info = []
            for doc in docs[:2]:  # Top 2 documents
                if doc.get("content"):
                    content = doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                    doc_info.append(f"Reference: {content}")
            if doc_info:
                prompt_parts.append("Supporting Information:\n" + "\n".join(doc_info))
        
        return "\n\n".join(prompt_parts)
    
    def _truncate_intelligently(self, context: str) -> str:
        """Intelligently truncate context while preserving important information."""
        if len(context) <= self.max_context_length:
            return context
        
        # Split into sections
        sections = context.split("\n\n")
        
        # Prioritize sections (query type and schema are most important)
        priority_order = ["Query Type:", "Relevant Tables:", "Similar Patterns:", "Supporting Information:"]
        
        truncated_sections = []
        current_length = 0
        
        # Add sections in priority order
        for priority in priority_order:
            for section in sections:
                if section.startswith(priority) and section not in truncated_sections:
                    if current_length + len(section) <= self.max_context_length - 100:  # Leave some buffer
                        truncated_sections.append(section)
                        current_length += len(section) + 2  # +2 for \n\n
                    break
        
        # Add remaining sections if space allows
        for section in sections:
            if section not in truncated_sections:
                if current_length + len(section) <= self.max_context_length - 100:
                    truncated_sections.append(section)
                    current_length += len(section) + 2
                else:
                    break
        
        result = "\n\n".join(truncated_sections)
        if len(result) > self.max_context_length:
            result = result[:self.max_context_length - 3] + "..."
        
        return result
    
    def _build_schema_layer(self, schema_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build schema layer for hierarchical augmentation."""
        return {
            "weight": self.config.schema_weight,
            "content": self._prioritize_schema_info(schema_context),
            "importance": "high"
        }
    
    def _build_patterns_layer(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build patterns layer for hierarchical augmentation."""
        return {
            "weight": self.config.pattern_weight,
            "content": self._prioritize_patterns(patterns),
            "importance": "medium"
        }
    
    def _build_documents_layer(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build documents layer for hierarchical augmentation."""
        return {
            "weight": self.config.document_weight,
            "content": self._prioritize_documents(documents),
            "importance": "medium"
        }
    
    def _build_adaptive_layer(self, adaptive_suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """Build adaptive layer for hierarchical augmentation."""
        return {
            "weight": 0.2,
            "content": adaptive_suggestions,
            "importance": "low"
        }
    
    def _combine_layers_with_weights(self, layers: Dict[str, Any]) -> str:
        """Combine hierarchical layers with weights."""
        weighted_parts = []
        
        # Sort layers by importance and weight
        sorted_layers = sorted(
            layers.items(),
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}.get(x[1].get("importance", "low"), 1),
                x[1].get("weight", 0.0)
            ),
            reverse=True
        )
        
        for layer_name, layer_data in sorted_layers:
            if layer_name == "core":
                weighted_parts.append(f"Query: {layer_data.get('query', '')}")
            else:
                content = layer_data.get("content")
                if content:
                    weighted_parts.append(f"{layer_name.title()}: {str(content)}")
        
        return "\n\n".join(weighted_parts)
    
    def _analyze_user_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user patterns for adaptive augmentation."""
        # This would analyze historical user behavior
        # For now, return a simple profile
        return {
            "query_complexity_preference": "moderate",
            "preferred_operations": ["select", "group_by"],
            "domain_expertise": "intermediate",
            "response_format_preference": "detailed"
        }
    
    def _adapt_context_to_user(
        self,
        context: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt context based on user profile."""
        adapted = context.copy()
        
        # Adjust based on user preferences
        complexity_pref = user_profile.get("query_complexity_preference", "moderate")
        
        if complexity_pref == "simple":
            # Simplify context, focus on basic information
            adapted["focus"] = "basic"
        elif complexity_pref == "advanced":
            # Include more detailed technical information
            adapted["focus"] = "detailed"
        else:
            adapted["focus"] = "balanced"
        
        return adapted
    
    def _build_personalized_prompt(
        self,
        adapted_context: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> str:
        """Build personalized prompt based on user profile."""
        # This would create a highly personalized context
        # For now, use contextual augmentation with user hints
        return self._build_contextual_prompt({
            "query_intent": self._extract_query_intent(adapted_context.get("query", "")),
            "relevant_schema": self._prioritize_schema_info(adapted_context.get("schema_context", {})),
            "similar_patterns": self._prioritize_patterns(adapted_context.get("query_patterns", [])),
            "supporting_documents": self._prioritize_documents(adapted_context.get("documents", [])),
            "user_preferences": user_profile
        })
