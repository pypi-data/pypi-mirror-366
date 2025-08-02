"""Swarm manager for coordinating multiple AI agents using OpenAI Swarm."""

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from swarm import Agent as SwarmAgent
from swarm import Swarm

from mlperf.agents.base import Agent, AgentContext, AgentResponse, AgentTask
from mlperf.utils.config import get_settings
from mlperf.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SwarmManager:
    """Manager for coordinating multiple AI agents using OpenAI Swarm."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Swarm manager."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required for Swarm manager")
        
        # Initialize Swarm client
        self.client = Swarm()
        
        # Agent registry
        self.agents: Dict[str, Agent] = {}
        self.swarm_agents: Dict[str, SwarmAgent] = {}
        
        # Task management
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: Dict[str, AgentResponse] = {}
        
        # Performance tracking
        self.agent_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "total_tokens_used": 0,
            "average_confidence": 0.0,
        })
        
        # Collaboration tracking
        self.agent_interactions: Dict[Tuple[str, str], int] = defaultdict(int)
        
        logger.info("SwarmManager initialized")
    
    def register_agent(self, agent: Agent) -> None:
        """Register an agent with the swarm."""
        if agent.name in self.agents:
            logger.warning(f"Agent {agent.name} already registered, overwriting")
        
        self.agents[agent.name] = agent
        
        # Create corresponding Swarm agent
        swarm_agent = SwarmAgent(
            name=agent.name,
            model=agent.model,
            instructions=agent.instructions,
            functions=[tool.to_openai_function() for tool in agent.tools] if agent.tools else [],
        )
        
        self.swarm_agents[agent.name] = swarm_agent
        
        logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        return self.agents.get(name)
    
    async def assign_task(
        self,
        task: AgentTask,
        agent_name: Optional[str] = None,
        context: Optional[AgentContext] = None
    ) -> str:
        """Assign a task to an agent or let the swarm decide."""
        # Store task
        self.active_tasks[task.task_id] = task
        
        if agent_name:
            # Direct assignment
            agent = self.get_agent(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            logger.info(f"Assigning task {task.task_id} to agent {agent_name}")
            response = await self._execute_task(agent, task, context or AgentContext())
        else:
            # Let swarm decide best agent
            best_agent = await self._select_best_agent(task, context)
            logger.info(f"Swarm selected agent {best_agent.name} for task {task.task_id}")
            response = await self._execute_task(best_agent, task, context or AgentContext())
        
        # Store result
        self.completed_tasks[task.task_id] = response
        del self.active_tasks[task.task_id]
        
        return response.task_id
    
    async def _select_best_agent(
        self,
        task: AgentTask,
        context: Optional[AgentContext]
    ) -> Agent:
        """Select the best agent for a task using Swarm intelligence."""
        # Simple selection based on task type and agent specialization
        # In a real implementation, this would use more sophisticated matching
        
        candidates = []
        
        for agent in self.agents.values():
            if await agent.validate_task(task):
                # Calculate suitability score
                score = self._calculate_agent_suitability(agent, task, context)
                candidates.append((agent, score))
        
        if not candidates:
            # Fallback to first available agent
            return list(self.agents.values())[0]
        
        # Sort by score and return best
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def _calculate_agent_suitability(
        self,
        agent: Agent,
        task: AgentTask,
        context: Optional[AgentContext]
    ) -> float:
        """Calculate how suitable an agent is for a task."""
        score = 0.0
        
        # Check task type match
        if task.task_type.lower() in agent.name.lower():
            score += 0.5
        
        # Check agent performance history
        metrics = self.agent_metrics[agent.name]
        if metrics["tasks_completed"] > 0:
            success_rate = metrics["tasks_completed"] / (
                metrics["tasks_completed"] + metrics["tasks_failed"]
            )
            score += success_rate * 0.3
            
            # Average confidence
            score += metrics["average_confidence"] * 0.2
        
        return score
    
    async def _execute_task(
        self,
        agent: Agent,
        task: AgentTask,
        context: AgentContext
    ) -> AgentResponse:
        """Execute a task with an agent."""
        start_time = datetime.utcnow()
        
        try:
            # Execute task
            response = await agent.process(task, context)
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_agent_metrics(
                agent.name,
                success=response.status == "success",
                execution_time=execution_time,
                tokens_used=response.tokens_used,
                confidence=response.confidence
            )
            
            # Update context
            agent.update_context(context, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id} with agent {agent.name}: {e}")
            
            # Create error response
            response = AgentResponse(
                task_id=task.task_id,
                status="failed",
                result={"error": str(e)},
                reasoning=f"Task execution failed: {e}",
                confidence=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            # Update metrics
            self._update_agent_metrics(agent.name, success=False)
            
            return response
    
    def _update_agent_metrics(
        self,
        agent_name: str,
        success: bool,
        execution_time: float = 0.0,
        tokens_used: int = 0,
        confidence: float = 0.0
    ) -> None:
        """Update agent performance metrics."""
        metrics = self.agent_metrics[agent_name]
        
        if success:
            metrics["tasks_completed"] += 1
        else:
            metrics["tasks_failed"] += 1
        
        metrics["total_execution_time"] += execution_time
        metrics["total_tokens_used"] += tokens_used
        
        # Update average confidence
        total_tasks = metrics["tasks_completed"] + metrics["tasks_failed"]
        if total_tasks > 0:
            metrics["average_confidence"] = (
                (metrics["average_confidence"] * (total_tasks - 1) + confidence) / total_tasks
            )
    
    async def collaborate(
        self,
        task: AgentTask,
        agent_names: List[str],
        context: Optional[AgentContext] = None,
        strategy: str = "sequential"
    ) -> Dict[str, AgentResponse]:
        """Have multiple agents collaborate on a task."""
        if not context:
            context = AgentContext()
        
        results = {}
        
        if strategy == "sequential":
            # Agents work in sequence, each building on previous results
            for agent_name in agent_names:
                agent = self.get_agent(agent_name)
                if not agent:
                    logger.warning(f"Agent {agent_name} not found, skipping")
                    continue
                
                # Add previous results to context
                if results:
                    context.shared_memory["previous_results"] = results
                
                response = await self._execute_task(agent, task, context)
                results[agent_name] = response
                
                # Track collaboration
                if len(results) > 1:
                    prev_agent = agent_names[agent_names.index(agent_name) - 1]
                    self.agent_interactions[(prev_agent, agent_name)] += 1
        
        elif strategy == "parallel":
            # Agents work in parallel
            tasks = []
            for agent_name in agent_names:
                agent = self.get_agent(agent_name)
                if agent:
                    tasks.append(self._execute_task(agent, task, context))
            
            responses = await asyncio.gather(*tasks)
            
            for agent_name, response in zip(agent_names, responses):
                results[agent_name] = response
        
        elif strategy == "consensus":
            # Agents work in parallel and then reach consensus
            # First, get all individual responses
            tasks = []
            for agent_name in agent_names:
                agent = self.get_agent(agent_name)
                if agent:
                    tasks.append(self._execute_task(agent, task, context))
            
            responses = await asyncio.gather(*tasks)
            
            for agent_name, response in zip(agent_names, responses):
                results[agent_name] = response
            
            # Then have a consensus phase (simplified)
            # In reality, this would involve more sophisticated consensus mechanisms
            consensus_task = AgentTask(
                task_id=f"{task.task_id}_consensus",
                task_type="consensus",
                description="Reach consensus on the best approach",
                parameters={
                    "original_task": task.dict(),
                    "agent_responses": {
                        name: resp.dict() for name, resp in results.items()
                    }
                }
            )
            
            # Use first agent as consensus leader
            if agent_names and agent_names[0] in self.agents:
                consensus_response = await self._execute_task(
                    self.agents[agent_names[0]],
                    consensus_task,
                    context
                )
                results["consensus"] = consensus_response
        
        return results
    
    def get_agent_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all agents."""
        report = {
            "agents": {},
            "collaborations": {},
            "summary": {
                "total_tasks": sum(
                    m["tasks_completed"] + m["tasks_failed"]
                    for m in self.agent_metrics.values()
                ),
                "total_tokens": sum(
                    m["total_tokens_used"] for m in self.agent_metrics.values()
                ),
                "total_execution_time": sum(
                    m["total_execution_time"] for m in self.agent_metrics.values()
                ),
            }
        }
        
        # Agent metrics
        for agent_name, metrics in self.agent_metrics.items():
            total_tasks = metrics["tasks_completed"] + metrics["tasks_failed"]
            report["agents"][agent_name] = {
                "tasks_completed": metrics["tasks_completed"],
                "tasks_failed": metrics["tasks_failed"],
                "success_rate": (
                    metrics["tasks_completed"] / total_tasks if total_tasks > 0 else 0
                ),
                "average_execution_time": (
                    metrics["total_execution_time"] / total_tasks if total_tasks > 0 else 0
                ),
                "average_confidence": metrics["average_confidence"],
                "total_tokens_used": metrics["total_tokens_used"],
            }
        
        # Collaboration metrics
        for (agent1, agent2), count in self.agent_interactions.items():
            key = f"{agent1} -> {agent2}"
            report["collaborations"][key] = count
        
        return report
    
    async def optimize_swarm(self) -> Dict[str, Any]:
        """Optimize swarm configuration based on performance data."""
        recommendations = {
            "agent_recommendations": [],
            "collaboration_recommendations": [],
            "resource_recommendations": []
        }
        
        # Analyze agent performance
        for agent_name, metrics in self.agent_metrics.items():
            total_tasks = metrics["tasks_completed"] + metrics["tasks_failed"]
            if total_tasks > 10:  # Only analyze agents with sufficient data
                success_rate = metrics["tasks_completed"] / total_tasks
                
                if success_rate < 0.7:
                    recommendations["agent_recommendations"].append({
                        "agent": agent_name,
                        "issue": "Low success rate",
                        "recommendation": "Review agent prompts or consider retraining"
                    })
                
                if metrics["average_confidence"] < 0.6:
                    recommendations["agent_recommendations"].append({
                        "agent": agent_name,
                        "issue": "Low confidence",
                        "recommendation": "Enhance agent tools or provide more context"
                    })
        
        # Analyze collaboration patterns
        collaboration_pairs = sorted(
            self.agent_interactions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for (agent1, agent2), count in collaboration_pairs:
            recommendations["collaboration_recommendations"].append({
                "agents": [agent1, agent2],
                "frequency": count,
                "recommendation": "Consider creating specialized workflow for this pair"
            })
        
        return recommendations
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        self.agent_metrics.clear()
        self.agent_interactions.clear()
        self.completed_tasks.clear()
        logger.info("Swarm metrics reset")