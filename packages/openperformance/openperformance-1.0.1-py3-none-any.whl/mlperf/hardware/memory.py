"""
Memory monitoring and information gathering.
"""

import psutil
from dataclasses import dataclass
from typing import Dict, Optional
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MemoryInfo:
    """Memory information container."""
    
    # Total memory
    total_bytes: int
    available_bytes: int
    used_bytes: int
    free_bytes: int
    
    # Usage percentages
    usage_percent: float
    available_percent: float
    
    # Memory types (if available)
    active_bytes: Optional[int]
    inactive_bytes: Optional[int]
    buffers_bytes: Optional[int]
    cached_bytes: Optional[int]
    shared_bytes: Optional[int]
    slab_bytes: Optional[int]
    
    # Swap information
    swap_total_bytes: Optional[int]
    swap_used_bytes: Optional[int]
    swap_free_bytes: Optional[int]
    swap_percent: Optional[float]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "total_bytes": self.total_bytes,
            "available_bytes": self.available_bytes,
            "used_bytes": self.used_bytes,
            "free_bytes": self.free_bytes,
            "usage_percent": self.usage_percent,
            "available_percent": self.available_percent,
            "active_bytes": self.active_bytes,
            "inactive_bytes": self.inactive_bytes,
            "buffers_bytes": self.buffers_bytes,
            "cached_bytes": self.cached_bytes,
            "shared_bytes": self.shared_bytes,
            "slab_bytes": self.slab_bytes,
            "swap_total_bytes": self.swap_total_bytes,
            "swap_used_bytes": self.swap_used_bytes,
            "swap_free_bytes": self.swap_free_bytes,
            "swap_percent": self.swap_percent,
        }
    
    @property
    def total_gb(self) -> float:
        """Total memory in GB."""
        return self.total_bytes / (1024 ** 3)
    
    @property
    def used_gb(self) -> float:
        """Used memory in GB."""
        return self.used_bytes / (1024 ** 3)
    
    @property
    def available_gb(self) -> float:
        """Available memory in GB."""
        return self.available_bytes / (1024 ** 3)
    
    @property
    def free_gb(self) -> float:
        """Free memory in GB."""
        return self.free_bytes / (1024 ** 3)


def get_memory_info() -> MemoryInfo:
    """Get comprehensive memory information."""
    try:
        # Get virtual memory info
        vm = psutil.virtual_memory()
        
        # Get swap memory info
        swap = psutil.swap_memory()
        
        # Get extended memory info if available
        active_bytes = None
        inactive_bytes = None
        buffers_bytes = None
        cached_bytes = None
        shared_bytes = None
        slab_bytes = None
        
        try:
            # Try to get extended memory info (Linux-specific)
            if hasattr(vm, 'active'):
                active_bytes = vm.active
            if hasattr(vm, 'inactive'):
                inactive_bytes = vm.inactive
            if hasattr(vm, 'buffers'):
                buffers_bytes = vm.buffers
            if hasattr(vm, 'cached'):
                cached_bytes = vm.cached
            if hasattr(vm, 'shared'):
                shared_bytes = vm.shared
            if hasattr(vm, 'slab'):
                slab_bytes = vm.slab
        except Exception:
            pass
        
        return MemoryInfo(
            total_bytes=vm.total,
            available_bytes=vm.available,
            used_bytes=vm.used,
            free_bytes=vm.free,
            usage_percent=vm.percent,
            available_percent=100.0 - vm.percent,
            active_bytes=active_bytes,
            inactive_bytes=inactive_bytes,
            buffers_bytes=buffers_bytes,
            cached_bytes=cached_bytes,
            shared_bytes=shared_bytes,
            slab_bytes=slab_bytes,
            swap_total_bytes=swap.total,
            swap_used_bytes=swap.used,
            swap_free_bytes=swap.free,
            swap_percent=swap.percent,
        )
        
    except Exception as e:
        logger.error(f"Error getting memory info: {e}")
        # Return minimal info
        return MemoryInfo(
            total_bytes=0,
            available_bytes=0,
            used_bytes=0,
            free_bytes=0,
            usage_percent=0.0,
            available_percent=0.0,
            active_bytes=None,
            inactive_bytes=None,
            buffers_bytes=None,
            cached_bytes=None,
            shared_bytes=None,
            slab_bytes=None,
            swap_total_bytes=None,
            swap_used_bytes=None,
            swap_free_bytes=None,
            swap_percent=None,
        ) 