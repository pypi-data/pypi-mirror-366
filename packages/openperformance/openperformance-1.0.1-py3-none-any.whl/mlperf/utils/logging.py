"""
Logging utilities for the ML Performance Engineering Platform.

This module provides structured logging with performance monitoring and
integration with external systems.
"""

import logging
import logging.config
import sys
import json
import time
import functools
from typing import Any, Dict, Optional, Callable
from pathlib import Path
from datetime import datetime

from .config import get_log_level, get_cache_directory


class PerformanceFilter(logging.Filter):
    """Custom logging filter that adds performance metrics."""
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
    
    def filter(self, record):
        """Add performance information to log records."""
        record.elapsed_time = time.time() - self.start_time
        record.timestamp_iso = datetime.now().isoformat()
        return True


class StructuredFormatter(logging.Formatter):
    """JSON structured logging formatter."""
    
    def __init__(self, include_fields: Optional[list] = None):
        super().__init__()
        self.include_fields = include_fields or [
            'timestamp', 'name', 'level', 'message', 'pathname', 'lineno'
        ]
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'name': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'pathname': record.pathname,
            'filename': record.filename,
            'lineno': record.lineno,
            'funcName': record.funcName,
            'process': record.process,
            'thread': record.thread,
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'elapsed_time'):
            log_data['elapsed_time'] = record.elapsed_time
        
        if hasattr(record, 'timestamp_iso'):
            log_data['timestamp_iso'] = record.timestamp_iso
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Filter fields based on include_fields
        if self.include_fields:
            log_data = {k: v for k, v in log_data.items() if k in self.include_fields}
        
        return json.dumps(log_data, default=str)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    structured: bool = True,
    enable_performance_filter: bool = True
) -> None:
    """
    Set up logging configuration for the platform.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs only to console)
        structured: Whether to use structured JSON logging
        enable_performance_filter: Whether to add performance metrics to logs
    """
    log_level = level or get_log_level()
    
    # Create handlers
    handlers = {}
    
    # Console handler
    console_handler = {
        'class': 'logging.StreamHandler',
        'level': log_level,
        'stream': 'ext://sys.stdout',
    }
    
    if structured:
        console_handler['formatter'] = 'structured'
    else:
        console_handler['formatter'] = 'standard'
    
    if enable_performance_filter:
        console_handler['filters'] = ['performance']
    
    handlers['console'] = console_handler
    
    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'filename': str(log_file),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'structured' if structured else 'standard',
        }
        
        if enable_performance_filter:
            file_handler['filters'] = ['performance']
        
        handlers['file'] = file_handler
    
    # Create formatters
    formatters = {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    }
    
    if structured:
        formatters['structured'] = {
            '()': 'mlperf.utils.logging.StructuredFormatter'
        }
    
    # Create filters
    filters = {}
    if enable_performance_filter:
        filters['performance'] = {
            '()': 'mlperf.utils.logging.PerformanceFilter'
        }
    
    # Logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'filters': filters,
        'handlers': handlers,
        'root': {
            'level': log_level,
            'handlers': list(handlers.keys())
        },
        'loggers': {
            'mlperf': {
                'level': log_level,
                'propagate': True
            },
            'uvicorn': {
                'level': 'INFO',
                'propagate': True
            },
            'fastapi': {
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    
    logging.config.dictConfig(config)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (defaults to calling module name)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if name is None:
        # Get the calling module name
        frame = sys._getframe(1)
        name = frame.f_globals.get('__name__', 'mlperf')
    
    return logging.getLogger(name)


def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function performance metrics.
    
    Args:
        func: Function to wrap
        
    Returns:
        Callable: Wrapped function with performance logging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed successfully",
                extra={
                    'function_name': func.__name__,
                    'execution_time': execution_time,
                    'success': True,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                f"Function {func.__name__} failed: {str(e)}",
                extra={
                    'function_name': func.__name__,
                    'execution_time': execution_time,
                    'success': False,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                },
                exc_info=True
            )
            
            raise
    
    return wrapper


def log_method_performance(cls):
    """
    Class decorator to add performance logging to all public methods.
    
    Args:
        cls: Class to decorate
        
    Returns:
        class: Decorated class with performance logging
    """
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        
        # Only decorate public methods (not starting with _)
        if (
            callable(attr) and 
            not attr_name.startswith('_') and 
            hasattr(attr, '__func__')
        ):
            setattr(cls, attr_name, log_performance(attr))
    
    return cls


class LoggingContext:
    """Context manager for adding structured logging context."""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_context = {}
    
    def __enter__(self):
        # Store old context and add new context
        for key, value in self.context.items():
            if hasattr(self.logger, key):
                self.old_context[key] = getattr(self.logger, key)
            setattr(self.logger, key, value)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old context
        for key in self.context:
            if key in self.old_context:
                setattr(self.logger, key, self.old_context[key])
            else:
                delattr(self.logger, key)


def create_audit_logger(name: str = "audit") -> logging.Logger:
    """
    Create a dedicated audit logger for security and compliance.
    
    Args:
        name: Name of the audit logger
        
    Returns:
        logging.Logger: Configured audit logger
    """
    audit_logger = logging.getLogger(f"mlperf.audit.{name}")
    
    # Create audit log file
    audit_log_file = get_cache_directory() / "logs" / f"audit_{name}.log"
    audit_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create file handler for audit logs
    handler = logging.handlers.RotatingFileHandler(
        audit_log_file,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10
    )
    
    # Use structured formatter for audit logs
    formatter = StructuredFormatter([
        'timestamp', 'level', 'message', 'pathname', 'lineno'
    ])
    handler.setFormatter(formatter)
    
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False  # Don't propagate to root logger
    
    return audit_logger


def setup_remote_logging(
    endpoint: str,
    api_key: Optional[str] = None,
    batch_size: int = 100,
    flush_interval: int = 60
) -> logging.Handler:
    """
    Set up remote logging to external service (e.g., Datadog, Splunk).
    
    Args:
        endpoint: Remote logging endpoint URL
        api_key: API key for authentication
        batch_size: Number of logs to batch before sending
        flush_interval: Interval in seconds to flush logs
        
    Returns:
        logging.Handler: Configured remote logging handler
    """
    # This is a simplified implementation
    # In production, you'd use proper libraries like datadog or splunk-sdk
    
    class RemoteHandler(logging.Handler):
        def __init__(self, endpoint, api_key, batch_size, flush_interval):
            super().__init__()
            self.endpoint = endpoint
            self.api_key = api_key
            self.batch_size = batch_size
            self.flush_interval = flush_interval
            self.buffer = []
            self.last_flush = time.time()
        
        def emit(self, record):
            try:
                log_entry = self.format(record)
                self.buffer.append(log_entry)
                
                # Flush if buffer is full or interval exceeded
                if (
                    len(self.buffer) >= self.batch_size or
                    time.time() - self.last_flush >= self.flush_interval
                ):
                    self.flush()
                    
            except Exception:
                self.handleError(record)
        
        def flush(self):
            if self.buffer:
                # Send logs to remote endpoint
                # Implementation would depend on the specific service
                self.buffer.clear()
                self.last_flush = time.time()
    
    handler = RemoteHandler(endpoint, api_key, batch_size, flush_interval)
    handler.setFormatter(StructuredFormatter())
    
    return handler


# Initialize default logging
try:
    log_file = get_cache_directory() / "logs" / "mlperf.log"
    setup_logging(log_file=log_file)
except Exception:
    # Fallback to basic logging if setup fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    ) 