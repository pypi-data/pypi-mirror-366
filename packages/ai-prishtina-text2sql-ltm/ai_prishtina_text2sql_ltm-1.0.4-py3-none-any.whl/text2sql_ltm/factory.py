"""
Integrated Agent Factory for Text2SQL-LTM.

This module provides a comprehensive factory system for creating fully integrated
Text2SQL agents with all AI features seamlessly connected and configured.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

from .agent import Text2SQLAgent
from .config import ConfigurationManager, create_default_config_manager
from .exceptions import Text2SQLLTMError, ConfigurationError, ValidationError

# Import AI features with fallbacks
try:
    from .ai_features.config import AIFeaturesConfig
except ImportError:
    AIFeaturesConfig = None

try:
    from .rag.manager import RAGManager
except ImportError:
    RAGManager = None

try:
    from .ai_features import (
        SQLValidator,
        MultiModalProcessor,
        SQLExplainer,
        SchemaDiscovery,
        QueryTranslator,
        SecurityAnalyzer,
        TestCaseGenerator
    )
except ImportError:
    SQLValidator = None
    MultiModalProcessor = None
    SQLExplainer = None
    SchemaDiscovery = None
    QueryTranslator = None
    SecurityAnalyzer = None
    TestCaseGenerator = None

logger = logging.getLogger(__name__)


class IntegratedText2SQLAgent:
    """
    Fully integrated Text2SQL agent with all AI features.
    
    This class provides a unified interface to all Text2SQL-LTM capabilities,
    ensuring seamless integration between components and easy configuration.
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core components
        self._agent: Optional[Text2SQLAgent] = None
        self._rag_manager: Optional[RAGManager] = None
        
        # AI feature components
        self._sql_validator: Optional[SQLValidator] = None
        self._multimodal_processor: Optional[MultiModalProcessor] = None
        self._sql_explainer: Optional[SQLExplainer] = None
        self._schema_discovery: Optional[SchemaDiscovery] = None
        self._query_translator: Optional[QueryTranslator] = None
        self._security_analyzer: Optional[SecurityAnalyzer] = None
        self._test_generator: Optional[TestCaseGenerator] = None
        
        # Configuration
        self.ai_config = self.config_manager.get_config("ai_features")
        
        # Initialization state
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all components and establish connections."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing integrated Text2SQL agent...")
            
            # Initialize core agent
            self._agent = Text2SQLAgent(self.config_manager)
            await self._agent.initialize()
            
            # Initialize AI features based on configuration
            await self._initialize_ai_features()
            
            # Establish component connections
            await self._connect_components()
            
            self._initialized = True
            self.logger.info("Integrated Text2SQL agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize integrated agent: {str(e)}")
            raise Text2SQLLTMError(f"Agent initialization failed: {str(e)}") from e
    
    async def _initialize_ai_features(self) -> None:
        """Initialize AI feature components based on configuration."""
        
        # Initialize RAG system
        if self.ai_config.enable_rag:
            self.logger.info("Initializing RAG system...")
            from .rag.manager import RAGConfig
            
            rag_config = RAGConfig(
                vector_store=self.ai_config.rag.vector_store,
                embedding=self.ai_config.rag.embedding,
                max_retrieved_docs=self.ai_config.rag.max_retrieved_docs,
                similarity_threshold=self.ai_config.rag.similarity_threshold,
                enable_schema_rag=self.ai_config.rag.enable_schema_rag,
                enable_query_rag=self.ai_config.rag.enable_query_rag,
                enable_adaptive_rag=self.ai_config.rag.enable_adaptive_rag
            )
            
            self._rag_manager = RAGManager(rag_config)
            await self._rag_manager.initialize()
        
        # Initialize SQL Validator
        if self.ai_config.enable_validation:
            self.logger.info("Initializing SQL validator...")
            self._sql_validator = SQLValidator(
                enable_ai_suggestions=self.ai_config.validation.enable_ai_suggestions,
                enable_auto_fix=self.ai_config.validation.enable_auto_correction,
                llm_provider=self._get_llm_provider()
            )
        
        # Initialize Multi-Modal Processor
        if self.ai_config.enable_multimodal:
            self.logger.info("Initializing multi-modal processor...")
            from .ai_features.multimodal import VoiceProcessor, ImageProcessor
            
            voice_processor = None
            if self.ai_config.multimodal.enable_voice_processing:
                voice_processor = VoiceProcessor(
                    provider=self.ai_config.multimodal.voice_provider,
                    api_key=self.ai_config.multimodal.voice_api_key,
                    language="en-US"
                )
            
            image_processor = None
            if self.ai_config.multimodal.enable_image_processing:
                image_processor = ImageProcessor(
                    ocr_provider=self.ai_config.multimodal.ocr_provider,
                    api_key=self.ai_config.multimodal.ocr_api_key,
                    enable_preprocessing=self.ai_config.multimodal.enable_preprocessing
                )
            
            self._multimodal_processor = MultiModalProcessor(
                voice_processor=voice_processor,
                image_processor=image_processor
            )
            await self._multimodal_processor.initialize()
        
        # Initialize SQL Explainer
        if self.ai_config.enable_explanation:
            self.logger.info("Initializing SQL explainer...")
            self._sql_explainer = SQLExplainer(
                llm_provider=self._get_llm_provider(),
                enable_interactive_mode=self.ai_config.explanation.enable_interactive_mode,
                enable_progress_tracking=self.ai_config.explanation.enable_progress_tracking
            )
        
        # Initialize Schema Discovery
        if self.ai_config.enable_schema_discovery:
            self.logger.info("Initializing schema discovery...")
            self._schema_discovery = SchemaDiscovery(
                llm_provider=self._get_llm_provider(),
                enable_ai_inference=self.ai_config.schema_discovery.enable_ai_inference,
                enable_data_profiling=self.ai_config.schema_discovery.enable_data_profiling
            )
        
        # Initialize Query Translator
        if self.ai_config.enable_translation:
            self.logger.info("Initializing query translator...")
            self._query_translator = QueryTranslator(
                enable_ai_enhancement=self.ai_config.translation.enable_ai_enhancement
            )
        
        # Initialize Security Analyzer
        if self.ai_config.enable_security_analysis:
            self.logger.info("Initializing security analyzer...")
            self._security_analyzer = SecurityAnalyzer(
                enable_ai_analysis=self.ai_config.security.enable_ai_analysis,
                strict_mode=self.ai_config.security.strict_mode
            )
        
        # Initialize Test Generator
        if self.ai_config.enable_test_generation:
            self.logger.info("Initializing test generator...")
            self._test_generator = TestCaseGenerator(
                enable_ai_generation=self.ai_config.test_generation.enable_ai_generation
            )
    
    async def _connect_components(self) -> None:
        """Establish connections between components."""
        
        # Connect RAG to agent
        if self._rag_manager and self._agent:
            self._agent.set_rag_manager(self._rag_manager)
        
        # Connect AI features to agent
        if self._sql_validator and self._agent:
            self._agent.set_sql_validator(self._sql_validator)
        
        if self._multimodal_processor and self._agent:
            self._agent.set_multimodal_processor(self._multimodal_processor)
        
        if self._sql_explainer and self._agent:
            self._agent.set_sql_explainer(self._sql_explainer)
        
        if self._schema_discovery and self._agent:
            self._agent.set_schema_discovery(self._schema_discovery)
        
        if self._query_translator and self._agent:
            self._agent.set_query_translator(self._query_translator)
        
        if self._security_analyzer and self._agent:
            self._agent.set_security_analyzer(self._security_analyzer)
        
        if self._test_generator and self._agent:
            self._agent.set_test_generator(self._test_generator)
    
    def _get_llm_provider(self) -> Any:
        """Get LLM provider for AI features."""
        # This would return the actual LLM provider instance
        # For now, return None as placeholder
        return None
    
    async def query(self, *args, **kwargs) -> Any:
        """Process query with full AI enhancement."""
        if not self._initialized:
            await self.initialize()
        
        return await self._agent.query(*args, **kwargs)
    
    async def close(self) -> None:
        """Close all components and cleanup resources."""
        if self._rag_manager:
            await self._rag_manager.close()
        
        if self._multimodal_processor:
            await self._multimodal_processor.close()
        
        if self._agent:
            await self._agent.close()
        
        self._initialized = False
    
    # Property accessors for components
    @property
    def agent(self) -> Text2SQLAgent:
        """Get the core agent."""
        return self._agent
    
    @property
    def rag_manager(self) -> Optional[RAGManager]:
        """Get the RAG manager."""
        return self._rag_manager
    
    @property
    def sql_validator(self) -> Optional[SQLValidator]:
        """Get the SQL validator."""
        return self._sql_validator
    
    @property
    def multimodal_processor(self) -> Optional[MultiModalProcessor]:
        """Get the multi-modal processor."""
        return self._multimodal_processor
    
    @property
    def sql_explainer(self) -> Optional[SQLExplainer]:
        """Get the SQL explainer."""
        return self._sql_explainer
    
    @property
    def schema_discovery(self) -> Optional[SchemaDiscovery]:
        """Get the schema discovery."""
        return self._schema_discovery
    
    @property
    def query_translator(self) -> Optional[QueryTranslator]:
        """Get the query translator."""
        return self._query_translator
    
    @property
    def security_analyzer(self) -> Optional[SecurityAnalyzer]:
        """Get the security analyzer."""
        return self._security_analyzer
    
    @property
    def test_generator(self) -> Optional[TestCaseGenerator]:
        """Get the test generator."""
        return self._test_generator


def create_integrated_agent(
    config_file: Optional[Union[str, Path]] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    **config_overrides
) -> IntegratedText2SQLAgent:
    """
    Create a fully integrated Text2SQL agent with all features.
    
    Args:
        config_file: Path to configuration file (YAML or INI)
        config_dict: Configuration dictionary
        **config_overrides: Configuration overrides
        
    Returns:
        Fully configured integrated agent
    """
    try:
        # Create configuration manager
        config_manager = create_default_config_manager()
        
        # Add AI features configuration
        config_manager.register_config(AIFeaturesConfig)
        
        # Load configuration from file if provided
        if config_file:
            config_manager.load_from_file(Path(config_file))
        
        # Load configuration from dictionary if provided
        if config_dict:
            config_manager.load_from_dict(config_dict)
        
        # Apply overrides
        if config_overrides:
            # Convert flat overrides to nested structure
            nested_overrides = {}
            for key, value in config_overrides.items():
                if "__" in key:
                    section, setting = key.split("__", 1)
                    if section not in nested_overrides:
                        nested_overrides[section] = {}
                    nested_overrides[section][setting] = value
                else:
                    nested_overrides[key] = value
            
            config_manager.load_from_dict(nested_overrides)
        
        # Load from environment variables
        config_manager.load_from_env("TEXT2SQL_LTM")
        
        # Validate all configurations
        config_manager.validate_all()
        
        # Create integrated agent
        return IntegratedText2SQLAgent(config_manager)
        
    except Exception as e:
        logger.error(f"Failed to create integrated agent: {str(e)}")
        raise ConfigurationError(f"Agent creation failed: {str(e)}") from e


def create_simple_agent(**kwargs) -> IntegratedText2SQLAgent:
    """
    Create a simple agent with minimal configuration.
    
    Args:
        **kwargs: Simple configuration options
        
    Returns:
        Configured integrated agent
    """
    # Default simple configuration
    simple_config = {
        "memory": {
            "storage_backend": "memory"
        },
        "agent": {
            "llm_provider": kwargs.get("llm_provider", "openai"),
            "llm_model": kwargs.get("llm_model", "gpt-4"),
            "llm_api_key": kwargs.get("api_key")
        },
        "ai_features": {
            "enable_rag": kwargs.get("enable_rag", True),
            "enable_validation": kwargs.get("enable_validation", True),
            "enable_explanation": kwargs.get("enable_explanation", True),
            "enable_schema_discovery": kwargs.get("enable_schema_discovery", True),
            "enable_translation": kwargs.get("enable_translation", True),
            "enable_security_analysis": kwargs.get("enable_security_analysis", True),
            "enable_test_generation": kwargs.get("enable_test_generation", False)
        },
        "security": {
            "require_authentication": False
        }
    }
    
    return create_integrated_agent(config_dict=simple_config)


def create_production_agent(config_file: Union[str, Path]) -> IntegratedText2SQLAgent:
    """
    Create a production-ready agent from configuration file.
    
    Args:
        config_file: Path to production configuration file
        
    Returns:
        Production-configured integrated agent
    """
    return create_integrated_agent(config_file=config_file)


# Convenience function for backward compatibility
def create_agent(**kwargs) -> IntegratedText2SQLAgent:
    """Create an integrated Text2SQL agent with specified configuration."""
    return create_simple_agent(**kwargs)


# Context manager for automatic cleanup
class Text2SQLSession:
    """Context manager for Text2SQL sessions with automatic cleanup."""
    
    def __init__(self, agent: IntegratedText2SQLAgent):
        self.agent = agent
    
    async def __aenter__(self) -> IntegratedText2SQLAgent:
        await self.agent.initialize()
        return self.agent
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.agent.close()


def create_session(**kwargs) -> Text2SQLSession:
    """Create a Text2SQL session with automatic cleanup."""
    agent = create_simple_agent(**kwargs)
    return Text2SQLSession(agent)
