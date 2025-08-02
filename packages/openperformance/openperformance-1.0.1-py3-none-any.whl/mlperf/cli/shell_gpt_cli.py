"""Shell-GPT integration for OpenPerformance CLI."""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
# from sgpt import ChatGPT, RoleManager  # Temporarily disabled due to interactive input issue

from mlperf.agents import AgentContext, AgentTask, SwarmManager
from mlperf.agents.benchmark import BenchmarkAgent
from mlperf.agents.optimization import OptimizationAgent
from mlperf.agents.performance import PerformanceAnalysisAgent
from mlperf.utils.config import get_settings
from mlperf.utils.logging import get_logger

logger = get_logger(__name__)
console = Console()
settings = get_settings()


class OpenPerformanceShellGPT:
    """Enhanced Shell-GPT integration for OpenPerformance."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Shell-GPT with OpenPerformance context."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required for Shell-GPT")
        
        # Initialize ChatGPT instance (simplified for now)
        self.chat = None  # Will use OpenAI directly
        self.role_manager = None
        
        # Store custom role
        self.system_role = self._get_openperformance_role()
        
        # Initialize swarm manager
        self.swarm_manager = None
        self._init_swarm_manager()
    
    def _get_openperformance_role(self):
        """Get the custom role for OpenPerformance assistance."""
        return """You are an ML performance engineering expert assistant integrated with the OpenPerformance platform. 

Your capabilities include:
1. Analyzing ML workload performance and providing optimization recommendations
2. Running benchmarks and interpreting results
3. Generating performance reports and insights
4. Helping with distributed training configuration
5. Assisting with GPU optimization and memory management
6. Writing and explaining performance optimization code
7. Executing shell commands for system monitoring and debugging

When asked about performance issues:
- First understand the workload characteristics (model size, batch size, hardware)
- Identify bottlenecks using profiling data if available
- Provide specific, actionable recommendations
- Consider trade-offs between different optimization strategies
- Suggest benchmarks to validate improvements

Always provide code examples and command-line instructions when relevant."""
    
    def _ask_gpt(self, prompt: str) -> str:
        """Simple GPT query using OpenAI directly."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error querying GPT: {e}"
    
    def _init_swarm_manager(self):
        """Initialize the swarm manager with agents."""
        try:
            self.swarm_manager = SwarmManager(api_key=self.api_key)
            
            # Register specialized agents
            self.swarm_manager.register_agent(BenchmarkAgent())
            self.swarm_manager.register_agent(OptimizationAgent())
            self.swarm_manager.register_agent(PerformanceAnalysisAgent())
            
            logger.info("Swarm manager initialized with performance agents")
        except Exception as e:
            logger.error(f"Failed to initialize swarm manager: {e}")
            self.swarm_manager = None
    
    def process_command(self, command: str, execute: bool = False) -> str:
        """Process a command with Shell-GPT assistance."""
        # Check if it's a performance-related query
        if self._is_performance_query(command):
            return self._handle_performance_query(command)
        
        # Regular shell command assistance
        if execute:
            # Get command suggestion from GPT (simplified)
            suggestion = self._ask_gpt(f"Provide a shell command for: {command}")
            
            # Show the command and ask for confirmation
            console.print(f"\n[bold cyan]Suggested command:[/bold cyan]")
            console.print(Syntax(suggestion, "bash"))
            
            if Confirm.ask("Execute this command?"):
                return self._execute_command(suggestion)
            else:
                return "Command execution cancelled."
        else:
            # Just provide assistance without execution
            return self._ask_gpt(command)
    
    def _is_performance_query(self, query: str) -> bool:
        """Check if the query is related to performance engineering."""
        performance_keywords = [
            "benchmark", "optimize", "performance", "gpu", "memory",
            "throughput", "latency", "profil", "bottleneck", "scale",
            "distributed", "parallel", "tensor", "batch", "train"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in performance_keywords)
    
    def _handle_performance_query(self, query: str) -> str:
        """Handle performance-related queries using specialized agents."""
        if not self.swarm_manager:
            return self._ask_gpt(query)  # Fallback to regular GPT
        
        # Create task for agents
        task = AgentTask(
            task_id=f"query_{hash(query)}",
            task_type="general",
            description=query,
            parameters={"question": query},
        )
        
        context = AgentContext()
        
        # Run async task synchronously
        response_id = asyncio.run(
            self.swarm_manager.assign_task(task, context=context)
        )
        response = self.swarm_manager.completed_tasks[response_id]
        
        if response.status == "success":
            # Format agent response
            result = f"[Analysis by {response.metadata.get('agent', 'AI Assistant')}]\n\n"
            
            if isinstance(response.result, dict):
                result += self._format_dict_response(response.result)
            else:
                result += str(response.result)
            
            if response.suggestions:
                result += "\n\nSuggestions:\n"
                for i, suggestion in enumerate(response.suggestions, 1):
                    result += f"{i}. {suggestion}\n"
            
            return result
        else:
            # Fallback to regular GPT on agent failure
            return self._ask_gpt(query)
    
    def _execute_command(self, command: str) -> str:
        """Execute a shell command and return the output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = ""
            if result.stdout:
                output += f"[green]Output:[/green]\n{result.stdout}\n"
            if result.stderr:
                output += f"[red]Error:[/red]\n{result.stderr}\n"
            if result.returncode != 0:
                output += f"[red]Command exited with code {result.returncode}[/red]\n"
            
            return output
        except subprocess.TimeoutExpired:
            return "[red]Command timed out after 30 seconds[/red]"
        except Exception as e:
            return f"[red]Error executing command: {e}[/red]"
    
    def _format_dict_response(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary response for display."""
        result = ""
        for key, value in data.items():
            if isinstance(value, dict):
                result += " " * indent + f"{key}:\n"
                result += self._format_dict_response(value, indent + 2)
            elif isinstance(value, list):
                result += " " * indent + f"{key}:\n"
                for item in value:
                    if isinstance(item, dict):
                        result += self._format_dict_response(item, indent + 2)
                    else:
                        result += " " * (indent + 2) + f"- {item}\n"
            else:
                result += " " * indent + f"{key}: {value}\n"
        return result
    
    def interactive_mode(self):
        """Run interactive Shell-GPT mode with OpenPerformance integration."""
        console.print(Panel.fit(
            "[bold cyan]OpenPerformance Shell-GPT Assistant[/bold cyan]\n"
            "AI-powered shell and performance engineering assistant\n\n"
            "Commands:\n"
            "  [bold]!<command>[/bold]     Execute shell command\n"
            "  [bold]?<command>[/bold]     Get command suggestion (no execution)\n"
            "  [bold]perf <query>[/bold]  Performance engineering assistance\n"
            "  [bold]help[/bold]          Show this help\n"
            "  [bold]exit[/bold]          Exit interactive mode",
            title="Interactive Shell-GPT",
        ))
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]openperf>[/bold green]")
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                
                if user_input.lower() == "help":
                    self._show_help()
                    continue
                
                # Handle different command types
                if user_input.startswith("!"):
                    # Execute command
                    command = user_input[1:].strip()
                    response = self.process_command(command, execute=True)
                elif user_input.startswith("?"):
                    # Get suggestion without execution
                    command = user_input[1:].strip()
                    response = self.process_command(command, execute=False)
                elif user_input.lower().startswith("perf "):
                    # Performance-specific query
                    query = user_input[5:].strip()
                    response = self._handle_performance_query(query)
                else:
                    # General query
                    response = self.process_command(user_input, execute=False)
                
                # Display response
                console.print(response)
                
            except KeyboardInterrupt:
                if Confirm.ask("\nDo you want to exit?"):
                    break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold]OpenPerformance Shell-GPT Commands:[/bold]

[bold cyan]Shell Commands:[/bold cyan]
  !<command>     Execute shell command with AI assistance
  ?<command>     Get command suggestion without execution
  
[bold cyan]Performance Commands:[/bold cyan]
  perf benchmark <workload>    Get benchmarking recommendations
  perf optimize <metric>       Get optimization suggestions
  perf analyze <data>         Analyze performance data
  
[bold cyan]Examples:[/bold cyan]
  !find large model files
  ?how to monitor GPU memory usage
  perf optimize throughput for transformer training
  perf analyze high memory usage in distributed training
  
[bold cyan]Tips:[/bold cyan]
  - Use specific details for better recommendations
  - Include hardware specs when asking about optimization
  - Mention framework (PyTorch, TensorFlow) for targeted advice
"""
        console.print(help_text)
    
    def generate_script(self, description: str, language: str = "python") -> str:
        """Generate a script based on description."""
        prompt = f"""Generate a {language} script for the following task:
{description}

Requirements:
- Include proper error handling
- Add helpful comments
- Follow best practices for ML performance
- Make it production-ready

Provide only the code without explanations."""
        
        code = self._ask_gpt(prompt)
        return code
    
    def explain_metrics(self, metrics: Dict[str, Any]) -> str:
        """Explain performance metrics in detail."""
        prompt = f"""Explain the following ML performance metrics in detail:
{json.dumps(metrics, indent=2)}

For each metric:
1. What it measures
2. What values are considered good/bad
3. How to improve it
4. Common issues that affect it"""
        
        return self._ask_gpt(prompt)
    
    def suggest_profiling_commands(self, framework: str, issue: str) -> List[str]:
        """Suggest profiling commands for specific issues."""
        prompt = f"""Suggest shell commands to profile and debug the following issue:
Framework: {framework}
Issue: {issue}

Provide a list of commands with brief explanations."""
        
        response = self._ask_gpt(prompt)
        
        # Parse commands from response (simplified)
        commands = []
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith(('$', '>', '#')) or '`' in line:
                # Extract command
                cmd = line.strip().strip('$>#` ')
                if cmd:
                    commands.append(cmd)
        
        return commands


def create_shell_gpt_app() -> typer.Typer:
    """Create Shell-GPT enhanced CLI app."""
    app = typer.Typer(
        name="openperf-gpt",
        help="OpenPerformance CLI with Shell-GPT integration",
        add_completion=True,
    )
    
    # Global Shell-GPT instance
    shell_gpt = None
    
    @app.callback()
    def callback():
        """Initialize Shell-GPT on app startup."""
        global shell_gpt
        try:
            shell_gpt = OpenPerformanceShellGPT()
        except Exception as e:
            console.print(f"[yellow]Warning: Shell-GPT initialization failed: {e}[/yellow]")
            console.print("[yellow]Some features may be unavailable[/yellow]")
    
    @app.command()
    def chat(
        query: Optional[str] = typer.Argument(None, help="Query for AI assistant"),
        execute: bool = typer.Option(False, "--execute", "-e", help="Execute suggested commands"),
        agent: str = typer.Option("auto", "--agent", "-a", help="Specific agent to use"),
    ):
        """Interactive chat with AI assistant."""
        if not shell_gpt:
            console.print("[red]Shell-GPT not initialized[/red]")
            raise typer.Exit(1)
        
        if query:
            # Single query mode
            response = shell_gpt.process_command(query, execute=execute)
            console.print(response)
        else:
            # Interactive mode
            shell_gpt.interactive_mode()
    
    @app.command()
    def generate(
        description: str = typer.Argument(..., help="Description of what to generate"),
        language: str = typer.Option("python", "--language", "-l", help="Programming language"),
        output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    ):
        """Generate code based on description."""
        if not shell_gpt:
            console.print("[red]Shell-GPT not initialized[/red]")
            raise typer.Exit(1)
        
        console.print(f"[bold]Generating {language} code...[/bold]")
        code = shell_gpt.generate_script(description, language)
        
        # Display code with syntax highlighting
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        console.print(syntax)
        
        # Save if output specified
        if output:
            output.write_text(code)
            console.print(f"\n[green]Code saved to {output}[/green]")
    
    @app.command()
    def explain(
        metrics_file: Path = typer.Argument(..., help="Path to metrics JSON file"),
    ):
        """Explain performance metrics in detail."""
        if not shell_gpt:
            console.print("[red]Shell-GPT not initialized[/red]")
            raise typer.Exit(1)
        
        try:
            metrics = json.loads(metrics_file.read_text())
            explanation = shell_gpt.explain_metrics(metrics)
            console.print(explanation)
        except Exception as e:
            console.print(f"[red]Error loading metrics: {e}[/red]")
            raise typer.Exit(1)
    
    @app.command()
    def profile(
        framework: str = typer.Argument(..., help="ML framework (pytorch/tensorflow)"),
        issue: str = typer.Argument(..., help="Performance issue description"),
        execute: bool = typer.Option(False, "--execute", "-e", help="Execute suggested commands"),
    ):
        """Get profiling command suggestions."""
        if not shell_gpt:
            console.print("[red]Shell-GPT not initialized[/red]")
            raise typer.Exit(1)
        
        commands = shell_gpt.suggest_profiling_commands(framework, issue)
        
        console.print(f"[bold]Suggested profiling commands for {framework}:[/bold]\n")
        
        for i, cmd in enumerate(commands, 1):
            console.print(f"{i}. {cmd}")
            
            if execute and Confirm.ask(f"Execute command {i}?"):
                output = shell_gpt._execute_command(cmd)
                console.print(output)
    
    @app.command()
    def optimize(
        workload_desc: str = typer.Argument(..., help="Workload description"),
        target_metric: str = typer.Option("throughput", "--target", "-t", help="Target metric to optimize"),
        constraints: Optional[str] = typer.Option(None, "--constraints", "-c", help="Constraints as JSON"),
    ):
        """Get optimization recommendations."""
        if not shell_gpt:
            console.print("[red]Shell-GPT not initialized[/red]")
            raise typer.Exit(1)
        
        # Build query
        query = f"Optimize {target_metric} for {workload_desc}"
        if constraints:
            query += f" with constraints: {constraints}"
        
        response = shell_gpt._handle_performance_query(query)
        console.print(response)
    
    return app


# Create the app instance
shell_gpt_app = create_shell_gpt_app()

if __name__ == "__main__":
    shell_gpt_app()