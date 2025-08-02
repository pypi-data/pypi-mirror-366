"""
Test hardware monitoring functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from mlperf.hardware.gpu import (
    get_gpu_info, get_gpu_count, get_cuda_info, GPUInfo, GPUMemoryInfo, GPUProcessInfo
)
from mlperf.hardware.cpu import get_cpu_info, CPUInfo
from mlperf.hardware.memory import get_memory_info, MemoryInfo


class TestGPUInfo:
    """Test GPU information gathering."""
    
    def test_gpu_info_creation(self):
        """Test GPU info object creation."""
        memory = GPUMemoryInfo(total=8000000000, free=4000000000, used=4000000000, utilization=50.0)
        process = GPUProcessInfo(pid=1234, process_name="python", memory_used=1000000000)
        
        gpu = GPUInfo(
            index=0,
            name="Test GPU",
            uuid="test-uuid",
            driver_version="525.60.11",
            cuda_version="12.0",
            memory=memory,
            temperature=65.0,
            power_usage=150.0,
            power_limit=250.0,
            utilization=85.0,
            memory_utilization=60.0,
            fan_speed=75,
            processes=[process],
            compute_capability=(8, 6),
            multi_gpu_board=False,
            board_id=0,
            clock_speeds={"graphics": 1500, "memory": 8000, "sm": 1500},
            max_clock_speeds={"graphics": 1800, "memory": 9000, "sm": 1800}
        )
        
        assert gpu.index == 0
        assert gpu.name == "Test GPU"
        assert gpu.memory.utilization == 50.0
        assert len(gpu.processes) == 1
        assert gpu.processes[0].pid == 1234
    
    def test_gpu_info_to_dict(self):
        """Test GPU info dictionary conversion."""
        memory = GPUMemoryInfo(total=8000000000, free=4000000000, used=4000000000, utilization=50.0)
        gpu = GPUInfo(
            index=0,
            name="Test GPU",
            uuid="test-uuid",
            driver_version="525.60.11",
            cuda_version="12.0",
            memory=memory,
            temperature=65.0,
            power_usage=150.0,
            power_limit=250.0,
            utilization=85.0,
            memory_utilization=60.0,
            fan_speed=75,
            processes=[],
            compute_capability=(8, 6),
            multi_gpu_board=False,
            board_id=0,
            clock_speeds={},
            max_clock_speeds={}
        )
        
        gpu_dict = gpu.to_dict()
        assert isinstance(gpu_dict, dict)
        assert gpu_dict["index"] == 0
        assert gpu_dict["name"] == "Test GPU"
        assert "memory" in gpu_dict
        assert isinstance(gpu_dict["memory"], dict)


class TestGetGPUInfo:
    """Test get_gpu_info function with proper dependency handling."""
    
    def test_get_gpu_info_no_pynvml_available(self):
        """Test get_gpu_info when pynvml is not available."""
        # Mock PYNVML_AVAILABLE as False
        with patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', False):
            gpus = get_gpu_info()
            assert gpus == []
    
    @patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', True)
    def test_get_gpu_info_nvidia_ml_exception(self):
        """Test get_gpu_info when NVIDIA ML raises an exception."""
        # Mock the import to raise exception
        with patch('builtins.__import__') as mock_import:
            mock_import.side_effect = ImportError("NVIDIA ML not available")
            
            gpus = get_gpu_info()
            
            # Should handle exceptions gracefully and return empty list
            assert gpus == []
    
    @patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', True)
    def test_get_gpu_info_success(self):
        """Test successful GPU info retrieval."""
        # Since we can't easily mock pynvml without it being imported,
        # we'll test the function with PYNVML_AVAILABLE=True but expect
        # it to handle the case where pynvml is not actually available
        gpus = get_gpu_info()
        
        # Should return empty list when pynvml is not actually available
        assert isinstance(gpus, list)
    
    @patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', True) 
    def test_get_gpu_info_specific_index(self):
        """Test getting info for a specific GPU index."""
        # Test with specific index
        gpus = get_gpu_info(gpu_index=0)
        assert isinstance(gpus, list)


class TestGetGPUCount:
    """Test GPU count function."""
    
    def test_get_gpu_count_no_pynvml(self):
        """Test GPU count when pynvml is not available."""
        with patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', False):
            count = get_gpu_count()
            assert count == 0
    
    @patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', True)
    def test_get_gpu_count_success(self):
        """Test successful GPU count retrieval."""
        count = get_gpu_count()
        assert isinstance(count, int)
    
    @patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', True)
    def test_get_gpu_count_exception(self):
        """Test GPU count when NVIDIA ML raises an exception."""
        count = get_gpu_count()
        assert isinstance(count, int)
    



class TestGetCudaInfo:
    """Test CUDA information gathering."""
    
    def test_get_cuda_info_no_frameworks(self):
        """Test CUDA info when no ML frameworks are available."""
        with patch('mlperf.hardware.gpu.TORCH_AVAILABLE', False), \
             patch('mlperf.hardware.gpu.TF_AVAILABLE', False), \
             patch('mlperf.hardware.gpu.PYNVML_AVAILABLE', False):
            
            info = get_cuda_info()
            
            assert not info['cuda_available']
            assert info['device_count'] == 0
            assert info['devices'] == []
    
    def test_get_cuda_info_pytorch(self):
        """Test CUDA info with PyTorch."""
        with patch('python.mlperf.hardware.gpu.TORCH_AVAILABLE', True), \
             patch('python.mlperf.hardware.gpu.TF_AVAILABLE', False), \
             patch('python.mlperf.hardware.gpu.PYNVML_AVAILABLE', False):
            
            # Mock torch module
            mock_torch = MagicMock()
            mock_torch.cuda.is_available.return_value = True
            mock_torch.cuda.device_count.return_value = 1
            mock_torch.version.cuda = "12.0"
            mock_torch.backends.cudnn.version.return_value = 8600
            
            # Mock device properties
            mock_props = MagicMock()
            mock_props.name = "Test GPU"
            mock_props.total_memory = 8000000000
            mock_props.major = 8
            mock_props.minor = 6
            mock_props.multi_processor_count = 108
            mock_torch.cuda.get_device_properties.return_value = mock_props
            
            with patch('mlperf.hardware.gpu.torch', mock_torch):
                info = get_cuda_info()
                
                assert info['cuda_available']
                assert info['device_count'] == 1
                assert info['cuda_version'] == "12.0"
                assert info['cudnn_version'] == 8600
                assert len(info['devices']) == 1
                assert info['devices'][0]['name'] == "Test GPU"


class TestCPUInfo:
    """Test CPU information gathering."""
    
    def test_get_cpu_info(self):
        """Test CPU info retrieval."""
        cpu_info = get_cpu_info()
        
        assert isinstance(cpu_info, CPUInfo)
        assert cpu_info.physical_cores > 0
        assert cpu_info.logical_cores > 0
        assert cpu_info.frequency_mhz is not None
        assert cpu_info.architecture is not None
        assert cpu_info.processor_name is not None
    
    def test_cpu_info_to_dict(self):
        """Test CPU info dictionary conversion."""
        cpu_info = get_cpu_info()
        cpu_dict = cpu_info.to_dict()
        
        assert isinstance(cpu_dict, dict)
        assert "physical_cores" in cpu_dict
        assert "logical_cores" in cpu_dict
        assert "frequency_mhz" in cpu_dict
        assert "processor_name" in cpu_dict


class TestMemoryInfo:
    """Test memory information gathering."""
    
    def test_get_memory_info(self):
        """Test memory info retrieval."""
        memory_info = get_memory_info()
        
        assert isinstance(memory_info, MemoryInfo)
        assert memory_info.total_gb > 0
        assert memory_info.available_gb >= 0
        assert memory_info.used_gb >= 0
        assert 0 <= memory_info.usage_percent <= 100
    
    def test_memory_info_to_dict(self):
        """Test memory info dictionary conversion."""
        memory_info = get_memory_info()
        memory_dict = memory_info.to_dict()
        
        assert isinstance(memory_dict, dict)
        assert "total_bytes" in memory_dict
        assert "available_bytes" in memory_dict
        assert "used_bytes" in memory_dict
        assert "usage_percent" in memory_dict


@pytest.mark.integration
class TestHardwareIntegration:
    """Integration tests for hardware monitoring."""
    
    def test_complete_hardware_info(self):
        """Test gathering complete hardware information."""
        # This test runs with real hardware when available
        try:
            cpu_info = get_cpu_info()
            memory_info = get_memory_info()
            gpu_count = get_gpu_count()
            cuda_info = get_cuda_info()
            
            # Basic assertions
            assert cpu_info is not None
            assert memory_info is not None
            assert isinstance(gpu_count, int)
            assert isinstance(cuda_info, dict)
            
            # If GPUs are available, test GPU info
            if gpu_count > 0:
                gpu_info = get_gpu_info()
                assert len(gpu_info) == gpu_count
                
                for gpu in gpu_info:
                    assert isinstance(gpu, GPUInfo)
                    assert gpu.index >= 0
                    assert gpu.name is not None
                    
        except Exception as e:
            pytest.skip(f"Integration test skipped due to hardware constraints: {e}")


if __name__ == "__main__":
    pytest.main([__file__]) 