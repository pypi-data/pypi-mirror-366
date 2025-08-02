"""
Tests for distributed optimization module.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from python.mlperf.optimization.distributed import (
    DistributedOptimizer,
    CommunicationConfig,
    MemoryConfig,
    MemoryTracker,
    NodeInfo,
    OpenAIHelper
)


class TestCommunicationConfig:
    """Test CommunicationConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = CommunicationConfig()
        assert config.backend == "nccl"
        assert config.bucket_size_mb == 25
        assert config.gradient_compression is False
        assert config.compression_ratio == 0.01
        assert config.allreduce_always_fp16 is False
        assert config.optimize_network_topology is True
        assert config.enable_mixed_precision is True
        assert config.zero_stage == 1
        assert config.num_threads == 4
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = CommunicationConfig(
            backend="gloo",
            bucket_size_mb=50,
            gradient_compression=True,
            zero_stage=3
        )
        assert config.backend == "gloo"
        assert config.bucket_size_mb == 50
        assert config.gradient_compression is True
        assert config.zero_stage == 3


class TestMemoryConfig:
    """Test MemoryConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = MemoryConfig()
        assert config.enable_activation_checkpointing is True
        assert config.enable_offloading is False
        assert config.memory_efficient_optimizer is True
        assert config.cudnn_benchmark is True
        assert config.use_custom_allocator is False


class TestNodeInfo:
    """Test NodeInfo class."""
    
    def test_node_info_creation(self):
        """Test NodeInfo creation and serialization."""
        node_info = NodeInfo(
            hostname="test-node",
            ip_address="192.168.1.100",
            rank=0,
            local_rank=0,
            world_size=4,
            cpu_cores=16,
            memory_gb=64.0
        )
        
        assert node_info.hostname == "test-node"
        assert node_info.rank == 0
        assert node_info.world_size == 4
        assert node_info.cpu_cores == 16
        assert node_info.memory_gb == 64.0
    
    def test_to_dict(self):
        """Test NodeInfo to_dict method."""
        node_info = NodeInfo(
            hostname="test-node",
            ip_address="192.168.1.100",
            rank=0,
            local_rank=0,
            world_size=4
        )
        
        data = node_info.to_dict()
        
        assert data["hostname"] == "test-node"
        assert data["ip_address"] == "192.168.1.100"
        assert data["rank"] == 0
        assert data["world_size"] == 4
        assert "gpus" in data
    
    def test_from_dict(self):
        """Test NodeInfo from_dict method."""
        data = {
            "hostname": "test-node",
            "ip_address": "192.168.1.100",
            "rank": 1,
            "local_rank": 1,
            "world_size": 4,
            "gpus": [],
            "cpu_cores": 8,
            "memory_gb": 32.0,
            "network_bandwidth_gbps": 10.0
        }
        
        node_info = NodeInfo.from_dict(data)
        
        assert node_info.hostname == "test-node"
        assert node_info.rank == 1
        assert node_info.cpu_cores == 8
        assert node_info.memory_gb == 32.0


class TestOpenAIHelper:
    """Test OpenAIHelper class."""
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch('python.mlperf.optimization.distributed.get_openai_api_key', return_value=None):
            helper = OpenAIHelper()
            assert helper.client is None
    
    def test_generate_recommendations_without_client(self):
        """Test generating recommendations without OpenAI client."""
        with patch('python.mlperf.optimization.distributed.get_openai_api_key', return_value=None):
            helper = OpenAIHelper()
            
            recommendations = helper.generate_recommendations(
                bottlenecks=[],
                category_times={},
                top_events=[],
                total_runtime=10.0
            )
            
            assert len(recommendations) == 1
            assert "OpenAI client not initialized" in recommendations[0]
    
    @patch('python.mlperf.optimization.distributed.openai.OpenAI')
    def test_generate_recommendations_with_client(self, mock_openai):
        """Test generating recommendations with OpenAI client."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Recommendation 1\nRecommendation 2"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('python.mlperf.optimization.distributed.get_openai_api_key', return_value="test-key"):
            helper = OpenAIHelper()
            
            recommendations = helper.generate_recommendations(
                bottlenecks=[{"type": "computation", "name": "conv2d", "percentage": 60.0}],
                category_times={"gpu_ops": 8.0, "memory": 2.0},
                top_events=[("conv2d", 6.0), ("batch_norm", 2.0)],
                total_runtime=10.0
            )
            
            assert len(recommendations) == 2
            assert "Recommendation 1" in recommendations
            assert "Recommendation 2" in recommendations


class TestDistributedOptimizer:
    """Test DistributedOptimizer class."""
    
    def test_init(self):
        """Test DistributedOptimizer initialization."""
        config = CommunicationConfig()
        optimizer = DistributedOptimizer(config=config, framework="pytorch")
        
        assert optimizer.config == config
        assert optimizer.framework == "pytorch"
        assert not optimizer.initialized
        assert optimizer.node_info is None
    
    def test_unsupported_framework(self):
        """Test initialization with unsupported framework."""
        config = CommunicationConfig()
        
        # The current implementation allows any framework name but checks availability
        # during initialization, so we test that instead
        optimizer = DistributedOptimizer(config=config, framework="unsupported")
        
        # Should create the optimizer but raise error during initialization
        with pytest.raises((ImportError, ValueError)):
            optimizer.initialize(rank=0, local_rank=0, world_size=1)
    
    def test_optimize_model_parallel_single_gpu(self):
        """Test model parallelism optimization for single GPU."""
        config = CommunicationConfig()
        optimizer = DistributedOptimizer(config=config, framework="pytorch")
        
        tp_size, pp_size = optimizer.optimize_model_parallel(
            model_size_gb=1.0,
            num_gpus=1,
            device_memory_gb=24.0
        )
        
        assert tp_size == 1
        assert pp_size == 1
    
    def test_optimize_model_parallel_large_model(self):
        """Test model parallelism optimization for large model."""
        config = CommunicationConfig()
        optimizer = DistributedOptimizer(config=config, framework="pytorch")
        
        tp_size, pp_size = optimizer.optimize_model_parallel(
            model_size_gb=50.0,  # Large model that doesn't fit on single GPU
            num_gpus=8,
            device_memory_gb=24.0
        )
        
        assert tp_size > 1
        assert pp_size >= 1
        assert tp_size * pp_size <= 8
    
    def test_optimize_communication(self):
        """Test communication optimization."""
        config = CommunicationConfig()
        optimizer = DistributedOptimizer(config=config, framework="pytorch")
        
        optimized = optimizer.optimize_communication(
            model_size_gb=10.0,
            num_parameters=1000000000,
            world_size=8
        )
        
        assert "backend" in optimized
        assert "bucket_size_mb" in optimized
        assert "gradient_compression" in optimized
        assert "zero_stage" in optimized
        
        # For medium size model, should use ZeRO stage 1
        assert optimized["zero_stage"] == 1
    
    def test_optimize_communication_large_model(self):
        """Test communication optimization for large model."""
        config = CommunicationConfig()
        optimizer = DistributedOptimizer(config=config, framework="pytorch")
        
        optimized = optimizer.optimize_communication(
            model_size_gb=50.0,  # Large model
            num_parameters=10000000000,
            world_size=32  # Large cluster
        )
        
        # Should enable gradient compression for large models/clusters
        assert optimized["gradient_compression"] is True
        
        # Should use ZeRO stage 2 for large models
        assert optimized["zero_stage"] == 2
    
    def test_optimize_communication_very_large_model(self):
        """Test communication optimization for very large model."""
        config = CommunicationConfig()
        optimizer = DistributedOptimizer(config=config, framework="pytorch")
        
        optimized = optimizer.optimize_communication(
            model_size_gb=150.0,  # Very large model
            num_parameters=100000000000,
            world_size=16
        )
        
        # Should use ZeRO stage 3 for very large models
        assert optimized["zero_stage"] == 3


class TestMemoryTracker:
    """Test MemoryTracker class."""
    
    def test_init(self):
        """Test MemoryTracker initialization."""
        # Test without PyTorch available
        with patch('python.mlperf.optimization.distributed.TORCH_AVAILABLE', False):
            with pytest.raises(ImportError, match="PyTorch not installed"):
                MemoryTracker(framework="pytorch")
    
    def test_start_stop_tracking(self):
        """Test starting and stopping memory tracking."""
        with patch('python.mlperf.optimization.distributed.TORCH_AVAILABLE', True):
            tracker = MemoryTracker(framework="pytorch")
            
            # Mock the memory usage method
            mock_memory_usage = Mock()
            mock_memory_usage.timestamp = 1000.0
            mock_memory_usage.used_bytes = 1024 * 1024 * 1024  # 1GB
            
            with patch.object(tracker, '_get_memory_usage', return_value=mock_memory_usage):
                tracker.start_tracking()
                assert tracker.tracking
                
                # Let it track for a short time
                import time
                time.sleep(0.1)
                
                logs = tracker.stop_tracking()
                assert not tracker.tracking
                assert len(logs) > 0
    
    def test_pytorch_memory_no_cuda(self):
        """Test PyTorch memory tracking without CUDA."""
        with patch('python.mlperf.optimization.distributed.TORCH_AVAILABLE', True):
            with patch('torch.cuda.is_available', return_value=False):
                tracker = MemoryTracker(framework="pytorch")
                
                memory_usage = tracker._get_pytorch_memory()
                
                # Should return MemoryUsage with CPU device
                assert memory_usage.device == "cpu"
                assert memory_usage.total_bytes == 0
                assert memory_usage.used_bytes == 0


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return CommunicationConfig(
        backend="nccl",
        bucket_size_mb=25,
        gradient_compression=False
    )


@pytest.fixture  
def sample_memory_config():
    """Sample memory configuration for testing."""
    return MemoryConfig(
        enable_activation_checkpointing=True,
        memory_efficient_optimizer=True
    )


class TestIntegration:
    """Integration tests for distributed optimization."""
    
    def test_full_optimization_workflow(self, sample_config):
        """Test a complete optimization workflow."""
        optimizer = DistributedOptimizer(config=sample_config, framework="pytorch")
        
        # Test model parallelism optimization
        tp_size, pp_size = optimizer.optimize_model_parallel(
            model_size_gb=5.0,
            num_gpus=4,
            device_memory_gb=16.0
        )
        
        assert tp_size >= 1
        assert pp_size >= 1
        
        # Test communication optimization
        comm_settings = optimizer.optimize_communication(
            model_size_gb=5.0,
            num_parameters=1000000000,
            world_size=4
        )
        
        assert isinstance(comm_settings, dict)
        assert "backend" in comm_settings
        assert "zero_stage" in comm_settings
    
    def test_memory_tracking_integration(self):
        """Test memory tracking integration."""
        with patch('python.mlperf.optimization.distributed.TORCH_AVAILABLE', True):
            tracker = MemoryTracker(framework="pytorch", interval_ms=50)
            
            # Mock memory usage
            mock_memory_usage = Mock()
            mock_memory_usage.timestamp = 1000.0
            mock_memory_usage.used_bytes = 1024 * 1024 * 1024  # 1GB
            mock_memory_usage.device = "cuda:0"
            
            with patch.object(tracker, '_get_memory_usage', return_value=mock_memory_usage):
                tracker.start_tracking()
                
                # Simulate some work
                import time
                time.sleep(0.2)
                
                logs = tracker.stop_tracking()
                
                assert len(logs) > 0
                assert all(log.used_bytes == 1024 * 1024 * 1024 for log in logs)
                assert all(log.device == "cuda:0" for log in logs)


if __name__ == "__main__":
    pytest.main([__file__]) 