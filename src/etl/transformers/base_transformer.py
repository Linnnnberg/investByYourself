"""
Base Data Transformer - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 2

This module provides the abstract base class for all data transformers,
defining the common interface and shared functionality.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)


class DataQualityLevel(Enum):
    """Data quality levels for validation and monitoring."""
    EXCELLENT = "excellent"  # 95-100% quality
    GOOD = "good"           # 80-94% quality
    FAIR = "fair"           # 60-79% quality
    POOR = "poor"           # 40-59% quality
    UNUSABLE = "unusable"   # <40% quality


@dataclass
class DataQualityMetrics:
    """Metrics for data quality assessment."""
    completeness: float = 0.0  # Percentage of required fields present
    accuracy: float = 0.0      # Percentage of data that passes validation
    consistency: float = 0.0   # Percentage of data that follows business rules
    timeliness: float = 0.0    # Data freshness score
    overall_score: float = 0.0 # Weighted average of all metrics
    
    def calculate_overall_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate overall quality score with optional weights."""
        if weights is None:
            weights = {
                'completeness': 0.3,
                'accuracy': 0.3,
                'consistency': 0.2,
                'timeliness': 0.2
            }
        
        self.overall_score = sum(
            getattr(self, metric) * weight 
            for metric, weight in weights.items()
        )
        return self.overall_score


@dataclass
class TransformationRule:
    """Defines a data transformation rule."""
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    field_mapping: Dict[str, str] = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)
    transformation_functions: List[str] = field(default_factory=list)
    priority: int = 1
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate rule configuration."""
        if not self.name:
            raise ValueError("Transformation rule must have a name")
        if not self.field_mapping and not self.transformation_functions:
            raise ValueError("Rule must have field mappings or transformation functions")


@dataclass
class TransformationResult:
    """Result of a data transformation operation."""
    transformation_id: str = field(default_factory=lambda: str(uuid4()))
    source_data: Dict[str, Any] = field(default_factory=dict)
    transformed_data: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: DataQualityMetrics = field(default_factory=DataQualityMetrics)
    transformation_rules_applied: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Check if transformation was successful."""
        return len(self.errors) == 0 and len(self.transformed_data) > 0
    
    @property
    def quality_level(self) -> DataQualityLevel:
        """Get the overall data quality level."""
        score = self.quality_metrics.overall_score
        if score >= 0.95:
            return DataQualityLevel.EXCELLENT
        elif score >= 0.80:
            return DataQualityLevel.GOOD
        elif score >= 0.60:
            return DataQualityLevel.FAIR
        elif score >= 0.40:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.UNUSABLE


class BaseDataTransformer(ABC):
    """
    Abstract base class for all data transformers.
    
    This class defines the common interface and shared functionality
    for transforming data from various sources into standardized formats.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        max_concurrent_transformations: int = 10,
        enable_validation: bool = True,
        enable_quality_monitoring: bool = True
    ):
        """Initialize the base transformer."""
        self.name = name
        self.description = description
        self.max_concurrent_transformations = max_concurrent_transformations
        self.enable_validation = enable_validation
        self.enable_quality_monitoring = enable_quality_monitoring
        
        # Transformation rules and configuration
        self.transformation_rules: List[TransformationRule] = []
        self.validation_rules: List[str] = []
        
        # Performance tracking
        self.total_transformations = 0
        self.successful_transformations = 0
        self.failed_transformations = 0
        self.total_processing_time = 0.0
        self.average_processing_time = 0.0
        
        # Quality metrics
        self.quality_history: List[DataQualityMetrics] = []
        self.current_quality_score = 0.0
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent_transformations)
        
        logger.info(
            f"Initialized {self.__class__.__name__}",
            name=name,
            max_concurrent=max_concurrent_transformations,
            enable_validation=enable_validation
        )
    
    @abstractmethod
    async def transform_data(
        self,
        data: Dict[str, Any],
        transformation_rules: Optional[List[TransformationRule]] = None
    ) -> TransformationResult:
        """
        Transform input data according to specified rules.
        
        Args:
            data: Input data to transform
            transformation_rules: Optional list of rules to apply
            
        Returns:
            Transformation result with transformed data and metrics
        """
        pass
    
    @abstractmethod
    async def validate_data(
        self,
        data: Dict[str, Any],
        validation_rules: Optional[List[str]] = None
    ) -> bool:
        """
        Validate input data against business rules.
        
        Args:
            data: Data to validate
            validation_rules: Optional list of validation rules
            
        Returns:
            True if data is valid, False otherwise
        """
        pass
    
    async def transform_batch(
        self,
        data_batch: List[Dict[str, Any]],
        transformation_rules: Optional[List[TransformationRule]] = None
    ) -> List[TransformationResult]:
        """
        Transform multiple data records concurrently.
        
        Args:
            data_batch: List of data records to transform
            transformation_rules: Optional transformation rules
            
        Returns:
            List of transformation results
        """
        start_time = datetime.now()
        
        # Create transformation tasks
        tasks = []
        for data in data_batch:
            task = self._transform_with_semaphore(data, transformation_rules)
            tasks.append(task)
        
        # Execute transformations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        transformation_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create failed result
                failed_result = TransformationResult(
                    source_data=data_batch[i],
                    errors=[str(result)],
                    processing_time=0.0
                )
                transformation_results.append(failed_result)
                self.failed_transformations += 1
            else:
                transformation_results.append(result)
                if result.success:
                    self.successful_transformations += 1
                else:
                    self.failed_transformations += 1
        
        # Update metrics
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        self.total_transformations += len(data_batch)
        self.total_processing_time += total_time
        self.average_processing_time = self.total_processing_time / self.total_transformations
        
        # Update quality metrics
        if self.enable_quality_monitoring:
            self._update_quality_metrics(transformation_results)
        
        logger.info(
            f"Batch transformation completed",
            total_records=len(data_batch),
            successful=len([r for r in transformation_results if r.success]),
            failed=len([r for r in transformation_results if not r.success]),
            total_time=total_time,
            average_time=self.average_processing_time
        )
        
        return transformation_results
    
    async def _transform_with_semaphore(
        self,
        data: Dict[str, Any],
        transformation_rules: Optional[List[TransformationRule]]
    ) -> TransformationResult:
        """Transform data with concurrency control."""
        async with self.semaphore:
            return await self.transform_data(data, transformation_rules)
    
    def add_transformation_rule(self, rule: TransformationRule) -> None:
        """Add a new transformation rule."""
        self.transformation_rules.append(rule)
        self.transformation_rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added transformation rule: {rule.name}")
    
    def remove_transformation_rule(self, rule_id: str) -> bool:
        """Remove a transformation rule by ID."""
        for i, rule in enumerate(self.transformation_rules):
            if rule.rule_id == rule_id:
                removed_rule = self.transformation_rules.pop(i)
                logger.info(f"Removed transformation rule: {removed_rule.name}")
                return True
        return False
    
    def get_transformation_rules(self) -> List[TransformationRule]:
        """Get all transformation rules."""
        return self.transformation_rules.copy()
    
    def _update_quality_metrics(self, results: List[TransformationResult]) -> None:
        """Update quality metrics based on recent transformations."""
        if not results:
            return
        
        # Calculate average quality scores
        avg_completeness = sum(r.quality_metrics.completeness for r in results) / len(results)
        avg_accuracy = sum(r.quality_metrics.accuracy for r in results) / len(results)
        avg_consistency = sum(r.quality_metrics.consistency for r in results) / len(results)
        avg_timeliness = sum(r.quality_metrics.timeliness for r in results) / len(results)
        
        # Create new quality metrics
        quality_metrics = DataQualityMetrics(
            completeness=avg_completeness,
            accuracy=avg_accuracy,
            consistency=avg_consistency,
            timeliness=avg_timeliness
        )
        quality_metrics.calculate_overall_score()
        
        # Update history and current score
        self.quality_history.append(quality_metrics)
        self.current_quality_score = quality_metrics.overall_score
        
        # Keep only recent history (last 100 entries)
        if len(self.quality_history) > 100:
            self.quality_history = self.quality_history[-100:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get transformer performance and quality metrics."""
        return {
            'name': self.name,
            'total_transformations': self.total_transformations,
            'successful_transformations': self.successful_transformations,
            'failed_transformations': self.failed_transformations,
            'success_rate': (self.successful_transformations / self.total_transformations * 100) 
                           if self.total_transformations > 0 else 0.0,
            'total_processing_time': self.total_processing_time,
            'average_processing_time': self.average_processing_time,
            'current_quality_score': self.current_quality_score,
            'transformation_rules_count': len(self.transformation_rules),
            'validation_rules_count': len(self.validation_rules),
            'quality_history_size': len(self.quality_history)
        }
    
    def reset_metrics(self) -> None:
        """Reset all performance and quality metrics."""
        self.total_transformations = 0
        self.successful_transformations = 0
        self.failed_transformations = 0
        self.total_processing_time = 0.0
        self.average_processing_time = 0.0
        self.quality_history.clear()
        self.current_quality_score = 0.0
        logger.info(f"Reset metrics for {self.name}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass
