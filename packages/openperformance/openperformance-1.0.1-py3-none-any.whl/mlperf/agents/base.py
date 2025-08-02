"""Base classes for AI agents."""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from mlperf.utils.logging import get_logger

logger = get_logger(__name__)


class AgentTask(BaseModel):
    """Task definition for agents."""
    
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task")
    description: str = Field(..., description="Task description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context")
    priority: int = Field(1, description="Task priority (1-10)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response from agent execution."""
    
    task_id: str
    status: str = Field(..., description="success, failed, partial")
    result: Any = Field(..., description="Task result")
    reasoning: str = Field(..., description="Agent's reasoning process")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score")
    suggestions: List[str] = Field(default_factory=list, description="Additional suggestions")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = Field(0.0, description="Execution time in seconds")
    tokens_used: int = Field(0, description="Number of tokens used")


@dataclass
class AgentContext:
    """Context for agent execution."""
    
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    session_id: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """Base class for AI agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gpt-4",
        instructions: str = "",
        tools: Optional[List[Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.name = name
        self.description = description
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.execution_count = 0
        self.total_tokens = 0
        
        # Initialize logger
        self.logger = get_logger(f"{__name__}.{self.name}")
    
    @abstractmethod
    async def process(self, task: AgentTask, context: AgentContext) -> AgentResponse:
        """Process a task and return response."""
        pass
    
    def get_system_prompt(self, task: AgentTask, context: AgentContext) -> str:
        """Generate system prompt for the agent."""
        base_prompt = f"""You are {self.name}, an AI assistant specialized in {self.description}.

{self.instructions}

Current task: {task.description}
Task type: {task.task_type}
Task parameters: {json.dumps(task.parameters, indent=2)}

Context:
- User ID: {context.user_id}
- Project ID: {context.project_id}
- Session ID: {context.session_id}

Please provide a detailed analysis and actionable recommendations."""
        
        return base_prompt
    
    def format_history(self, context: AgentContext, max_entries: int = 10) -> str:
        """Format conversation history for context."""
        if not context.history:
            return "No previous interactions."
        
        recent_history = context.history[-max_entries:]
        formatted = []
        
        for entry in recent_history:
            formatted.append(f"[{entry.get('timestamp', 'Unknown')}] {entry.get('role', 'Unknown')}: {entry.get('content', '')}")
        
        return "\n".join(formatted)
    
    async def validate_task(self, task: AgentTask) -> bool:
        """Validate if the agent can handle the task."""
        # Override in subclasses for specific validation
        return True
    
    def update_context(self, context: AgentContext, response: AgentResponse) -> None:
        """Update context after task execution."""
        context.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "role": self.name,
            "task_id": response.task_id,
            "content": response.result,
            "metadata": response.metadata,
        })
    
    def get_tools_description(self) -> str:
        """Get description of available tools."""
        if not self.tools:
            return "No specialized tools available."
        
        descriptions = []
        for tool in self.tools:
            if hasattr(tool, "description"):
                descriptions.append(f"- {tool.name}: {tool.description}")
            else:
                descriptions.append(f"- {tool.__name__}")
        
        return "\n".join(descriptions)
    
    def __repr__(self) -> str:
        return f"<Agent(name={self.name}, model={self.model})>"


class ToolFunction:
    """Wrapper for tool functions that agents can use."""
    
    def __init__(self, func, name: str, description: str, parameters: Dict[str, Any]):
        self.func = func
        self.name = name
        self.description = description
        self.parameters = parameters
    
    async def __call__(self, *args, **kwargs):
        """Execute the tool function."""
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(*args, **kwargs)
        return self.func(*args, **kwargs)
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


def create_tool(name: str, description: str, parameters: Dict[str, Any]):
    """Decorator to create tool functions for agents."""
    def decorator(func):
        return ToolFunction(func, name, description, parameters)
    return decorator


# Example tools for agents
@create_tool(
    name="analyze_metrics",
    description="Analyze performance metrics and identify bottlenecks",
    parameters={
        "type": "object",
        "properties": {
            "metrics": {
                "type": "object",
                "description": "Performance metrics to analyze"
            },
            "baseline": {
                "type": "object",
                "description": "Baseline metrics for comparison",
                "required": False
            }
        },
        "required": ["metrics"]
    }
)
def analyze_metrics(metrics: Dict[str, Any], baseline: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analyze performance metrics."""
    analysis = {
        "bottlenecks": [],
        "improvements": [],
        "recommendations": []
    }
    
    # Simple analysis logic (to be enhanced)
    if "gpu_utilization" in metrics and metrics["gpu_utilization"] < 0.7:
        analysis["bottlenecks"].append("Low GPU utilization")
        analysis["recommendations"].append("Increase batch size or optimize data loading")
    
    if "memory_usage" in metrics and metrics["memory_usage"] > 0.9:
        analysis["bottlenecks"].append("High memory usage")
        analysis["recommendations"].append("Enable gradient checkpointing or reduce model size")
    
    if baseline:
        for key, value in metrics.items():
            if key in baseline:
                improvement = ((value - baseline[key]) / baseline[key]) * 100
                analysis["improvements"].append({
                    "metric": key,
                    "improvement": improvement,
                    "current": value,
                    "baseline": baseline[key]
                })
    
    return analysis


@create_tool(
    name="suggest_optimization",
    description="Suggest optimization strategies based on workload characteristics",
    parameters={
        "type": "object",
        "properties": {
            "workload_type": {
                "type": "string",
                "description": "Type of workload (training, inference, etc.)"
            },
            "framework": {
                "type": "string",
                "description": "ML framework being used"
            },
            "hardware": {
                "type": "object",
                "description": "Hardware configuration"
            },
            "current_performance": {
                "type": "object",
                "description": "Current performance metrics"
            }
        },
        "required": ["workload_type", "framework"]
    }
)
def suggest_optimization(
    workload_type: str,
    framework: str,
    hardware: Optional[Dict[str, Any]] = None,
    current_performance: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Suggest optimization strategies."""
    suggestions = []
    
    # Framework-specific optimizations
    if framework.lower() == "pytorch":
        suggestions.append({
            "type": "compilation",
            "strategy": "torch.compile",
            "description": "Use torch.compile for 10-30% speedup",
            "effort": "low",
            "impact": "medium"
        })
        
        if workload_type == "training":
            suggestions.append({
                "type": "mixed_precision",
                "strategy": "Automatic Mixed Precision",
                "description": "Enable AMP for faster training with minimal accuracy loss",
                "effort": "low",
                "impact": "high"
            })
    
    elif framework.lower() == "tensorflow":
        suggestions.append({
            "type": "compilation",
            "strategy": "XLA",
            "description": "Enable XLA compilation for optimized kernels",
            "effort": "low",
            "impact": "medium"
        })
    
    # Hardware-specific optimizations
    if hardware and hardware.get("gpu_count", 0) > 1:
        suggestions.append({
            "type": "parallelism",
            "strategy": "Data Parallel Training",
            "description": "Utilize multiple GPUs with DDP or similar",
            "effort": "medium",
            "impact": "high"
        })
    
    # Performance-based optimizations
    if current_performance:
        if current_performance.get("gpu_memory_usage", 0) > 0.8:
            suggestions.append({
                "type": "memory",
                "strategy": "Gradient Checkpointing",
                "description": "Trade computation for memory to fit larger models",
                "effort": "low",
                "impact": "medium"
            })
        
        if current_performance.get("data_loading_time", 0) > 0.2:
            suggestions.append({
                "type": "io",
                "strategy": "Optimize Data Pipeline",
                "description": "Use parallel data loading and prefetching",
                "effort": "medium",
                "impact": "medium"
            })
    
    return suggestions