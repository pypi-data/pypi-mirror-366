"""
AI-Powered SQL Explainer and Teaching Assistant.

This revolutionary module provides intelligent SQL explanation and teaching capabilities:
- Step-by-step query breakdown
- Interactive learning modes
- Personalized explanations based on user level
- Visual query execution flow
- Common mistake identification
- Best practice suggestions
- Real-time learning assistance
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..types import SQLQuery, UserID, SchemaInfo, SQLDialect
from ..exceptions import ExplanationError, Text2SQLLTMError

logger = logging.getLogger(__name__)


class ExplanationLevel(str, Enum):
    """Explanation complexity levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ADAPTIVE = "adaptive"


class TeachingMode(str, Enum):
    """Teaching interaction modes."""
    EXPLANATION = "explanation"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    GUIDED_PRACTICE = "guided_practice"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"


class ConceptDifficulty(str, Enum):
    """SQL concept difficulty levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class SQLConcept:
    """SQL concept with learning metadata."""
    name: str
    category: str
    difficulty: ConceptDifficulty
    description: str
    examples: List[str]
    prerequisites: List[str]
    common_mistakes: List[str]
    best_practices: List[str]


@dataclass
class ExplanationStep:
    """Individual step in query explanation."""
    step_number: int
    operation: str
    description: str
    sql_fragment: str
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    concepts_used: List[str] = None
    tips: List[str] = None


@dataclass
class QueryExplanation:
    """Comprehensive query explanation."""
    query: str
    overall_purpose: str
    complexity_level: ConceptDifficulty
    execution_steps: List[ExplanationStep]
    concepts_covered: List[SQLConcept]
    performance_notes: List[str]
    alternative_approaches: List[str]
    learning_objectives: List[str]
    estimated_learning_time: int  # minutes
    metadata: Dict[str, Any]


@dataclass
class LearningProgress:
    """User's learning progress tracking."""
    user_id: UserID
    concepts_mastered: Dict[str, float]  # concept -> mastery level (0-1)
    queries_explained: int
    total_learning_time: int  # minutes
    preferred_explanation_level: ExplanationLevel
    learning_goals: List[str]
    weak_areas: List[str]
    last_activity: datetime


class SQLExplainer:
    """
    AI-powered SQL explainer and teaching assistant.
    
    This class provides comprehensive SQL education capabilities:
    - Intelligent query explanation
    - Adaptive learning paths
    - Interactive teaching modes
    - Progress tracking
    - Personalized content delivery
    """
    
    def __init__(
        self,
        llm_provider: Optional[Any] = None,
        enable_interactive_mode: bool = True,
        enable_progress_tracking: bool = True
    ):
        self.llm_provider = llm_provider
        self.enable_interactive_mode = enable_interactive_mode
        self.enable_progress_tracking = enable_progress_tracking
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # SQL concepts database
        self.sql_concepts = self._load_sql_concepts()
        
        # User progress tracking
        self.user_progress: Dict[UserID, LearningProgress] = {}
        
        # Teaching strategies
        self.teaching_strategies = self._load_teaching_strategies()
        
        # Metrics
        self._metrics = {
            "explanations_generated": 0,
            "interactive_sessions": 0,
            "concepts_taught": 0,
            "user_progress_updates": 0,
            "average_explanation_time": 0.0
        }
    
    async def explain_query(
        self,
        sql_query: SQLQuery,
        user_id: Optional[UserID] = None,
        explanation_level: ExplanationLevel = ExplanationLevel.ADAPTIVE,
        teaching_mode: TeachingMode = TeachingMode.EXPLANATION,
        schema: Optional[SchemaInfo] = None,
        include_alternatives: bool = True
    ) -> QueryExplanation:
        """
        Generate comprehensive explanation for SQL query.
        
        Args:
            sql_query: SQL query to explain
            user_id: Optional user ID for personalization
            explanation_level: Level of explanation detail
            teaching_mode: Teaching interaction mode
            schema: Optional schema for context
            include_alternatives: Whether to include alternative approaches
            
        Returns:
            Comprehensive query explanation
        """
        start_time = datetime.utcnow()
        
        try:
            # Get or create user progress
            user_progress = None
            if user_id and self.enable_progress_tracking:
                user_progress = await self._get_user_progress(user_id)
                
                # Adapt explanation level based on user progress
                if explanation_level == ExplanationLevel.ADAPTIVE:
                    explanation_level = self._determine_adaptive_level(user_progress)
            
            # Analyze query structure
            query_analysis = await self._analyze_query_structure(sql_query, schema)
            
            # Determine concepts covered
            concepts_covered = await self._identify_concepts(sql_query, query_analysis)
            
            # Generate execution steps
            execution_steps = await self._generate_execution_steps(
                sql_query, query_analysis, explanation_level, schema
            )
            
            # Create overall explanation
            overall_purpose = await self._generate_overall_purpose(sql_query, query_analysis)
            
            # Generate performance notes
            performance_notes = await self._generate_performance_notes(sql_query, schema)
            
            # Generate alternatives if requested
            alternatives = []
            if include_alternatives:
                alternatives = await self._generate_alternatives(sql_query, query_analysis)
            
            # Determine learning objectives
            learning_objectives = self._determine_learning_objectives(concepts_covered, user_progress)
            
            # Estimate learning time
            learning_time = self._estimate_learning_time(concepts_covered, explanation_level)
            
            # Create explanation
            explanation = QueryExplanation(
                query=sql_query,
                overall_purpose=overall_purpose,
                complexity_level=self._determine_complexity_level(concepts_covered),
                execution_steps=execution_steps,
                concepts_covered=concepts_covered,
                performance_notes=performance_notes,
                alternative_approaches=alternatives,
                learning_objectives=learning_objectives,
                estimated_learning_time=learning_time,
                metadata={
                    "explanation_level": explanation_level.value,
                    "teaching_mode": teaching_mode.value,
                    "user_id": user_id,
                    "schema_available": schema is not None,
                    "generation_time_ms": 0  # Will be calculated
                }
            )
            
            # Update user progress
            if user_progress:
                await self._update_user_progress(user_progress, concepts_covered)
            
            # Calculate generation time
            generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            explanation.metadata["generation_time_ms"] = generation_time
            
            # Update metrics
            self._metrics["explanations_generated"] += 1
            self._update_average_time(generation_time)
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Query explanation failed: {str(e)}")
            raise ExplanationError(f"Query explanation failed: {str(e)}") from e
    
    async def start_interactive_session(
        self,
        user_id: UserID,
        learning_goal: str,
        session_type: TeachingMode = TeachingMode.INTERACTIVE
    ) -> Dict[str, Any]:
        """
        Start an interactive learning session.
        
        Args:
            user_id: User identifier
            learning_goal: What the user wants to learn
            session_type: Type of interactive session
            
        Returns:
            Session configuration and first interaction
        """
        try:
            if not self.enable_interactive_mode:
                raise ExplanationError("Interactive mode is disabled")
            
            # Get user progress
            user_progress = await self._get_user_progress(user_id)
            
            # Create session plan
            session_plan = await self._create_session_plan(
                user_progress, learning_goal, session_type
            )
            
            # Generate first interaction
            first_interaction = await self._generate_first_interaction(session_plan)
            
            # Update metrics
            self._metrics["interactive_sessions"] += 1
            
            return {
                "session_id": f"session_{datetime.utcnow().timestamp()}",
                "session_plan": session_plan,
                "current_interaction": first_interaction,
                "progress": {
                    "current_step": 1,
                    "total_steps": len(session_plan.get("steps", [])),
                    "estimated_time": session_plan.get("estimated_time", 30)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Interactive session start failed: {str(e)}")
            raise ExplanationError(f"Interactive session start failed: {str(e)}") from e
    
    async def _analyze_query_structure(
        self,
        sql_query: str,
        schema: Optional[SchemaInfo]
    ) -> Dict[str, Any]:
        """Analyze SQL query structure and components."""
        analysis = {
            "query_type": "SELECT",  # Would be detected
            "tables_used": [],
            "columns_used": [],
            "joins": [],
            "where_conditions": [],
            "aggregations": [],
            "subqueries": [],
            "complexity_score": 0
        }
        
        # Basic query type detection
        query_upper = sql_query.upper().strip()
        if query_upper.startswith("SELECT"):
            analysis["query_type"] = "SELECT"
        elif query_upper.startswith("INSERT"):
            analysis["query_type"] = "INSERT"
        elif query_upper.startswith("UPDATE"):
            analysis["query_type"] = "UPDATE"
        elif query_upper.startswith("DELETE"):
            analysis["query_type"] = "DELETE"
        
        # Extract components (simplified - would use proper SQL parser)
        import re
        
        # Find tables
        table_pattern = r'(?:FROM|JOIN|UPDATE|INTO)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        tables = re.findall(table_pattern, sql_query, re.IGNORECASE)
        analysis["tables_used"] = list(set(tables))
        
        # Find joins
        if "JOIN" in query_upper:
            analysis["joins"] = ["INNER JOIN"]  # Simplified
        
        # Find aggregations
        agg_functions = ["COUNT", "SUM", "AVG", "MAX", "MIN"]
        for func in agg_functions:
            if func in query_upper:
                analysis["aggregations"].append(func)
        
        # Calculate complexity
        complexity = 0
        complexity += len(analysis["tables_used"])
        complexity += len(analysis["joins"]) * 2
        complexity += len(analysis["aggregations"])
        if "GROUP BY" in query_upper:
            complexity += 2
        if "ORDER BY" in query_upper:
            complexity += 1
        if "(" in sql_query:  # Subqueries
            complexity += 3
        
        analysis["complexity_score"] = complexity
        
        return analysis
    
    async def _identify_concepts(
        self,
        sql_query: str,
        query_analysis: Dict[str, Any]
    ) -> List[SQLConcept]:
        """Identify SQL concepts used in the query."""
        concepts = []
        
        # Map query components to concepts
        concept_mapping = {
            "SELECT": "basic_select",
            "WHERE": "filtering",
            "JOIN": "table_joins",
            "GROUP BY": "grouping",
            "ORDER BY": "sorting",
            "COUNT": "aggregate_functions",
            "SUM": "aggregate_functions",
            "AVG": "aggregate_functions"
        }
        
        query_upper = sql_query.upper()
        
        for keyword, concept_name in concept_mapping.items():
            if keyword in query_upper and concept_name in self.sql_concepts:
                concepts.append(self.sql_concepts[concept_name])
        
        # Remove duplicates
        seen_names = set()
        unique_concepts = []
        for concept in concepts:
            if concept.name not in seen_names:
                unique_concepts.append(concept)
                seen_names.add(concept.name)
        
        return unique_concepts
    
    async def _generate_execution_steps(
        self,
        sql_query: str,
        query_analysis: Dict[str, Any],
        explanation_level: ExplanationLevel,
        schema: Optional[SchemaInfo]
    ) -> List[ExplanationStep]:
        """Generate step-by-step execution explanation."""
        steps = []
        step_number = 1
        
        # FROM clause
        if query_analysis["tables_used"]:
            steps.append(ExplanationStep(
                step_number=step_number,
                operation="FROM",
                description=f"Start by accessing the {', '.join(query_analysis['tables_used'])} table(s)",
                sql_fragment=f"FROM {', '.join(query_analysis['tables_used'])}",
                concepts_used=["table_access"],
                tips=["The FROM clause specifies which table(s) to query"]
            ))
            step_number += 1
        
        # JOIN operations
        for join in query_analysis["joins"]:
            steps.append(ExplanationStep(
                step_number=step_number,
                operation="JOIN",
                description=f"Combine tables using {join}",
                sql_fragment="JOIN ...",
                concepts_used=["table_joins"],
                tips=["JOINs combine data from multiple tables based on related columns"]
            ))
            step_number += 1
        
        # WHERE clause
        if "WHERE" in sql_query.upper():
            steps.append(ExplanationStep(
                step_number=step_number,
                operation="WHERE",
                description="Filter rows based on specified conditions",
                sql_fragment="WHERE ...",
                concepts_used=["filtering"],
                tips=["WHERE clause reduces the result set to only matching rows"]
            ))
            step_number += 1
        
        # GROUP BY
        if "GROUP BY" in sql_query.upper():
            steps.append(ExplanationStep(
                step_number=step_number,
                operation="GROUP BY",
                description="Group rows with the same values in specified columns",
                sql_fragment="GROUP BY ...",
                concepts_used=["grouping"],
                tips=["GROUP BY is used with aggregate functions to summarize data"]
            ))
            step_number += 1
        
        # SELECT clause
        steps.append(ExplanationStep(
            step_number=step_number,
            operation="SELECT",
            description="Choose which columns to include in the final result",
            sql_fragment="SELECT ...",
            concepts_used=["column_selection"],
            tips=["SELECT determines what data appears in your query results"]
        ))
        step_number += 1
        
        # ORDER BY
        if "ORDER BY" in sql_query.upper():
            steps.append(ExplanationStep(
                step_number=step_number,
                operation="ORDER BY",
                description="Sort the final results",
                sql_fragment="ORDER BY ...",
                concepts_used=["sorting"],
                tips=["ORDER BY controls how results are arranged"]
            ))
        
        return steps
    
    async def _generate_overall_purpose(
        self,
        sql_query: str,
        query_analysis: Dict[str, Any]
    ) -> str:
        """Generate overall purpose description for the query."""
        query_type = query_analysis["query_type"]
        tables = query_analysis["tables_used"]
        
        if query_type == "SELECT":
            if query_analysis["aggregations"]:
                return f"This query calculates summary statistics from the {', '.join(tables)} table(s)"
            elif query_analysis["joins"]:
                return f"This query combines and retrieves data from multiple tables: {', '.join(tables)}"
            else:
                return f"This query retrieves data from the {', '.join(tables)} table(s)"
        elif query_type == "INSERT":
            return f"This query adds new data to the {', '.join(tables)} table"
        elif query_type == "UPDATE":
            return f"This query modifies existing data in the {', '.join(tables)} table"
        elif query_type == "DELETE":
            return f"This query removes data from the {', '.join(tables)} table"
        
        return "This query performs a database operation"
    
    async def _generate_performance_notes(
        self,
        sql_query: str,
        schema: Optional[SchemaInfo]
    ) -> List[str]:
        """Generate performance-related notes."""
        notes = []
        
        query_upper = sql_query.upper()
        
        if "SELECT *" in query_upper:
            notes.append("Consider selecting only needed columns instead of using SELECT * for better performance")
        
        if "LIKE '%'" in query_upper:
            notes.append("Leading wildcards in LIKE patterns can prevent index usage")
        
        if "ORDER BY" in query_upper and "LIMIT" not in query_upper:
            notes.append("Consider adding LIMIT if you don't need all sorted results")
        
        return notes
    
    async def _generate_alternatives(
        self,
        sql_query: str,
        query_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate alternative query approaches."""
        alternatives = []
        
        # Example alternatives based on query structure
        if query_analysis["joins"]:
            alternatives.append("Could use subqueries instead of JOINs for some scenarios")
        
        if query_analysis["aggregations"]:
            alternatives.append("Consider using window functions for running totals or rankings")
        
        return alternatives
    
    def _load_sql_concepts(self) -> Dict[str, SQLConcept]:
        """Load SQL concepts database."""
        concepts = {
            "basic_select": SQLConcept(
                name="Basic SELECT",
                category="fundamentals",
                difficulty=ConceptDifficulty.BASIC,
                description="Retrieving data from database tables",
                examples=["SELECT * FROM users", "SELECT name, email FROM users"],
                prerequisites=[],
                common_mistakes=["Forgetting FROM clause", "Using SELECT * unnecessarily"],
                best_practices=["Select only needed columns", "Use meaningful column aliases"]
            ),
            "filtering": SQLConcept(
                name="WHERE Clause",
                category="fundamentals",
                difficulty=ConceptDifficulty.BASIC,
                description="Filtering rows based on conditions",
                examples=["WHERE age > 18", "WHERE name LIKE 'John%'"],
                prerequisites=["basic_select"],
                common_mistakes=["Using = instead of LIKE for pattern matching"],
                best_practices=["Use indexes on filtered columns", "Be specific with conditions"]
            ),
            "table_joins": SQLConcept(
                name="Table JOINs",
                category="intermediate",
                difficulty=ConceptDifficulty.INTERMEDIATE,
                description="Combining data from multiple tables",
                examples=["INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
                prerequisites=["basic_select", "filtering"],
                common_mistakes=["Forgetting JOIN conditions", "Using wrong JOIN type"],
                best_practices=["Always specify JOIN conditions", "Use table aliases"]
            ),
            "aggregate_functions": SQLConcept(
                name="Aggregate Functions",
                category="intermediate",
                difficulty=ConceptDifficulty.INTERMEDIATE,
                description="Calculating summary values",
                examples=["COUNT(*)", "SUM(amount)", "AVG(score)"],
                prerequisites=["basic_select"],
                common_mistakes=["Mixing aggregates with non-grouped columns"],
                best_practices=["Use GROUP BY with aggregates", "Handle NULL values"]
            )
        }
        
        return concepts
    
    def _load_teaching_strategies(self) -> Dict[str, Any]:
        """Load teaching strategies for different modes."""
        return {
            "beginner": {
                "explanation_style": "step_by_step",
                "include_examples": True,
                "include_analogies": True,
                "vocabulary_level": "simple"
            },
            "intermediate": {
                "explanation_style": "conceptual",
                "include_examples": True,
                "include_best_practices": True,
                "vocabulary_level": "technical"
            },
            "advanced": {
                "explanation_style": "concise",
                "include_performance_tips": True,
                "include_alternatives": True,
                "vocabulary_level": "expert"
            }
        }
    
    async def _get_user_progress(self, user_id: UserID) -> LearningProgress:
        """Get or create user learning progress."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = LearningProgress(
                user_id=user_id,
                concepts_mastered={},
                queries_explained=0,
                total_learning_time=0,
                preferred_explanation_level=ExplanationLevel.BEGINNER,
                learning_goals=[],
                weak_areas=[],
                last_activity=datetime.utcnow()
            )
        
        return self.user_progress[user_id]
    
    def _determine_adaptive_level(self, user_progress: LearningProgress) -> ExplanationLevel:
        """Determine appropriate explanation level based on user progress."""
        mastery_scores = list(user_progress.concepts_mastered.values())
        
        if not mastery_scores:
            return ExplanationLevel.BEGINNER
        
        average_mastery = sum(mastery_scores) / len(mastery_scores)
        
        if average_mastery < 0.3:
            return ExplanationLevel.BEGINNER
        elif average_mastery < 0.6:
            return ExplanationLevel.INTERMEDIATE
        elif average_mastery < 0.8:
            return ExplanationLevel.ADVANCED
        else:
            return ExplanationLevel.EXPERT
    
    def _determine_complexity_level(self, concepts: List[SQLConcept]) -> ConceptDifficulty:
        """Determine overall complexity level of concepts."""
        if not concepts:
            return ConceptDifficulty.BASIC
        
        max_difficulty = max(concept.difficulty for concept in concepts)
        return max_difficulty
    
    def _determine_learning_objectives(
        self,
        concepts: List[SQLConcept],
        user_progress: Optional[LearningProgress]
    ) -> List[str]:
        """Determine learning objectives for the explanation."""
        objectives = []
        
        for concept in concepts:
            if not user_progress or concept.name not in user_progress.concepts_mastered:
                objectives.append(f"Understand {concept.name}")
            elif user_progress.concepts_mastered[concept.name] < 0.8:
                objectives.append(f"Master {concept.name}")
        
        return objectives
    
    def _estimate_learning_time(
        self,
        concepts: List[SQLConcept],
        explanation_level: ExplanationLevel
    ) -> int:
        """Estimate learning time in minutes."""
        base_time = len(concepts) * 5  # 5 minutes per concept
        
        # Adjust based on explanation level
        level_multipliers = {
            ExplanationLevel.BEGINNER: 1.5,
            ExplanationLevel.INTERMEDIATE: 1.0,
            ExplanationLevel.ADVANCED: 0.8,
            ExplanationLevel.EXPERT: 0.6
        }
        
        multiplier = level_multipliers.get(explanation_level, 1.0)
        return int(base_time * multiplier)
    
    async def _update_user_progress(
        self,
        user_progress: LearningProgress,
        concepts: List[SQLConcept]
    ) -> None:
        """Update user progress based on explained concepts."""
        for concept in concepts:
            current_mastery = user_progress.concepts_mastered.get(concept.name, 0.0)
            # Increase mastery slightly with each explanation
            new_mastery = min(current_mastery + 0.1, 1.0)
            user_progress.concepts_mastered[concept.name] = new_mastery
        
        user_progress.queries_explained += 1
        user_progress.last_activity = datetime.utcnow()
        
        self._metrics["user_progress_updates"] += 1
    
    async def _create_session_plan(
        self,
        user_progress: LearningProgress,
        learning_goal: str,
        session_type: TeachingMode
    ) -> Dict[str, Any]:
        """Create interactive session plan."""
        return {
            "goal": learning_goal,
            "type": session_type.value,
            "steps": [
                {"step": 1, "activity": "Introduction", "duration": 5},
                {"step": 2, "activity": "Concept explanation", "duration": 15},
                {"step": 3, "activity": "Practice", "duration": 10},
                {"step": 4, "activity": "Review", "duration": 5}
            ],
            "estimated_time": 35
        }
    
    async def _generate_first_interaction(self, session_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate first interaction for session."""
        return {
            "type": "introduction",
            "message": f"Welcome! Let's learn about {session_plan['goal']}. Are you ready to start?",
            "options": ["Yes, let's begin!", "I need more information first"],
            "expected_response": "choice"
        }
    
    def _update_average_time(self, new_time: int) -> None:
        """Update average explanation time metric."""
        current_avg = self._metrics["average_explanation_time"]
        total_explanations = self._metrics["explanations_generated"]
        
        if total_explanations == 1:
            self._metrics["average_explanation_time"] = new_time
        else:
            self._metrics["average_explanation_time"] = (
                (current_avg * (total_explanations - 1) + new_time) / total_explanations
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get explainer metrics."""
        return self._metrics.copy()
    
    async def get_user_progress_summary(self, user_id: UserID) -> Dict[str, Any]:
        """Get user progress summary."""
        if user_id not in self.user_progress:
            return {"error": "User not found"}
        
        progress = self.user_progress[user_id]
        
        return {
            "user_id": user_id,
            "queries_explained": progress.queries_explained,
            "concepts_mastered": len([m for m in progress.concepts_mastered.values() if m >= 0.8]),
            "total_concepts": len(progress.concepts_mastered),
            "average_mastery": sum(progress.concepts_mastered.values()) / len(progress.concepts_mastered) if progress.concepts_mastered else 0,
            "learning_time_hours": progress.total_learning_time / 60,
            "current_level": progress.preferred_explanation_level.value,
            "learning_goals": progress.learning_goals,
            "weak_areas": progress.weak_areas,
            "last_activity": progress.last_activity.isoformat()
        }
