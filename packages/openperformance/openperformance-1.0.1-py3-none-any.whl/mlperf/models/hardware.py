"""Hardware-related database models."""

import enum
from datetime import datetime
from typing import Any, Dict, Optional

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


class HardwareType(str, enum.Enum):
    """Types of hardware."""
    
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    NPU = "npu"
    CUSTOM = "custom"


class GPUModel(str, enum.Enum):
    """Common GPU models."""
    
    # NVIDIA Consumer
    RTX_4090 = "rtx_4090"
    RTX_4080 = "rtx_4080"
    RTX_4070_TI = "rtx_4070_ti"
    RTX_4070 = "rtx_4070"
    RTX_3090 = "rtx_3090"
    RTX_3080 = "rtx_3080"
    RTX_3070 = "rtx_3070"
    
    # NVIDIA Data Center
    H100 = "h100"
    A100 = "a100"
    A40 = "a40"
    A30 = "a30"
    A10 = "a10"
    V100 = "v100"
    T4 = "t4"
    
    # AMD
    MI300X = "mi300x"
    MI250X = "mi250x"
    MI210 = "mi210"
    MI100 = "mi100"
    
    # Other
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class HardwareProfile(Base):
    """Hardware configuration profile."""
    
    __tablename__ = "hardware_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # System information
    hostname = Column(String(255), nullable=True)
    platform = Column(String(100), nullable=True)  # Linux, Windows, macOS
    platform_version = Column(String(100), nullable=True)
    architecture = Column(String(50), nullable=True)  # x86_64, arm64
    
    # CPU information
    cpu_model = Column(String(255), nullable=True)
    cpu_cores = Column(Integer, nullable=True)
    cpu_threads = Column(Integer, nullable=True)
    cpu_frequency_ghz = Column(Float, nullable=True)
    cpu_cache_mb = Column(Float, nullable=True)
    
    # Memory information
    memory_total_gb = Column(Float, nullable=True)
    memory_speed_mhz = Column(Integer, nullable=True)
    memory_type = Column(String(50), nullable=True)  # DDR4, DDR5
    
    # GPU information
    gpu_count = Column(Integer, default=0)
    gpu_models = Column(JSON, nullable=True)  # List of GPU models
    gpu_memory_total_gb = Column(Float, nullable=True)
    gpu_driver_version = Column(String(50), nullable=True)
    cuda_version = Column(String(50), nullable=True)
    
    # Storage information
    storage_type = Column(String(50), nullable=True)  # SSD, HDD, NVMe
    storage_total_gb = Column(Float, nullable=True)
    storage_speed_mbps = Column(Float, nullable=True)
    
    # Network information
    network_type = Column(String(100), nullable=True)  # Ethernet, InfiniBand
    network_speed_gbps = Column(Float, nullable=True)
    
    # Cloud/Cluster information
    is_cloud = Column(Boolean, default=False)
    cloud_provider = Column(String(100), nullable=True)  # AWS, GCP, Azure
    instance_type = Column(String(100), nullable=True)
    cluster_name = Column(String(255), nullable=True)
    node_count = Column(Integer, nullable=True)
    
    # Additional metadata
    data_metadata = Column(JSON, nullable=True, default={})
    tags = Column(JSON, nullable=True, default=[])
    
    # Validation and benchmarking
    validated = Column(Boolean, default=False)
    validation_date = Column(DateTime, nullable=True)
    benchmark_scores = Column(JSON, nullable=True)  # Standard benchmark results
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, nullable=True)
    
    # Relationships
    benchmark_runs = relationship("BenchmarkRun", backref="hardware_profile")
    system_metrics = relationship("SystemMetrics", back_populates="hardware_profile", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_hardware_profile_user", "user_id"),
        Index("idx_hardware_profile_org", "organization_id"),
        Index("idx_hardware_profile_platform", "platform"),
        UniqueConstraint("name", "user_id", name="uq_hardware_profile_name_user"),
    )
    
    def __repr__(self) -> str:
        return f"<HardwareProfile(id={self.id}, name={self.name}, gpus={self.gpu_count})>"
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information summary."""
        if not self.gpu_models:
            return {"count": 0, "models": [], "total_memory_gb": 0}
        
        return {
            "count": self.gpu_count,
            "models": self.gpu_models,
            "total_memory_gb": self.gpu_memory_total_gb,
            "driver_version": self.gpu_driver_version,
            "cuda_version": self.cuda_version,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "system": {
                "hostname": self.hostname,
                "platform": self.platform,
                "platform_version": self.platform_version,
                "architecture": self.architecture,
            },
            "cpu": {
                "model": self.cpu_model,
                "cores": self.cpu_cores,
                "threads": self.cpu_threads,
                "frequency_ghz": self.cpu_frequency_ghz,
                "cache_mb": self.cpu_cache_mb,
            },
            "memory": {
                "total_gb": self.memory_total_gb,
                "speed_mhz": self.memory_speed_mhz,
                "type": self.memory_type,
            },
            "gpu": self.get_gpu_info(),
            "storage": {
                "type": self.storage_type,
                "total_gb": self.storage_total_gb,
                "speed_mbps": self.storage_speed_mbps,
            },
            "network": {
                "type": self.network_type,
                "speed_gbps": self.network_speed_gbps,
            },
            "cloud": {
                "is_cloud": self.is_cloud,
                "provider": self.cloud_provider,
                "instance_type": self.instance_type,
            },
            "cluster": {
                "name": self.cluster_name,
                "node_count": self.node_count,
            },
            "metadata": self.metadata or {},
            "tags": self.tags or [],
            "validated": self.validated,
            "validation_date": self.validation_date.isoformat() if self.validation_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SystemMetrics(Base):
    """Real-time system metrics and monitoring data."""
    
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    hardware_profile_id = Column(Integer, ForeignKey("hardware_profiles.id"), nullable=False, index=True)
    benchmark_run_id = Column(Integer, ForeignKey("benchmark_runs.id"), nullable=True, index=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # CPU metrics
    cpu_usage_percent = Column(Float, nullable=True)
    cpu_usage_per_core = Column(JSON, nullable=True)  # Array of per-core usage
    cpu_temperature_c = Column(Float, nullable=True)
    cpu_frequency_mhz = Column(Float, nullable=True)
    
    # Memory metrics
    memory_used_gb = Column(Float, nullable=True)
    memory_available_gb = Column(Float, nullable=True)
    memory_percent = Column(Float, nullable=True)
    swap_used_gb = Column(Float, nullable=True)
    swap_percent = Column(Float, nullable=True)
    
    # GPU metrics (aggregated)
    gpu_usage_percent = Column(Float, nullable=True)
    gpu_memory_used_gb = Column(Float, nullable=True)
    gpu_memory_percent = Column(Float, nullable=True)
    gpu_temperature_c = Column(Float, nullable=True)
    gpu_power_watts = Column(Float, nullable=True)
    
    # Per-GPU metrics
    gpu_metrics = Column(JSON, nullable=True)  # Detailed per-GPU metrics
    
    # Disk I/O
    disk_read_mbps = Column(Float, nullable=True)
    disk_write_mbps = Column(Float, nullable=True)
    disk_usage_percent = Column(Float, nullable=True)
    
    # Network I/O
    network_sent_mbps = Column(Float, nullable=True)
    network_recv_mbps = Column(Float, nullable=True)
    
    # Process-specific metrics
    process_count = Column(Integer, nullable=True)
    thread_count = Column(Integer, nullable=True)
    
    # Additional metrics
    metrics = Column(JSON, nullable=True)  # Flexible additional metrics
    
    # Relationships
    hardware_profile = relationship("HardwareProfile", back_populates="system_metrics")
    
    # Indexes
    __table_args__ = (
        Index("idx_system_metrics_profile_time", "hardware_profile_id", "timestamp"),
        Index("idx_system_metrics_run", "benchmark_run_id"),
        Index("idx_system_metrics_timestamp", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<SystemMetrics(id={self.id}, profile_id={self.hardware_profile_id}, time={self.timestamp})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "hardware_profile_id": self.hardware_profile_id,
            "benchmark_run_id": self.benchmark_run_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "cpu": {
                "usage_percent": self.cpu_usage_percent,
                "usage_per_core": self.cpu_usage_per_core,
                "temperature_c": self.cpu_temperature_c,
                "frequency_mhz": self.cpu_frequency_mhz,
            },
            "memory": {
                "used_gb": self.memory_used_gb,
                "available_gb": self.memory_available_gb,
                "percent": self.memory_percent,
                "swap_used_gb": self.swap_used_gb,
                "swap_percent": self.swap_percent,
            },
            "gpu": {
                "usage_percent": self.gpu_usage_percent,
                "memory_used_gb": self.gpu_memory_used_gb,
                "memory_percent": self.gpu_memory_percent,
                "temperature_c": self.gpu_temperature_c,
                "power_watts": self.gpu_power_watts,
                "per_gpu_metrics": self.gpu_metrics,
            },
            "disk": {
                "read_mbps": self.disk_read_mbps,
                "write_mbps": self.disk_write_mbps,
                "usage_percent": self.disk_usage_percent,
            },
            "network": {
                "sent_mbps": self.network_sent_mbps,
                "recv_mbps": self.network_recv_mbps,
            },
            "process": {
                "count": self.process_count,
                "thread_count": self.thread_count,
            },
            "additional_metrics": self.metrics or {},
        }