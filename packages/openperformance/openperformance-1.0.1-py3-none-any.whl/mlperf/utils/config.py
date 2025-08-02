"""
Configuration management for ML Performance Engineering Platform.

This module handles API keys, environment variables, and system configuration.
Enhanced with authentication and security settings.
"""

import os
import logging
import json
import yaml
from functools import lru_cache
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Enhanced application settings with authentication support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application settings
    APP_NAME: str = "OpenPerformance"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(False)
    ENVIRONMENT: str = Field("development")
    
    # API settings
    API_HOST: str = Field("0.0.0.0")
    API_PORT: int = Field(8000)
    API_PREFIX: str = Field("/api/v1")
    API_WORKERS: int = Field(1)
    API_RELOAD: bool = Field(False)
    
    # Security settings
    SECRET_KEY: str = Field("dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7)
    ALGORITHM: str = Field("HS256")
    BCRYPT_ROUNDS: int = Field(12)
    
    # Database settings
    DATABASE_URL: str = Field("sqlite:///mlperf.db")
    DATABASE_POOL_SIZE: int = Field(10)
    DATABASE_MAX_OVERFLOW: int = Field(20)
    DATABASE_POOL_PRE_PING: bool = Field(True)
    DATABASE_ECHO: bool = Field(False)
    
    # Redis settings
    REDIS_URL: str = Field("redis://localhost:6379/0")
    REDIS_POOL_SIZE: int = Field(10)
    REDIS_DECODE_RESPONSES: bool = Field(True)
    CACHE_TTL: int = Field(300)
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(["*"])
    CORS_ALLOW_CREDENTIALS: bool = Field(True)
    
    # Logging settings
    LOG_LEVEL: str = Field("INFO")
    LOG_FORMAT: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_FILE: Optional[str] = Field(None)
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = Field(True)
    RATE_LIMIT_DEFAULT: str = Field("100/hour")
    RATE_LIMIT_STORAGE_URL: Optional[str] = Field(None)
    
    # Security features
    ENFORCE_HTTPS: bool = Field(False)
    IP_WHITELIST: List[str] = Field([])
    MAX_LOGIN_ATTEMPTS: int = Field(5)
    LOCKOUT_DURATION_MINUTES: int = Field(30)
    
    # ML/GPU settings
    CUDA_VISIBLE_DEVICES: Optional[str] = Field(None)
    GPU_MEMORY_FRACTION: float = Field(0.9)
    ENABLE_MIXED_PRECISION: bool = Field(True)
    
    # Feature flags
    ENABLE_2FA: bool = Field(True)
    ENABLE_API_KEYS: bool = Field(True)
    ENABLE_AUDIT_LOGS: bool = Field(True)
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(None)
    ANTHROPIC_API_KEY: Optional[str] = Field(None)
    WANDB_API_KEY: Optional[str] = Field(None)
    
    # Directory settings
    CACHE_DIR: str = Field("./cache")
    RESULTS_DIR: str = Field("./results")
    OUTPUT_DIR: str = Field("./outputs")
    
    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key length."""
        if v == "dev-secret-key-change-in-production":
            logger.warning("Using default SECRET_KEY - change in production!")
        elif len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed}")
        return v
    
    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {allowed}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create settings instance
settings = get_settings()


@dataclass
class Config:
    """Legacy configuration class for backward compatibility."""
    openai_api_key: Optional[str] = None
    log_level: str = "INFO"
    log_file: Optional[str] = None
    redis_url: str = "redis://localhost:6379"
    database_url: str = "sqlite:///mlperf.db"
    cache_dir: str = "./cache"
    results_dir: str = "./results"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///mlperf.db"),
            cache_dir=os.getenv("MLPERF_CACHE_DIR", "./cache"),
            results_dir=os.getenv("MLPERF_RESULTS_DIR", "./results")
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """Load configuration from a file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path) as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def save(self, config_path: Path) -> None:
        """Save configuration to a file."""
        data = self.to_dict()
        
        with open(config_path, 'w') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)


# Legacy functions for backward compatibility
def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment or config."""
    return settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")


def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment variables."""
    return (
        settings.ANTHROPIC_API_KEY or
        os.getenv("ANTHROPIC_API_KEY") or 
        os.getenv("MLPERF_ANTHROPIC_KEY")
    )


def get_wandb_api_key() -> Optional[str]:
    """Get Weights & Biases API key from environment variables."""
    return (
        settings.WANDB_API_KEY or
        os.getenv("WANDB_API_KEY") or 
        os.getenv("MLPERF_WANDB_KEY")
    )


def get_mlflow_tracking_uri() -> str:
    """Get MLflow tracking URI."""
    return os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")


def get_redis_url() -> str:
    """Get Redis connection URL."""
    return settings.REDIS_URL


def get_database_url() -> str:
    """Get database connection URL."""
    return settings.DATABASE_URL


def get_log_level() -> str:
    """Get logging level from environment."""
    return settings.LOG_LEVEL


def get_cache_directory() -> Path:
    """Get cache directory path."""
    cache_dir = Path(settings.CACHE_DIR).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_output_directory() -> Path:
    """Get output directory for results."""
    output_dir = Path(settings.OUTPUT_DIR).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_distributed_config() -> Dict[str, Any]:
    """Get distributed training configuration."""
    return {
        "backend": os.getenv("MLPERF_DISTRIBUTED_BACKEND", "nccl"),
        "master_addr": os.getenv("MASTER_ADDR", "localhost"),
        "master_port": int(os.getenv("MASTER_PORT", "29500")),
        "world_size": int(os.getenv("WORLD_SIZE", "1")),
        "rank": int(os.getenv("RANK", "0")),
        "local_rank": int(os.getenv("LOCAL_RANK", "0")),
    }


def get_gpu_config() -> Dict[str, Any]:
    """Get GPU configuration."""
    return {
        "cuda_visible_devices": settings.CUDA_VISIBLE_DEVICES,
        "gpu_memory_fraction": settings.GPU_MEMORY_FRACTION,
        "allow_growth": os.getenv("GPU_ALLOW_GROWTH", "true").lower() == "true",
        "mixed_precision": settings.ENABLE_MIXED_PRECISION,
    }


def get_profiling_config() -> Dict[str, Any]:
    """Get profiling configuration."""
    return {
        "enable_profiling": os.getenv("ENABLE_PROFILING", "false").lower() == "true",
        "profile_memory": os.getenv("PROFILE_MEMORY", "true").lower() == "true",
        "profile_cpu": os.getenv("PROFILE_CPU", "true").lower() == "true",
        "profile_gpu": os.getenv("PROFILE_GPU", "true").lower() == "true",
        "profile_network": os.getenv("PROFILE_NETWORK", "false").lower() == "true",
        "trace_file_format": os.getenv("TRACE_FILE_FORMAT", "chrome"),
        "sample_rate": float(os.getenv("PROFILE_SAMPLE_RATE", "0.01")),
    }


def get_optimization_config() -> Dict[str, Any]:
    """Get optimization configuration."""
    return {
        "enable_activation_checkpointing": os.getenv("ACTIVATION_CHECKPOINTING", "false").lower() == "true",
        "enable_gradient_compression": os.getenv("GRADIENT_COMPRESSION", "false").lower() == "true",
        "enable_mixed_precision": settings.ENABLE_MIXED_PRECISION,
        "enable_cpu_offload": os.getenv("CPU_OFFLOAD", "false").lower() == "true",
        "bucket_size_mb": int(os.getenv("BUCKET_SIZE_MB", "25")),
        "compression_ratio": float(os.getenv("COMPRESSION_RATIO", "0.01")),
    }


def get_api_config() -> Dict[str, Any]:
    """Get API server configuration."""
    return {
        "host": settings.API_HOST,
        "port": settings.API_PORT,
        "workers": settings.API_WORKERS,
        "reload": settings.API_RELOAD,
        "debug": settings.DEBUG,
        "cors_origins": settings.CORS_ORIGINS,
    }


def get_monitoring_config() -> Dict[str, Any]:
    """Get monitoring configuration."""
    return {
        "enable_prometheus": os.getenv("ENABLE_PROMETHEUS", "false").lower() == "true",
        "prometheus_port": int(os.getenv("PROMETHEUS_PORT", "9090")),
        "enable_grafana": os.getenv("ENABLE_GRAFANA", "false").lower() == "true",
        "grafana_url": os.getenv("GRAFANA_URL", "http://localhost:3000"),
        "metrics_collection_interval": int(os.getenv("METRICS_INTERVAL", "10")),
    }


def get_security_config() -> Dict[str, Any]:
    """Get security configuration."""
    return {
        "secret_key": settings.SECRET_KEY,
        "enable_auth": os.getenv("ENABLE_AUTH", "false").lower() == "true",
        "jwt_expiry_hours": settings.ACCESS_TOKEN_EXPIRE_MINUTES / 60,
        "rate_limit": settings.RATE_LIMIT_DEFAULT,
    }


def get_config() -> Config:
    """Get the current configuration."""
    # Try to load from file first, then environment
    config_file = Path("config.yaml")
    if config_file.exists():
        return Config.from_file(config_file)
    
    config_file = Path("config.json")
    if config_file.exists():
        return Config.from_file(config_file)
    
    # Fallback to environment
    return Config.from_env()


def reload_config() -> Config:
    """Reload configuration from environment variables."""
    global config
    config = Config()
    return config