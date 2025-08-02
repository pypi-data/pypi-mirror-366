"""Benchmark agent for running and analyzing benchmarks."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from mlperf.agents.base import Agent, AgentContext, AgentResponse, AgentTask
from mlperf.utils.logging import get_logger

logger = get_logger(__name__)


class BenchmarkAgent(Agent):
    """Agent specialized in running and analyzing benchmarks."""
    
    def __init__(self):
        super().__init__(
            name="BenchmarkAgent",
            description="ML benchmark execution and analysis",
            model="gpt-4",
            instructions="""You are an expert in ML benchmarking and performance testing.
            
Your responsibilities include:
1. Selecting appropriate benchmarks for given workloads
2. Configuring benchmark parameters for optimal testing
3. Analyzing benchmark results and identifying performance issues
4. Comparing results across different configurations
5. Providing actionable recommendations based on benchmark data

When analyzing benchmarks, consider:
- Hardware utilization (GPU, CPU, memory)
- Throughput and latency metrics
- Scalability across different batch sizes
- Framework-specific optimizations
- Cost-performance trade-offs
""",
            temperature=0.3,  # Lower temperature for more consistent analysis
        )
    
    async def process(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Process benchmark-related tasks."""
        start_time = datetime.utcnow()
        
        try:
            # Validate task
            if not await self.validate_task(task):
                return AgentResponse(
                    task_id=task.task_id,
                    status="failed",
                    result={"error": "Invalid task for BenchmarkAgent"},
                    reasoning="Task type not supported by this agent",
                    confidence=0.0,
                    execution_time=0.0,
                )
            
            # Route to appropriate handler
            if task.task_type == "select_benchmark":
                response = await self._select_benchmark(task, context)
            elif task.task_type == "configure_benchmark":
                response = await self._configure_benchmark(task, context)
            elif task.task_type == "analyze_results":
                response = await self._analyze_results(task, context)
            elif task.task_type == "compare_benchmarks":
                response = await self._compare_benchmarks(task, context)
            else:
                response = await self._general_benchmark_task(task, context)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            response.execution_time = execution_time
            
            # Update context
            self.update_context(context, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in BenchmarkAgent: {e}")
            return AgentResponse(
                task_id=task.task_id,
                status="failed",
                result={"error": str(e)},
                reasoning=f"Error during benchmark task processing: {e}",
                confidence=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
            )
    
    async def validate_task(self, task: AgentTask) -> bool:
        """Validate if this agent can handle the task."""
        valid_types = [
            "select_benchmark",
            "configure_benchmark",
            "analyze_results",
            "compare_benchmarks",
            "benchmark",
            "performance_test",
        ]
        return task.task_type in valid_types
    
    async def _select_benchmark(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Select appropriate benchmarks for a workload."""
        params = task.parameters
        
        # Extract workload characteristics
        workload_type = params.get("workload_type", "training")
        framework = params.get("framework", "pytorch")
        model_type = params.get("model_type", "transformer")
        hardware = params.get("hardware", {})
        
        # Select benchmarks based on characteristics
        selected_benchmarks = []
        reasoning = []
        
        # Training benchmarks
        if workload_type == "training":
            if model_type == "transformer":
                selected_benchmarks.append({
                    "name": "transformer_training_benchmark",
                    "type": "training",
                    "description": "Transformer model training performance",
                    "parameters": {
                        "model_sizes": ["small", "base", "large"],
                        "batch_sizes": [8, 16, 32, 64],
                        "sequence_lengths": [128, 256, 512],
                        "precision": ["fp32", "fp16", "bf16"],
                    }
                })
                reasoning.append("Selected transformer training benchmark for comprehensive performance analysis")
            
            selected_benchmarks.append({
                "name": "memory_bandwidth_test",
                "type": "memory",
                "description": "Memory bandwidth and efficiency test",
                "parameters": {
                    "test_sizes": ["1GB", "4GB", "8GB"],
                    "access_patterns": ["sequential", "random"],
                }
            })
            reasoning.append("Added memory bandwidth test to identify potential memory bottlenecks")
        
        # Inference benchmarks
        elif workload_type == "inference":
            selected_benchmarks.append({
                "name": "inference_latency_benchmark",
                "type": "inference",
                "description": "Model inference latency testing",
                "parameters": {
                    "batch_sizes": [1, 8, 16, 32],
                    "optimization_levels": ["none", "onnx", "tensorrt"],
                    "quantization": ["none", "int8", "fp16"],
                }
            })
            reasoning.append("Selected inference latency benchmark for deployment optimization")
        
        # Multi-GPU benchmarks
        if hardware.get("gpu_count", 1) > 1:
            selected_benchmarks.append({
                "name": "distributed_scaling_test",
                "type": "distributed",
                "description": "Multi-GPU scaling efficiency",
                "parameters": {
                    "gpu_counts": [1, 2, 4, hardware.get("gpu_count")],
                    "communication_backends": ["nccl", "gloo"],
                }
            })
            reasoning.append(f"Added distributed scaling test for {hardware.get('gpu_count')} GPUs")
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result={
                "selected_benchmarks": selected_benchmarks,
                "total_benchmarks": len(selected_benchmarks),
                "estimated_runtime": sum(b.get("estimated_runtime", 300) for b in selected_benchmarks),
            },
            reasoning=" ".join(reasoning),
            confidence=0.9,
            suggestions=[
                "Run benchmarks in order of increasing complexity",
                "Monitor system resources during benchmark execution",
                "Ensure consistent thermal conditions for reliable results",
            ],
            next_steps=[
                "Configure each benchmark with optimal parameters",
                "Set up monitoring for benchmark execution",
                "Prepare baseline results for comparison",
            ],
        )
    
    async def _configure_benchmark(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Configure benchmark parameters for optimal testing."""
        params = task.parameters
        benchmark_name = params.get("benchmark_name")
        hardware = params.get("hardware", {})
        constraints = params.get("constraints", {})
        
        # Generate configuration based on hardware and constraints
        configuration = {
            "execution_mode": "performance",  # or "accuracy", "stress"
            "warmup_iterations": 10,
            "measurement_iterations": 100,
            "timeout_seconds": 3600,
            "resource_limits": {
                "max_memory_gb": hardware.get("gpu_memory_gb", 16) * 0.9,  # Leave 10% buffer
                "max_threads": hardware.get("cpu_threads", 32),
            },
            "optimization_flags": [],
            "environment_variables": {},
        }
        
        # Framework-specific configurations
        if params.get("framework") == "pytorch":
            configuration["optimization_flags"].extend([
                "--cuda-graphs",
                "--channels-last",
                "--tf32",
            ])
            configuration["environment_variables"].update({
                "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512",
                "CUDA_LAUNCH_BLOCKING": "0",
            })
        elif params.get("framework") == "tensorflow":
            configuration["optimization_flags"].extend([
                "--xla",
                "--mixed-precision",
            ])
            configuration["environment_variables"].update({
                "TF_XLA_FLAGS": "--tf_xla_auto_jit=2",
                "TF_CUDNN_DETERMINISTIC": "0",
            })
        
        # Adjust based on constraints
        if constraints.get("max_runtime_minutes"):
            configuration["timeout_seconds"] = constraints["max_runtime_minutes"] * 60
            configuration["measurement_iterations"] = min(
                configuration["measurement_iterations"],
                constraints["max_runtime_minutes"] * 60 // 10  # Assume 10s per iteration
            )
        
        reasoning = f"Configured benchmark for {params.get('framework')} on {hardware.get('gpu_model', 'GPU')}"
        reasoning += f" with {configuration['measurement_iterations']} iterations"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result={
                "configuration": configuration,
                "estimated_runtime_seconds": configuration["warmup_iterations"] * 5 + configuration["measurement_iterations"] * 10,
            },
            reasoning=reasoning,
            confidence=0.85,
            suggestions=[
                "Adjust warmup iterations if results show high variance",
                "Consider running multiple times for statistical significance",
                "Monitor temperature throttling during execution",
            ],
            next_steps=[
                "Validate configuration with a quick test run",
                "Set up result collection and monitoring",
                "Prepare for benchmark execution",
            ],
        )
    
    async def _analyze_results(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Analyze benchmark results and identify issues."""
        results = task.parameters.get("results", {})
        baseline = task.parameters.get("baseline", {})
        
        analysis = {
            "performance_summary": {},
            "bottlenecks": [],
            "optimization_opportunities": [],
            "anomalies": [],
        }
        
        # Analyze key metrics
        if "throughput" in results:
            throughput = results["throughput"]
            analysis["performance_summary"]["throughput"] = {
                "value": throughput,
                "unit": "samples/sec",
                "rating": self._rate_throughput(throughput, results.get("batch_size", 32)),
            }
            
            if baseline and "throughput" in baseline:
                improvement = ((throughput - baseline["throughput"]) / baseline["throughput"]) * 100
                analysis["performance_summary"]["throughput"]["improvement"] = improvement
        
        # Identify bottlenecks
        if results.get("gpu_utilization", 0) < 80:
            analysis["bottlenecks"].append({
                "type": "gpu_underutilization",
                "severity": "high" if results.get("gpu_utilization", 0) < 50 else "medium",
                "description": f"GPU utilization is only {results.get('gpu_utilization', 0)}%",
                "impact": "Suboptimal performance, wasting GPU resources",
            })
            analysis["optimization_opportunities"].append({
                "type": "increase_batch_size",
                "description": "Increase batch size to improve GPU utilization",
                "expected_improvement": "15-30%",
            })
        
        if results.get("memory_bandwidth_utilization", 0) > 90:
            analysis["bottlenecks"].append({
                "type": "memory_bandwidth",
                "severity": "high",
                "description": "Memory bandwidth is saturated",
                "impact": "Performance limited by memory transfer speed",
            })
            analysis["optimization_opportunities"].append({
                "type": "memory_optimization",
                "description": "Enable tensor cores or reduce memory access patterns",
                "expected_improvement": "10-20%",
            })
        
        # Check for anomalies
        if "latency_percentiles" in results:
            p99 = results["latency_percentiles"].get("p99", 0)
            p50 = results["latency_percentiles"].get("p50", 0)
            if p99 > p50 * 3:
                analysis["anomalies"].append({
                    "type": "high_latency_variance",
                    "description": "P99 latency is more than 3x P50",
                    "recommendation": "Investigate source of latency spikes",
                })
        
        reasoning = f"Analyzed benchmark results with {len(analysis['bottlenecks'])} bottlenecks identified"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=analysis,
            reasoning=reasoning,
            confidence=0.8,
            suggestions=[
                f"Focus on addressing {analysis['bottlenecks'][0]['type']}" if analysis['bottlenecks'] else "Performance looks good",
                "Run profiling tools for deeper analysis",
                "Test optimization suggestions in isolation",
            ],
            next_steps=[
                f"Implement {opt['type']} optimization" for opt in analysis['optimization_opportunities'][:3]
            ],
        )
    
    async def _compare_benchmarks(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Compare benchmark results across different configurations."""
        benchmark_runs = task.parameters.get("runs", [])
        comparison_metrics = task.parameters.get("metrics", ["throughput", "latency", "memory_usage"])
        
        comparison = {
            "summary": {},
            "best_configuration": None,
            "rankings": {},
            "trade_offs": [],
        }
        
        # Calculate rankings for each metric
        for metric in comparison_metrics:
            values = []
            for i, run in enumerate(benchmark_runs):
                if metric in run.get("results", {}):
                    values.append({
                        "run_id": run.get("id", i),
                        "configuration": run.get("configuration", {}),
                        "value": run["results"][metric],
                    })
            
            # Sort by metric (higher is better for throughput, lower for latency)
            reverse = metric in ["throughput", "samples_per_second"]
            values.sort(key=lambda x: x["value"], reverse=reverse)
            
            comparison["rankings"][metric] = values
            
            if values:
                comparison["summary"][metric] = {
                    "best": values[0],
                    "worst": values[-1],
                    "improvement": ((values[0]["value"] - values[-1]["value"]) / values[-1]["value"] * 100) if reverse
                    else ((values[-1]["value"] - values[0]["value"]) / values[0]["value"] * 100),
                }
        
        # Identify best overall configuration
        if comparison["rankings"]:
            # Simple scoring based on rankings
            scores = {}
            for metric_rankings in comparison["rankings"].values():
                for i, entry in enumerate(metric_rankings):
                    run_id = entry["run_id"]
                    scores[run_id] = scores.get(run_id, 0) + len(metric_rankings) - i
            
            best_run_id = max(scores, key=scores.get)
            comparison["best_configuration"] = {
                "run_id": best_run_id,
                "score": scores[best_run_id],
                "configuration": next(r["configuration"] for r in benchmark_runs if r.get("id") == best_run_id),
            }
        
        # Identify trade-offs
        if "throughput" in comparison["rankings"] and "memory_usage" in comparison["rankings"]:
            comparison["trade_offs"].append({
                "type": "throughput_vs_memory",
                "description": "Higher throughput configurations typically use more memory",
                "recommendation": "Choose based on your resource constraints",
            })
        
        reasoning = f"Compared {len(benchmark_runs)} benchmark runs across {len(comparison_metrics)} metrics"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=comparison,
            reasoning=reasoning,
            confidence=0.85,
            suggestions=[
                f"Best overall configuration is run {comparison['best_configuration']['run_id']}" if comparison.get("best_configuration") else "Need more data for comparison",
                "Consider running additional configurations to find optimal settings",
                "Validate results with longer benchmark runs",
            ],
            next_steps=[
                "Deploy best configuration to production",
                "Document configuration choices and trade-offs",
                "Set up continuous benchmarking pipeline",
            ],
        )
    
    async def _general_benchmark_task(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Handle general benchmark-related tasks."""
        # This is a fallback for general benchmark questions
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result={
                "response": "General benchmark task processed",
                "task_type": task.task_type,
                "parameters": task.parameters,
            },
            reasoning="Processed general benchmark task using domain expertise",
            confidence=0.7,
            suggestions=[
                "Consider running specific benchmarks for detailed analysis",
                "Use profiling tools for deeper insights",
                "Compare against industry baselines",
            ],
            next_steps=[
                "Define specific benchmark objectives",
                "Select appropriate benchmark suite",
                "Configure benchmark parameters",
            ],
        )
    
    def _rate_throughput(self, throughput: float, batch_size: int) -> str:
        """Rate throughput performance."""
        # Simple heuristic - adjust based on actual hardware capabilities
        samples_per_gpu_per_sec = throughput / batch_size
        
        if samples_per_gpu_per_sec > 1000:
            return "excellent"
        elif samples_per_gpu_per_sec > 500:
            return "good"
        elif samples_per_gpu_per_sec > 100:
            return "acceptable"
        else:
            return "poor"