"""
GPU hardware monitoring and information module.

This module provides comprehensive GPU monitoring, information gathering,
and performance metrics for the ML Performance Engineering Platform.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GPUMemoryInfo:
    """GPU memory information."""
    total: int  # Total memory in bytes
    free: int   # Free memory in bytes
    used: int   # Used memory in bytes
    utilization: float  # Memory utilization percentage


@dataclass
class GPUProcessInfo:
    """Information about a process using the GPU."""
    pid: int
    process_name: str
    memory_used: int  # Memory used by this process in bytes


@dataclass
class MemoryUsage:
    """Memory usage information for tracking."""
    timestamp: float
    device: str
    total_bytes: int
    used_bytes: int
    reserved_bytes: int = 0
    active_bytes: int = 0
    inactive_bytes: int = 0
    fragmentation: float = 0.0
    
    @property
    def utilization(self) -> float:
        """Calculate memory utilization percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.used_bytes / self.total_bytes) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "device": self.device,
            "total_bytes": self.total_bytes,
            "used_bytes": self.used_bytes,
            "reserved_bytes": self.reserved_bytes,
            "active_bytes": self.active_bytes,
            "inactive_bytes": self.inactive_bytes,
            "fragmentation": self.fragmentation,
            "utilization": self.utilization
        }


@dataclass
class GPUInfo:
    """Comprehensive GPU information."""
    index: int
    name: str
    uuid: str
    driver_version: str
    cuda_version: str
    memory: GPUMemoryInfo
    temperature: float  # Temperature in Celsius
    power_usage: float  # Power usage in watts
    power_limit: float  # Power limit in watts
    utilization: float  # GPU utilization percentage
    memory_utilization: float  # Memory utilization percentage
    fan_speed: int  # Fan speed percentage
    processes: List[GPUProcessInfo]
    compute_capability: Tuple[int, int]  # Major, minor version
    multi_gpu_board: bool
    board_id: int
    clock_speeds: Dict[str, int]  # Current clock speeds
    max_clock_speeds: Dict[str, int]  # Maximum clock speeds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['memory'] = asdict(self.memory)
        data['processes'] = [asdict(p) for p in self.processes]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GPUInfo':
        """Create from dictionary."""
        memory_data = data.pop('memory')
        processes_data = data.pop('processes', [])
        
        memory = GPUMemoryInfo(**memory_data)
        processes = [GPUProcessInfo(**p) for p in processes_data]
        
        return cls(
            memory=memory,
            processes=processes,
            **data
        )


class GPUMonitor:
    """Real-time GPU monitoring."""
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Initialize NVML if available
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
                logger.info("NVIDIA ML library initialized successfully")
            except Exception as e:
                self.nvml_initialized = False
                logger.warning(f"Failed to initialize NVIDIA ML library: {e}")
        else:
            self.nvml_initialized = False
            logger.warning("NVIDIA ML library not available")
    
    def start_monitoring(self) -> None:
        """Start continuous GPU monitoring."""
        if self.monitoring:
            logger.warning("GPU monitoring already started")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("GPU monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop GPU monitoring."""
        if not self.monitoring:
            logger.warning("GPU monitoring not started")
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("GPU monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self.monitoring:
            try:
                metrics = self.get_current_metrics()
                
                # Add timestamp
                metrics['timestamp'] = datetime.now().isoformat()
                
                # Store in history
                self.metrics_history.append(metrics)
                
                # Limit history size
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
            except Exception as e:
                logger.error(f"Error in GPU monitoring loop: {e}")
            
            time.sleep(self.update_interval)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current GPU metrics."""
        metrics = {
            'gpus': [],
            'total_memory_used': 0,
            'total_memory_available': 0,
            'average_utilization': 0,
            'average_temperature': 0,
            'total_power_usage': 0,
        }
        
        gpu_infos = get_gpu_info()
        
        if not gpu_infos:
            return metrics
        
        total_util = 0
        total_temp = 0
        
        for gpu in gpu_infos:
            gpu_metrics = {
                'index': gpu.index,
                'name': gpu.name,
                'memory_used': gpu.memory.used,
                'memory_total': gpu.memory.total,
                'memory_utilization': gpu.memory_utilization,
                'utilization': gpu.utilization,
                'temperature': gpu.temperature,
                'power_usage': gpu.power_usage,
                'fan_speed': gpu.fan_speed,
                'processes': len(gpu.processes),
            }
            
            metrics['gpus'].append(gpu_metrics)
            metrics['total_memory_used'] += gpu.memory.used
            metrics['total_memory_available'] += gpu.memory.total
            total_util += gpu.utilization
            total_temp += gpu.temperature
            metrics['total_power_usage'] += gpu.power_usage
        
        # Calculate averages
        num_gpus = len(gpu_infos)
        metrics['average_utilization'] = total_util / num_gpus if num_gpus > 0 else 0
        metrics['average_temperature'] = total_temp / num_gpus if num_gpus > 0 else 0
        
        return metrics
    
    def get_metrics_history(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get metrics history."""
        if last_n is None:
            return self.metrics_history.copy()
        return self.metrics_history[-last_n:].copy()
    
    def get_peak_metrics(self) -> Dict[str, Any]:
        """Get peak metrics from history."""
        if not self.metrics_history:
            return {}
        
        peak_metrics = {
            'max_memory_used': 0,
            'max_utilization': 0,
            'max_temperature': 0,
            'max_power_usage': 0,
            'peak_timestamp': None,
        }
        
        for metrics in self.metrics_history:
            if metrics['total_memory_used'] > peak_metrics['max_memory_used']:
                peak_metrics['max_memory_used'] = metrics['total_memory_used']
            
            if metrics['average_utilization'] > peak_metrics['max_utilization']:
                peak_metrics['max_utilization'] = metrics['average_utilization']
                peak_metrics['peak_timestamp'] = metrics['timestamp']
            
            if metrics['average_temperature'] > peak_metrics['max_temperature']:
                peak_metrics['max_temperature'] = metrics['average_temperature']
            
            if metrics['total_power_usage'] > peak_metrics['max_power_usage']:
                peak_metrics['max_power_usage'] = metrics['total_power_usage']
        
        return peak_metrics


def get_gpu_count() -> int:
    """Get the number of available GPUs."""
    if not PYNVML_AVAILABLE:
        return 0
    
    try:
        pynvml.nvmlInit()
        return pynvml.nvmlDeviceGetCount()
    except Exception:
        return 0


def get_gpu_info(gpu_index: Optional[int] = None) -> List[GPUInfo]:
    """
    Get comprehensive information about GPUs.
    
    Args:
        gpu_index: Specific GPU index to query (if None, returns all GPUs)
        
    Returns:
        List[GPUInfo]: List of GPU information objects
    """
    gpus = []
    
    if not PYNVML_AVAILABLE:
        logger.warning("NVIDIA ML library not available, returning empty GPU info")
        return gpus
    
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        
        # Determine which GPUs to query
        if gpu_index is not None:
            if 0 <= gpu_index < device_count:
                indices = [gpu_index]
            else:
                logger.error(f"Invalid GPU index {gpu_index}, available: 0-{device_count-1}")
                return gpus
        else:
            indices = list(range(device_count))
        
        for i in indices:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                gpu_info = _get_single_gpu_info(handle, i)
                gpus.append(gpu_info)
            except Exception as e:
                logger.error(f"Failed to get info for GPU {i}: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Failed to initialize NVML or get GPU info: {e}")
    
    return gpus


def _get_single_gpu_info(handle, index: int) -> GPUInfo:
    """Get information for a single GPU."""
    # Basic device info
    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
    uuid = pynvml.nvmlDeviceGetUUID(handle).decode('utf-8')
    
    # Driver and CUDA version
    try:
        driver_version = pynvml.nvmlSystemGetDriverVersion().decode('utf-8')
    except Exception:
        driver_version = "Unknown"
    
    try:
        cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
        cuda_version = f"{cuda_version // 1000}.{(cuda_version % 1000) // 10}"
    except Exception:
        cuda_version = "Unknown"
    
    # Memory information
    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    memory = GPUMemoryInfo(
        total=memory_info.total,
        free=memory_info.free,
        used=memory_info.used,
        utilization=(memory_info.used / memory_info.total) * 100 if memory_info.total > 0 else 0
    )
    
    # Temperature
    try:
        temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    except Exception:
        temperature = 0.0
    
    # Power information
    try:
        power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
    except Exception:
        power_usage = 0.0
    
    try:
        power_limit = pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] / 1000.0
    except Exception:
        power_limit = 0.0
    
    # Utilization
    try:
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        utilization = util.gpu
        memory_utilization = util.memory
    except Exception:
        utilization = 0.0
        memory_utilization = 0.0
    
    # Fan speed
    try:
        fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
    except Exception:
        fan_speed = 0
    
    # Running processes
    processes = []
    try:
        proc_infos = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        for proc in proc_infos:
            try:
                proc_name = pynvml.nvmlSystemGetProcessName(proc.pid).decode('utf-8')
            except Exception:
                proc_name = f"PID {proc.pid}"
            
            processes.append(GPUProcessInfo(
                pid=proc.pid,
                process_name=proc_name,
                memory_used=proc.usedGpuMemory if hasattr(proc, 'usedGpuMemory') else 0
            ))
    except Exception:
        pass
    
    # Compute capability
    try:
        major = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[0]
        minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[1]
        compute_capability = (major, minor)
    except Exception:
        compute_capability = (0, 0)
    
    # Multi-GPU board information
    try:
        multi_gpu_board = pynvml.nvmlDeviceOnSameBoard(handle, handle)
        board_id = pynvml.nvmlDeviceGetBoardId(handle)
    except Exception:
        multi_gpu_board = False
        board_id = 0
    
    # Clock speeds
    clock_speeds = {}
    max_clock_speeds = {}
    
    try:
        clock_speeds['graphics'] = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
        clock_speeds['memory'] = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
        clock_speeds['sm'] = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_SM)
    except Exception:
        pass
    
    try:
        max_clock_speeds['graphics'] = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
        max_clock_speeds['memory'] = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_MEM)
        max_clock_speeds['sm'] = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_SM)
    except Exception:
        pass
    
    return GPUInfo(
        index=index,
        name=name,
        uuid=uuid,
        driver_version=driver_version,
        cuda_version=cuda_version,
        memory=memory,
        temperature=temperature,
        power_usage=power_usage,
        power_limit=power_limit,
        utilization=utilization,
        memory_utilization=memory_utilization,
        fan_speed=fan_speed,
        processes=processes,
        compute_capability=compute_capability,
        multi_gpu_board=multi_gpu_board,
        board_id=board_id,
        clock_speeds=clock_speeds,
        max_clock_speeds=max_clock_speeds,
    )


def get_cuda_info() -> Dict[str, Any]:
    """Get CUDA runtime and driver information."""
    info = {
        'cuda_available': False,
        'cuda_version': None,
        'cudnn_version': None,
        'driver_version': None,
        'device_count': 0,
        'devices': [],
    }
    
    # PyTorch CUDA info
    if TORCH_AVAILABLE:
        info['cuda_available'] = torch.cuda.is_available()
        if info['cuda_available']:
            info['device_count'] = torch.cuda.device_count()
            info['cuda_version'] = torch.version.cuda
            
            try:
                info['cudnn_version'] = torch.backends.cudnn.version()
            except Exception:
                pass
            
            # Device properties
            for i in range(info['device_count']):
                props = torch.cuda.get_device_properties(i)
                device_info = {
                    'index': i,
                    'name': props.name,
                    'total_memory': props.total_memory,
                    'major': props.major,
                    'minor': props.minor,
                    'multi_processor_count': props.multi_processor_count,
                }
                info['devices'].append(device_info)
    
    # TensorFlow CUDA info
    elif TF_AVAILABLE:
        physical_devices = tf.config.list_physical_devices('GPU')
        info['cuda_available'] = len(physical_devices) > 0
        info['device_count'] = len(physical_devices)
        
        for i, device in enumerate(physical_devices):
            device_info = {
                'index': i,
                'name': device.name,
                'device_type': device.device_type,
            }
            info['devices'].append(device_info)
    
    # NVML driver version
    if PYNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            info['driver_version'] = pynvml.nvmlSystemGetDriverVersion().decode('utf-8')
        except Exception:
            pass
    
    return info


def set_gpu_memory_growth(enable: bool = True) -> None:
    """Set GPU memory growth to avoid allocating all memory upfront."""
    if TF_AVAILABLE:
        try:
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, enable)
                logger.info(f"Set GPU memory growth to {enable} for {len(gpus)} GPUs")
        except Exception as e:
            logger.error(f"Failed to set GPU memory growth: {e}")
    else:
        logger.warning("TensorFlow not available, cannot set GPU memory growth")


def limit_gpu_memory(memory_limit_mb: int, gpu_index: int = 0) -> None:
    """Limit GPU memory usage."""
    if TF_AVAILABLE:
        try:
            gpus = tf.config.list_physical_devices('GPU')
            if gpus and gpu_index < len(gpus):
                tf.config.experimental.set_virtual_device_configuration(
                    gpus[gpu_index],
                    [tf.config.experimental.VirtualDeviceConfiguration(
                        memory_limit=memory_limit_mb
                    )]
                )
                logger.info(f"Limited GPU {gpu_index} memory to {memory_limit_mb}MB")
        except Exception as e:
            logger.error(f"Failed to limit GPU memory: {e}")
    else:
        logger.warning("TensorFlow not available, cannot limit GPU memory")


def clear_gpu_memory() -> None:
    """Clear GPU memory cache."""
    if TORCH_AVAILABLE and torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("Cleared PyTorch GPU memory cache")
    
    if TF_AVAILABLE:
        try:
            tf.keras.backend.clear_session()
            logger.info("Cleared TensorFlow GPU memory")
        except Exception as e:
            logger.error(f"Failed to clear TensorFlow GPU memory: {e}")


def get_optimal_batch_size(
    model_memory_mb: float,
    available_memory_mb: float,
    safety_factor: float = 0.8
) -> int:
    """
    Estimate optimal batch size based on model and available memory.
    
    Args:
        model_memory_mb: Memory required for the model in MB
        available_memory_mb: Available GPU memory in MB
        safety_factor: Safety factor to leave memory headroom
        
    Returns:
        int: Estimated optimal batch size
    """
    usable_memory = available_memory_mb * safety_factor
    
    if model_memory_mb <= 0:
        logger.warning("Invalid model memory size, returning batch size 1")
        return 1
    
    # Rough estimation - assumes linear scaling with batch size
    # In practice, this would be more sophisticated
    estimated_batch_size = max(1, int(usable_memory / model_memory_mb))
    
    logger.info(
        f"Estimated optimal batch size: {estimated_batch_size} "
        f"(model: {model_memory_mb}MB, available: {available_memory_mb}MB)"
    )
    
    return estimated_batch_size


# Global GPU monitor instance
_gpu_monitor: Optional[GPUMonitor] = None


def get_gpu_monitor() -> GPUMonitor:
    """Get the global GPU monitor instance."""
    global _gpu_monitor
    if _gpu_monitor is None:
        _gpu_monitor = GPUMonitor()
    return _gpu_monitor 