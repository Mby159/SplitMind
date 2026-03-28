"""
SplitMind CLI - Command line interface for SplitMind.
"""

import sys
from typing import Optional
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


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
@click.argument("text", required=False)
@click.option("--share", "-s", is_flag=True, help="Generate shareable report")
def demo(text: Optional[str], share: bool):
    """
    Zero-config privacy demonstration.
    
    Shows how SplitMind protects your sensitive information
    without requiring any API keys or configuration.
    """
    from splitmind_cli.demo import PrivacyDemo
    
    if not text:
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
    
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]SPLITMIND Privacy Protection Demo[/bold cyan]")
    console.print("=" * 70)
    
    console.print("\nPrivacy Risk Assessment")
    risk_color = "red" if result.risk_level in ["high", "critical"] else "yellow"
    console.print(f"   Risk Level: [{risk_color}]{result.risk_level.upper()}[/{risk_color}]")
    console.print(f"   Risk Score: {result.risk_score}/100")
    console.print(f"   Protection Rate: [green]{result.protection_rate:.0f}%[/green]")
    
    console.print("\n" + "-" * 70)
    console.print("WITHOUT SplitMind (Direct to AI):")
    console.print("   All sensitive information is exposed:")
    for info_type, items in result.detected_items.items():
        console.print(f"   * {info_type}: {items[0][:30]}..." if len(str(items[0])) > 30 else f"   * {info_type}: {items[0]}")
    
    console.print("\nWITH SplitMind (Protected):")
    console.print("   Sensitive data is redacted:")
    console.print(Panel(result.redacted_text[:500], border_style="green", title="Protected Output"))
    
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
    
    if share:
        console.print("\n" + "-" * 70)
        console.print("Share this analysis:")
        card = demo_engine.generate_share_card(result)
        console.print(Panel(card, border_style="blue"))
    
    console.print("\n" + "=" * 70)
    console.print("Try it with your own text: splitmind demo \"your text here\"")
    console.print("Learn more: https://github.com/yourusername/splitmind")
    console.print("=" * 70 + "\n")


@cli.command()
@click.argument("text")
def analyze(text: str):
    """Analyze text for sensitive information."""
    
    from splitmind_core.privacy import PrivacyHandler
    
    handler = PrivacyHandler()
    report = handler.generate_report(text)
    
    risk_color = "red" if report.risk_level in ["high", "critical"] else "yellow"
    console.print(Panel(
        f"Risk Level: [{risk_color}]{report.risk_level}[/{risk_color}]",
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
@click.argument("text")
@click.option("--output", "-o", type=click.Path(), help="Save redacted text to file")
def redact(text: str, output: Optional[str]):
    """Redact sensitive information from text."""
    
    from splitmind_core.privacy import PrivacyHandler
    
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


def main():
    cli()


if __name__ == "__main__":
    main()
