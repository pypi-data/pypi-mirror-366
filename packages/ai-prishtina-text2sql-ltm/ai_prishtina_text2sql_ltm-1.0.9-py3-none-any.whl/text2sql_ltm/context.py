"""
Context engine for memory-enhanced query processing.

This module provides intelligent context processing that integrates
long-term memory with current query context to improve SQL generation.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
import re
import structlog

from .config import AgentConfig
from .exceptions import ContextError, ContextResolutionError, AmbiguousContextError

logger = structlog.get_logger(__name__)


@dataclass
class QueryContext:
    """
    Represents the complete context for a query including memory influences.
    """
    user_id: str
    session_id: str
    current_query: str
    conversation_history: List[Any] = field(default_factory=list)
    database_schema: Optional[Dict[str, Any]] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Extracted context elements
    table_names: List[str] = field(default_factory=list)
    column_names: List[str] = field(default_factory=list)
    query_intent: Optional[str] = None
    referenced_entities: List[str] = field(default_factory=list)
    
    # Memory influences
    memory_influences: List[Dict[str, Any]] = field(default_factory=list)
    relevance_score: float = 0.0


@dataclass
class EnhancedQueryContext:
    """
    Enhanced query context with memory integration and resolution.
    """
    original_context: QueryContext
    resolved_query: str
    memory_influences: List[Dict[str, Any]] = field(default_factory=list)
    context_resolution: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0
    confidence: float = 0.0
    
    # Resolved elements
    resolved_tables: List[str] = field(default_factory=list)
    resolved_columns: List[str] = field(default_factory=list)
    resolved_relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    # Enhancement metadata
    enhancement_applied: List[str] = field(default_factory=list)
    ambiguity_warnings: List[str] = field(default_factory=list)


class ContextEngine:
    """
    Context engine that enhances queries using long-term memory.
    
    This engine:
    - Analyzes current query context
    - Retrieves relevant memories
    - Resolves ambiguous references
    - Enhances query understanding with historical context
    """
    
    def __init__(self, memory_manager: Any, config: AgentConfig):
        self.memory_manager = memory_manager
        self.config = config
        self.logger = logger.bind(component="ContextEngine")
        
        # Context analysis patterns
        self._table_patterns = [
            r'\bfrom\s+(\w+)',
            r'\bjoin\s+(\w+)',
            r'\btable\s+(\w+)',
            r'\b(\w+)\s+table',
        ]
        
        self._column_patterns = [
            r'\bselect\s+([^from]+)',
            r'\bwhere\s+(\w+)',
            r'\border\s+by\s+(\w+)',
            r'\bgroup\s+by\s+(\w+)',
        ]
        
        self._intent_patterns = {
            'select': r'\b(show|get|find|list|display|retrieve)\b',
            'aggregate': r'\b(count|sum|avg|average|total|max|min)\b',
            'filter': r'\b(where|filter|condition|criteria)\b',
            'join': r'\b(join|combine|merge|relate)\b',
            'sort': r'\b(sort|order|arrange)\b',
            'group': r'\b(group|categorize|segment)\b',
        }
        
        self.logger.info("ContextEngine initialized")
    
    async def enhance_query_context(
        self,
        query_context: QueryContext,
        user_id: str,
        session_history: List[Any]
    ) -> EnhancedQueryContext:
        """
        Enhance query context with memory and historical information.
        
        Args:
            query_context: Original query context
            user_id: User identifier
            session_history: Session conversation history
            
        Returns:
            Enhanced query context with memory influences
        """
        try:
            self.logger.info("Enhancing query context",
                           user_id=user_id,
                           query=query_context.current_query[:100])
            
            # Step 1: Analyze current query
            analyzed_context = await self._analyze_query_context(query_context)
            
            # Step 2: Retrieve relevant memories
            relevant_memories = await self._retrieve_relevant_memories(
                user_id, analyzed_context
            )
            
            # Step 3: Resolve context ambiguities
            resolved_context = await self._resolve_context_ambiguities(
                analyzed_context, relevant_memories, session_history
            )
            
            # Step 4: Apply memory enhancements
            enhanced_context = await self._apply_memory_enhancements(
                resolved_context, relevant_memories
            )
            
            # Step 5: Calculate confidence and relevance scores
            enhanced_context = self._calculate_context_scores(enhanced_context)
            
            self.logger.info("Query context enhanced successfully",
                           user_id=user_id,
                           memory_influences=len(enhanced_context.memory_influences),
                           relevance_score=enhanced_context.relevance_score)
            
            return enhanced_context
            
        except Exception as e:
            self.logger.error("Failed to enhance query context",
                            user_id=user_id,
                            error=str(e))
            raise ContextError(f"Context enhancement failed: {str(e)}", cause=e)
    
    async def _analyze_query_context(self, context: QueryContext) -> QueryContext:
        """Analyze the current query to extract context elements."""
        query = context.current_query.lower()
        
        # Extract table names
        for pattern in self._table_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            context.table_names.extend(matches)
        
        # Extract column references
        for pattern in self._column_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            context.column_names.extend([m.strip() for m in matches if m.strip()])
        
        # Determine query intent
        for intent, pattern in self._intent_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                context.query_intent = intent
                break
        
        # Extract referenced entities (customers, products, etc.)
        entity_patterns = [
            r'\bcustomer[s]?\s+(\w+)',
            r'\bproduct[s]?\s+(\w+)',
            r'\border[s]?\s+(\w+)',
            r'\buser[s]?\s+(\w+)',
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            context.referenced_entities.extend(matches)
        
        # Clean up extracted elements
        context.table_names = list(set([t for t in context.table_names if t]))
        context.column_names = list(set([c for c in context.column_names if c]))
        context.referenced_entities = list(set([e for e in context.referenced_entities if e]))
        
        return context
    
    async def _retrieve_relevant_memories(
        self,
        user_id: str,
        context: QueryContext
    ) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to the current context."""
        try:
            # Build search context for memory retrieval
            from .memory.context import MemoryContext
            
            memory_context = MemoryContext(
                current_query=context.current_query,
                table_names=context.table_names,
                column_names=context.column_names,
                query_intent=context.query_intent,
                referenced_entities=context.referenced_entities
            )
            
            # Search for contextually relevant memories
            relevant_memories = await self.memory_manager.search_contextual_memories(
                user_id=user_id,
                context=memory_context,
                limit=10
            )
            
            return relevant_memories
            
        except Exception as e:
            self.logger.warning("Failed to retrieve relevant memories",
                              user_id=user_id,
                              error=str(e))
            return []
    
    async def _resolve_context_ambiguities(
        self,
        context: QueryContext,
        memories: List[Dict[str, Any]],
        session_history: List[Any]
    ) -> QueryContext:
        """Resolve ambiguous references using memory and session history."""
        resolved_query = context.current_query
        ambiguities_found = []
        
        # Resolve pronoun references (this, that, it, etc.)
        pronoun_patterns = [
            (r'\bthis\b', 'current_entity'),
            (r'\bthat\b', 'previous_entity'),
            (r'\bit\b', 'referenced_entity'),
            (r'\bthese\b', 'current_entities'),
            (r'\bthose\b', 'previous_entities'),
        ]
        
        for pattern, reference_type in pronoun_patterns:
            if re.search(pattern, resolved_query, re.IGNORECASE):
                # Try to resolve from session history
                resolution = self._resolve_from_session_history(
                    reference_type, session_history
                )
                if resolution:
                    resolved_query = re.sub(
                        pattern, resolution, resolved_query, flags=re.IGNORECASE
                    )
                else:
                    ambiguities_found.append(f"Unresolved reference: {reference_type}")
        
        # Resolve table/column ambiguities using memories
        for memory in memories:
            memory_content = memory.get('content', {})
            if isinstance(memory_content, dict):
                # Check for table mappings
                memory_tables = memory_content.get('tables_used', [])
                for table in memory_tables:
                    if table.lower() in resolved_query.lower():
                        # Table reference found in memory - high confidence
                        if table not in context.table_names:
                            context.table_names.append(table)
        
        # Update context with resolved query
        context.current_query = resolved_query
        
        return context
    
    async def _apply_memory_enhancements(
        self,
        context: QueryContext,
        memories: List[Dict[str, Any]]
    ) -> EnhancedQueryContext:
        """Apply memory-based enhancements to the query context."""
        enhanced_context = EnhancedQueryContext(
            original_context=context,
            resolved_query=context.current_query
        )
        
        # Process each relevant memory
        for memory in memories:
            memory_content = memory.get('content', {})
            memory_metadata = memory.get('metadata', {})
            relevance_score = memory.get('relevance_score', 0.0)
            
            if relevance_score < 0.1:  # Skip low-relevance memories
                continue
            
            # Extract enhancements from memory
            enhancement = {
                'memory_id': memory.get('id'),
                'memory_type': memory.get('memory_type', 'unknown'),
                'relevance_score': relevance_score,
                'enhancements': {}
            }
            
            if isinstance(memory_content, dict):
                # Table enhancements
                memory_tables = memory_content.get('tables_used', [])
                if memory_tables:
                    enhancement['enhancements']['suggested_tables'] = memory_tables
                    enhanced_context.resolved_tables.extend(memory_tables)
                
                # Query pattern enhancements
                if memory_content.get('sql'):
                    enhancement['enhancements']['similar_sql_pattern'] = memory_content['sql']
                
                # Intent confirmation
                if memory_content.get('query_type') == context.query_intent:
                    enhancement['enhancements']['intent_confirmation'] = True
            
            # Add enhancement if it provides value
            if enhancement['enhancements']:
                enhanced_context.memory_influences.append(enhancement)
                enhanced_context.enhancement_applied.append(
                    f"Applied {memory.get('memory_type', 'unknown')} memory enhancement"
                )
        
        # Deduplicate resolved elements
        enhanced_context.resolved_tables = list(set(enhanced_context.resolved_tables))
        
        return enhanced_context
    
    def _calculate_context_scores(self, context: EnhancedQueryContext) -> EnhancedQueryContext:
        """Calculate confidence and relevance scores for the enhanced context."""
        # Base confidence from query analysis
        base_confidence = 0.5
        
        # Boost confidence based on memory influences
        memory_boost = min(len(context.memory_influences) * 0.1, 0.3)
        
        # Boost confidence based on resolved elements
        resolution_boost = 0.0
        if context.resolved_tables:
            resolution_boost += 0.1
        if context.resolved_columns:
            resolution_boost += 0.1
        
        # Calculate final confidence
        context.confidence = min(base_confidence + memory_boost + resolution_boost, 1.0)
        
        # Calculate relevance score based on memory influences
        if context.memory_influences:
            relevance_scores = [m['relevance_score'] for m in context.memory_influences]
            context.relevance_score = sum(relevance_scores) / len(relevance_scores)
        else:
            context.relevance_score = 0.0
        
        return context
    
    def _resolve_from_session_history(
        self,
        reference_type: str,
        session_history: List[Any]
    ) -> Optional[str]:
        """Resolve references from session history."""
        if not session_history:
            return None
        
        # Simple resolution based on most recent queries
        recent_queries = session_history[-3:] if len(session_history) >= 3 else session_history
        
        for query_history in reversed(recent_queries):
            query_text = getattr(query_history, 'natural_language', '')
            
            # Extract potential entities from recent queries
            if reference_type in ['current_entity', 'referenced_entity']:
                # Look for table names or entities in recent queries
                entities = re.findall(r'\b(\w+)\s+(?:table|data|records)\b', query_text, re.IGNORECASE)
                if entities:
                    return entities[0]
            
            elif reference_type in ['previous_entity']:
                # Look for entities from earlier in the conversation
                entities = re.findall(r'\b(\w+)\s+(?:table|data|records)\b', query_text, re.IGNORECASE)
                if entities:
                    return entities[-1]  # Last mentioned entity
        
        return None
    
    async def resolve_ambiguous_query(
        self,
        query: str,
        user_id: str,
        possible_interpretations: List[str]
    ) -> str:
        """
        Resolve an ambiguous query by choosing the most likely interpretation.
        
        Args:
            query: Ambiguous query
            user_id: User identifier
            possible_interpretations: List of possible query interpretations
            
        Returns:
            Most likely query interpretation
        """
        try:
            if len(possible_interpretations) <= 1:
                return possible_interpretations[0] if possible_interpretations else query
            
            # Score each interpretation based on user's memory
            interpretation_scores = []
            
            for interpretation in possible_interpretations:
                # Create temporary context for scoring
                temp_context = QueryContext(
                    user_id=user_id,
                    session_id="temp",
                    current_query=interpretation
                )
                
                # Analyze and score
                analyzed_context = await self._analyze_query_context(temp_context)
                memories = await self._retrieve_relevant_memories(user_id, analyzed_context)
                
                # Calculate score based on memory relevance
                score = 0.0
                if memories:
                    relevance_scores = [m.get('relevance_score', 0.0) for m in memories]
                    score = sum(relevance_scores) / len(relevance_scores)
                
                interpretation_scores.append((interpretation, score))
            
            # Return interpretation with highest score
            best_interpretation = max(interpretation_scores, key=lambda x: x[1])
            
            self.logger.info("Ambiguous query resolved",
                           user_id=user_id,
                           original_query=query[:50],
                           resolved_query=best_interpretation[0][:50],
                           confidence_score=best_interpretation[1])
            
            return best_interpretation[0]
            
        except Exception as e:
            self.logger.error("Failed to resolve ambiguous query",
                            user_id=user_id,
                            error=str(e))
            # Return first interpretation as fallback
            return possible_interpretations[0] if possible_interpretations else query
