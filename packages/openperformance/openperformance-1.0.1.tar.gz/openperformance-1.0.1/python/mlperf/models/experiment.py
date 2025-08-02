"""Experiment and ML model tracking database models."""

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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from mlperf.utils.database import Base


class ExperimentStatus(str, enum.Enum):
    """Status of experiments."""
    
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    ARCHIVED = "archived"


class ModelFramework(str, enum.Enum):
    """ML frameworks."""
    
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    JAX = "jax"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    CUSTOM = "custom"


class Experiment(Base):
    """ML experiment tracking."""
    
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Experiment configuration
    hypothesis = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    framework = Column(Enum(ModelFramework), nullable=False)
    model_architecture = Column(String(255), nullable=True)
    
    # Hyperparameters
    hyperparameters = Column(JSON, nullable=False, default={})
    search_space = Column(JSON, nullable=True)  # For hyperparameter tuning
    
    # Data configuration
    dataset_name = Column(String(255), nullable=True)
    dataset_version = Column(String(50), nullable=True)
    data_config = Column(JSON, nullable=True, default={})
    
    # Training configuration
    training_config = Column(JSON, nullable=False, default={})
    optimization_config = Column(JSON, nullable=True, default={})
    
    # Environment
    environment = Column(JSON, nullable=True)  # Python packages, system info
    requirements = Column(Text, nullable=True)  # requirements.txt content
    
    # Tracking
    tags = Column(JSON, nullable=True, default=[])
    data_metadata = Column(JSON, nullable=True, default={})
    notes = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.DRAFT, nullable=False, index=True)
    
    # Best results
    best_metric_name = Column(String(100), nullable=True)
    best_metric_value = Column(Float, nullable=True)
    best_run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="experiments")
    runs = relationship("ExperimentRun", back_populates="experiment", cascade="all, delete-orphan", foreign_keys="ExperimentRun.experiment_id")
    model_versions = relationship("ModelVersion", back_populates="experiment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_experiment_project", "project_id"),
        Index("idx_experiment_user", "user_id"),
        Index("idx_experiment_status", "status"),
        Index("idx_experiment_framework", "framework"),
    )
    
    def __repr__(self) -> str:
        return f"<Experiment(id={self.id}, name={self.name}, status={self.status})>"
    
    def update_best_result(self, metric_name: str, metric_value: float, run_id: int) -> bool:
        """Update best result if improved."""
        if self.best_metric_value is None or metric_value > self.best_metric_value:
            self.best_metric_name = metric_name
            self.best_metric_value = metric_value
            self.best_run_id = run_id
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "hypothesis": self.hypothesis,
            "objective": self.objective,
            "framework": self.framework.value,
            "model_architecture": self.model_architecture,
            "hyperparameters": self.hyperparameters,
            "search_space": self.search_space,
            "dataset": {
                "name": self.dataset_name,
                "version": self.dataset_version,
                "config": self.data_config or {},
            },
            "training_config": self.training_config,
            "optimization_config": self.optimization_config or {},
            "environment": self.environment or {},
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "notes": self.notes,
            "status": self.status.value,
            "best_result": {
                "metric_name": self.best_metric_name,
                "metric_value": self.best_metric_value,
                "run_id": self.best_run_id,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class ExperimentRun(Base):
    """Individual run within an experiment."""
    
    __tablename__ = "experiment_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False, index=True)
    run_number = Column(Integer, nullable=False)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Run configuration (may override experiment defaults)
    hyperparameters = Column(JSON, nullable=False, default={})
    config_overrides = Column(JSON, nullable=True, default={})
    
    # Hardware used
    hardware_profile_id = Column(Integer, ForeignKey("hardware_profiles.id"), nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Status
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.RUNNING, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Metrics
    metrics = Column(JSON, nullable=False, default={})  # All tracked metrics
    final_metrics = Column(JSON, nullable=True)  # Final/best metrics
    
    # Training progress
    current_epoch = Column(Integer, nullable=True)
    total_epochs = Column(Integer, nullable=True)
    current_step = Column(Integer, nullable=True)
    total_steps = Column(Integer, nullable=True)
    
    # Model artifacts
    model_path = Column(String(500), nullable=True)
    checkpoint_paths = Column(JSON, nullable=True, default=[])
    best_checkpoint_path = Column(String(500), nullable=True)
    
    # Logs and outputs
    log_path = Column(String(500), nullable=True)
    tensorboard_path = Column(String(500), nullable=True)
    artifacts_path = Column(String(500), nullable=True)
    
    # Metadata
    git_commit = Column(String(100), nullable=True)
    git_branch = Column(String(100), nullable=True)
    git_dirty = Column(Boolean, nullable=True)
    data_metadata = Column(JSON, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="runs", foreign_keys=[experiment_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_experiment_run_status", "status"),
        Index("idx_experiment_run_started", "started_at"),
        UniqueConstraint("experiment_id", "run_number", name="uq_experiment_run_number"),
    )
    
    def __repr__(self) -> str:
        return f"<ExperimentRun(id={self.id}, run_id={self.run_id}, status={self.status})>"
    
    def calculate_duration(self) -> Optional[float]:
        """Calculate run duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return self.duration_seconds
    
    def get_progress(self) -> Dict[str, Any]:
        """Get training progress."""
        progress = {}
        
        if self.total_epochs:
            progress["epoch_progress"] = (self.current_epoch or 0) / self.total_epochs * 100
        
        if self.total_steps:
            progress["step_progress"] = (self.current_step or 0) / self.total_steps * 100
        
        return progress
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "run_number": self.run_number,
            "run_id": self.run_id,
            "hyperparameters": self.hyperparameters,
            "config_overrides": self.config_overrides or {},
            "hardware_profile_id": self.hardware_profile_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.calculate_duration(),
            "status": self.status.value,
            "error_message": self.error_message,
            "metrics": self.metrics,
            "final_metrics": self.final_metrics or {},
            "progress": self.get_progress(),
            "current_epoch": self.current_epoch,
            "total_epochs": self.total_epochs,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "artifacts": {
                "model_path": self.model_path,
                "checkpoint_paths": self.checkpoint_paths or [],
                "best_checkpoint_path": self.best_checkpoint_path,
                "log_path": self.log_path,
                "tensorboard_path": self.tensorboard_path,
                "artifacts_path": self.artifacts_path,
            },
            "git": {
                "commit": self.git_commit,
                "branch": self.git_branch,
                "dirty": self.git_dirty,
            },
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ModelVersion(Base):
    """Versioned ML models from experiments."""
    
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False, index=True)
    run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=True)
    
    # Model identification
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Model details
    framework = Column(Enum(ModelFramework), nullable=False)
    architecture = Column(String(255), nullable=True)
    model_size_mb = Column(Float, nullable=True)
    parameter_count = Column(Integer, nullable=True)
    
    # Performance metrics
    metrics = Column(JSON, nullable=False, default={})
    benchmark_results = Column(JSON, nullable=True)
    
    # Model files
    model_path = Column(String(500), nullable=False)
    weights_path = Column(String(500), nullable=True)
    config_path = Column(String(500), nullable=True)
    
    # Deployment
    is_deployed = Column(Boolean, default=False)
    deployment_endpoints = Column(JSON, nullable=True, default=[])
    serving_framework = Column(String(100), nullable=True)  # TorchServe, TF Serving, etc.
    
    # Metadata
    tags = Column(JSON, nullable=True, default=[])
    data_metadata = Column(JSON, nullable=True, default={})
    
    # Status
    is_active = Column(Boolean, default=True)
    is_latest = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deployed_at = Column(DateTime, nullable=True)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="model_versions")
    
    # Indexes
    __table_args__ = (
        Index("idx_model_version_name", "name"),
        Index("idx_model_version_active", "is_active"),
        UniqueConstraint("name", "version", name="uq_model_name_version"),
    )
    
    def __repr__(self) -> str:
        return f"<ModelVersion(id={self.id}, name={self.name}, version={self.version})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "framework": self.framework.value,
            "architecture": self.architecture,
            "model_size_mb": self.model_size_mb,
            "parameter_count": self.parameter_count,
            "metrics": self.metrics,
            "benchmark_results": self.benchmark_results or {},
            "paths": {
                "model": self.model_path,
                "weights": self.weights_path,
                "config": self.config_path,
            },
            "deployment": {
                "is_deployed": self.is_deployed,
                "endpoints": self.deployment_endpoints or [],
                "serving_framework": self.serving_framework,
                "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            },
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "is_active": self.is_active,
            "is_latest": self.is_latest,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }