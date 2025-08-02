"""
Command Line Interface for ML Performance Engineering Platform.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from ..utils.logging import get_logger, setup_logging
from ..utils.config import Config
from ..hardware.gpu import get_gpu_info
from ..optimization.distributed import (
    DistributedOptimizer, 
    CommunicationConfig, 
    MemoryConfig,
    MemoryTracker
)
try:
    from .shell_gpt_cli import OpenPerformanceShellGPT, shell_gpt_app
except ImportError:
    OpenPerformanceShellGPT = None
    shell_gpt_app = None

# Initialize console and logger
console = Console()
logger = get_logger(__name__)

# Create Typer app
app = typer.Typer(
    name="mlperf",
    help="ML Performance Engineering Platform CLI",
    rich_markup_mode="rich"
)

@app.command()
def info(
    output_format: str = typer.Option(
        "table", 
        "--format", 
        "-f", 
        help="Output format: table, json"
    )
) -> None:
    """Show system hardware information."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Gathering hardware information...", total=None)
            
            # Get GPU information
            gpus = get_gpu_info()
            
            # Get CPU information
            try:
                import psutil
                cpu_count = psutil.cpu_count()
                memory_gb = psutil.virtual_memory().total / (1024 ** 3)
                cpu_freq = psutil.cpu_freq()
                cpu_percent = psutil.cpu_percent(interval=1)
            except ImportError:
                cpu_count = os.cpu_count()
                memory_gb = 0
                cpu_freq = None
                cpu_percent = 0

        if output_format == "json":
            # JSON output
            info_data = {
                "cpu": {
                    "count": cpu_count,
                    "usage_percent": cpu_percent,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total_gb": round(memory_gb, 2)
                },
                "gpus": [gpu.to_dict() for gpu in gpus]
            }
            console.print_json(json.dumps(info_data, indent=2))
        else:
            # Table output
            console.print("\n[bold blue]System Hardware Information[/bold blue]\n")
            
            # CPU Table
            cpu_table = Table(title="CPU Information")
            cpu_table.add_column("Property", style="cyan")
            cpu_table.add_column("Value", style="magenta")
            
            cpu_table.add_row("CPU Cores", str(cpu_count))
            cpu_table.add_row("CPU Usage", f"{cpu_percent}%")
            if cpu_freq:
                cpu_table.add_row("CPU Frequency", f"{cpu_freq.current:.2f} MHz")
            cpu_table.add_row("Memory", f"{memory_gb:.2f} GB")
            
            console.print(cpu_table)
            console.print()
            
            # GPU Table
            if gpus:
                gpu_table = Table(title="GPU Information")
                gpu_table.add_column("GPU", style="cyan")
                gpu_table.add_column("Name", style="green")
                gpu_table.add_column("Memory", style="magenta")
                gpu_table.add_column("Utilization", style="yellow")
                gpu_table.add_column("Temperature", style="red")
                
                for i, gpu in enumerate(gpus):
                    gpu_table.add_row(
                        f"GPU {i}",
                        gpu.name,
                        f"{gpu.memory_used_mb:.0f} / {gpu.memory_total_mb:.0f} MB",
                        f"{gpu.utilization_percent}%",
                        f"{gpu.temperature_c}°C" if gpu.temperature_c else "N/A"
                    )
                
                console.print(gpu_table)
            else:
                console.print("[yellow]No GPUs detected[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Error gathering system information: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def benchmark(
    framework: str = typer.Option(
        "pytorch", 
        "--framework", 
        "-f", 
        help="ML framework: pytorch, tensorflow, jax"
    ),
    model_size: float = typer.Option(
        1.0, 
        "--model-size", 
        "-s", 
        help="Model size in GB"
    ),
    batch_size: int = typer.Option(
        32, 
        "--batch-size", 
        "-b", 
        help="Batch size"
    ),
    iterations: int = typer.Option(
        100, 
        "--iterations", 
        "-i", 
        help="Number of iterations"
    ),
    distributed: bool = typer.Option(
        False, 
        "--distributed", 
        "-d", 
        help="Enable distributed training simulation"
    ),
    output_file: Optional[str] = typer.Option(
        None, 
        "--output", 
        "-o", 
        help="Output file for results"
    )
) -> None:
    """Run performance benchmarks."""
    try:
        console.print(f"\n[bold blue]Starting {framework} Benchmark[/bold blue]\n")
        
        # Setup configuration
        comm_config = CommunicationConfig(
            backend="nccl" if framework == "pytorch" else "gloo",
            enable_mixed_precision=True
        )
        
        # Initialize optimizer
        optimizer = DistributedOptimizer(
            config=comm_config,
            framework=framework
        )
        
        if distributed:
            console.print("[yellow]Simulating distributed training setup...[/yellow]")
            # Simulate distributed setup
            optimizer.initialize(rank=0, local_rank=0, world_size=1)
        
        # Run memory tracking
        memory_tracker = MemoryTracker(framework=framework)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                description=f"Running {iterations} iterations...", 
                total=iterations
            )
            
            memory_tracker.start_tracking()
            
            # Simulate benchmark (placeholder)
            import time
            for i in range(iterations):
                time.sleep(0.01)  # Simulate work
                progress.update(task, advance=1)
            
            memory_logs = memory_tracker.stop_tracking()
        
        # Generate results
        results = {
            "framework": framework,
            "model_size_gb": model_size,
            "batch_size": batch_size,
            "iterations": iterations,
            "distributed": distributed,
            "memory_samples": len(memory_logs),
            "peak_memory_gb": max(log.used_bytes for log in memory_logs) / (1024**3) if memory_logs else 0,
            "avg_memory_gb": sum(log.used_bytes for log in memory_logs) / len(memory_logs) / (1024**3) if memory_logs else 0
        }
        
        # Display results
        results_table = Table(title="Benchmark Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="magenta")
        
        for key, value in results.items():
            if isinstance(value, float):
                value_str = f"{value:.3f}"
            else:
                value_str = str(value)
            results_table.add_row(key.replace("_", " ").title(), value_str)
        
        console.print(results_table)
        
        # Save results if output file specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"\n[green]Results saved to {output_file}[/green]")
            
    except Exception as e:
        console.print(f"[red]Benchmark failed: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def profile(
    script: str = typer.Argument(..., help="Python script to profile"),
    framework: str = typer.Option(
        "pytorch", 
        "--framework", 
        "-f", 
        help="ML framework: pytorch, tensorflow, jax"
    ),
    output_dir: str = typer.Option(
        "./profiling_results", 
        "--output-dir", 
        "-o", 
        help="Output directory for profiling results"
    ),
    track_memory: bool = typer.Option(
        True, 
        "--track-memory", 
        help="Enable memory tracking"
    )
) -> None:
    """Profile a Python script for performance analysis."""
    try:
        script_path = Path(script)
        if not script_path.exists():
            console.print(f"[red]Script not found: {script}[/red]")
            raise typer.Exit(1)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        console.print(f"\n[bold blue]Profiling {script}[/bold blue]\n")
        
        # Start memory tracking if enabled
        memory_tracker = None
        if track_memory:
            memory_tracker = MemoryTracker(framework=framework)
            memory_tracker.start_tracking()
            console.print("[green]Memory tracking enabled[/green]")
        
        # Run the script (simplified - would use actual profiling)
        import subprocess
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Running script...", total=None)
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True
            )
        
        # Stop memory tracking
        memory_logs = []
        if memory_tracker:
            memory_logs = memory_tracker.stop_tracking()
            console.print(f"[green]Collected {len(memory_logs)} memory samples[/green]")
        
        # Generate profiling report
        report = {
            "script": str(script_path),
            "framework": framework,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "memory_tracking": {
                "enabled": track_memory,
                "samples": len(memory_logs),
                "peak_memory_gb": max(log.used_bytes for log in memory_logs) / (1024**3) if memory_logs else 0,
                "avg_memory_gb": sum(log.used_bytes for log in memory_logs) / len(memory_logs) / (1024**3) if memory_logs else 0
            }
        }
        
        # Save report
        report_file = output_path / "profiling_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        if result.returncode == 0:
            console.print(f"[green]Profiling completed successfully[/green]")
        else:
            console.print(f"[red]Script exited with code {result.returncode}[/red]")
        
        console.print(f"[blue]Report saved to {report_file}[/blue]")
        
        if memory_logs:
            console.print(f"[yellow]Peak memory usage: {report['memory_tracking']['peak_memory_gb']:.3f} GB[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Profiling failed: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def optimize(
    config_file: str = typer.Argument(..., help="Configuration file (JSON/YAML)"),
    dry_run: bool = typer.Option(
        False, 
        "--dry-run", 
        help="Show optimization recommendations without applying"
    )
) -> None:
    """Optimize ML workload based on configuration."""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            console.print(f"[red]Configuration file not found: {config_file}[/red]")
            raise typer.Exit(1)
        
        # Load configuration
        with open(config_path) as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                import yaml
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        console.print(f"\n[bold blue]Analyzing Configuration[/bold blue]\n")
        
        # Extract parameters
        framework = config_data.get('framework', 'pytorch')
        model_size_gb = config_data.get('model_size_gb', 1.0)
        num_gpus = config_data.get('num_gpus', 1)
        world_size = config_data.get('world_size', 1)
        
        # Setup optimizer
        comm_config = CommunicationConfig()
        optimizer = DistributedOptimizer(config=comm_config, framework=framework)
        
        # Get optimization recommendations
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Generating optimization recommendations...", total=None)
            
            # Model parallelism optimization
            if num_gpus > 1:
                tp_size, pp_size = optimizer.optimize_model_parallel(
                    model_size_gb=model_size_gb,
                    num_gpus=num_gpus,
                    device_memory_gb=24.0  # Assume 24GB GPU memory
                )
            else:
                tp_size, pp_size = 1, 1
            
            # Communication optimization
            comm_settings = optimizer.optimize_communication(
                model_size_gb=model_size_gb,
                num_parameters=int(model_size_gb * 1e9 / 4),  # Rough estimate
                world_size=world_size
            )
        
        # Display recommendations
        recommendations_table = Table(title="Optimization Recommendations")
        recommendations_table.add_column("Category", style="cyan")
        recommendations_table.add_column("Recommendation", style="green")
        recommendations_table.add_column("Value", style="magenta")
        
        recommendations_table.add_row("Model Parallelism", "Tensor Parallel Size", str(tp_size))
        recommendations_table.add_row("Model Parallelism", "Pipeline Parallel Size", str(pp_size))
        
        for key, value in comm_settings.items():
            recommendations_table.add_row("Communication", key.replace("_", " ").title(), str(value))
        
        console.print(recommendations_table)
        
        if dry_run:
            console.print("\n[yellow]Dry run mode - recommendations not applied[/yellow]")
        else:
            console.print("\n[green]Use these recommendations in your training script[/green]")
            
    except Exception as e:
        console.print(f"[red]Optimization failed: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def version() -> None:
    """Show version information."""
    from .. import __version__, __description__
    console.print(f"ML Performance Engineering Platform v{__version__}")
    console.print(__description__)

@app.command()
def gpt(
    query: Optional[str] = typer.Argument(None, help="Query for AI assistant"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute suggested commands"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Start interactive mode"),
) -> None:
    """AI-powered shell assistance with GPT integration."""
    try:
        # Initialize Shell-GPT
        shell_gpt = OpenPerformanceShellGPT()
        
        if interactive or query is None:
            # Interactive mode
            shell_gpt.interactive_mode()
        else:
            # Single query mode
            response = shell_gpt.process_command(query, execute=execute)
            console.print(response)
            
    except Exception as e:
        console.print(f"[red]Shell-GPT error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def chat(
    question: Optional[str] = typer.Argument(None, help="Question to ask AI agents"),
    agent: str = typer.Option("auto", "--agent", "-a", help="Specific agent (auto/benchmark/optimization/performance)"),
) -> None:
    """Chat with specialized ML performance AI agents."""
    try:
        # Initialize Shell-GPT for agent access
        shell_gpt = OpenPerformanceShellGPT()
        
        if question:
            # Process single question
            if agent != "auto":
                question = f"[{agent}] {question}"
            
            response = shell_gpt._handle_performance_query(question)
            console.print(response)
        else:
            # Interactive chat mode
            console.print("[bold cyan]OpenPerformance AI Chat[/bold cyan]")
            console.print("Chat with ML performance engineering experts")
            console.print("Type 'exit' to quit\n")
            
            from rich.prompt import Prompt
            
            while True:
                user_input = Prompt.ask("[bold green]You[/bold green]")
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                
                response = shell_gpt._handle_performance_query(user_input)
                console.print(f"\n[bold blue]AI Assistant[/bold blue]")
                console.print(response)
                console.print()
                
    except Exception as e:
        console.print(f"[red]AI chat error: {e}[/red]")
        raise typer.Exit(1)

@app.callback()
def main(
    verbose: bool = typer.Option(
        False, 
        "--verbose", 
        "-v", 
        help="Enable verbose logging"
    ),
    log_file: Optional[str] = typer.Option(
        None, 
        "--log-file", 
        help="Log file path"
    )
) -> None:
    """ML Performance Engineering Platform CLI."""
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, log_file=log_file)

if __name__ == "__main__":
    app() 