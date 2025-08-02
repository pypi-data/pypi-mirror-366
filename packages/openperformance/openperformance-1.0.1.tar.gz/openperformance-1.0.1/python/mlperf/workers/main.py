"""
Background workers for ML Performance Engineering Platform.
"""

import asyncio
import json
import os
import time
from typing import Dict, Any, List
import traceback

import redis
from celery import Celery
from celery.signals import worker_ready, worker_shutdown

from ..utils.logging import get_logger, setup_logging
from ..utils.config import Config
from ..optimization.distributed import (
    DistributedOptimizer,
    CommunicationConfig,
    MemoryTracker,
    OpenAIHelper
)
from ..hardware.gpu import get_gpu_info

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize Celery app
celery_app = Celery(
    'mlperf-workers',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    include=['python.mlperf.workers.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)


class BenchmarkWorker:
    """Worker for running ML benchmarks."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.config = Config()
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        
    async def run_benchmark(self, benchmark_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a benchmark based on configuration."""
        try:
            self.logger.info(f"Starting benchmark: {benchmark_config.get('name', 'unknown')}")
            
            # Extract configuration
            framework = benchmark_config.get('framework', 'pytorch')
            model_size_gb = benchmark_config.get('model_size_gb', 1.0)
            batch_size = benchmark_config.get('batch_size', 32)
            iterations = benchmark_config.get('iterations', 100)
            distributed = benchmark_config.get('distributed', False)
            
            # Setup distributed optimizer
            comm_config = CommunicationConfig(
                backend="nccl" if framework == "pytorch" else "gloo",
                enable_mixed_precision=True
            )
            
            optimizer = DistributedOptimizer(
                config=comm_config,
                framework=framework
            )
            
            if distributed:
                # Initialize distributed training
                optimizer.initialize(rank=0, local_rank=0, world_size=1)
            
            # Start memory tracking
            memory_tracker = MemoryTracker(framework=framework)
            memory_tracker.start_tracking()
            
            # Simulate benchmark workload
            results = await self._simulate_workload(
                framework=framework,
                model_size_gb=model_size_gb,
                batch_size=batch_size,
                iterations=iterations
            )
            
            # Stop memory tracking
            memory_logs = memory_tracker.stop_tracking()
            
            # Calculate memory statistics
            memory_stats = self._calculate_memory_stats(memory_logs)
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                framework=framework,
                model_size_gb=model_size_gb,
                results=results,
                memory_stats=memory_stats
            )
            
            # Compile final results
            benchmark_results = {
                "benchmark_id": benchmark_config.get('id'),
                "name": benchmark_config.get('name'),
                "framework": framework,
                "model_size_gb": model_size_gb,
                "batch_size": batch_size,
                "iterations": iterations,
                "distributed": distributed,
                "performance": results,
                "memory": memory_stats,
                "recommendations": recommendations,
                "timestamp": time.time(),
                "status": "completed"
            }
            
            self.logger.info(f"Benchmark completed: {benchmark_config.get('name')}")
            return benchmark_results
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {e}")
            self.logger.error(traceback.format_exc())
            
            return {
                "benchmark_id": benchmark_config.get('id'),
                "name": benchmark_config.get('name'),
                "status": "failed",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _simulate_workload(
        self,
        framework: str,
        model_size_gb: float,
        batch_size: int,
        iterations: int
    ) -> Dict[str, Any]:
        """Simulate ML workload and measure performance."""
        start_time = time.time()
        
        # Simulate computation time based on model size and batch size
        base_time_per_iter = 0.01  # 10ms base time
        size_factor = model_size_gb / 1.0  # Scale with model size
        batch_factor = batch_size / 32.0  # Scale with batch size
        
        total_compute_time = 0.0
        iteration_times = []
        
        for i in range(iterations):
            iter_start = time.time()
            
            # Simulate variable computation time
            compute_time = base_time_per_iter * size_factor * batch_factor
            compute_time *= (0.8 + 0.4 * (i % 10) / 10)  # Add variation
            
            await asyncio.sleep(compute_time)
            
            iter_end = time.time()
            iter_duration = iter_end - iter_start
            iteration_times.append(iter_duration)
            total_compute_time += compute_time
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate performance metrics
        avg_iteration_time = sum(iteration_times) / len(iteration_times)
        throughput = batch_size / avg_iteration_time  # samples per second
        
        return {
            "total_time_seconds": total_time,
            "compute_time_seconds": total_compute_time,
            "avg_iteration_time_ms": avg_iteration_time * 1000,
            "min_iteration_time_ms": min(iteration_times) * 1000,
            "max_iteration_time_ms": max(iteration_times) * 1000,
            "throughput_samples_per_sec": throughput,
            "iterations_completed": iterations,
            "framework": framework
        }
    
    def _calculate_memory_stats(self, memory_logs: List) -> Dict[str, Any]:
        """Calculate memory usage statistics from logs."""
        if not memory_logs:
            return {
                "peak_memory_gb": 0.0,
                "avg_memory_gb": 0.0,
                "memory_efficiency": 0.0,
                "samples": 0
            }
        
        # Convert to GB
        memory_usage_gb = [log.used_bytes / (1024**3) for log in memory_logs]
        total_memory_gb = memory_logs[0].total_bytes / (1024**3) if memory_logs[0].total_bytes > 0 else 0
        
        peak_memory = max(memory_usage_gb)
        avg_memory = sum(memory_usage_gb) / len(memory_usage_gb)
        
        # Calculate memory efficiency (how well we're using available memory)
        efficiency = (avg_memory / total_memory_gb * 100) if total_memory_gb > 0 else 0
        
        return {
            "peak_memory_gb": peak_memory,
            "avg_memory_gb": avg_memory,
            "total_memory_gb": total_memory_gb,
            "memory_efficiency_percent": efficiency,
            "samples": len(memory_logs),
            "fragmentation": getattr(memory_logs[-1], 'fragmentation', 0.0) if memory_logs else 0.0
        }
    
    async def _generate_recommendations(
        self,
        framework: str,
        model_size_gb: float,
        results: Dict[str, Any],
        memory_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Performance-based recommendations
        if results.get("throughput_samples_per_sec", 0) < 100:
            recommendations.append("Consider increasing batch size to improve throughput")
        
        # Memory-based recommendations
        if memory_stats.get("memory_efficiency_percent", 0) < 50:
            recommendations.append("Low memory utilization detected. Consider increasing batch size or model size")
        
        if memory_stats.get("peak_memory_gb", 0) > memory_stats.get("total_memory_gb", 0) * 0.9:
            recommendations.append("High memory usage detected. Consider enabling gradient checkpointing or reducing batch size")
        
        if memory_stats.get("fragmentation", 0) > 0.2:
            recommendations.append("High memory fragmentation detected. Consider using memory-efficient optimizers")
        
        # Framework-specific recommendations
        if framework == "pytorch":
            recommendations.append("Consider using torch.compile for better performance")
            if model_size_gb > 10:
                recommendations.append("For large models, consider using DeepSpeed ZeRO for memory optimization")
        elif framework == "tensorflow":
            recommendations.append("Consider using mixed precision training for better performance")
            recommendations.append("Enable memory growth to avoid allocating all GPU memory upfront")
        
        # Try to get AI-powered recommendations
        try:
            openai_helper = OpenAIHelper()
            
            # Construct performance data for AI analysis
            bottlenecks = []
            if results.get("throughput_samples_per_sec", 0) < 50:
                bottlenecks.append({
                    "type": "performance",
                    "name": "low_throughput",
                    "percentage": 100.0
                })
            
            category_times = {
                "compute": results.get("compute_time_seconds", 0),
                "memory": results.get("total_time_seconds", 0) - results.get("compute_time_seconds", 0)
            }
            
            top_events = [
                ("model_forward", results.get("compute_time_seconds", 0) * 0.7),
                ("memory_allocation", results.get("compute_time_seconds", 0) * 0.3)
            ]
            
            ai_recommendations = openai_helper.generate_recommendations(
                bottlenecks=bottlenecks,
                category_times=category_times,
                top_events=top_events,
                total_runtime=results.get("total_time_seconds", 0)
            )
            
            recommendations.extend(ai_recommendations)
            
        except Exception as e:
            self.logger.warning(f"Failed to generate AI recommendations: {e}")
            recommendations.append("AI-powered recommendations unavailable")
        
        return recommendations


class MonitoringWorker:
    """Worker for system monitoring and alerting."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.config = Config()
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # Get GPU information
            gpus = get_gpu_info()
            
            # Get CPU and memory info
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                cpu_info = {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
                }
                
                memory_info = {
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "usage_percent": memory.percent
                }
                
                disk_info = {
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "usage_percent": (disk.used / disk.total) * 100
                }
                
            except ImportError:
                cpu_info = {"usage_percent": 0, "count": os.cpu_count()}
                memory_info = {"total_gb": 0, "used_gb": 0, "available_gb": 0, "usage_percent": 0}
                disk_info = {"total_gb": 0, "used_gb": 0, "free_gb": 0, "usage_percent": 0}
            
            metrics = {
                "timestamp": time.time(),
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "gpus": [gpu.to_dict() for gpu in gpus]
            }
            
            # Store metrics in Redis with TTL
            self.redis_client.setex(
                "system_metrics:latest",
                300,  # 5 minutes TTL
                json.dumps(metrics)
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check system health and generate alerts if needed."""
        try:
            metrics = await self.collect_system_metrics()
            
            alerts = []
            health_score = 100
            
            # Check CPU usage
            cpu_usage = metrics.get("cpu", {}).get("usage_percent", 0)
            if cpu_usage > 90:
                alerts.append({
                    "level": "critical",
                    "component": "cpu",
                    "message": f"High CPU usage: {cpu_usage:.1f}%"
                })
                health_score -= 20
            elif cpu_usage > 70:
                alerts.append({
                    "level": "warning",
                    "component": "cpu",
                    "message": f"Elevated CPU usage: {cpu_usage:.1f}%"
                })
                health_score -= 10
            
            # Check memory usage
            memory_usage = metrics.get("memory", {}).get("usage_percent", 0)
            if memory_usage > 90:
                alerts.append({
                    "level": "critical",
                    "component": "memory",
                    "message": f"High memory usage: {memory_usage:.1f}%"
                })
                health_score -= 20
            elif memory_usage > 70:
                alerts.append({
                    "level": "warning",
                    "component": "memory",
                    "message": f"Elevated memory usage: {memory_usage:.1f}%"
                })
                health_score -= 10
            
            # Check GPU health
            for gpu in metrics.get("gpus", []):
                gpu_util = gpu.get("utilization_percent", 0)
                gpu_temp = gpu.get("temperature_c", 0)
                
                if gpu_temp and gpu_temp > 85:
                    alerts.append({
                        "level": "warning",
                        "component": f"gpu_{gpu.get('index', 0)}",
                        "message": f"High GPU temperature: {gpu_temp}°C"
                    })
                    health_score -= 5
            
            # Check disk usage
            disk_usage = metrics.get("disk", {}).get("usage_percent", 0)
            if disk_usage > 90:
                alerts.append({
                    "level": "critical",
                    "component": "disk",
                    "message": f"High disk usage: {disk_usage:.1f}%"
                })
                health_score -= 15
            elif disk_usage > 80:
                alerts.append({
                    "level": "warning",
                    "component": "disk",
                    "message": f"Elevated disk usage: {disk_usage:.1f}%"
                })
                health_score -= 5
            
            health_status = {
                "timestamp": time.time(),
                "health_score": max(0, health_score),
                "status": "healthy" if health_score > 80 else "degraded" if health_score > 50 else "unhealthy",
                "alerts": alerts,
                "metrics": metrics
            }
            
            # Store health status
            self.redis_client.setex(
                "system_health:latest",
                300,  # 5 minutes TTL
                json.dumps(health_status)
            )
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Failed to check system health: {e}")
            return {
                "timestamp": time.time(),
                "health_score": 0,
                "status": "unknown",
                "alerts": [{"level": "critical", "component": "monitoring", "message": f"Health check failed: {e}"}],
                "metrics": {}
            }


# Celery tasks
@celery_app.task(bind=True)
def run_benchmark_task(self, benchmark_config: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task to run benchmark."""
    worker = BenchmarkWorker()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(worker.run_benchmark(benchmark_config))
        return result
    finally:
        loop.close()


@celery_app.task
def collect_metrics_task() -> Dict[str, Any]:
    """Celery task to collect system metrics."""
    worker = MonitoringWorker()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(worker.collect_system_metrics())
        return result
    finally:
        loop.close()


@celery_app.task
def health_check_task() -> Dict[str, Any]:
    """Celery task to check system health."""
    worker = MonitoringWorker()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(worker.check_system_health())
        return result
    finally:
        loop.close()


# Setup periodic tasks
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'collect-metrics': {
        'task': 'python.mlperf.workers.main.collect_metrics_task',
        'schedule': 30.0,  # Every 30 seconds
    },
    'health-check': {
        'task': 'python.mlperf.workers.main.health_check_task',
        'schedule': 60.0,  # Every minute
    },
}


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Handle worker ready signal."""
    logger.info("ML Performance worker is ready")


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Handle worker shutdown signal."""
    logger.info("ML Performance worker is shutting down")


if __name__ == "__main__":
    # Run worker directly
    celery_app.start() 