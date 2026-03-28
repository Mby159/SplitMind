"""
SplitMind CLI - Command line interface for SplitMind.
"""

import asyncio
import json
import sys
from typing import Optional
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()


def get_engine(local_model_config=None):
    from splitmind.core.engine import SplitMindEngine
    from splitmind.core.local_model import LocalModelConfig, LocalModelBackend
    from splitmind.config import config_manager
    
    # Create local model config if not provided
    if local_model_config is None:
        default_model = config_manager.get_default_model()
        local_model_config = LocalModelConfig(
            model_name=default_model,  # Default small model from config
            backend=LocalModelBackend.OLLAMA,
            base_url="http://localhost:11434/api",
            timeout=30,
            max_retries=3,
            temperature=0.7,
            max_tokens=512
        )
    
    engine = SplitMindEngine(local_model_config=local_model_config)
    # Set default execution mode from config
    engine.config.execution_mode = config_manager.get_execution_mode()
    # Set privacy protection from config
    engine.config.enable_privacy_protection = config_manager.get_privacy_protection()
    
    return engine


@click.group()
@click.version_option(version="0.1.0", prog_name="splitmind")
def cli():
    """
    SplitMind - Privacy-preserving multi-agent task orchestration.
    
    Split tasks for privacy protection, distribute to multiple AI providers,
    and aggregate results.
    """
    pass


@cli.command()
@click.argument("task", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Read task from file")
@click.option("--context", "-c", help="Additional context for the task")
@click.option("--strategy", "-s", 
              type=click.Choice(["auto", "single", "section", "semantic", "parallel"]),
              default="auto", help="Task splitting strategy")
@click.option("--mode", "-M", 
              type=click.Choice(["local_only", "hybrid", "online"]),
              default="hybrid", help="Execution mode (local_only, hybrid, online)")
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.option("--format", "output_format",
              type=click.Choice(["text", "json", "markdown"]),
              default="text", help="Output format")
@click.option("--no-privacy", is_flag=True, help="Disable privacy protection")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed execution info")
@click.option("--model", "-m", help="Local model to use (e.g., llama3.2:3b)")
def run(
    task: Optional[str],
    file: Optional[str],
    context: Optional[str],
    strategy: str,
    mode: str,
    output: Optional[str],
    output_format: str,
    no_privacy: bool,
    verbose: bool,
    model: Optional[str],
):
    """Execute a task with privacy-preserving multi-agent orchestration."""
    
    if file:
        task = Path(file).read_text(encoding="utf-8")
    
    if not task:
        console.print("[red]Error: No task provided. Use --task or --file[/red]")
        sys.exit(1)
    
    # Create local model config if model is specified
    local_model_config = None
    if model:
        from splitmind.core.local_model import LocalModelConfig, LocalModelBackend
        local_model_config = LocalModelConfig(
            model_name=model,
            backend=LocalModelBackend.OLLAMA,
            base_url="http://localhost:11434/api",
            timeout=30,
            max_retries=3,
            temperature=0.7,
            max_tokens=512
        )
    
    engine = get_engine(local_model_config)
    if no_privacy:
        engine.config.enable_privacy_protection = False
    
    # Set execution mode
    from splitmind.core.engine import ExecutionMode
    engine.config.execution_mode = ExecutionMode(mode)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task("Executing task...", total=None)
        
        result = engine.execute_sync(
            task=task,
            context=context,
            split_strategy=strategy,
        )
        
        progress.remove_task(task_id)
    
    if output_format == "json":
        output_content = json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
        console.print(Syntax(output_content, "json", theme="monokai"))
    elif output_format == "markdown":
        output_content = f"# Task Result\n\n{result.final_result}"
        if verbose and result.aggregated_result:
            output_content += f"\n\n## Execution Details\n"
            output_content += f"- Strategy: {result.aggregated_result.aggregation_strategy.value}\n"
            output_content += f"- Providers: {', '.join(result.aggregated_result.providers_used)}\n"
            output_content += f"- Time: {result.execution_time:.2f}s\n"
        console.print(Markdown(output_content))
    else:
        console.print(Panel(result.final_result, title="Result", border_style="green"))
        
        if verbose:
            console.print()
            
            if result.privacy_report:
                table = Table(title="Privacy Report")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                table.add_row("Risk Level", result.privacy_report["risk_level"])
                table.add_row("Items Detected", str(result.privacy_report["total_detected"]))
                console.print(table)
            
            if result.split_result:
                table = Table(title="Task Split")
                table.add_column("ID", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("Description")
                for st in result.split_result.subtasks:
                    table.add_row(st.id, st.task_type.value, st.description[:50] + "...")
                console.print(table)
            
            if result.aggregated_result:
                console.print(f"\n[dim]Execution time: {result.execution_time:.2f}s[/dim]")
                console.print(f"[dim]Confidence: {result.aggregated_result.confidence_score:.0%}[/dim]")
    
    if output:
        Path(output).write_text(result.final_result, encoding="utf-8")
        console.print(f"\n[green]Output saved to {output}[/green]")


@cli.command()
@click.argument("task")
@click.option("--strategy", "-s",
              type=click.Choice(["auto", "single", "section", "semantic", "parallel"]),
              default="auto", help="Task splitting strategy")
def preview(task: str, strategy: str):
    """Preview how a task will be split without executing."""
    
    engine = get_engine()
    preview_result = engine.preview_split(task, strategy=strategy)
    
    console.print(Panel(f"Task Type: {preview_result['task_type']}", 
                       title="Task Analysis", border_style="blue"))
    
    table = Table(title="Subtasks Preview")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Description")
    table.add_column("Sensitive Info", style="red")
    
    for st in preview_result["subtasks"]:
        table.add_row(
            st["id"],
            st["task_type"],
            st["description"][:40] + "..." if len(st["description"]) > 40 else st["description"],
            str(st["sensitive_info_count"]),
        )
    
    console.print(table)
    console.print(f"\nTotal subtasks: {preview_result['total_subtasks']}")
    console.print(f"Split strategy: {preview_result['split_strategy']}")


@cli.command()
@click.argument("text")
def analyze(text: str):
    """Analyze text for sensitive information."""
    
    from splitmind.core.privacy import PrivacyHandler
    
    handler = PrivacyHandler()
    report = handler.generate_report(text)
    
    risk_color = "red" if report.overall_risk_level.value in ["high", "critical"] else "yellow"
    console.print(Panel(
        f"Risk Level: [{risk_color}]{report.overall_risk_level.value}[/{risk_color}]",
        title="Privacy Analysis",
        border_style="blue",
    ))
    
    if report.items_by_type:
        table = Table(title="Detected Sensitive Information")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="yellow")
        
        for info_type, count in report.items_by_type.items():
            table.add_row(info_type, str(count))
        
        console.print(table)
    else:
        console.print("[green]No sensitive information detected.[/green]")
    
    console.print(f"\nTotal items: {report.total_items_detected}")


@cli.command()
def providers():
    """List available online AI providers."""
    
    from splitmind.providers.registry import ProviderRegistry
    
    registry = ProviderRegistry()
    available_providers = registry.list_providers()
    
    if available_providers:
        console.print(Panel("Available Online AI Providers", border_style="blue"))
        table = Table()
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        
        for provider in available_providers:
            table.add_row(provider, "Available")
        
        console.print(table)
    else:
        console.print("[yellow]No online providers configured. Add API keys to use online services.[/yellow]")
    
    console.print("\n[dim]Note: SplitMind can still work with local models without online providers.[/dim]")


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def serve(host: str, port: int):
    """Start the web server."""
    
    try:
        import uvicorn
        from splitmind.web.app import app
        
        console.print(f"[green]Starting web server at http://{host}:{port}[/green]")
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        console.print("[red]Web dependencies not installed. Run: pip install splitmind[web][/red]")


@cli.command()
@click.argument("text")
@click.option("--output", "-o", type=click.Path(), help="Save redacted text to file")
def redact(text: str, output: Optional[str]):
    """Redact sensitive information from text."""
    
    from splitmind.core.privacy import PrivacyHandler
    
    handler = PrivacyHandler()
    redacted, mapping = handler.redact(text)
    
    console.print(Panel(redacted, title="Redacted Text", border_style="green"))
    
    if mapping:
        console.print("\n[dim]Redaction mapping:[/dim]")
        for placeholder, original in mapping.items():
            console.print(f"  {placeholder} -> {original[:20]}...")
    
    if output:
        Path(output).write_text(redacted, encoding="utf-8")
        console.print(f"\n[green]Redacted text saved to {output}[/green]")


@cli.group()
def config():
    """Manage SplitMind configuration."""
    pass


@config.command()
def show():
    """Show current configuration."""
    from splitmind.config import config_manager
    
    config = config_manager.load()
    
    console.print(Panel("SplitMind Configuration", border_style="blue"))
    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Execution Mode", config.execution_mode)
    table.add_row("Default Model", config.default_model)
    table.add_row("Privacy Protection", str(config.enable_privacy_protection))
    table.add_row("Default Strategy", config.default_strategy)
    table.add_row("Max Concurrent Tasks", str(config.max_concurrent_tasks))
    table.add_row("Timeout per Task", str(config.timeout_per_task))
    table.add_row("Retry Failed Tasks", str(config.retry_failed_tasks))
    table.add_row("Max Retries", str(config.max_retries))
    
    console.print(table)


@config.command()
@click.argument("mode", type=click.Choice(["local_only", "hybrid", "online"]))
def set_mode(mode: str):
    """Set default execution mode."""
    from splitmind.config import config_manager
    from splitmind.core.engine import ExecutionMode
    
    try:
        execution_mode = ExecutionMode(mode)
        config_manager.set_execution_mode(execution_mode)
        console.print(f"[green]Default execution mode set to: {mode}[/green]")
    except ValueError:
        console.print("[red]Invalid execution mode. Use: local_only, hybrid, or online[/red]")


@config.command()
@click.argument("model")
def set_model(model: str):
    """Set default local model."""
    from splitmind.config import config_manager
    
    config_manager.set_default_model(model)
    console.print(f"[green]Default local model set to: {model}[/green]")


@config.command()
@click.argument("enabled", type=click.BOOL)
def set_privacy(enabled: bool):
    """Set privacy protection setting."""
    from splitmind.config import config_manager
    
    config_manager.set_privacy_protection(enabled)
    status = "enabled" if enabled else "disabled"
    console.print(f"[green]Privacy protection {status}[/green]")


@cli.command()
@click.argument("text", required=False)
@click.option("--share", "-s", is_flag=True, help="Generate shareable report")
def demo(text: Optional[str], share: bool):
    """
    Zero-config privacy demonstration.
    
    Shows how SplitMind protects your sensitive information
    without requiring any API keys or configuration.
    """
    from splitmind.demo import PrivacyDemo, quick_demo
    
    if not text:
        # Use example text if none provided
        text = """
客户信息：
姓名：张三
电话：13812345678
邮箱：zhangsan@example.com
身份证号：320123199001011234
地址：北京市朝阳区xxx街道123号
        """.strip()
    
    demo_engine = PrivacyDemo()
    result = demo_engine.analyze(text)
    
    # Header
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]SPLITMIND Privacy Protection Demo[/bold cyan]")
    console.print("=" * 70)
    
    # Risk assessment
    console.print("\nPrivacy Risk Assessment")
    risk_color = "red" if result.risk_level in ["high", "critical"] else "yellow"
    console.print(f"   Risk Level: [{risk_color}]{result.risk_level.upper()}[/{risk_color}]")
    console.print(f"   Risk Score: {result.risk_score}/100")
    console.print(f"   Protection Rate: [green]{result.protection_rate:.0f}%[/green]")
    
    # Comparison
    console.print("\n" + "-" * 70)
    console.print("WITHOUT SplitMind (Direct to AI):")
    console.print("   All sensitive information is exposed:")
    for info_type, items in result.detected_items.items():
        console.print(f"   * {info_type}: {items[0][:30]}..." if len(str(items[0])) > 30 else f"   * {info_type}: {items[0]}")
    
    console.print("\nWITH SplitMind (Protected):")
    console.print("   Sensitive data is redacted:")
    console.print(Panel(result.redacted_text[:500], border_style="green", title="Protected Output"))
    
    # Detected items detail
    if result.detected_items:
        console.print("\nDetected Sensitive Information:")
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right", style="yellow")
        table.add_column("Example", style="dim")
        
        for info_type, items in result.detected_items.items():
            table.add_row(
                info_type,
                str(len(items)),
                items[0][:40] + "..." if len(str(items[0])) > 40 else items[0]
            )
        console.print(table)
    
    # Share card
    if share:
        console.print("\n" + "-" * 70)
        console.print("Share this analysis:")
        card = demo_engine.generate_share_card(result)
        console.print(Panel(card, border_style="blue"))
    
    # Footer
    console.print("\n" + "=" * 70)
    console.print("Try it with your own text: splitmind demo \"your text here\"")
    console.print("Learn more: https://github.com/yourusername/splitmind")
    console.print("=" * 70 + "\n")


def main():
    cli()


if __name__ == "__main__":
    main()
