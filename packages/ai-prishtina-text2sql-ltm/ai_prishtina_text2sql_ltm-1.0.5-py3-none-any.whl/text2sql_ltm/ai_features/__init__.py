"""
AI-Powered Features for Text2SQL-LTM library.

This module provides cutting-edge AI features that enhance the Text2SQL experience:
- Intelligent SQL validation and optimization
- Multi-modal query understanding (text, voice, images)
- Real-time query explanation and teaching
- Automated schema discovery and documentation
- Intelligent error recovery and suggestions
- Natural language SQL debugging
- Query performance prediction
- Automated test case generation
"""

from .sql_validator import SQLValidator, ValidationResult, OptimizationSuggestion
from .query_translator import QueryTranslator
from .security_analyzer import SecurityAnalyzer

# Import with fallbacks for optional modules
try:
    from .explainer import SQLExplainer
except ImportError:
    SQLExplainer = None

try:
    from .schema_discovery import SchemaDiscovery
except ImportError:
    SchemaDiscovery = None

try:
    from .test_generator import TestCaseGenerator
except ImportError:
    TestCaseGenerator = None

__all__ = [
    # SQL Intelligence
    "SQLValidator",
    "ValidationResult",
    "OptimizationSuggestion",

    # Query Translation
    "QueryTranslator",

    # Security Analysis
    "SecurityAnalyzer",

    # Optional modules (conditionally available)
    "SQLExplainer",
    "SchemaDiscovery",
    "TestCaseGenerator",
    "OptimizationStrategy",
    "QueryComplexityAnalyzer",
]
