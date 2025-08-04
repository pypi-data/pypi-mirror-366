#!/usr/bin/env python3
"""
Command-line interface for ai-prishtina-TEXT2SQL-LTM.

This module provides a comprehensive CLI for managing and interacting with
the Text2SQL agent with long-term memory capabilities.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from . import Text2SQLAgent, MemoryConfig, AgentConfig, create_agent
from .exceptions import Text2SQLLTMError

app = typer.Typer(
    name="text2sql-ltm",
    help="ai-prishtina-TEXT2SQL-LTM: Text2SQL Agent with Long-Term Memory",
    add_completion=False,
)
console = Console()


@app.command()
def query(
    text: str = typer.Argument(..., help="Natural language query"),
    user_id: str = typer.Option("cli_user", "--user", "-u", help="User ID"),
    database: str = typer.Option("default", "--database", "-d", help="Database name"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Session ID"),
    remember: bool = typer.Option(True, "--remember/--no-remember", help="Remember this query"),
    explain: bool = typer.Option(True, "--explain/--no-explain", help="Show explanation"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Process a natural language query and generate SQL."""
    async def _query():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Processing query...", total=None)
                
                # Initialize agent
                agent = create_agent()
                await agent.initialize()
                
                progress.update(task, description="Generating SQL...")
                
                # Process query
                result = await agent.query(
                    natural_language=text,
                    user_id=user_id,
                    session_id=session_id,
                    remember_query=remember
                )
                
                progress.update(task, description="Complete!", completed=True)
            
            # Display results
            console.print(Panel.fit(
                f"[bold blue]Query:[/bold blue] {text}",
                title="🤖 Natural Language Input"
            ))
            
            # SQL output
            sql_syntax = Syntax(result.sql, "sql", theme="monokai", line_numbers=True)
            console.print(Panel(
                sql_syntax,
                title="🔍 Generated SQL",
                border_style="green"
            ))
            
            # Metadata table
            metadata_table = Table(title="📊 Query Metadata")
            metadata_table.add_column("Property", style="cyan")
            metadata_table.add_column("Value", style="green")
            
            metadata_table.add_row("Confidence", f"{result.confidence:.2%}")
            metadata_table.add_row("Query Type", result.query_type or "Unknown")
            metadata_table.add_row("Tables Used", ", ".join(result.tables_used) if result.tables_used else "None")
            metadata_table.add_row("Processing Time", f"{result.processing_time:.3f}s")
            metadata_table.add_row("Memory Enhanced", "Yes" if result.metadata.get("memory_enhanced") else "No")
            
            console.print(metadata_table)
            
            # Explanation
            if explain and result.explanation:
                console.print(Panel(
                    result.explanation,
                    title="💡 Explanation",
                    border_style="yellow"
                ))
            
            # Memory context
            if result.memory_context_used:
                console.print(Panel(
                    f"Used {len(result.memory_context_used)} memory influences",
                    title="🧠 Memory Context",
                    border_style="purple"
                ))
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)
        finally:
            if 'agent' in locals():
                await agent.cleanup()
    
    asyncio.run(_query())


@app.command()
def chat(
    user_id: str = typer.Option("cli_user", "--user", "-u", help="User ID"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Session ID"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file"),
):
    """Start an interactive chat session with the Text2SQL agent."""
    async def _chat():
        agent = None
        try:
            console.print(Panel.fit(
                "[bold blue]ai-prishtina-TEXT2SQL-LTM Interactive Chat[/bold blue]\n"
                "Type your natural language queries. Type 'quit' or 'exit' to end.\n"
                "Type 'help' for available commands.",
                title="🤖 Chat Mode"
            ))
            
            # Initialize agent
            with Progress(
                SpinnerColumn(),
                TextColumn("Initializing agent..."),
                console=console,
            ) as progress:
                task = progress.add_task("Loading...", total=None)
                agent = create_agent()
                await agent.initialize()
                progress.update(task, completed=True)
            
            # Create session
            session = agent.create_session(user_id, session_id)
            console.print(f"[green]Session created: {session.session_id}[/green]")
            
            query_count = 0
            
            while True:
                try:
                    # Get user input
                    query = Prompt.ask("\n[bold cyan]Query[/bold cyan]")
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        break
                    elif query.lower() == 'help':
                        _show_chat_help()
                        continue
                    elif query.lower() == 'stats':
                        await _show_session_stats(agent, user_id, session.session_id)
                        continue
                    elif query.lower() == 'history':
                        _show_session_history(session)
                        continue
                    elif query.lower().startswith('feedback'):
                        # Handle feedback command
                        continue
                    
                    # Process query
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("Processing..."),
                        console=console,
                    ) as progress:
                        task = progress.add_task("Generating SQL...", total=None)
                        
                        result = await agent.query(
                            natural_language=query,
                            user_id=user_id,
                            session_id=session.session_id
                        )
                        
                        progress.update(task, completed=True)
                    
                    query_count += 1
                    
                    # Display result
                    console.print(f"\n[bold green]SQL #{query_count}:[/bold green]")
                    sql_syntax = Syntax(result.sql, "sql", theme="monokai")
                    console.print(sql_syntax)
                    
                    console.print(f"[dim]Confidence: {result.confidence:.1%} | "
                                f"Time: {result.processing_time:.3f}s | "
                                f"Memory: {'Yes' if result.metadata.get('memory_enhanced') else 'No'}[/dim]")
                    
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'quit' to exit properly.[/yellow]")
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
            
            # Show session summary
            stats = session.get_stats()
            console.print(Panel(
                f"Queries processed: {stats['total_queries']}\n"
                f"Session duration: {stats['session_duration_minutes']:.1f} minutes\n"
                f"Average confidence: {stats['avg_confidence']:.1%}",
                title="📊 Session Summary"
            ))
            
        except Exception as e:
            console.print(f"[red]Chat session error: {str(e)}[/red]")
            sys.exit(1)
        finally:
            if agent:
                await agent.cleanup()
    
    asyncio.run(_chat())


@app.command()
def memory(
    action: str = typer.Argument(..., help="Action: list, search, delete, stats"),
    user_id: str = typer.Option("cli_user", "--user", "-u", help="User ID"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Search query"),
    memory_type: Optional[str] = typer.Option(None, "--type", "-t", help="Memory type filter"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results"),
):
    """Manage user memories."""
    async def _memory():
        try:
            agent = create_agent()
            await agent.initialize()
            
            if action == "list":
                memories = await agent.memory_manager.retrieve_memories(
                    user_id=user_id,
                    memory_type=memory_type,
                    limit=limit
                )
                
                if not memories:
                    console.print("[yellow]No memories found.[/yellow]")
                    return
                
                table = Table(title=f"🧠 Memories for {user_id}")
                table.add_column("ID", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Content", style="white")
                table.add_column("Created", style="dim")
                
                for memory in memories:
                    content = str(memory.get('content', ''))[:50] + "..."
                    created = memory.get('created_at', 'Unknown')
                    table.add_row(
                        memory.get('id', 'N/A')[:8],
                        memory.get('memory_type', 'unknown'),
                        content,
                        created
                    )
                
                console.print(table)
            
            elif action == "search":
                if not query:
                    console.print("[red]Search query required with --query[/red]")
                    return
                
                memories = await agent.memory_manager.retrieve_memories(
                    user_id=user_id,
                    query=query,
                    memory_type=memory_type,
                    limit=limit
                )
                
                console.print(f"[green]Found {len(memories)} memories matching '{query}'[/green]")
                
                for i, memory in enumerate(memories, 1):
                    console.print(Panel(
                        f"Content: {memory.get('content', 'N/A')}\n"
                        f"Type: {memory.get('memory_type', 'unknown')}\n"
                        f"Relevance: {memory.get('relevance_score', 0):.2f}",
                        title=f"Memory {i}"
                    ))
            
            elif action == "stats":
                stats = await agent.memory_manager.get_user_memory_stats(user_id)
                
                table = Table(title=f"📊 Memory Statistics for {user_id}")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Total Memories", str(stats.get('total_memories', 0)))
                table.add_row("Oldest Memory", stats.get('oldest_memory', 'N/A'))
                table.add_row("Newest Memory", stats.get('newest_memory', 'N/A'))
                table.add_row("Estimated Size", f"{stats.get('total_size_estimate', 0)} bytes")
                
                console.print(table)
                
                # Memory types breakdown
                memory_types = stats.get('memory_types', {})
                if memory_types:
                    type_table = Table(title="Memory Types")
                    type_table.add_column("Type", style="cyan")
                    type_table.add_column("Count", style="green")
                    
                    for mem_type, count in memory_types.items():
                        type_table.add_row(mem_type, str(count))
                    
                    console.print(type_table)
            
            else:
                console.print(f"[red]Unknown action: {action}[/red]")
                console.print("Available actions: list, search, stats")
        
        except Exception as e:
            console.print(f"[red]Memory operation failed: {str(e)}[/red]")
            sys.exit(1)
        finally:
            if 'agent' in locals():
                await agent.cleanup()
    
    asyncio.run(_memory())


@app.command()
def config(
    action: str = typer.Argument(..., help="Action: show, validate, create"),
    config_file: Optional[Path] = typer.Option(None, "--file", "-f", help="Configuration file"),
):
    """Manage configuration."""
    if action == "show":
        from .config import get_config
        config_data = get_config()
        
        console.print(Panel(
            json.dumps({
                "memory": config_data["memory"].dict(),
                "agent": config_data["agent"].dict(),
            }, indent=2),
            title="🔧 Current Configuration"
        ))
    
    elif action == "validate":
        try:
            from .config import load_config
            config_data = load_config(config_file)
            console.print("[green]✓ Configuration is valid[/green]")
        except Exception as e:
            console.print(f"[red]✗ Configuration error: {str(e)}[/red]")
            sys.exit(1)
    
    elif action == "create":
        if not config_file:
            config_file = Path("text2sql_ltm_config.yaml")
        
        if config_file.exists():
            if not Confirm.ask(f"File {config_file} exists. Overwrite?"):
                return
        
        # Create sample configuration
        sample_config = {
            "memory": {
                "storage_backend": "mem0",
                "user_isolation": True,
                "learning_enabled": True,
                "memory_ttl_days": 90,
            },
            "agent": {
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.1,
                "enable_query_optimization": True,
            }
        }
        
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False)
        
        console.print(f"[green]✓ Sample configuration created: {config_file}[/green]")
    
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Available actions: show, validate, create")


@app.command()
def info():
    """Show system information and status."""
    from . import __version__, get_features, check_dependencies
    
    # System info
    info_table = Table(title="🔍 System Information")
    info_table.add_column("Component", style="cyan")
    info_table.add_column("Status", style="green")
    
    info_table.add_row("Version", __version__)
    info_table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    console.print(info_table)
    
    # Dependencies
    deps_table = Table(title="📦 Dependencies")
    deps_table.add_column("Dependency", style="cyan")
    deps_table.add_column("Available", style="green")
    
    dependencies = check_dependencies()
    for dep, available in dependencies.items():
        status = "✓ Yes" if available else "✗ No"
        color = "green" if available else "red"
        deps_table.add_row(dep, f"[{color}]{status}[/{color}]")
    
    console.print(deps_table)
    
    # Features
    features_table = Table(title="🚀 Features")
    features_table.add_column("Feature", style="cyan")
    features_table.add_column("Enabled", style="green")
    
    features = get_features()
    for feature, enabled in features.items():
        status = "✓ Yes" if enabled else "✗ No"
        color = "green" if enabled else "yellow"
        features_table.add_row(feature, f"[{color}]{status}[/{color}]")
    
    console.print(features_table)


def _show_chat_help():
    """Show chat mode help."""
    help_text = """
[bold]Available Commands:[/bold]
• [cyan]help[/cyan] - Show this help message
• [cyan]stats[/cyan] - Show session statistics
• [cyan]history[/cyan] - Show query history
• [cyan]quit/exit[/cyan] - End chat session

[bold]Query Examples:[/bold]
• "Show me all customers from New York"
• "What's the total revenue for last month?"
• "Find products with low inventory"
• "List top 10 customers by order value"
"""
    console.print(Panel(help_text, title="💡 Chat Help"))


async def _show_session_stats(agent, user_id: str, session_id: str):
    """Show session statistics."""
    try:
        session = agent.session_manager.get_session(user_id, session_id)
        if session:
            stats = session.get_stats()
            
            table = Table(title="📊 Session Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Queries", str(stats["total_queries"]))
            table.add_row("Successful Queries", str(stats["successful_queries"]))
            table.add_row("Memory Enhanced", str(stats["memory_enhanced_queries"]))
            table.add_row("Average Confidence", f"{stats['avg_confidence']:.1%}")
            table.add_row("Session Duration", f"{stats['session_duration_minutes']:.1f} min")
            
            console.print(table)
        else:
            console.print("[yellow]Session not found[/yellow]")
    except Exception as e:
        console.print(f"[red]Error getting stats: {str(e)}[/red]")


def _show_session_history(session):
    """Show session query history."""
    history = session.get_history(limit=10)
    
    if not history:
        console.print("[yellow]No query history[/yellow]")
        return
    
    table = Table(title="📜 Query History")
    table.add_column("#", style="dim")
    table.add_column("Query", style="cyan")
    table.add_column("Confidence", style="green")
    table.add_column("Time", style="dim")
    
    for i, query_history in enumerate(history, 1):
        confidence = query_history.metadata.get('confidence', 0)
        table.add_row(
            str(i),
            query_history.natural_language[:50] + "...",
            f"{confidence:.1%}",
            query_history.timestamp.strftime("%H:%M:%S")
        )
    
    console.print(table)


def main():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
