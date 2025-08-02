"""
CPU monitoring and information gathering.
"""

import os
import psutil
from dataclasses import dataclass
from typing import Dict, List, Optional
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CPUInfo:
    """CPU information container."""
    
    # Basic info
    physical_cores: int
    logical_cores: int
    architecture: str
    processor_name: str
    
    # Current state
    usage_percent: float
    frequency_mhz: Optional[float]
    temperature_c: Optional[float]
    
    # Load averages (Unix-like systems)
    load_avg_1min: Optional[float]
    load_avg_5min: Optional[float]
    load_avg_15min: Optional[float]
    
    # Cache info
    l1_cache_size: Optional[int]
    l2_cache_size: Optional[int]
    l3_cache_size: Optional[int]
    
    # Performance
    current_freq_mhz: Optional[float]
    min_freq_mhz: Optional[float]
    max_freq_mhz: Optional[float]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "physical_cores": self.physical_cores,
            "logical_cores": self.logical_cores,
            "architecture": self.architecture,
            "processor_name": self.processor_name,
            "usage_percent": self.usage_percent,
            "frequency_mhz": self.frequency_mhz,
            "temperature_c": self.temperature_c,
            "load_avg_1min": self.load_avg_1min,
            "load_avg_5min": self.load_avg_5min,
            "load_avg_15min": self.load_avg_15min,
            "l1_cache_size": self.l1_cache_size,
            "l2_cache_size": self.l2_cache_size,
            "l3_cache_size": self.l3_cache_size,
            "current_freq_mhz": self.current_freq_mhz,
            "min_freq_mhz": self.min_freq_mhz,
            "max_freq_mhz": self.max_freq_mhz,
        }


def get_cpu_info() -> CPUInfo:
    """Get comprehensive CPU information."""
    try:
        # Basic CPU info
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        
        # Architecture and processor name
        architecture = os.uname().machine if hasattr(os, 'uname') else "unknown"
        processor_name = "Unknown"
        
        # Try to get processor name from various sources
        try:
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("model name"):
                            processor_name = line.split(":")[1].strip()
                            break
            elif os.path.exists("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies"):
                processor_name = "ARM Processor"  # Likely ARM
            else:
                processor_name = "x86_64 Processor"  # Default assumption
        except Exception:
            processor_name = "Unknown Processor"
        
        # Current usage
        usage_percent = psutil.cpu_percent(interval=0.1)
        
        # Frequency info
        freq_info = psutil.cpu_freq()
        current_freq = freq_info.current if freq_info else None
        min_freq = freq_info.min if freq_info else None
        max_freq = freq_info.max if freq_info else None
        
        # Load averages (Unix-like systems)
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (None, None, None)
        
        # Temperature (platform dependent)
        temperature = None
        try:
            if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    temp_raw = f.read().strip()
                    temperature = float(temp_raw) / 1000.0  # Convert from millidegrees
        except Exception:
            pass
        
        # Cache sizes (platform dependent)
        l1_cache = None
        l2_cache = None
        l3_cache = None
        
        try:
            if os.path.exists("/sys/devices/system/cpu/cpu0/cache"):
                # Try to read cache info from sysfs
                for i in range(4):  # Check first 4 cache levels
                    cache_path = f"/sys/devices/system/cpu/cpu0/cache/index{i}"
                    if os.path.exists(f"{cache_path}/size"):
                        with open(f"{cache_path}/size", "r") as f:
                            size_str = f.read().strip()
                            size_kb = int(size_str.replace("K", ""))
                            if i == 0:
                                l1_cache = size_kb * 1024
                            elif i == 1:
                                l2_cache = size_kb * 1024
                            elif i == 2:
                                l3_cache = size_kb * 1024
        except Exception:
            pass
        
        return CPUInfo(
            physical_cores=physical_cores or 0,
            logical_cores=logical_cores or 0,
            architecture=architecture,
            processor_name=processor_name,
            usage_percent=usage_percent,
            frequency_mhz=current_freq,
            temperature_c=temperature,
            load_avg_1min=load_avg[0] if load_avg[0] is not None else None,
            load_avg_5min=load_avg[1] if load_avg[1] is not None else None,
            load_avg_15min=load_avg[2] if load_avg[2] is not None else None,
            l1_cache_size=l1_cache,
            l2_cache_size=l2_cache,
            l3_cache_size=l3_cache,
            current_freq_mhz=current_freq,
            min_freq_mhz=min_freq,
            max_freq_mhz=max_freq,
        )
        
    except Exception as e:
        logger.error(f"Error getting CPU info: {e}")
        # Return minimal info
        return CPUInfo(
            physical_cores=os.cpu_count() or 0,
            logical_cores=os.cpu_count() or 0,
            architecture="unknown",
            processor_name="Unknown",
            usage_percent=0.0,
            frequency_mhz=None,
            temperature_c=None,
            load_avg_1min=None,
            load_avg_5min=None,
            load_avg_15min=None,
            l1_cache_size=None,
            l2_cache_size=None,
            l3_cache_size=None,
            current_freq_mhz=None,
            min_freq_mhz=None,
            max_freq_mhz=None,
        ) 