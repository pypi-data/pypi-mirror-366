"""Optimization-related database models."""

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from mlperf.utils.database import Base


class OptimizationType(str, enum.Enum):
    """Types of optimizations."""
    
    MEMORY = "memory"
    COMPUTE = "compute"
    COMMUNICATION = "communication"
    IO = "io"
    PARALLELISM = "parallelism"
    QUANTIZATION = "quantization"
    PRUNING = "pruning"
    COMPILATION = "compilation"
    CUSTOM = "custom"


class OptimizationPriority(str, enum.Enum):
    """Priority levels for optimizations."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OptimizationStatus(str, enum.Enum):
    """Status of optimization recommendations."""
    
    SUGGESTED = "suggested"
    IN_PROGRESS = "in_progress"
    APPLIED = "applied"
    REJECTED = "rejected"
    FAILED = "failed"


class OptimizationProfile(Base):
    """Optimization profile for specific workloads."""
    
    __tablename__ = "optimization_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Target workload
    framework = Column(String(100), nullable=False, index=True)
    model_type = Column(String(100), nullable=True)  # transformer, cnn, rnn, etc.
    workload_type = Column(String(100), nullable=True)  # training, inference, fine-tuning
    
    # Optimization strategies
    strategies = Column(JSON, nullable=False, default={})
    enabled_optimizations = Column(JSON, nullable=False, default=[])
    
    # Configuration templates
    memory_optimization = Column(JSON, nullable=True)
    compute_optimization = Column(JSON, nullable=True)
    communication_optimization = Column(JSON, nullable=True)
    io_optimization = Column(JSON, nullable=True)
    
    # Hardware requirements
    min_gpu_memory_gb = Column(Float, nullable=True)
    recommended_gpu_models = Column(JSON, nullable=True, default=[])
    
    # Performance targets
    target_throughput = Column(Float, nullable=True)
    target_latency_ms = Column(Float, nullable=True)
    target_memory_reduction = Column(Float, nullable=True)  # Percentage
    
    # Validation
    validated = Column(Boolean, default=False)
    validation_results = Column(JSON, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True, default=[])
    data_metadata = Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    recommendations = relationship("OptimizationRecommendation", back_populates="profile", cascade="all, delete-orphan")
    results = relationship("OptimizationResult", back_populates="profile", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_optimization_profile_framework", "framework"),
        Index("idx_optimization_profile_model", "model_type"),
    )
    
    def __repr__(self) -> str:
        return f"<OptimizationProfile(id={self.id}, name={self.name})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "framework": self.framework,
            "model_type": self.model_type,
            "workload_type": self.workload_type,
            "strategies": self.strategies,
            "enabled_optimizations": self.enabled_optimizations,
            "configurations": {
                "memory": self.memory_optimization,
                "compute": self.compute_optimization,
                "communication": self.communication_optimization,
                "io": self.io_optimization,
            },
            "hardware_requirements": {
                "min_gpu_memory_gb": self.min_gpu_memory_gb,
                "recommended_gpus": self.recommended_gpu_models or [],
            },
            "performance_targets": {
                "throughput": self.target_throughput,
                "latency_ms": self.target_latency_ms,
                "memory_reduction": self.target_memory_reduction,
            },
            "validated": self.validated,
            "validation_results": self.validation_results or {},
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OptimizationRecommendation(Base):
    """Specific optimization recommendations."""
    
    __tablename__ = "optimization_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("optimization_profiles.id"), nullable=True, index=True)
    benchmark_run_id = Column(Integer, ForeignKey("benchmark_runs.id"), nullable=True, index=True)
    experiment_run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=True, index=True)
    
    # Recommendation details
    type = Column(Enum(OptimizationType), nullable=False, index=True)
    priority = Column(Enum(OptimizationPriority), default=OptimizationPriority.MEDIUM, nullable=False)
    status = Column(Enum(OptimizationStatus), default=OptimizationStatus.SUGGESTED, nullable=False, index=True)
    
    # Description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    
    # Implementation
    implementation_steps = Column(JSON, nullable=True, default=[])
    code_snippets = Column(JSON, nullable=True, default={})
    configuration_changes = Column(JSON, nullable=True, default={})
    
    # Expected impact
    estimated_impact = Column(Float, nullable=True)  # Percentage improvement
    impact_metrics = Column(JSON, nullable=True, default={})
    effort_estimate = Column(String(50), nullable=True)  # low, medium, high
    risk_level = Column(String(50), nullable=True)  # low, medium, high
    
    # Conditions
    applicable_conditions = Column(JSON, nullable=True, default={})
    prerequisites = Column(JSON, nullable=True, default=[])
    
    # Results (if applied)
    applied_at = Column(DateTime, nullable=True)
    applied_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    actual_impact = Column(Float, nullable=True)
    result_metrics = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True, default=[])
    data_metadata = Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    profile = relationship("OptimizationProfile", back_populates="recommendations")
    
    # Indexes
    __table_args__ = (
        Index("idx_optimization_rec_type_priority", "type", "priority"),
        Index("idx_optimization_rec_status", "status"),
        Index("idx_optimization_rec_run", "benchmark_run_id"),
    )
    
    def __repr__(self) -> str:
        return f"<OptimizationRecommendation(id={self.id}, type={self.type}, priority={self.priority})>"
    
    def calculate_effectiveness(self) -> Optional[float]:
        """Calculate effectiveness if applied."""
        if self.estimated_impact and self.actual_impact:
            return self.actual_impact / self.estimated_impact
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "benchmark_run_id": self.benchmark_run_id,
            "experiment_run_id": self.experiment_run_id,
            "type": self.type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "implementation": {
                "steps": self.implementation_steps or [],
                "code_snippets": self.code_snippets or {},
                "configuration_changes": self.configuration_changes or {},
            },
            "expected_impact": {
                "percentage": self.estimated_impact,
                "metrics": self.impact_metrics or {},
                "effort": self.effort_estimate,
                "risk": self.risk_level,
            },
            "conditions": {
                "applicable": self.applicable_conditions or {},
                "prerequisites": self.prerequisites or [],
            },
            "application": {
                "applied_at": self.applied_at.isoformat() if self.applied_at else None,
                "applied_by": self.applied_by,
                "actual_impact": self.actual_impact,
                "result_metrics": self.result_metrics or {},
                "effectiveness": self.calculate_effectiveness(),
                "feedback": self.feedback,
            },
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OptimizationResult(Base):
    """Results from applying optimizations."""
    
    __tablename__ = "optimization_results"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("optimization_recommendations.id"), nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("optimization_profiles.id"), nullable=True, index=True)
    
    # Before/After runs
    before_run_id = Column(Integer, ForeignKey("benchmark_runs.id"), nullable=True)
    after_run_id = Column(Integer, ForeignKey("benchmark_runs.id"), nullable=True)
    
    # Performance comparison
    throughput_improvement = Column(Float, nullable=True)  # Percentage
    latency_reduction = Column(Float, nullable=True)  # Percentage
    memory_reduction = Column(Float, nullable=True)  # Percentage
    
    # Detailed metrics
    before_metrics = Column(JSON, nullable=False, default={})
    after_metrics = Column(JSON, nullable=False, default={})
    metric_improvements = Column(JSON, nullable=True, default={})
    
    # Resource usage
    before_resource_usage = Column(JSON, nullable=True)
    after_resource_usage = Column(JSON, nullable=True)
    
    # Cost analysis
    cost_reduction = Column(Float, nullable=True)  # Percentage or absolute
    roi_estimate = Column(Float, nullable=True)
    
    # Validation
    validated = Column(Boolean, default=False)
    validation_method = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    issues_encountered = Column(JSON, nullable=True, default=[])
    
    # Metadata
    environment_changes = Column(JSON, nullable=True, default={})
    data_metadata = Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    validated_at = Column(DateTime, nullable=True)
    
    # Relationships
    profile = relationship("OptimizationProfile", back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index("idx_optimization_result_recommendation", "recommendation_id"),
        Index("idx_optimization_result_profile", "profile_id"),
    )
    
    def __repr__(self) -> str:
        return f"<OptimizationResult(id={self.id}, recommendation_id={self.recommendation_id})>"
    
    def calculate_overall_improvement(self) -> float:
        """Calculate overall improvement score."""
        improvements = []
        
        if self.throughput_improvement is not None:
            improvements.append(self.throughput_improvement)
        if self.latency_reduction is not None:
            improvements.append(self.latency_reduction)
        if self.memory_reduction is not None:
            improvements.append(self.memory_reduction)
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "recommendation_id": self.recommendation_id,
            "profile_id": self.profile_id,
            "before_run_id": self.before_run_id,
            "after_run_id": self.after_run_id,
            "improvements": {
                "throughput": self.throughput_improvement,
                "latency": self.latency_reduction,
                "memory": self.memory_reduction,
                "overall": self.calculate_overall_improvement(),
            },
            "metrics": {
                "before": self.before_metrics,
                "after": self.after_metrics,
                "improvements": self.metric_improvements or {},
            },
            "resource_usage": {
                "before": self.before_resource_usage or {},
                "after": self.after_resource_usage or {},
            },
            "cost_analysis": {
                "reduction": self.cost_reduction,
                "roi": self.roi_estimate,
            },
            "validation": {
                "validated": self.validated,
                "method": self.validation_method,
                "confidence": self.confidence_score,
                "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            },
            "notes": self.notes,
            "issues": self.issues_encountered or [],
            "environment_changes": self.environment_changes or {},
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }