"""Optimization agent for performance tuning and improvements."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from mlperf.agents.base import Agent, AgentContext, AgentResponse, AgentTask
from mlperf.utils.logging import get_logger

logger = get_logger(__name__)


class OptimizationAgent(Agent):
    """Agent specialized in ML performance optimization strategies."""
    
    def __init__(self):
        super().__init__(
            name="OptimizationAgent",
            description="ML performance optimization and tuning expert",
            model="gpt-4",
            instructions="""You are an expert in ML system optimization and performance tuning.

Your expertise includes:
1. Memory optimization (gradient checkpointing, mixed precision, model parallelism)
2. Compute optimization (kernel fusion, operator optimization, compilation)
3. Communication optimization (gradient compression, overlapping, NCCL tuning)
4. I/O optimization (data loading, caching, prefetching)
5. Framework-specific optimizations (PyTorch, TensorFlow, JAX)

When providing optimization recommendations:
- Consider the hardware constraints and capabilities
- Analyze the workload characteristics
- Identify bottlenecks and their root causes
- Provide actionable steps with expected impact
- Consider trade-offs between different optimizations
- Prioritize based on implementation effort vs impact
""",
            temperature=0.4,  # Balanced for technical accuracy
        )
        
        # Optimization knowledge base
        self.optimization_strategies = {
            "memory": {
                "gradient_checkpointing": {
                    "description": "Trade compute for memory by recomputing activations",
                    "impact": "30-50% memory reduction",
                    "effort": "low",
                    "frameworks": ["pytorch", "tensorflow"],
                },
                "mixed_precision": {
                    "description": "Use FP16/BF16 for compute, FP32 for master weights",
                    "impact": "50% memory reduction, 2-3x speedup",
                    "effort": "low",
                    "frameworks": ["pytorch", "tensorflow", "jax"],
                },
                "model_sharding": {
                    "description": "Distribute model parameters across devices",
                    "impact": "Enable larger models",
                    "effort": "high",
                    "frameworks": ["pytorch", "tensorflow"],
                },
            },
            "compute": {
                "torch_compile": {
                    "description": "JIT compilation for PyTorch models",
                    "impact": "10-30% speedup",
                    "effort": "low",
                    "frameworks": ["pytorch"],
                },
                "xla_compilation": {
                    "description": "XLA compilation for optimized kernels",
                    "impact": "20-40% speedup",
                    "effort": "medium",
                    "frameworks": ["tensorflow", "jax"],
                },
                "kernel_fusion": {
                    "description": "Fuse multiple operations into single kernel",
                    "impact": "10-20% speedup",
                    "effort": "medium",
                    "frameworks": ["pytorch", "tensorflow"],
                },
            },
            "communication": {
                "gradient_compression": {
                    "description": "Compress gradients during communication",
                    "impact": "30-50% communication reduction",
                    "effort": "medium",
                    "frameworks": ["pytorch", "tensorflow"],
                },
                "overlapping": {
                    "description": "Overlap computation and communication",
                    "impact": "20-30% speedup",
                    "effort": "medium",
                    "frameworks": ["pytorch", "tensorflow"],
                },
                "nccl_tuning": {
                    "description": "Tune NCCL parameters for optimal communication",
                    "impact": "10-20% communication speedup",
                    "effort": "low",
                    "frameworks": ["pytorch", "tensorflow"],
                },
            },
            "io": {
                "data_prefetching": {
                    "description": "Prefetch data to GPU while computing",
                    "impact": "Eliminate I/O bottleneck",
                    "effort": "low",
                    "frameworks": ["pytorch", "tensorflow"],
                },
                "parallel_data_loading": {
                    "description": "Use multiple workers for data loading",
                    "impact": "2-4x data loading speedup",
                    "effort": "low",
                    "frameworks": ["pytorch", "tensorflow"],
                },
                "caching": {
                    "description": "Cache preprocessed data",
                    "impact": "Eliminate preprocessing overhead",
                    "effort": "medium",
                    "frameworks": ["pytorch", "tensorflow", "jax"],
                },
            },
        }
    
    async def process(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Process optimization-related tasks."""
        start_time = datetime.utcnow()
        
        try:
            # Validate task
            if not await self.validate_task(task):
                return AgentResponse(
                    task_id=task.task_id,
                    status="failed",
                    result={"error": "Invalid task for OptimizationAgent"},
                    reasoning="Task type not supported by this agent",
                    confidence=0.0,
                    execution_time=0.0,
                )
            
            # Route to appropriate handler
            if task.task_type == "analyze_bottlenecks":
                response = await self._analyze_bottlenecks(task, context)
            elif task.task_type == "suggest_optimizations":
                response = await self._suggest_optimizations(task, context)
            elif task.task_type == "implement_optimization":
                response = await self._implement_optimization(task, context)
            elif task.task_type == "validate_optimization":
                response = await self._validate_optimization(task, context)
            elif task.task_type == "optimization_roadmap":
                response = await self._create_optimization_roadmap(task, context)
            else:
                response = await self._general_optimization_task(task, context)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            response.execution_time = execution_time
            
            # Update context
            self.update_context(context, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in OptimizationAgent: {e}")
            return AgentResponse(
                task_id=task.task_id,
                status="failed",
                result={"error": str(e)},
                reasoning=f"Error during optimization task processing: {e}",
                confidence=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
            )
    
    async def validate_task(self, task: AgentTask) -> bool:
        """Validate if this agent can handle the task."""
        valid_types = [
            "analyze_bottlenecks",
            "suggest_optimizations",
            "implement_optimization",
            "validate_optimization",
            "optimization_roadmap",
            "optimize",
            "performance_tuning",
        ]
        return task.task_type in valid_types
    
    async def _analyze_bottlenecks(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Analyze performance bottlenecks."""
        metrics = task.parameters.get("metrics", {})
        hardware = task.parameters.get("hardware", {})
        workload = task.parameters.get("workload", {})
        
        bottlenecks = []
        analysis = {
            "primary_bottleneck": None,
            "bottlenecks": [],
            "resource_utilization": {},
            "recommendations": [],
        }
        
        # Analyze GPU utilization
        gpu_util = metrics.get("gpu_utilization", 0)
        if gpu_util < 80:
            severity = "critical" if gpu_util < 50 else "high"
            bottlenecks.append({
                "type": "compute",
                "resource": "GPU",
                "severity": severity,
                "current_utilization": gpu_util,
                "target_utilization": 85,
                "impact": f"Wasting {100 - gpu_util}% of GPU compute capacity",
                "root_causes": self._identify_gpu_bottleneck_causes(metrics, workload),
            })
        
        # Analyze memory bandwidth
        mem_bandwidth_util = metrics.get("memory_bandwidth_utilization", 0)
        if mem_bandwidth_util > 85:
            bottlenecks.append({
                "type": "memory_bandwidth",
                "resource": "GPU Memory",
                "severity": "high",
                "current_utilization": mem_bandwidth_util,
                "target_utilization": 75,
                "impact": "Memory bandwidth saturated, limiting performance",
                "root_causes": ["Large model size", "Inefficient memory access patterns", "Lack of tensor core usage"],
            })
        
        # Analyze CPU-GPU transfer
        pcie_util = metrics.get("pcie_bandwidth_utilization", 0)
        if pcie_util > 50:
            bottlenecks.append({
                "type": "data_transfer",
                "resource": "PCIe",
                "severity": "medium",
                "current_utilization": pcie_util,
                "target_utilization": 30,
                "impact": "Excessive CPU-GPU data transfer",
                "root_causes": ["Small batch processing", "Frequent model updates", "Inefficient data pipeline"],
            })
        
        # Analyze data loading
        data_loading_time = metrics.get("data_loading_time_ratio", 0)
        if data_loading_time > 0.1:  # More than 10% time in data loading
            bottlenecks.append({
                "type": "io",
                "resource": "Data Pipeline",
                "severity": "medium",
                "current_utilization": data_loading_time * 100,
                "target_utilization": 5,
                "impact": f"Spending {data_loading_time * 100:.1f}% time in data loading",
                "root_causes": ["Insufficient data workers", "Complex preprocessing", "No prefetching"],
            })
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        bottlenecks.sort(key=lambda x: severity_order.get(x["severity"], 4))
        
        analysis["bottlenecks"] = bottlenecks
        analysis["primary_bottleneck"] = bottlenecks[0] if bottlenecks else None
        
        # Generate recommendations
        for bottleneck in bottlenecks[:3]:  # Top 3 bottlenecks
            recommendations = self._get_bottleneck_recommendations(bottleneck, workload, hardware)
            analysis["recommendations"].extend(recommendations)
        
        reasoning = f"Identified {len(bottlenecks)} bottlenecks, with {bottlenecks[0]['type'] if bottlenecks else 'none'} as primary"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=analysis,
            reasoning=reasoning,
            confidence=0.85,
            suggestions=[
                f"Focus on resolving {analysis['primary_bottleneck']['type']} bottleneck first" if analysis['primary_bottleneck'] else "System is well-balanced",
                "Profile specific operations for deeper insights",
                "Consider workload characteristics when applying optimizations",
            ],
            next_steps=[
                f"Apply optimization for {b['type']}" for b in bottlenecks[:3]
            ],
        )
    
    async def _suggest_optimizations(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Suggest optimization strategies."""
        bottlenecks = task.parameters.get("bottlenecks", [])
        workload = task.parameters.get("workload", {})
        hardware = task.parameters.get("hardware", {})
        constraints = task.parameters.get("constraints", {})
        
        suggestions = []
        optimization_plan = {
            "immediate": [],  # Can be applied now
            "short_term": [],  # Requires some changes
            "long_term": [],  # Requires significant changes
        }
        
        # Get framework
        framework = workload.get("framework", "pytorch").lower()
        
        # Analyze each bottleneck and suggest optimizations
        for bottleneck in bottlenecks:
            bottleneck_type = bottleneck.get("type", "")
            
            if bottleneck_type == "compute" and bottleneck.get("resource") == "GPU":
                # GPU compute optimizations
                if framework == "pytorch":
                    optimization_plan["immediate"].append({
                        "name": "Enable torch.compile",
                        "type": "compute",
                        "description": "JIT compile model for optimized execution",
                        "implementation": "model = torch.compile(model, mode='max-autotune')",
                        "expected_impact": "10-30% speedup",
                        "effort": "low",
                        "risk": "low",
                    })
                
                if not workload.get("uses_mixed_precision", False):
                    optimization_plan["immediate"].append({
                        "name": "Enable Mixed Precision",
                        "type": "memory_compute",
                        "description": "Use FP16/BF16 for faster computation and lower memory",
                        "implementation": self._get_mixed_precision_implementation(framework),
                        "expected_impact": "2-3x speedup, 50% memory reduction",
                        "effort": "low",
                        "risk": "low",
                    })
                
                if workload.get("batch_size", 1) < hardware.get("recommended_batch_size", 32):
                    optimization_plan["immediate"].append({
                        "name": "Increase Batch Size",
                        "type": "compute",
                        "description": f"Increase batch size from {workload.get('batch_size')} to {hardware.get('recommended_batch_size', 32)}",
                        "implementation": "Adjust dataloader and model configuration",
                        "expected_impact": "Better GPU utilization",
                        "effort": "low",
                        "risk": "low",
                    })
            
            elif bottleneck_type == "memory_bandwidth":
                # Memory bandwidth optimizations
                optimization_plan["short_term"].append({
                    "name": "Enable Gradient Checkpointing",
                    "type": "memory",
                    "description": "Trade compute for memory by recomputing activations",
                    "implementation": self._get_gradient_checkpointing_implementation(framework),
                    "expected_impact": "30-50% memory reduction",
                    "effort": "medium",
                    "risk": "low",
                })
                
                if hardware.get("supports_flash_attention", True):
                    optimization_plan["short_term"].append({
                        "name": "Use Flash Attention",
                        "type": "memory_compute",
                        "description": "Memory-efficient attention implementation",
                        "implementation": "Replace standard attention with Flash Attention",
                        "expected_impact": "4x memory reduction for attention, 2x speedup",
                        "effort": "medium",
                        "risk": "medium",
                    })
            
            elif bottleneck_type == "data_transfer":
                # Data transfer optimizations
                optimization_plan["immediate"].append({
                    "name": "Enable Data Pinning",
                    "type": "io",
                    "description": "Pin memory for faster CPU-GPU transfer",
                    "implementation": "DataLoader(..., pin_memory=True)",
                    "expected_impact": "2x faster data transfer",
                    "effort": "low",
                    "risk": "low",
                })
                
                optimization_plan["short_term"].append({
                    "name": "Use GPU Direct Storage",
                    "type": "io",
                    "description": "Bypass CPU for data loading",
                    "implementation": "Implement GPU Direct Storage pipeline",
                    "expected_impact": "Eliminate CPU bottleneck",
                    "effort": "high",
                    "risk": "medium",
                })
            
            elif bottleneck_type == "io":
                # I/O optimizations
                optimization_plan["immediate"].append({
                    "name": "Increase Data Workers",
                    "type": "io",
                    "description": f"Increase num_workers to {hardware.get('cpu_cores', 8) // 2}",
                    "implementation": f"DataLoader(..., num_workers={hardware.get('cpu_cores', 8) // 2})",
                    "expected_impact": "2-4x faster data loading",
                    "effort": "low",
                    "risk": "low",
                })
                
                optimization_plan["immediate"].append({
                    "name": "Enable Prefetching",
                    "type": "io",
                    "description": "Prefetch data to GPU while computing",
                    "implementation": "DataLoader(..., prefetch_factor=2)",
                    "expected_impact": "Hide data loading latency",
                    "effort": "low",
                    "risk": "low",
                })
        
        # Add distributed training if multiple GPUs available
        if hardware.get("gpu_count", 1) > 1 and not workload.get("is_distributed", False):
            optimization_plan["long_term"].append({
                "name": "Enable Distributed Training",
                "type": "scaling",
                "description": f"Utilize all {hardware.get('gpu_count')} GPUs",
                "implementation": "Implement DDP or FSDP for multi-GPU training",
                "expected_impact": f"{hardware.get('gpu_count')}x throughput increase",
                "effort": "high",
                "risk": "medium",
            })
        
        # Calculate total expected impact
        total_impact = self._estimate_combined_impact(optimization_plan)
        
        reasoning = f"Suggested {sum(len(opts) for opts in optimization_plan.values())} optimizations across immediate, short-term, and long-term categories"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result={
                "optimization_plan": optimization_plan,
                "total_optimizations": sum(len(opts) for opts in optimization_plan.values()),
                "estimated_total_impact": total_impact,
                "implementation_order": self._get_implementation_order(optimization_plan),
            },
            reasoning=reasoning,
            confidence=0.8,
            suggestions=[
                "Start with immediate optimizations for quick wins",
                "Test each optimization in isolation before combining",
                "Monitor system stability after each change",
            ],
            next_steps=[
                f"Implement {opt['name']}" for opt in optimization_plan["immediate"][:3]
            ],
        )
    
    async def _implement_optimization(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Provide detailed implementation guide for optimization."""
        optimization = task.parameters.get("optimization", {})
        framework = task.parameters.get("framework", "pytorch")
        current_code = task.parameters.get("current_code", "")
        
        implementation_guide = {
            "optimization": optimization.get("name"),
            "steps": [],
            "code_changes": [],
            "configuration": {},
            "validation": [],
            "rollback_plan": [],
        }
        
        # Generate implementation steps based on optimization type
        opt_type = optimization.get("type", "")
        
        if opt_type == "compute" and "torch.compile" in optimization.get("name", ""):
            implementation_guide["steps"] = [
                "Install latest PyTorch version (>= 2.0)",
                "Wrap model with torch.compile",
                "Choose compilation mode based on needs",
                "Handle dynamic shapes if present",
                "Test with sample inputs",
            ]
            
            implementation_guide["code_changes"].append({
                "description": "Add torch.compile to model",
                "before": "model = MyModel()",
                "after": """model = MyModel()
model = torch.compile(
    model,
    mode='max-autotune',  # Options: 'default', 'reduce-overhead', 'max-autotune'
    fullgraph=True,       # Compile entire graph
    dynamic=False         # Set True if using dynamic shapes
)""",
            })
            
            implementation_guide["configuration"] = {
                "environment_variables": {
                    "TORCH_COMPILE_DEBUG": "0",
                    "TORCH_LOGS": "+dynamo",
                    "TORCH_DYNAMO_VERBOSE": "1",
                },
                "compilation_options": {
                    "backend": "inductor",  # Default backend
                    "mode": "max-autotune",
                    "cache_size_limit": 64,
                },
            }
            
            implementation_guide["validation"] = [
                "Compare outputs with original model",
                "Measure compilation time (first iteration)",
                "Measure speedup after warmup",
                "Check memory usage",
            ]
        
        elif opt_type in ["memory_compute", "memory"] and "mixed_precision" in optimization.get("name", "").lower():
            implementation_guide["steps"] = [
                "Install apex or use native AMP",
                "Wrap model and optimizer",
                "Scale loss for gradient computation",
                "Update training loop",
                "Monitor for numerical instability",
            ]
            
            if framework == "pytorch":
                implementation_guide["code_changes"].append({
                    "description": "Enable Automatic Mixed Precision",
                    "before": """for batch in dataloader:
    optimizer.zero_grad()
    output = model(batch)
    loss = criterion(output, target)
    loss.backward()
    optimizer.step()""",
                    "after": """scaler = torch.cuda.amp.GradScaler()

for batch in dataloader:
    optimizer.zero_grad()
    
    with torch.cuda.amp.autocast(dtype=torch.float16):
        output = model(batch)
        loss = criterion(output, target)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()""",
                })
        
        elif opt_type == "memory" and "gradient_checkpointing" in optimization.get("name", "").lower():
            implementation_guide["steps"] = [
                "Identify checkpointing boundaries",
                "Modify model to support checkpointing",
                "Update forward pass",
                "Verify gradient computation",
                "Measure memory savings",
            ]
            
            implementation_guide["code_changes"].append({
                "description": "Enable gradient checkpointing",
                "before": "output = model(input)",
                "after": """# For transformer models
model.gradient_checkpointing_enable()
output = model(input)

# For custom models
from torch.utils.checkpoint import checkpoint

class CheckpointedModel(nn.Module):
    def forward(self, x):
        # Checkpoint specific layers
        x = checkpoint(self.layer1, x)
        x = checkpoint(self.layer2, x)
        return self.layer3(x)""",
            })
        
        # Rollback plan
        implementation_guide["rollback_plan"] = [
            "Keep original model configuration",
            "Create feature flag for optimization",
            "Implement A/B testing capability",
            "Monitor performance metrics",
            "Have quick rollback script ready",
        ]
        
        reasoning = f"Generated implementation guide for {optimization.get('name')} with {len(implementation_guide['steps'])} steps"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=implementation_guide,
            reasoning=reasoning,
            confidence=0.85,
            suggestions=[
                "Test in development environment first",
                "Implement gradual rollout",
                "Monitor system metrics closely",
                "Document all changes for team",
            ],
            next_steps=[
                "Implement code changes",
                "Run validation tests",
                "Measure performance impact",
                "Update documentation",
            ],
        )
    
    async def _validate_optimization(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Validate optimization results."""
        before_metrics = task.parameters.get("before_metrics", {})
        after_metrics = task.parameters.get("after_metrics", {})
        optimization = task.parameters.get("optimization", {})
        
        validation_result = {
            "success": False,
            "improvements": {},
            "regressions": {},
            "unexpected_changes": [],
            "recommendations": [],
        }
        
        # Compare key metrics
        metrics_to_compare = [
            ("throughput", True),  # Higher is better
            ("latency", False),    # Lower is better
            ("memory_usage", False),
            ("gpu_utilization", True),
            ("accuracy", True),
        ]
        
        for metric, higher_is_better in metrics_to_compare:
            if metric in before_metrics and metric in after_metrics:
                before_val = before_metrics[metric]
                after_val = after_metrics[metric]
                
                if before_val > 0:  # Avoid division by zero
                    change = ((after_val - before_val) / before_val) * 100
                    
                    if (higher_is_better and change > 5) or (not higher_is_better and change < -5):
                        validation_result["improvements"][metric] = {
                            "before": before_val,
                            "after": after_val,
                            "change_percent": change,
                        }
                    elif (higher_is_better and change < -5) or (not higher_is_better and change > 5):
                        validation_result["regressions"][metric] = {
                            "before": before_val,
                            "after": after_val,
                            "change_percent": change,
                        }
        
        # Check if optimization met expectations
        expected_impact = optimization.get("expected_impact", "")
        actual_impact = validation_result["improvements"].get("throughput", {}).get("change_percent", 0)
        
        validation_result["success"] = len(validation_result["improvements"]) > len(validation_result["regressions"])
        
        # Check for unexpected changes
        if "accuracy" in validation_result["regressions"]:
            validation_result["unexpected_changes"].append({
                "issue": "Accuracy degradation",
                "severity": "high",
                "recommendation": "Review numerical precision settings",
            })
        
        if "memory_usage" in validation_result["improvements"] and "memory" not in optimization.get("type", ""):
            validation_result["unexpected_changes"].append({
                "issue": "Unexpected memory improvement",
                "severity": "low",
                "recommendation": "Verify measurement methodology",
            })
        
        # Generate recommendations
        if validation_result["success"]:
            validation_result["recommendations"].append("Optimization successful, consider deploying")
            validation_result["recommendations"].append("Document configuration for reproducibility")
        else:
            validation_result["recommendations"].append("Review optimization parameters")
            validation_result["recommendations"].append("Consider alternative approaches")
        
        reasoning = f"Validation {'successful' if validation_result['success'] else 'failed'} with {len(validation_result['improvements'])} improvements and {len(validation_result['regressions'])} regressions"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success" if validation_result["success"] else "partial",
            result=validation_result,
            reasoning=reasoning,
            confidence=0.9,
            suggestions=[
                "Run extended validation with production workload",
                "Monitor long-term stability",
                "Create performance regression tests",
            ],
            next_steps=[
                "Deploy optimization" if validation_result["success"] else "Investigate regressions",
                "Update performance baselines",
                "Share results with team",
            ],
        )
    
    async def _create_optimization_roadmap(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Create comprehensive optimization roadmap."""
        current_performance = task.parameters.get("current_performance", {})
        target_performance = task.parameters.get("target_performance", {})
        constraints = task.parameters.get("constraints", {})
        timeline = task.parameters.get("timeline_weeks", 12)
        
        roadmap = {
            "phases": [],
            "milestones": [],
            "risk_mitigation": [],
            "success_metrics": [],
            "resource_requirements": {},
        }
        
        # Calculate performance gaps
        throughput_gap = (target_performance.get("throughput", 0) - current_performance.get("throughput", 0)) / current_performance.get("throughput", 1)
        latency_gap = (current_performance.get("latency", 0) - target_performance.get("latency", 0)) / current_performance.get("latency", 1)
        
        # Phase 1: Quick wins (Weeks 1-2)
        roadmap["phases"].append({
            "name": "Quick Wins",
            "duration_weeks": 2,
            "objectives": ["Implement low-effort optimizations", "Establish baselines"],
            "optimizations": [
                {
                    "name": "Enable Compilation",
                    "effort_days": 1,
                    "expected_impact": "10-20% speedup",
                    "risk": "low",
                },
                {
                    "name": "Optimize Data Pipeline",
                    "effort_days": 2,
                    "expected_impact": "Eliminate I/O bottleneck",
                    "risk": "low",
                },
                {
                    "name": "Tune Batch Sizes",
                    "effort_days": 1,
                    "expected_impact": "Better resource utilization",
                    "risk": "low",
                },
            ],
            "deliverables": ["Performance baseline report", "Initial optimization results"],
        })
        
        # Phase 2: Core optimizations (Weeks 3-6)
        roadmap["phases"].append({
            "name": "Core Optimizations",
            "duration_weeks": 4,
            "objectives": ["Implement major performance improvements", "Address primary bottlenecks"],
            "optimizations": [
                {
                    "name": "Mixed Precision Training",
                    "effort_days": 3,
                    "expected_impact": "2x speedup, 50% memory reduction",
                    "risk": "medium",
                },
                {
                    "name": "Gradient Checkpointing",
                    "effort_days": 2,
                    "expected_impact": "40% memory reduction",
                    "risk": "low",
                },
                {
                    "name": "Kernel Optimization",
                    "effort_days": 5,
                    "expected_impact": "20-30% compute speedup",
                    "risk": "medium",
                },
            ],
            "deliverables": ["Optimized model configuration", "Performance improvement report"],
        })
        
        # Phase 3: Advanced optimizations (Weeks 7-10)
        roadmap["phases"].append({
            "name": "Advanced Optimizations",
            "duration_weeks": 4,
            "objectives": ["Implement distributed training", "Fine-tune performance"],
            "optimizations": [
                {
                    "name": "Multi-GPU Scaling",
                    "effort_days": 5,
                    "expected_impact": "Linear scaling with GPUs",
                    "risk": "high",
                },
                {
                    "name": "Advanced Memory Management",
                    "effort_days": 3,
                    "expected_impact": "Enable larger models",
                    "risk": "medium",
                },
                {
                    "name": "Custom Operators",
                    "effort_days": 7,
                    "expected_impact": "30% speedup for specific ops",
                    "risk": "high",
                },
            ],
            "deliverables": ["Distributed training setup", "Custom optimization library"],
        })
        
        # Phase 4: Production hardening (Weeks 11-12)
        roadmap["phases"].append({
            "name": "Production Hardening",
            "duration_weeks": 2,
            "objectives": ["Ensure stability", "Create monitoring"],
            "optimizations": [
                {
                    "name": "Stability Testing",
                    "effort_days": 3,
                    "expected_impact": "Production readiness",
                    "risk": "low",
                },
                {
                    "name": "Performance Monitoring",
                    "effort_days": 2,
                    "expected_impact": "Continuous optimization",
                    "risk": "low",
                },
            ],
            "deliverables": ["Production deployment guide", "Monitoring dashboard"],
        })
        
        # Define milestones
        roadmap["milestones"] = [
            {
                "week": 2,
                "name": "Baseline Established",
                "success_criteria": "10% performance improvement",
            },
            {
                "week": 6,
                "name": "Core Optimizations Complete",
                "success_criteria": "50% progress toward target",
            },
            {
                "week": 10,
                "name": "Advanced Features Implemented",
                "success_criteria": "80% of target performance achieved",
            },
            {
                "week": 12,
                "name": "Production Ready",
                "success_criteria": "Meet all performance targets with stability",
            },
        ]
        
        # Risk mitigation
        roadmap["risk_mitigation"] = [
            {
                "risk": "Accuracy degradation",
                "mitigation": "Continuous accuracy monitoring, gradual rollout",
            },
            {
                "risk": "System instability",
                "mitigation": "Comprehensive testing, rollback procedures",
            },
            {
                "risk": "Resource constraints",
                "mitigation": "Phased implementation, resource planning",
            },
        ]
        
        # Success metrics
        roadmap["success_metrics"] = [
            {
                "metric": "Throughput",
                "current": current_performance.get("throughput", 0),
                "target": target_performance.get("throughput", 0),
                "measurement": "Samples per second",
            },
            {
                "metric": "Latency",
                "current": current_performance.get("latency", 0),
                "target": target_performance.get("latency", 0),
                "measurement": "P99 latency in ms",
            },
            {
                "metric": "Cost Efficiency",
                "current": current_performance.get("cost_per_sample", 0),
                "target": target_performance.get("cost_per_sample", 0),
                "measurement": "$ per million inferences",
            },
        ]
        
        # Resource requirements
        roadmap["resource_requirements"] = {
            "engineering_hours": sum(
                opt["effort_days"] * 8
                for phase in roadmap["phases"]
                for opt in phase["optimizations"]
            ),
            "compute_resources": "4x A100 GPUs for testing",
            "tools": ["Profiling tools", "Monitoring infrastructure"],
        }
        
        reasoning = f"Created {timeline}-week optimization roadmap with {len(roadmap['phases'])} phases"
        
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result=roadmap,
            reasoning=reasoning,
            confidence=0.8,
            suggestions=[
                "Adjust timeline based on team capacity",
                "Create detailed project plan",
                "Establish regular review checkpoints",
            ],
            next_steps=[
                "Get stakeholder approval",
                "Allocate resources",
                "Begin Phase 1 implementation",
            ],
        )
    
    async def _general_optimization_task(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Handle general optimization tasks."""
        return AgentResponse(
            task_id=task.task_id,
            status="success",
            result={
                "response": "General optimization task processed",
                "task_type": task.task_type,
                "framework_recommendations": self._get_framework_specific_tips(
                    task.parameters.get("framework", "pytorch")
                ),
            },
            reasoning="Processed general optimization query using knowledge base",
            confidence=0.75,
            suggestions=[
                "Profile your specific workload",
                "Start with easy optimizations",
                "Measure impact of each change",
            ],
            next_steps=[
                "Identify performance bottlenecks",
                "Select appropriate optimizations",
                "Implement and validate",
            ],
        )
    
    def _identify_gpu_bottleneck_causes(self, metrics: Dict[str, Any], workload: Dict[str, Any]) -> List[str]:
        """Identify root causes of GPU underutilization."""
        causes = []
        
        if metrics.get("cpu_utilization", 0) > 90:
            causes.append("CPU bottleneck limiting GPU feed rate")
        
        if workload.get("batch_size", 1) < 16:
            causes.append("Small batch size not fully utilizing GPU")
        
        if metrics.get("data_loading_time_ratio", 0) > 0.1:
            causes.append("Data pipeline cannot keep up with GPU")
        
        if metrics.get("kernel_launch_overhead", 0) > 0.2:
            causes.append("Too many small kernels, consider fusion")
        
        return causes if causes else ["Unknown cause - requires profiling"]
    
    def _get_bottleneck_recommendations(
        self,
        bottleneck: Dict[str, Any],
        workload: Dict[str, Any],
        hardware: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get specific recommendations for a bottleneck."""
        recommendations = []
        bottleneck_type = bottleneck.get("type", "")
        
        if bottleneck_type == "compute":
            if workload.get("framework") == "pytorch":
                recommendations.append({
                    "optimization": "torch.compile",
                    "priority": "high",
                    "effort": "low",
                })
            recommendations.append({
                "optimization": "mixed_precision",
                "priority": "high",
                "effort": "low",
            })
        
        elif bottleneck_type == "memory_bandwidth":
            recommendations.append({
                "optimization": "gradient_checkpointing",
                "priority": "high",
                "effort": "medium",
            })
            recommendations.append({
                "optimization": "model_parallelism",
                "priority": "medium",
                "effort": "high",
            })
        
        return recommendations
    
    def _get_mixed_precision_implementation(self, framework: str) -> str:
        """Get framework-specific mixed precision implementation."""
        implementations = {
            "pytorch": """# PyTorch Automatic Mixed Precision
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
for batch in dataloader:
    with autocast():
        output = model(batch)
        loss = criterion(output, target)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()""",
            
            "tensorflow": """# TensorFlow Mixed Precision
from tensorflow.keras import mixed_precision

policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)

# Wrap optimizer
optimizer = mixed_precision.LossScaleOptimizer(optimizer)""",
            
            "jax": """# JAX Mixed Precision
from jax import config
config.update("jax_enable_x64", False)

# Use jnp.float16 for computations
params = jax.tree_map(lambda x: x.astype(jnp.float16), params)"""
        }
        
        return implementations.get(framework, "Framework-specific implementation needed")
    
    def _get_gradient_checkpointing_implementation(self, framework: str) -> str:
        """Get framework-specific gradient checkpointing implementation."""
        implementations = {
            "pytorch": """# PyTorch Gradient Checkpointing
from torch.utils.checkpoint import checkpoint

# For existing models
model.gradient_checkpointing_enable()

# For custom implementation
def forward(self, x):
    x = checkpoint(self.layer1, x)
    x = checkpoint(self.layer2, x)
    return self.layer3(x)""",
            
            "tensorflow": """# TensorFlow Gradient Checkpointing
import tensorflow as tf

@tf.recompute_grad
def checkpointed_block(x):
    # Expensive operations here
    return layer(x)""",
        }
        
        return implementations.get(framework, "Framework-specific implementation needed")
    
    def _estimate_combined_impact(self, optimization_plan: Dict[str, List]) -> Dict[str, Any]:
        """Estimate combined impact of optimizations."""
        # Simple estimation - in reality would use more sophisticated modeling
        total_speedup = 1.0
        total_memory_reduction = 0.0
        
        for phase_opts in optimization_plan.values():
            for opt in phase_opts:
                impact = opt.get("expected_impact", "")
                
                # Parse speedup
                if "speedup" in impact:
                    if "2x" in impact:
                        total_speedup *= 2.0
                    elif "3x" in impact:
                        total_speedup *= 3.0
                    elif "%" in impact:
                        percent = float(impact.split("%")[0].split()[-1])
                        total_speedup *= (1 + percent / 100)
                
                # Parse memory reduction
                if "memory reduction" in impact and "%" in impact:
                    percent = float(impact.split("%")[0].split()[-1])
                    total_memory_reduction += percent
        
        return {
            "estimated_speedup": f"{total_speedup:.1f}x",
            "estimated_memory_reduction": f"{min(total_memory_reduction, 70):.0f}%",
            "confidence": "medium",
        }
    
    def _get_implementation_order(self, optimization_plan: Dict[str, List]) -> List[str]:
        """Get recommended implementation order."""
        order = []
        
        # Sort by effort and impact
        all_opts = []
        for phase, opts in optimization_plan.items():
            for opt in opts:
                all_opts.append((phase, opt))
        
        # Simple heuristic: low effort + high impact first
        effort_score = {"low": 1, "medium": 2, "high": 3}
        
        all_opts.sort(key=lambda x: (
            effort_score.get(x[1].get("effort", "medium"), 2),
            x[0] != "immediate"  # Immediate phase first
        ))
        
        return [opt[1]["name"] for opt in all_opts[:5]]  # Top 5
    
    def _get_framework_specific_tips(self, framework: str) -> List[str]:
        """Get framework-specific optimization tips."""
        tips = {
            "pytorch": [
                "Use torch.compile for automatic optimization",
                "Enable cudnn.benchmark for consistent workloads",
                "Use channels_last memory format for CNNs",
                "Profile with torch.profiler",
            ],
            "tensorflow": [
                "Enable XLA compilation with jit_compile=True",
                "Use tf.function for graph optimization",
                "Enable mixed precision with keras.mixed_precision",
                "Profile with TensorBoard Profiler",
            ],
            "jax": [
                "Use jax.jit for compilation",
                "Leverage XLA's optimization passes",
                "Use jax.pmap for data parallelism",
                "Profile with jax.profiler",
            ],
        }
        
        return tips.get(framework, ["Profile your workload", "Start with standard optimizations"])