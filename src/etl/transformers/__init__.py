"""
Data Transformers Package - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 2

This package provides data transformation, validation, and enrichment capabilities
for the ETL pipeline.
"""

from .base_transformer import (
    BaseDataTransformer,
    DataQualityMetrics,
    TransformationResult,
    TransformationRule,
)
from .financial_transformer import (
    FinancialDataTransformer,
    FinancialMetricsCalculator,
    FinancialRatioCalculator,
)

# Economic transformer - planned for future implementation
# from .economic_transformer import (
#     EconomicDataTransformer,
#     EconomicIndicatorProcessor,
#     TrendAnalysisEngine
# )

# Data enricher - planned for future implementation
# from .data_enricher import (
#     DataEnricher,
#     EnrichmentRule,
#     EnrichmentResult
# )

# Data validator - planned for future implementation
# from .data_validator import (
#     DataValidator,
#     ValidationRule,
#     ValidationResult,
#     DataQualityLevel
# )

# Transformation pipeline - planned for future implementation
# from .transformation_pipeline import (
#     TransformationPipeline,
#     PipelineStage,
#     PipelineResult
# )

__all__ = [
    # Base classes
    "BaseDataTransformer",
    "TransformationRule",
    "TransformationResult",
    "DataQualityMetrics",
    # Financial transformers
    "FinancialDataTransformer",
    "FinancialMetricsCalculator",
    "FinancialRatioCalculator",
    # Economic transformers - planned for future implementation
    # 'EconomicDataTransformer',
    # 'EconomicIndicatorProcessor',
    # 'TrendAnalysisEngine',
    # Data enrichment - planned for future implementation
    # 'DataEnricher',
    # 'EnrichmentRule',
    # 'EnrichmentResult',
    # Data validation - planned for future implementation
    # 'DataValidator',
    # 'ValidationRule',
    # 'ValidationResult',
    # 'DataQualityLevel',
    # Pipeline orchestration - planned for future implementation
    # 'TransformationPipeline',
    # 'PipelineStage',
    # 'PipelineResult'
]
