"""
Configuration classes for AI Features in Text2SQL-LTM.

This module provides comprehensive configuration for all AI-powered features,
ensuring seamless integration and easy setup through configuration files.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..config.base import BaseConfig
from ..types import SQLDialect, LLMProvider


class VectorStoreType(str, Enum):
    """Supported vector store types."""
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    FAISS = "faiss"
    MILVUS = "milvus"


class EmbeddingProvider(str, Enum):
    """Supported embedding providers."""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    COHERE = "cohere"
    AZURE_OPENAI = "azure_openai"




@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    provider: VectorStoreType = VectorStoreType.CHROMA
    connection_string: Optional[str] = None
    api_key: Optional[str] = None
    collection_name: str = "text2sql_knowledge"
    dimension: int = 1536
    distance_metric: str = "cosine"
    index_params: Dict[str, Any] = field(default_factory=dict)
    
    # Chroma specific
    persist_directory: Optional[str] = None
    
    # Pinecone specific
    environment: Optional[str] = None
    
    # Qdrant specific
    host: Optional[str] = None
    port: Optional[int] = None


@dataclass
class EmbeddingConfig:
    """Embedding configuration."""
    provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    model_name: str = "text-embedding-ada-002"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    batch_size: int = 100
    max_retries: int = 3
    timeout: int = 30
    
    # HuggingFace specific
    model_path: Optional[str] = None
    device: str = "auto"
    
    # Azure OpenAI specific
    azure_endpoint: Optional[str] = None
    azure_deployment: Optional[str] = None


@dataclass
class RAGConfig:
    """RAG system configuration."""
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    
    # Retrieval settings
    max_retrieved_docs: int = 10
    similarity_threshold: float = 0.7
    enable_reranking: bool = True
    reranker_model: Optional[str] = None
    
    # Schema RAG
    enable_schema_rag: bool = True
    schema_weight: float = 0.3
    
    # Query RAG
    enable_query_rag: bool = True
    query_pattern_weight: float = 0.2
    
    # Adaptive RAG
    enable_adaptive_rag: bool = True
    learning_rate: float = 0.01
    adaptation_threshold: float = 0.8


@dataclass
class ValidationConfig:
    """SQL validation configuration."""
    enable_syntax_validation: bool = True
    enable_semantic_validation: bool = True
    enable_security_validation: bool = True
    enable_performance_validation: bool = True
    enable_auto_correction: bool = True
    
    # AI enhancement
    enable_ai_suggestions: bool = True
    llm_provider: Optional[LLMProvider] = None
    
    # Validation levels
    strict_mode: bool = False
    max_validation_time: int = 30  # seconds
    
    # Security settings
    block_dangerous_queries: bool = True
    allowed_functions: List[str] = field(default_factory=list)
    blocked_functions: List[str] = field(default_factory=list)


@dataclass
class ExplanationConfig:
    """Query explanation configuration."""
    enable_explanations: bool = True
    enable_interactive_mode: bool = True
    enable_progress_tracking: bool = True
    
    # Explanation settings
    default_level: str = "adaptive"
    include_execution_steps: bool = True
    include_performance_notes: bool = True
    include_alternatives: bool = True
    
    # Teaching settings
    enable_teaching_mode: bool = True
    personalized_learning: bool = True
    track_user_progress: bool = True
    
    # AI enhancement
    llm_provider: Optional[LLMProvider] = None
    explanation_model: Optional[str] = None


@dataclass
class SchemaDiscoveryConfig:
    """Schema discovery configuration."""
    enable_discovery: bool = True
    enable_ai_inference: bool = True
    enable_data_profiling: bool = True
    
    # Discovery settings
    sample_size: int = 1000
    confidence_threshold: float = 0.8
    max_analysis_time: int = 300  # seconds
    
    # AI settings
    llm_provider: Optional[LLMProvider] = None
    inference_model: Optional[str] = None
    
    # Documentation
    auto_generate_docs: bool = True
    doc_formats: List[str] = field(default_factory=lambda: ["markdown", "html"])
    include_diagrams: bool = True


@dataclass
class TranslationConfig:
    """Query translation configuration."""
    enable_translation: bool = True
    enable_ai_enhancement: bool = True
    
    # Supported dialects
    supported_dialects: List[SQLDialect] = field(default_factory=lambda: [
        SQLDialect.POSTGRESQL,
        SQLDialect.MYSQL,
        SQLDialect.SQLITE,
        SQLDialect.MSSQL
    ])
    
    # Translation settings
    optimize_for_target: bool = True
    include_warnings: bool = True
    confidence_threshold: float = 0.7
    
    # AI settings
    llm_provider: Optional[LLMProvider] = None
    translation_model: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security analysis configuration."""
    enable_security_analysis: bool = True
    enable_ai_analysis: bool = True
    strict_mode: bool = False
    
    # Analysis settings
    vulnerability_scanning: bool = True
    compliance_checking: bool = True
    real_time_monitoring: bool = True
    
    # Compliance standards
    enable_gdpr_checks: bool = True
    enable_pci_dss_checks: bool = True
    enable_sox_checks: bool = True
    
    # AI settings
    llm_provider: Optional[LLMProvider] = None
    security_model: Optional[str] = None
    
    # Response settings
    block_threats: bool = True
    alert_on_threats: bool = True
    log_security_events: bool = True


@dataclass
class TestGenerationConfig:
    """Test generation configuration."""
    enable_test_generation: bool = True
    enable_ai_generation: bool = True
    
    # Test types
    generate_functional_tests: bool = True
    generate_edge_case_tests: bool = True
    generate_performance_tests: bool = True
    generate_security_tests: bool = True
    
    # Generation settings
    default_test_count: int = 10
    max_test_data_rows: int = 1000
    include_edge_cases: bool = True
    
    # AI settings
    llm_provider: Optional[LLMProvider] = None
    generation_model: Optional[str] = None
    
    # Execution settings
    auto_run_tests: bool = False
    test_timeout: int = 60  # seconds


class AIFeaturesConfig(BaseConfig):
    """
    Comprehensive configuration for all AI features.
    
    This class provides a unified configuration interface for all AI-powered
    features in Text2SQL-LTM, ensuring seamless integration and easy setup.
    """
    
    # Feature toggles
    enable_rag: bool = True
    enable_validation: bool = True
    enable_explanation: bool = True
    enable_schema_discovery: bool = True
    enable_translation: bool = True
    enable_security_analysis: bool = True
    enable_test_generation: bool = False  # Disabled - basic implementation only
    
    # Component configurations
    rag: RAGConfig = field(default_factory=RAGConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    explanation: ExplanationConfig = field(default_factory=ExplanationConfig)
    schema_discovery: SchemaDiscoveryConfig = field(default_factory=SchemaDiscoveryConfig)
    translation: TranslationConfig = field(default_factory=TranslationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    test_generation: TestGenerationConfig = field(default_factory=TestGenerationConfig)
    
    # Global AI settings
    default_llm_provider: LLMProvider = LLMProvider.OPENAI
    default_llm_model: str = "gpt-4"
    ai_timeout: int = 30  # seconds
    max_concurrent_ai_requests: int = 10
    
    # Performance settings
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds
    enable_async_processing: bool = True

    @classmethod
    def get_config_section(cls) -> str:
        """Get the configuration section name."""
        return "ai_features"

    def validate_production_ready(self) -> None:
        """Validate that configuration is production-ready."""
        # Check that essential features are properly configured
        if self.enable_rag and not self.rag.vector_store.provider:
            raise ValueError("RAG vector store provider must be configured for production")

        # Ensure reasonable timeout values
        if self.ai_timeout < 5:
            raise ValueError("AI timeout should be at least 5 seconds for production")

    def validate(self) -> None:
        """Validate the configuration."""
        super().validate()
        
        # Validate vector store configuration
        if self.enable_rag:
            if not self.rag.vector_store.provider:
                raise ValueError("Vector store provider must be specified when RAG is enabled")
            
            if not self.rag.embedding.provider:
                raise ValueError("Embedding provider must be specified when RAG is enabled")
        

        # Validate AI provider settings
        ai_features = [
            self.enable_validation and self.validation.enable_ai_suggestions,
            self.enable_explanation,
            self.enable_schema_discovery and self.schema_discovery.enable_ai_inference,
            self.enable_translation and self.translation.enable_ai_enhancement,
            self.enable_security_analysis and self.security.enable_ai_analysis,
            self.enable_test_generation and self.test_generation.enable_ai_generation
        ]
        
        if any(ai_features) and not self.default_llm_provider:
            raise ValueError("LLM provider must be specified when AI features are enabled")
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features."""
        features = []
        
        if self.enable_rag:
            features.append("rag")
        if self.enable_validation:
            features.append("validation")
        if self.enable_multimodal:
            features.append("multimodal")
        if self.enable_explanation:
            features.append("explanation")
        if self.enable_schema_discovery:
            features.append("schema_discovery")
        if self.enable_translation:
            features.append("translation")
        if self.enable_security_analysis:
            features.append("security_analysis")
        if self.enable_test_generation:
            features.append("test_generation")
        
        return features
    
    def get_required_api_keys(self) -> Dict[str, List[str]]:
        """Get required API keys for enabled features."""
        required_keys = {}
        
        if self.enable_rag:
            if self.rag.embedding.provider == EmbeddingProvider.OPENAI:
                required_keys.setdefault("openai", []).append("embedding")
            if self.rag.vector_store.provider == VectorStoreType.PINECONE:
                required_keys.setdefault("pinecone", []).append("vector_store")
        
        if self.enable_multimodal:
            if self.multimodal.enable_voice_processing:
                provider = self.multimodal.voice_provider.value
                required_keys.setdefault(provider, []).append("voice")
            
            if self.multimodal.enable_image_processing:
                provider = self.multimodal.ocr_provider.value
                required_keys.setdefault(provider, []).append("ocr")
        
        # Add LLM provider keys for AI features
        ai_features = [
            self.enable_validation and self.validation.enable_ai_suggestions,
            self.enable_explanation,
            self.enable_schema_discovery and self.schema_discovery.enable_ai_inference,
            self.enable_translation and self.translation.enable_ai_enhancement,
            self.enable_security_analysis and self.security.enable_ai_analysis,
            self.enable_test_generation and self.test_generation.enable_ai_generation
        ]
        
        if any(ai_features):
            provider = self.default_llm_provider.value
            required_keys.setdefault(provider, []).append("llm")
        
        return required_keys
