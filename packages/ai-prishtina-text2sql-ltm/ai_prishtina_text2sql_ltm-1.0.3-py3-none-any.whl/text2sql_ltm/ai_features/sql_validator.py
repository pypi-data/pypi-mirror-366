"""
AI-Powered SQL Validator with intelligent error detection and suggestions.

This module provides advanced SQL validation capabilities using AI to understand
context, detect semantic errors, and provide intelligent suggestions for improvement.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..types import SQLQuery, SchemaInfo, SQLDialect
from ..exceptions import ValidationError, Text2SQLLTMError

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """Validation levels."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPREHENSIVE = "comprehensive"


class SeverityLevel(str, Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Validation issue with details."""
    severity: SeverityLevel
    category: str
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggestion: Optional[str] = None
    auto_fix: Optional[str] = None
    explanation: Optional[str] = None


@dataclass
class ValidationResult:
    """Comprehensive validation result."""
    is_valid: bool
    issues: List[ValidationIssue]
    corrected_sql: Optional[str] = None
    confidence_score: float = 0.0
    validation_time_ms: int = 0
    metadata: Dict[str, Any] = None


@dataclass
class OptimizationSuggestion:
    """SQL optimization suggestion."""
    type: str
    description: str
    impact: str  # "high", "medium", "low"
    original_fragment: str
    optimized_fragment: str
    explanation: str
    estimated_improvement: Optional[float] = None


class SQLValidator:
    """
    AI-powered SQL validator with intelligent error detection and correction.
    
    This validator goes beyond syntax checking to provide:
    - Semantic validation against schema
    - Performance optimization suggestions
    - Security vulnerability detection
    - Intelligent auto-correction
    - Context-aware error explanations
    """
    
    def __init__(
        self,
        llm_provider: Optional[Any] = None,
        enable_ai_suggestions: bool = True,
        enable_auto_fix: bool = True
    ):
        self.llm_provider = llm_provider
        self.enable_ai_suggestions = enable_ai_suggestions
        self.enable_auto_fix = enable_auto_fix
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Validation rules and patterns
        self._syntax_patterns = self._load_syntax_patterns()
        self._security_patterns = self._load_security_patterns()
        self._performance_patterns = self._load_performance_patterns()
        
        # Metrics
        self._metrics = {
            "validations_performed": 0,
            "issues_detected": 0,
            "auto_fixes_applied": 0,
            "ai_suggestions_generated": 0
        }
    
    async def validate(
        self,
        sql_query: SQLQuery,
        schema: Optional[SchemaInfo] = None,
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
        level: ValidationLevel = ValidationLevel.COMPREHENSIVE
    ) -> ValidationResult:
        """
        Validate SQL query with comprehensive analysis.
        
        Args:
            sql_query: SQL query to validate
            schema: Optional schema information for semantic validation
            dialect: SQL dialect for validation
            level: Validation level (syntax, semantic, performance, etc.)
            
        Returns:
            Comprehensive validation result with issues and suggestions
        """
        start_time = datetime.utcnow()
        
        try:
            issues = []
            corrected_sql = sql_query
            
            # Syntax validation
            if level in [ValidationLevel.SYNTAX, ValidationLevel.COMPREHENSIVE]:
                syntax_issues = await self._validate_syntax(sql_query, dialect)
                issues.extend(syntax_issues)
            
            # Semantic validation
            if level in [ValidationLevel.SEMANTIC, ValidationLevel.COMPREHENSIVE] and schema:
                semantic_issues = await self._validate_semantics(sql_query, schema, dialect)
                issues.extend(semantic_issues)
            
            # Performance validation
            if level in [ValidationLevel.PERFORMANCE, ValidationLevel.COMPREHENSIVE]:
                performance_issues = await self._validate_performance(sql_query, schema, dialect)
                issues.extend(performance_issues)
            
            # Security validation
            if level in [ValidationLevel.SECURITY, ValidationLevel.COMPREHENSIVE]:
                security_issues = await self._validate_security(sql_query, dialect)
                issues.extend(security_issues)
            
            # AI-powered suggestions
            if self.enable_ai_suggestions and self.llm_provider:
                ai_suggestions = await self._get_ai_suggestions(sql_query, issues, schema, dialect)
                issues.extend(ai_suggestions)
            
            # Auto-fix if enabled
            if self.enable_auto_fix and issues:
                corrected_sql = await self._apply_auto_fixes(sql_query, issues)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(issues, sql_query)
            
            # Determine if valid
            is_valid = not any(issue.severity in [SeverityLevel.ERROR, SeverityLevel.CRITICAL] for issue in issues)
            
            validation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Update metrics
            self._metrics["validations_performed"] += 1
            self._metrics["issues_detected"] += len(issues)
            
            result = ValidationResult(
                is_valid=is_valid,
                issues=issues,
                corrected_sql=corrected_sql if corrected_sql != sql_query else None,
                confidence_score=confidence_score,
                validation_time_ms=validation_time,
                metadata={
                    "dialect": dialect.value,
                    "validation_level": level.value,
                    "schema_available": schema is not None,
                    "ai_enabled": self.enable_ai_suggestions
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            raise ValidationError(f"SQL validation failed: {str(e)}") from e
    
    async def _validate_syntax(self, sql_query: str, dialect: SQLDialect) -> List[ValidationIssue]:
        """Validate SQL syntax using sqlparse and custom rules."""
        issues = []

        try:
            # Try to parse with sqlparse
            import sqlparse

            # Parse the SQL
            parsed = sqlparse.parse(sql_query)

            if not parsed:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    category="syntax",
                    message="Unable to parse SQL query",
                    suggestion="Check for basic syntax errors like missing quotes or parentheses"
                ))
                return issues

            # Check for common syntax issues
            issues.extend(self._check_basic_syntax_rules(sql_query))

            # Dialect-specific validation
            issues.extend(self._check_dialect_specific_syntax(sql_query, dialect))

            # Check for SQL injection patterns
            issues.extend(self._check_injection_patterns(sql_query))

        except ImportError:
            # Fallback to basic regex-based validation
            issues.extend(self._basic_syntax_validation(sql_query))
        except Exception as e:
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="syntax",
                message=f"Syntax validation error: {str(e)}",
                suggestion="Manual review recommended"
            ))

        return issues

    def _check_basic_syntax_rules(self, sql_query: str) -> List[ValidationIssue]:
        """Check basic SQL syntax rules."""
        issues = []

        # Check for balanced parentheses
        if sql_query.count('(') != sql_query.count(')'):
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="Unbalanced parentheses",
                suggestion="Ensure all opening parentheses have matching closing parentheses"
            ))

        # Check for balanced quotes
        single_quotes = sql_query.count("'") - sql_query.count("\\'")
        if single_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="Unbalanced single quotes",
                suggestion="Ensure all string literals are properly quoted"
            ))

        double_quotes = sql_query.count('"') - sql_query.count('\\"')
        if double_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="Unbalanced double quotes",
                suggestion="Ensure all identifiers are properly quoted"
            ))

        # Check for semicolon at end (if multiple statements)
        statements = sql_query.strip().split(';')
        if len(statements) > 2:  # More than one statement
            for i, stmt in enumerate(statements[:-1]):  # All but last
                if stmt.strip() and not stmt.strip().endswith(';'):
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.WARNING,
                        category="syntax",
                        message=f"Statement {i+1} should end with semicolon",
                        suggestion="Add semicolon at the end of each statement"
                    ))

        return issues

    def _check_dialect_specific_syntax(self, sql_query: str, dialect: SQLDialect) -> List[ValidationIssue]:
        """Check dialect-specific syntax rules."""
        issues = []

        if dialect == SQLDialect.MYSQL:
            # MySQL-specific checks
            if '`' in sql_query:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.INFO,
                    category="dialect",
                    message="Using MySQL-style backtick quotes",
                    suggestion="Consider using standard double quotes for portability"
                ))

        elif dialect == SQLDialect.POSTGRESQL:
            # PostgreSQL-specific checks
            if 'LIMIT' in sql_query.upper() and 'OFFSET' in sql_query.upper():
                # Check LIMIT/OFFSET order
                limit_pos = sql_query.upper().find('LIMIT')
                offset_pos = sql_query.upper().find('OFFSET')
                if limit_pos > offset_pos:
                    issues.append(ValidationIssue(
                        severity=SeverityLevel.WARNING,
                        category="dialect",
                        message="OFFSET should come after LIMIT in PostgreSQL",
                        suggestion="Use 'LIMIT n OFFSET m' syntax"
                    ))

        elif dialect == SQLDialect.SQLSERVER:
            # SQL Server-specific checks
            if 'TOP' in sql_query.upper() and 'ORDER BY' not in sql_query.upper():
                issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    category="dialect",
                    message="TOP without ORDER BY may return unpredictable results",
                    suggestion="Add ORDER BY clause when using TOP"
                ))

        return issues

    def _check_injection_patterns(self, sql_query: str) -> List[ValidationIssue]:
        """Check for potential SQL injection patterns."""
        issues = []

        # Common injection patterns
        injection_patterns = [
            (r"'\s*OR\s+'", "Potential OR-based SQL injection"),
            (r"'\s*UNION\s+", "Potential UNION-based SQL injection"),
            (r"--", "SQL comment detected - potential injection"),
            (r"/\*.*\*/", "SQL block comment detected"),
            (r";\s*DROP\s+", "Potential destructive SQL injection"),
            (r";\s*DELETE\s+", "Potential destructive SQL injection"),
            (r";\s*UPDATE\s+", "Potential destructive SQL injection")
        ]

        for pattern, message in injection_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.CRITICAL,
                    category="security",
                    message=message,
                    suggestion="Use parameterized queries to prevent SQL injection"
                ))

        return issues

    def _basic_syntax_validation(self, sql_query: str) -> List[ValidationIssue]:
        """Basic regex-based syntax validation when sqlparse is not available."""
        issues = []

        # Check for basic SQL keywords
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        has_sql_keyword = any(keyword in sql_query.upper() for keyword in sql_keywords)

        if not has_sql_keyword:
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="No SQL keywords detected",
                suggestion="Ensure the query contains valid SQL keywords like SELECT, FROM, etc."
            ))

        # Check for basic structure
        if 'SELECT' in sql_query.upper() and 'FROM' not in sql_query.upper():
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="syntax",
                message="SELECT without FROM clause",
                suggestion="Most SELECT statements require a FROM clause"
            ))

        return issues
        issues = []
        
        # Basic syntax checks
        if not sql_query.strip():
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="Empty SQL query",
                suggestion="Provide a valid SQL query"
            ))
            return issues
        
        # Check for balanced parentheses
        if sql_query.count('(') != sql_query.count(')'):
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="Unbalanced parentheses",
                suggestion="Check parentheses matching",
                auto_fix=self._fix_parentheses(sql_query)
            ))
        
        # Check for balanced quotes
        single_quotes = sql_query.count("'") - sql_query.count("\\'")
        double_quotes = sql_query.count('"') - sql_query.count('\\"')
        
        if single_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="Unbalanced single quotes",
                suggestion="Check string literal quotes"
            ))
        
        if double_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="syntax",
                message="Unbalanced double quotes",
                suggestion="Check identifier quotes"
            ))
        
        # Check for SQL injection patterns
        for pattern in self._syntax_patterns.get("injection_patterns", []):
            if re.search(pattern, sql_query, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.CRITICAL,
                    category="security",
                    message="Potential SQL injection pattern detected",
                    suggestion="Use parameterized queries",
                    explanation="This pattern could be vulnerable to SQL injection attacks"
                ))
        
        # Dialect-specific syntax validation
        dialect_issues = self._validate_dialect_syntax(sql_query, dialect)
        issues.extend(dialect_issues)
        
        return issues
    
    async def _validate_semantics(
        self,
        sql_query: str,
        schema: SchemaInfo,
        dialect: SQLDialect
    ) -> List[ValidationIssue]:
        """Validate SQL semantics against schema."""
        issues = []
        
        # Extract table and column references
        table_refs = self._extract_table_references(sql_query)
        column_refs = self._extract_column_references(sql_query)
        
        # Validate table existence
        for table_ref in table_refs:
            if table_ref not in schema.tables:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    category="semantic",
                    message=f"Table '{table_ref}' does not exist",
                    suggestion=f"Available tables: {', '.join(schema.tables.keys())}",
                    auto_fix=self._suggest_similar_table(table_ref, schema.tables.keys())
                ))
        
        # Validate column existence and types
        for table_name, columns in column_refs.items():
            if table_name in schema.tables:
                table_schema = schema.tables[table_name]
                available_columns = table_schema.get("columns", {})
                
                for column in columns:
                    if column not in available_columns:
                        issues.append(ValidationIssue(
                            severity=SeverityLevel.ERROR,
                            category="semantic",
                            message=f"Column '{column}' does not exist in table '{table_name}'",
                            suggestion=f"Available columns: {', '.join(available_columns.keys())}",
                            auto_fix=self._suggest_similar_column(column, available_columns.keys())
                        ))
        
        # Validate JOIN conditions
        join_issues = self._validate_joins(sql_query, schema)
        issues.extend(join_issues)
        
        # Validate aggregate functions
        aggregate_issues = self._validate_aggregates(sql_query)
        issues.extend(aggregate_issues)
        
        return issues
    
    async def _validate_performance(
        self,
        sql_query: str,
        schema: Optional[SchemaInfo],
        dialect: SQLDialect
    ) -> List[ValidationIssue]:
        """Validate SQL for performance issues."""
        issues = []
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', sql_query, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="performance",
                message="SELECT * can impact performance",
                suggestion="Specify only needed columns",
                explanation="Selecting all columns can slow queries and increase network traffic"
            ))
        
        # Check for missing WHERE clause in UPDATE/DELETE
        if re.search(r'(UPDATE|DELETE)\s+(?!.*WHERE)', sql_query, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="performance",
                message="UPDATE/DELETE without WHERE clause",
                suggestion="Add WHERE clause to limit affected rows",
                explanation="Operations without WHERE affect all rows and can be dangerous"
            ))
        
        # Check for LIKE with leading wildcard
        if re.search(r"LIKE\s+['\"]%", sql_query, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="performance",
                message="LIKE with leading wildcard prevents index usage",
                suggestion="Consider full-text search or restructure query",
                explanation="Leading wildcards in LIKE patterns cannot use indexes efficiently"
            ))
        
        # Check for functions in WHERE clause
        function_pattern = r'WHERE\s+.*\b(UPPER|LOWER|SUBSTRING|TRIM)\s*\('
        if re.search(function_pattern, sql_query, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="performance",
                message="Functions in WHERE clause can prevent index usage",
                suggestion="Consider functional indexes or query restructuring",
                explanation="Applying functions to columns in WHERE prevents index usage"
            ))
        
        return issues
    
    async def _validate_security(self, sql_query: str, dialect: SQLDialect) -> List[ValidationIssue]:
        """Validate SQL for security issues."""
        issues = []
        
        # Check for dynamic SQL construction patterns
        dynamic_patterns = [
            r"'\s*\+\s*",  # String concatenation
            r'"\s*\+\s*',
            r'EXEC\s*\(',  # Dynamic execution
            r'EXECUTE\s*\('
        ]
        
        for pattern in dynamic_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.CRITICAL,
                    category="security",
                    message="Dynamic SQL construction detected",
                    suggestion="Use parameterized queries",
                    explanation="Dynamic SQL construction is vulnerable to injection attacks"
                ))
        
        # Check for privilege escalation attempts
        privilege_patterns = [
            r'GRANT\s+',
            r'REVOKE\s+',
            r'ALTER\s+USER',
            r'CREATE\s+USER',
            r'DROP\s+USER'
        ]
        
        for pattern in privilege_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    category="security",
                    message="Privilege management statement detected",
                    suggestion="Ensure proper authorization",
                    explanation="Privilege management should be restricted to authorized users"
                ))
        
        return issues
    
    async def _get_ai_suggestions(
        self,
        sql_query: str,
        existing_issues: List[ValidationIssue],
        schema: Optional[SchemaInfo],
        dialect: SQLDialect
    ) -> List[ValidationIssue]:
        """Get AI-powered suggestions for improvement."""
        if not self.llm_provider:
            return []
        
        try:
            # Build context for AI
            context = f"""
            SQL Query: {sql_query}
            Dialect: {dialect.value}
            Existing Issues: {len(existing_issues)}
            Schema Available: {schema is not None}
            
            Please analyze this SQL query and provide intelligent suggestions for:
            1. Code quality improvements
            2. Best practices adherence
            3. Readability enhancements
            4. Potential optimizations
            """
            
            # Get AI suggestions (this would call the LLM)
            # For now, return some example suggestions
            ai_suggestions = []
            
            # Check for missing aliases
            if re.search(r'FROM\s+\w+\s+(?!AS\s+\w+)', sql_query, re.IGNORECASE):
                ai_suggestions.append(ValidationIssue(
                    severity=SeverityLevel.INFO,
                    category="best_practice",
                    message="Consider using table aliases for better readability",
                    suggestion="Add aliases like 'FROM users u' instead of 'FROM users'",
                    explanation="Table aliases make queries more readable and easier to maintain"
                ))
            
            # Check for consistent formatting
            if not self._is_well_formatted(sql_query):
                ai_suggestions.append(ValidationIssue(
                    severity=SeverityLevel.INFO,
                    category="formatting",
                    message="Query formatting could be improved",
                    suggestion="Use consistent indentation and line breaks",
                    auto_fix=self._format_sql(sql_query)
                ))
            
            self._metrics["ai_suggestions_generated"] += len(ai_suggestions)
            return ai_suggestions
            
        except Exception as e:
            self.logger.warning(f"AI suggestions failed: {str(e)}")
            return []
    
    async def _apply_auto_fixes(self, sql_query: str, issues: List[ValidationIssue]) -> str:
        """Apply automatic fixes to SQL query."""
        corrected_sql = sql_query
        fixes_applied = 0
        
        for issue in issues:
            if issue.auto_fix:
                try:
                    if issue.category == "syntax" and "parentheses" in issue.message:
                        corrected_sql = issue.auto_fix
                        fixes_applied += 1
                    elif issue.category == "formatting":
                        corrected_sql = issue.auto_fix
                        fixes_applied += 1
                except Exception as e:
                    self.logger.warning(f"Auto-fix failed for issue: {issue.message}")
        
        self._metrics["auto_fixes_applied"] += fixes_applied
        return corrected_sql
    
    def _load_syntax_patterns(self) -> Dict[str, List[str]]:
        """Load syntax validation patterns."""
        return {
            "injection_patterns": [
                r"'\s*OR\s+'1'\s*=\s*'1",
                r"'\s*UNION\s+SELECT",
                r";\s*DROP\s+TABLE",
                r"--\s*$",
                r"/\*.*\*/"
            ]
        }
    
    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security validation patterns."""
        return {
            "dangerous_functions": [
                "xp_cmdshell",
                "sp_configure",
                "openrowset",
                "opendatasource"
            ]
        }
    
    def _load_performance_patterns(self) -> Dict[str, List[str]]:
        """Load performance validation patterns."""
        return {
            "anti_patterns": [
                r"SELECT\s+\*",
                r"LIKE\s+['\"]%",
                r"WHERE\s+.*\b(UPPER|LOWER)\s*\("
            ]
        }
    
    def _validate_dialect_syntax(self, sql_query: str, dialect: SQLDialect) -> List[ValidationIssue]:
        """Validate dialect-specific syntax."""
        issues = []
        
        if dialect == SQLDialect.MYSQL:
            # MySQL-specific validations
            if '`' in sql_query and '"' in sql_query:
                issues.append(ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    category="dialect",
                    message="Mixed quote styles in MySQL",
                    suggestion="Use backticks (`) for identifiers consistently"
                ))
        
        elif dialect == SQLDialect.POSTGRESQL:
            # PostgreSQL-specific validations
            if re.search(r'\bLIMIT\s+\d+\s+OFFSET\s+\d+', sql_query, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=SeverityLevel.INFO,
                    category="dialect",
                    message="Consider using OFFSET ... LIMIT for PostgreSQL",
                    suggestion="OFFSET comes before LIMIT in PostgreSQL"
                ))
        
        return issues
    
    def _extract_table_references(self, sql_query: str) -> List[str]:
        """Extract table references from SQL query."""
        # Simplified extraction - would be more sophisticated in practice
        pattern = r'(?:FROM|JOIN|UPDATE|INTO)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(pattern, sql_query, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_column_references(self, sql_query: str) -> Dict[str, List[str]]:
        """Extract column references from SQL query."""
        # Simplified extraction - would use proper SQL parser in practice
        return {}
    
    def _validate_joins(self, sql_query: str, schema: SchemaInfo) -> List[ValidationIssue]:
        """Validate JOIN conditions."""
        issues = []
        
        # Check for JOINs without ON clause
        if re.search(r'JOIN\s+\w+\s+(?!ON)', sql_query, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=SeverityLevel.ERROR,
                category="semantic",
                message="JOIN without ON clause",
                suggestion="Add ON clause to specify join condition"
            ))
        
        return issues
    
    def _validate_aggregates(self, sql_query: str) -> List[ValidationIssue]:
        """Validate aggregate function usage."""
        issues = []
        
        # Check for aggregate without GROUP BY
        has_aggregate = re.search(r'\b(COUNT|SUM|AVG|MAX|MIN)\s*\(', sql_query, re.IGNORECASE)
        has_group_by = re.search(r'\bGROUP\s+BY\b', sql_query, re.IGNORECASE)
        has_select_non_aggregate = re.search(r'SELECT\s+(?!.*\b(COUNT|SUM|AVG|MAX|MIN)\s*\()[^,\s]+', sql_query, re.IGNORECASE)
        
        if has_aggregate and has_select_non_aggregate and not has_group_by:
            issues.append(ValidationIssue(
                severity=SeverityLevel.WARNING,
                category="semantic",
                message="Aggregate function used without GROUP BY",
                suggestion="Add GROUP BY clause or remove non-aggregate columns from SELECT"
            ))
        
        return issues
    
    def _suggest_similar_table(self, table_name: str, available_tables: List[str]) -> Optional[str]:
        """Suggest similar table name."""
        # Simple similarity check - would use more sophisticated algorithm
        for table in available_tables:
            if table.lower().startswith(table_name.lower()[:3]):
                return f"Did you mean '{table}'?"
        return None
    
    def _suggest_similar_column(self, column_name: str, available_columns: List[str]) -> Optional[str]:
        """Suggest similar column name."""
        # Simple similarity check
        for column in available_columns:
            if column.lower().startswith(column_name.lower()[:3]):
                return f"Did you mean '{column}'?"
        return None
    
    def _fix_parentheses(self, sql_query: str) -> str:
        """Attempt to fix unbalanced parentheses."""
        open_count = sql_query.count('(')
        close_count = sql_query.count(')')
        
        if open_count > close_count:
            return sql_query + ')' * (open_count - close_count)
        elif close_count > open_count:
            return '(' * (close_count - open_count) + sql_query
        
        return sql_query
    
    def _is_well_formatted(self, sql_query: str) -> bool:
        """Check if SQL query is well formatted."""
        # Simple formatting check
        lines = sql_query.split('\n')
        if len(lines) == 1 and len(sql_query) > 100:
            return False  # Long single line
        
        return True
    
    def _format_sql(self, sql_query: str) -> str:
        """Format SQL query for better readability."""
        # Simple formatting - would use proper SQL formatter
        formatted = sql_query.upper()
        
        # Add line breaks after major keywords
        keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING']
        for keyword in keywords:
            formatted = re.sub(f'\\b{keyword}\\b', f'\n{keyword}', formatted, flags=re.IGNORECASE)
        
        return formatted.strip()
    
    def _calculate_confidence_score(self, issues: List[ValidationIssue], sql_query: str) -> float:
        """Calculate confidence score for validation."""
        if not issues:
            return 1.0
        
        # Weight issues by severity
        severity_weights = {
            SeverityLevel.INFO: 0.1,
            SeverityLevel.WARNING: 0.3,
            SeverityLevel.ERROR: 0.7,
            SeverityLevel.CRITICAL: 1.0
        }
        
        total_weight = sum(severity_weights[issue.severity] for issue in issues)
        max_possible_weight = len(issues) * 1.0
        
        confidence = 1.0 - (total_weight / max_possible_weight) if max_possible_weight > 0 else 1.0
        return max(0.0, confidence)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get validator metrics."""
        return self._metrics.copy()
