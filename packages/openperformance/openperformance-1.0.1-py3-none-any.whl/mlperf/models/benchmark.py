"""Benchmark-related database models."""

import enum
import json
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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from mlperf.utils.database import Base


class BenchmarkType(str, enum.Enum):
    """Types of benchmarks."""
    
    TRAINING = "training"
    INFERENCE = "inference"
    DISTRIBUTED = "distributed"
    MEMORY = "memory"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    CUSTOM = "custom"


class BenchmarkStatus(str, enum.Enum):
    """Status of benchmark runs."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Benchmark(Base):
    """Benchmark definition model."""
    
    __tablename__ = "benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(BenchmarkType), nullable=False, index=True)
    framework = Column(String(100), nullable=False, index=True)  # pytorch, tensorflow, jax
    version = Column(String(50), nullable=False)
    
    # Configuration
    config = Column(JSON, nullable=False, default={})
    default_params = Column(JSON, nullable=False, default={})
    validation_rules = Column(JSON, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True, default=[])
    category = Column(String(100), nullable=True, index=True)
    difficulty = Column(String(50), nullable=True)  # easy, medium, hard
    estimated_runtime = Column(Integer, nullable=True)  # in seconds
    
    # Resource requirements
    min_gpu_memory_gb = Column(Float, nullable=True)
    min_cpu_cores = Column(Integer, nullable=True)
    min_memory_gb = Column(Float, nullable=True)
    requires_cuda = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    runs = relationship("BenchmarkRun", back_populates="benchmark", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_benchmark_type_framework", "type", "framework"),
        Index("idx_benchmark_category", "category"),
    )
    
    def __repr__(self) -> str:
        return f"<Benchmark(id={self.id}, name={self.name}, type={self.type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "framework": self.framework,
            "version": self.version,
            "config": self.config,
            "tags": self.tags or [],
            "category": self.category,
            "difficulty": self.difficulty,
            "estimated_runtime": self.estimated_runtime,
            "resource_requirements": {
                "min_gpu_memory_gb": self.min_gpu_memory_gb,
                "min_cpu_cores": self.min_cpu_cores,
                "min_memory_gb": self.min_memory_gb,
                "requires_cuda": self.requires_cuda,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BenchmarkRun(Base):
    """Individual benchmark run instance."""
    
    __tablename__ = "benchmark_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    benchmark_id = Column(Integer, ForeignKey("benchmarks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    hardware_profile_id = Column(Integer, ForeignKey("hardware_profiles.id"), nullable=True, index=True)
    
    # Run details
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(BenchmarkStatus), default=BenchmarkStatus.PENDING, nullable=False, index=True)
    
    # Configuration
    parameters = Column(JSON, nullable=False, default={})
    environment = Column(JSON, nullable=True)  # Environment variables, versions, etc.
    
    # Timing
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Results summary
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    warnings = Column(JSON, nullable=True, default=[])
    
    # Performance metrics summary
    primary_metric = Column(Float, nullable=True)  # Main metric (e.g., throughput)
    primary_metric_name = Column(String(100), nullable=True)
    
    # Storage
    output_path = Column(String(500), nullable=True)
    log_path = Column(String(500), nullable=True)
    artifacts_path = Column(String(500), nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True, default=[])
    data_metadata = Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    benchmark = relationship("Benchmark", back_populates="runs")
    results = relationship("BenchmarkResult", back_populates="run", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_benchmark_run_status", "status"),
        Index("idx_benchmark_run_user", "user_id"),
        Index("idx_benchmark_run_project", "project_id"),
        Index("idx_benchmark_run_started", "started_at"),
        UniqueConstraint("run_id", name="uq_benchmark_run_id"),
    )
    
    def __repr__(self) -> str:
        return f"<BenchmarkRun(id={self.id}, run_id={self.run_id}, status={self.status})>"
    
    def calculate_duration(self) -> Optional[float]:
        """Calculate run duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return self.duration_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "run_id": self.run_id,
            "benchmark_id": self.benchmark_id,
            "benchmark_name": self.benchmark.name if self.benchmark else None,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "hardware_profile_id": self.hardware_profile_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "parameters": self.parameters,
            "environment": self.environment,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.calculate_duration(),
            "success": self.success,
            "error_message": self.error_message,
            "warnings": self.warnings or [],
            "primary_metric": self.primary_metric,
            "primary_metric_name": self.primary_metric_name,
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BenchmarkResult(Base):
    """Detailed benchmark results and metrics."""
    
    __tablename__ = "benchmark_results"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("benchmark_runs.id"), nullable=False, index=True)
    
    # Metric information
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    metric_type = Column(String(50), nullable=True)  # throughput, latency, accuracy, etc.
    
    # Additional context
    iteration = Column(Integer, nullable=True)
    epoch = Column(Integer, nullable=True)
    batch_size = Column(Integer, nullable=True)
    
    # Statistics
    mean = Column(Float, nullable=True)
    std = Column(Float, nullable=True)
    min = Column(Float, nullable=True)
    max = Column(Float, nullable=True)
    p50 = Column(Float, nullable=True)
    p90 = Column(Float, nullable=True)
    p95 = Column(Float, nullable=True)
    p99 = Column(Float, nullable=True)
    
    # Raw data (for detailed analysis)
    raw_values = Column(JSON, nullable=True)  # Array of individual measurements
    histogram = Column(JSON, nullable=True)  # Histogram data
    
    # Metadata
    data_metadata = Column(JSON, nullable=True, default={})
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    run = relationship("BenchmarkRun", back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index("idx_benchmark_result_run_metric", "run_id", "metric_name"),
        Index("idx_benchmark_result_metric", "metric_name"),
        Index("idx_benchmark_result_timestamp", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<BenchmarkResult(id={self.id}, metric={self.metric_name}, value={self.metric_value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "run_id": self.run_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "metric_type": self.metric_type,
            "iteration": self.iteration,
            "epoch": self.epoch,
            "batch_size": self.batch_size,
            "statistics": {
                "mean": self.mean,
                "std": self.std,
                "min": self.min,
                "max": self.max,
                "p50": self.p50,
                "p90": self.p90,
                "p95": self.p95,
                "p99": self.p99,
            },
            "metadata": self.metadata or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }