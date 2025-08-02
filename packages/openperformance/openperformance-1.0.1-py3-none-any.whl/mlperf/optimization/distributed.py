"""
Distributed Optimization Module for ML Performance Engineering

This module provides tools for optimizing distributed machine learning training,
including communication optimization, model parallelism, and AI-powered performance
recommendations using OpenAI.

Author: Nik Jois <nikjois@llamasearch.ai>
License: Apache 2.0
"""

import os
import time
import json
import logging
import socket
import threading
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
import numpy as np

from ..utils.logging import get_logger
from ..hardware.gpu import GPUInfo, get_gpu_info, MemoryUsage
import openai
from ..utils.config import get_openai_api_key

logger = get_logger(__name__)

# Check for framework availability
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

try:
    import jax
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

# Helper class for OpenAI interactions
class OpenAIHelper:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_openai_api_key()
        if not self.api_key:
            logger.warning("OpenAI API key not provided. AI-powered recommendations will be disabled.")
            self.client = None
        else:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def generate_recommendations(self, bottlenecks: List[Dict[str, Any]], category_times: Dict[str, float], top_events: List[Tuple[str, float]], total_runtime: float) -> List[str]:
        if not self.client:
            return ["OpenAI client not initialized. Cannot generate AI recommendations."]

        prompt = self._construct_prompt(bottlenecks, category_times, top_events, total_runtime)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Upgraded to GPT-4 for better recommendations
                messages=[
                    {"role": "system", "content": "You are an expert in ML performance engineering. Provide actionable recommendations based on the following profiling data. Focus on optimizing distributed training, memory usage, and communication bottlenecks."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more deterministic outputs
            )
            ai_recommendations = response.choices[0].message.content.strip().split('\n')
            return [rec.strip() for rec in ai_recommendations if rec.strip()]
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return [f"Error generating AI recommendations: {e}"]

    def _construct_prompt(
        self,
        bottlenecks: List[Dict[str, Any]],
        category_times: Dict[str, float],
        top_events: List[Tuple[str, float]],
        total_runtime: float
    ) -> str:
        prompt = "Profiling Analysis:\n"
        prompt += f"- Total Runtime: {total_runtime:.2f}s\n"
        prompt += "- Identified Bottlenecks:\n"
        for bottleneck in bottlenecks:
            prompt += f"  - Type: {bottleneck['type']}, Name: {bottleneck.get('name', 'N/A')}, Percentage: {bottleneck.get('percentage', 0):.1f}%\n"
        prompt += "- Top Time-Consuming Events:\n"
        for name, duration in top_events[:10]:  # Increased to top 10 events
            prompt += f"  - Event: {name}, Duration: {duration:.4f}s, Percentage: {(duration / total_runtime) * 100:.1f}%\n"
        prompt += "- Time Distribution by Category:\n"
        for category, time in category_times.items():
            prompt += f"  - Category: {category}, Time: {time:.4f}s, Percentage: {(time / total_runtime) * 100:.1f}%\n"
        prompt += "\nPlease provide actionable recommendations to optimize performance based on this data. Focus on:"
        prompt += "\n1. Reducing communication overhead"
        prompt += "\n2. Optimizing memory usage"
        prompt += "\n3. Improving model parallelism"
        prompt += "\n4. Leveraging hardware capabilities"
        return prompt

@dataclass
class NodeInfo:
    """Information about a node in the distributed cluster."""
    hostname: str
    ip_address: str
    rank: int
    local_rank: int
    world_size: int
    gpus: List[GPUInfo] = field(default_factory=list)
    cpu_cores: int = 0
    memory_gb: float = 0
    network_bandwidth_gbps: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "rank": self.rank,
            "local_rank": self.local_rank,
            "world_size": self.world_size,
            "gpus": [gpu.to_dict() for gpu in self.gpus],
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "network_bandwidth_gbps": self.network_bandwidth_gbps
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeInfo':
        """Create from dictionary."""
        return cls(
            hostname=data["hostname"],
            ip_address=data["ip_address"],
            rank=data["rank"],
            local_rank=data["local_rank"],
            world_size=data["world_size"],
            gpus=[GPUInfo.from_dict(gpu) for gpu in data.get("gpus", [])],
            cpu_cores=data.get("cpu_cores", 0),
            memory_gb=data.get("memory_gb", 0),
            network_bandwidth_gbps=data.get("network_bandwidth_gbps", 0)
        )
    
    @classmethod
    def get_current(cls, rank: int, local_rank: int, world_size: int) -> 'NodeInfo':
        """Get information about the current node."""
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            ip_address = "127.0.0.1"
        
        # Get GPU information
        gpus = get_gpu_info()
        
        # Get CPU and memory information
        try:
            import psutil
            cpu_cores = os.cpu_count() or 0
            memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        except ImportError:
            cpu_cores = os.cpu_count() or 0
            memory_gb = 0.0
        
        # Estimate network bandwidth using basic system information
        network_bandwidth_gbps = 1.0  # Default to 1 Gbps
        try:
            import psutil
            net_if_stats = psutil.net_if_stats()
            for interface, stats in net_if_stats.items():
                if stats.speed > 0 and not interface.startswith('lo'):
                    # Convert Mbps to Gbps
                    speed_gbps = stats.speed / 1000.0
                    if speed_gbps > network_bandwidth_gbps:
                        network_bandwidth_gbps = speed_gbps
        except (ImportError, AttributeError):
            pass
        
        return cls(
            hostname=hostname,
            ip_address=ip_address,
            rank=rank,
            local_rank=local_rank,
            world_size=world_size,
            gpus=gpus,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            network_bandwidth_gbps=network_bandwidth_gbps
        )

@dataclass
class CommunicationConfig:
    """Configuration for optimizing distributed communication."""
    backend: str = "nccl"  # nccl, gloo, mpi
    bucket_size_mb: int = 25
    gradient_compression: bool = False
    compression_ratio: float = 0.01  # For algorithms like PowerSGD
    allreduce_always_fp16: bool = False
    optimize_network_topology: bool = True
    enable_mixed_precision: bool = True
    enable_zero_redundancy: bool = False
    zero_stage: int = 1  # 1, 2, or 3 for ZeRO stages
    overlap_comm_comp: bool = True
    num_threads: int = 4

@dataclass
class MemoryConfig:
    """Memory optimization configuration."""
    enable_activation_checkpointing: bool = True
    enable_offloading: bool = False
    offload_optimizer_state: bool = False
    offload_parameters: bool = False
    offload_activations: bool = False
    cpu_offload_params: bool = False
    cpu_offload_use_pin_memory: bool = True
    memory_efficient_optimizer: bool = True
    overlap_comm_prepostprocessing: bool = True
    min_params_bucket_size: int = int(1e8)
    max_reuse_distance_in_numel: int = int(1e9)
    release_inference_cache: bool = True
    optimize_memory_usage: bool = True
    cudnn_benchmark: bool = True
    use_custom_allocator: bool = False

class DistributedOptimizer:
    """Optimizes distributed training performance."""
    
    def __init__(
        self,
        config: CommunicationConfig,
        framework: str = "pytorch",
        profile_first_step: bool = True
    ):
        self.config = config
        self.framework = framework.lower()
        self.profile_first_step = profile_first_step
        self.node_info = None
        self.cluster_info = []
        self.initialized = False
        
        # Check framework availability
        if self.framework == "pytorch" and not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available")
        elif self.framework == "tensorflow" and not TF_AVAILABLE:
            raise ImportError("TensorFlow not available")
        elif self.framework == "jax" and not JAX_AVAILABLE:
            raise ImportError("JAX not available")
    
    def initialize(
        self,
        rank: int,
        local_rank: int,
        world_size: int,
        master_addr: Optional[str] = None,
        master_port: int = 29500
    ) -> None:
        """Initialize distributed training environment."""
        # Get information about the current node
        self.node_info = NodeInfo.get_current(rank, local_rank, world_size)
        
        # Initialize framework-specific distributed environment
        if self.framework == "pytorch":
            self._init_pytorch(rank, world_size, master_addr, master_port)
        elif self.framework == "tensorflow":
            self._init_tensorflow(rank, world_size)
        elif self.framework == "jax":
            self._init_jax(rank, world_size)
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
        
        self.initialized = True
        logger.info(f"Initialized distributed training for rank {rank}/{world_size}")
    
    def _init_pytorch(self, rank: int, world_size: int, master_addr: Optional[str], master_port: int) -> None:
        """Initialize PyTorch distributed environment."""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not installed")
        
        import torch.distributed as dist
        import torch
        
        # Set environment variables if not already set
        os.environ["RANK"] = str(rank)
        os.environ["WORLD_SIZE"] = str(world_size)
        if master_addr:
            os.environ["MASTER_ADDR"] = master_addr
        os.environ["MASTER_PORT"] = str(master_port)
        
        # Initialize distributed process group
        backend = self.config.backend
        if not dist.is_initialized():
            dist.init_process_group(
                backend=backend,
                rank=rank,
                world_size=world_size
            )
        
        # Set optimization parameters
        if self.config.allreduce_always_fp16:
            os.environ["TORCH_DISTRIBUTED_ALLREDUCE_ALWAYS_FP16"] = "1"
        
        # Set NCCL optimization environment variables
        if backend == "nccl":
            os.environ["NCCL_DEBUG"] = "INFO"
            os.environ["NCCL_SOCKET_IFNAME"] = "^lo"
            if self.config.optimize_network_topology:
                os.environ["NCCL_IB_DISABLE"] = "0"
                os.environ["NCCL_IB_GID_INDEX"] = "3"
                os.environ["NCCL_IB_HCA"] = "^mlx5_0"
                os.environ["NCCL_NET_GDR_LEVEL"] = "5"
        
        logger.info(f"PyTorch distributed initialized with backend {backend}")
    
    def _init_tensorflow(self, rank: int, world_size: int) -> None:
        """Initialize TensorFlow distributed environment."""
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow not installed")
        
        import tensorflow as tf
        
        # Set multi-threading parameters
        if self.config.num_threads > 0:
            tf.config.threading.set_intra_op_parallelism_threads(self.config.num_threads)
            tf.config.threading.set_inter_op_parallelism_threads(self.config.num_threads)
        
        # Initialize distributed strategy
        if world_size > 1:
            os.environ["TF_CONFIG"] = json.dumps({
                "cluster": {
                    "worker": [f"localhost:{12345 + i}" for i in range(world_size)]
                },
                "task": {"type": "worker", "index": rank}
            })
            
            strategy = tf.distribute.MultiWorkerMirroredStrategy()
            logger.info(f"TensorFlow distributed initialized with {world_size} workers")
        else:
            strategy = tf.distribute.MirroredStrategy()
            logger.info("TensorFlow single-node multi-GPU strategy initialized")
        
        # Store strategy for later use
        self.strategy = strategy
    
    def _init_jax(self, rank: int, world_size: int) -> None:
        """Initialize JAX distributed environment."""
        if not JAX_AVAILABLE:
            raise ImportError("JAX not installed")
        
        import jax
        
        # Configure JAX to use all available devices
        jax.config.update('jax_platforms', 'cpu,gpu,tpu')
        devices = jax.devices()
        logger.info(f"JAX using {len(devices)} devices: {jax.devices()}")
        
        # Set process ID for communication
        if world_size > 1:
            jax.distributed.initialize()
            logger.info(f"JAX distributed initialized for rank {rank}/{world_size}")
    
    def optimize_model_parallel(self, model_size_gb: float, num_gpus: int, device_memory_gb: float) -> Tuple[int, int]:
        """
        Optimize model parallelism configuration.
        
        Returns:
            Tuple of (tensor_parallel_size, pipeline_parallel_size)
        """
        if model_size_gb <= device_memory_gb:
            return 1, 1
        
        memory_per_gpu = device_memory_gb * 0.8
        tensor_parallel_size = min(num_gpus, max(1, int(np.ceil(model_size_gb / memory_per_gpu))))
        
        remaining_gpus = num_gpus // tensor_parallel_size
        pipeline_parallel_size = min(4, remaining_gpus)
        
        logger.info(f"Model parallelism configuration: TP={tensor_parallel_size}, PP={pipeline_parallel_size}")
        return tensor_parallel_size, pipeline_parallel_size
    
    def optimize_communication(self, model_size_gb: float, num_parameters: int, world_size: int) -> Dict[str, Any]:
        """Optimize communication settings for distributed training."""
        optimized = {
            "backend": self.config.backend,
            "bucket_size_mb": self.config.bucket_size_mb,
            "gradient_compression": self.config.gradient_compression,
            "compression_ratio": self.config.compression_ratio,
            "allreduce_always_fp16": self.config.allreduce_always_fp16,
            "zero_stage": self.config.zero_stage
        }
        
        # Adjust bucket size based on model size and world size
        if model_size_gb > 10:
            optimized["bucket_size_mb"] = min(200, max(25, int(100 * model_size_gb / 40)))
        elif world_size > 16:
            optimized["bucket_size_mb"] = max(5, min(25, int(25 * 16 / world_size)))
        
        # Enable gradient compression for very large models or clusters
        if model_size_gb > 20 or world_size > 32:
            optimized["gradient_compression"] = True
            if model_size_gb > 40:
                optimized["compression_ratio"] = 0.001
            elif model_size_gb > 20:
                optimized["compression_ratio"] = 0.005
            else:
                optimized["compression_ratio"] = 0.01
        
        # Optimize ZeRO stage based on model size and world size
        if model_size_gb > 100:
            optimized["zero_stage"] = 3
        elif model_size_gb > 20 or world_size > 16:
            optimized["zero_stage"] = 2
        else:
            optimized["zero_stage"] = 1
        
        logger.info(f"Optimized communication settings: {optimized}")
        return optimized

    def optimize_memory(self, model, optimizer):
        """Optimize memory usage for distributed training."""
        if self.framework == "pytorch":
            self._optimize_pytorch_memory(model, optimizer)
        elif self.framework == "tensorflow":
            self._optimize_tensorflow_memory(model, optimizer)
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")

    def _optimize_pytorch_memory(self, model, optimizer):
        """Optimize PyTorch memory usage."""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available")
        
        # Apply activation checkpointing if enabled
        if self.config.enable_activation_checkpointing:
            try:
                from torch.utils.checkpoint import checkpoint_sequential
                
                # Find sequential modules suitable for checkpointing
                sequential_modules = []
                for name, module in model.named_children():
                    if isinstance(module, torch.nn.Sequential) and len(list(module.children())) > 2:
                        sequential_modules.append((name, module))
                
                # Apply checkpointing to suitable modules
                for name, module in sequential_modules:
                    if hasattr(module, '__len__') and len(module) > 2:
                        # Create checkpointed version of the module
                        segments = len(module) // 2  # Checkpoint every 2 layers
                        checkpointed_module = lambda x: checkpoint_sequential(module, segments, x)
                        setattr(model, name, checkpointed_module)
                
                logger.info(f"Applied activation checkpointing to {len(sequential_modules)} modules")
            except Exception as e:
                logger.error(f"Failed to apply activation checkpointing: {e}")
        
        # Apply CPU offloading if enabled
        if self.config.enable_offloading and self.config.cpu_offload_params:
            try:
                device = next(model.parameters()).device
                cpu_parameters = {}
                
                # Move infrequently used parameters to CPU
                for name, param in model.named_parameters():
                    if any(x in name.lower() for x in ['embedding', 'classifier', 'norm']):
                        cpu_parameters[name] = param.data.clone()
                        param.data = param.data.to('cpu')
                        if self.config.cpu_offload_use_pin_memory:
                            cpu_parameters[name] = cpu_parameters[name].pin_memory()
                
                logger.info(f"Applied CPU parameter offloading to {len(cpu_parameters)} parameters")
            except Exception as e:
                logger.error(f"Failed to apply CPU offloading: {e}")
        
        # Apply memory-efficient optimizer if enabled
        if self.config.memory_efficient_optimizer and optimizer is not None:
            try:
                if isinstance(optimizer, torch.optim.Adam):
                    try:
                        from torch.optim import AdamW
                        
                        # Get current optimizer configuration
                        state_dict = optimizer.state_dict()
                        param_groups = optimizer.param_groups
                        
                        # Create new optimizer with better memory efficiency
                        new_optimizer = AdamW(
                            model.parameters(),
                            lr=param_groups[0]['lr'],
                            betas=param_groups[0].get('betas', (0.9, 0.999)),
                            eps=param_groups[0].get('eps', 1e-8),
                            weight_decay=param_groups[0].get('weight_decay', 0),
                            amsgrad=param_groups[0].get('amsgrad', False)
                        )
                        
                        new_optimizer.load_state_dict(state_dict)
                        optimizer = new_optimizer
                        
                        logger.info("Replaced optimizer with memory-efficient AdamW")
                    except ImportError:
                        logger.warning("Memory-efficient AdamW not available")
            except Exception as e:
                logger.error(f"Failed to apply memory-efficient optimizer: {e}")

class MemoryTracker:
    """Tracks memory usage during training and inference."""
    
    def __init__(self, framework: str = "pytorch", interval_ms: int = 100):
        self.framework = framework.lower()
        self.interval_ms = interval_ms
        self.tracking = False
        self.memory_logs = []
        self.tracking_thread = None
        self.stop_event = threading.Event()
        
        # Initialize memory tracker based on framework
        if self.framework == "pytorch" and not TORCH_AVAILABLE:
            raise ImportError("PyTorch not installed but framework set to pytorch")
        elif self.framework == "tensorflow" and not TF_AVAILABLE:
            raise ImportError("TensorFlow not installed but framework set to tensorflow")
    
    def start_tracking(self) -> None:
        """Start tracking memory usage."""
        if self.tracking:
            logger.warning("Memory tracking already started")
            return
        
        self.stop_event.clear()
        self.memory_logs = []
        self.tracking = True
        
        self.tracking_thread = threading.Thread(
            target=self._tracking_loop,
            daemon=True
        )
        self.tracking_thread.start()
        
        logger.info(f"Started memory tracking for {self.framework}")
    
    def stop_tracking(self) -> List[MemoryUsage]:
        """Stop tracking memory usage and return logged data."""
        if not self.tracking:
            logger.warning("Memory tracking not started")
            return self.memory_logs
        
        self.stop_event.set()
        if self.tracking_thread:
            self.tracking_thread.join(timeout=5)
        
        self.tracking = False
        logger.info(f"Stopped memory tracking, collected {len(self.memory_logs)} samples")
        
        return self.memory_logs
    
    def _tracking_loop(self) -> None:
        """Background loop for memory tracking."""
        while not self.stop_event.is_set():
            try:
                memory_usage = self._get_memory_usage()
                self.memory_logs.append(memory_usage)
            except Exception as e:
                logger.error(f"Error in memory tracking: {e}")
            
            time.sleep(self.interval_ms / 1000)
    
    def _get_memory_usage(self) -> MemoryUsage:
        """Get current memory usage based on framework."""
        if self.framework == "pytorch":
            return self._get_pytorch_memory()
        elif self.framework == "tensorflow":
            return self._get_tensorflow_memory()
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
    
    def _get_pytorch_memory(self) -> MemoryUsage:
        """Get PyTorch GPU memory usage."""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available")
        
        import torch
        
        if not torch.cuda.is_available():
            return MemoryUsage(
                timestamp=time.time(),
                device="cpu",
                total_bytes=0,
                used_bytes=0
            )
        
        device = torch.cuda.current_device()
        
        # Get memory statistics
        total_bytes = torch.cuda.get_device_properties(device).total_memory
        used_bytes = torch.cuda.memory_allocated(device)
        reserved_bytes = torch.cuda.memory_reserved(device)
        
        # Get additional statistics if available
        try:
            active_bytes = torch.cuda.memory_stats(device)["active_bytes.all.current"]
            inactive_bytes = reserved_bytes - active_bytes
            
            # Estimate fragmentation
            fragmentation = 0.0
            if reserved_bytes > 0:
                fragmentation = 1.0 - (used_bytes / reserved_bytes)
                
        except (KeyError, RuntimeError):
            active_bytes = 0
            inactive_bytes = 0
            fragmentation = 0.0
        
        return MemoryUsage(
            timestamp=time.time(),
            device=f"cuda:{device}",
            total_bytes=total_bytes,
            used_bytes=used_bytes,
            reserved_bytes=reserved_bytes,
            active_bytes=active_bytes,
            inactive_bytes=inactive_bytes,
            fragmentation=fragmentation
        )
    
    def _get_tensorflow_memory(self) -> MemoryUsage:
        """Get TensorFlow GPU memory usage."""
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow not available")
        
        import tensorflow as tf
        
        if not tf.config.list_physical_devices('GPU'):
            return MemoryUsage(
                timestamp=time.time(),
                device="cpu",
                total_bytes=0,
                used_bytes=0
            )
        
        # Get available GPUs
        gpus = tf.config.list_physical_devices('GPU')
        device = 0  # Use first GPU by default
        
        # Get memory info using experimental memory_info API
        try:
            mem_info = tf.config.experimental.get_memory_info(f'GPU:{device}')
            used_bytes = mem_info.get('current', 0)
            total_bytes = 0  # TensorFlow doesn't provide total memory easily
            
            return MemoryUsage(
                timestamp=time.time(),
                device=f"GPU:{device}",
                total_bytes=total_bytes,
                used_bytes=used_bytes
            )
            
        except (AttributeError, ValueError) as e:
            logger.warning(f"Failed to get TensorFlow memory info: {e}")
            
            # Fallback to less accurate information
            return MemoryUsage(
                timestamp=time.time(),
                device=f"GPU:{device}",
                total_bytes=0,
                used_bytes=0
            ) 