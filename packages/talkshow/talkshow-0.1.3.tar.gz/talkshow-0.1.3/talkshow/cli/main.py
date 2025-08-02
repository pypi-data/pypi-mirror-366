#!/usr/bin/env python3
"""
TalkShow CLI Main Module

Provides command-line interface for TalkShow functionality.
"""

import click
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel

# Import configuration manager
from ..config.manager import ConfigManager

console = Console()

# Global config manager
config_manager = ConfigManager()

def get_project_root() -> Path:
    """Find the project root containing .specstory directory."""
    current_dir = Path.cwd()
    
    # Check current directory and parents
    for parent in [current_dir] + list(current_dir.parents):
        specstory_dir = parent / ".specstory"
        if specstory_dir.exists() and specstory_dir.is_dir():
            return parent
    
    return current_dir

def load_config(config_path: Path) -> Optional[Dict[str, Any]]:
    """Load configuration from YAML file."""
    return config_manager.load_config()

def save_config(config_path: Path, config: Dict[str, Any]) -> bool:
    """Save configuration to YAML file."""
    return config_manager.save_project_config(config)

@click.group()
@click.version_option(version="0.2.0")
def cli():
    """🎭 TalkShow - Chat History Analysis and Visualization Tool
    
    Analyze and visualize chat history from SpecStory plugin.
    """
    pass

@cli.command()
def init():
    """Initialize TalkShow configuration in .specstory directory."""
    console.print(Panel.fit(
        "[bold blue]🔧 TalkShow Initialization[/bold blue]\n"
        "Setting up configuration and directories...",
        border_style="blue"
    ))
    
    # Check for .specstory directory
    project_root = get_project_root()
    specstory_dir = project_root / ".specstory"
    history_dir = specstory_dir / "history"
    
    if not specstory_dir.exists():
        console.print("[red]❌ .specstory directory not found![/red]")
        console.print("Please ensure you're in a project with .specstory directory.")
        return 1
    
    if not history_dir.exists():
        console.print("[red]❌ .specstory/history directory not found![/red]")
        console.print("Please ensure .specstory/history directory exists.")
        return 1
    
    # Create data directory
    data_dir = specstory_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Load default configuration
    default_config = config_manager.load_config()
    
    # Create project-specific configuration
    project_config = {
        "llm": default_config.get("llm", {}),
        "paths": {
            "config_file": ".specstory/talkshow.yaml",
            "history_dir": ".specstory/history",
            "output_dir": ".specstory/data"
        },
        "project": default_config.get("project", {}),
        "server": {
            "host": default_config.get("web", {}).get("host", "127.0.0.1"),
            "port": default_config.get("web", {}).get("port", 8000),
            "reload": default_config.get("web", {}).get("reload", True)
        },
        "summarizer": default_config.get("summarizer", {})
    }
    
    # Save project configuration
    config_path = specstory_dir / "talkshow.yaml"
    if save_config(config_path, project_config):
        console.print(f"✅ Configuration saved to: {config_path}")
    else:
        console.print("[red]❌ Failed to save configuration![/red]")
        return 1
    
    console.print(f"📁 Project root: {project_root}")
    console.print(f"📁 History directory: {history_dir}")
    console.print(f"📁 Data directory: {data_dir}")
    console.print(f"⚙️  Configuration: {config_path}")
    console.print(f"🌐 Server port: {project_config['server']['port']}")
    
    console.print("\n[green]✅ TalkShow initialized successfully![/green]")
    console.print("Next steps:")
    console.print("  [blue]talkshow parse[/blue] - Parse chat history")
    console.print("  [blue]talkshow server[/blue] - Start web server")
    
    return 0

@cli.command()
@click.option('--use-llm', is_flag=True, help='Use LLM for summarization')
def parse(use_llm: bool):
    """Parse chat history and generate JSON files."""
    console.print(Panel.fit(
        "[bold green]📁 TalkShow Parser[/bold green]\n"
        "Parsing chat history and generating summaries...",
        border_style="green"
    ))
    
    # Load configuration
    config = load_config(None)
    if not config:
        console.print("[red]❌ Failed to load configuration![/red]")
        return 1
    
    # Get paths from config manager
    history_dir = config_manager.get_history_dir()
    output_dir = config_manager.get_output_dir()
    data_file = config_manager.get_data_file_path()
    
    if not history_dir.exists():
        console.print(f"[red]❌ History directory not found: {history_dir}[/red]")
        console.print("Please run [blue]talkshow init[/blue] first.")
        return 1
    
    console.print(f"📁 Parsing files from: {history_dir}")
    
    try:
        # Import parser components
        from ..parser.md_parser import MDParser
        from ..summarizer.rule_summarizer import RuleSummarizer
        from ..summarizer.llm_summarizer import LLMSummarizer
        from ..storage.json_storage import JSONStorage
        
        # Initialize components
        parser = MDParser()
        storage = JSONStorage(str(data_file))
        
        # Choose summarizer
        if use_llm and config.get("summarizer", {}).get("llm", {}).get("enabled", False):
            summarizer = LLMSummarizer()
            console.print("🧠 Using LLM summarization")
        else:
            summarizer = RuleSummarizer()
            console.print("📝 Using rule-based summarization")
        
        # Parse files
        sessions = []
        for md_file in history_dir.glob("*.md"):
            try:
                session = parser.parse_file(md_file)
                if session:
                    sessions.append(session)
            except Exception as e:
                console.print(f"[yellow]⚠️  Failed to parse {md_file.name}: {e}[/yellow]")
        
        console.print(f"✅ Found {len(sessions)} valid chat sessions")
        
        # Generate summaries
        console.print("📝 Generating summaries...")
        summary_count = 0
        for session in sessions:
            for qa in session.qa_pairs:
                if summarizer.summarize_qa(qa):
                    summary_count += 2  # question + answer
        
        console.print(f"📝 Generated {summary_count} summaries")
        
        # Save sessions
        storage.save_sessions(sessions)
        console.print(f"💾 Sessions saved to: {data_file}")
        
        # Print statistics
        total_qa = sum(len(session.qa_pairs) for session in sessions)
        file_size = data_file.stat().st_size if data_file.exists() else 0
        
        console.print(f"\n📊 Statistics:")
        console.print(f"  📁 Sessions: {len(sessions)}")
        console.print(f"  💬 Q&A pairs: {total_qa}")
        console.print(f"  💾 File size: {file_size / 1024 / 1024:.1f}MB")
        
        return 0
        
    except Exception as e:
        console.print(f"[red]❌ Error during parsing: {e}[/red]")
        return 1

@cli.command()
@click.option('--port', '-p', type=int, help='Server port (overrides config)')
@click.option('--host', '-h', help='Server host (overrides config)')
@click.option('--data-file', help='Data file path (overrides config)')
def server(port: Optional[int], host: Optional[str], data_file: Optional[str]):
    """Start the TalkShow web server."""
    console.print(Panel.fit(
        "[bold blue]🌐 TalkShow Web Server[/bold blue]\n"
        "Starting web interface for chat history visualization...",
        border_style="blue"
    ))
    
    # Load configuration
    config = load_config(None)
    if not config:
        console.print("[red]❌ Failed to load configuration![/red]")
        return 1
    
    # Get server settings
    # Check both 'server' and 'web' keys for compatibility
    server_config = config.get("server", {})
    web_config = config.get("web", {})
    
    server_host = host or server_config.get("host") or web_config.get("host", "127.0.0.1")
    server_port = port or server_config.get("port") or web_config.get("port", 8000)
    
    # Get data file path
    if data_file:
        data_file_path = Path(data_file)
    else:
        data_file_path = config_manager.get_data_file_path()
    
    if not data_file_path.exists():
        console.print(f"[red]❌ Data file not found: {data_file_path}[/red]")
        console.print("Please run [blue]talkshow parse[/blue] first.")
        return 1
    
    console.print(f"📁 Data file: {data_file_path}")
    console.print(f"🌐 Starting server at: http://{server_host}:{server_port}")
    console.print(f"📱 API docs at: http://{server_host}:{server_port}/docs")
    console.print("🔄 Press Ctrl+C to stop")
    console.print("=" * 50)
    
    try:
        # Import and run the FastAPI app
        from talkshow.web.app import app
        
        import uvicorn
        
        # Fix uvicorn reload issue
        if config.get("web", {}).get("reload", True):
            # Use string import for reload mode
            uvicorn.run(
                "talkshow.web.app:app",
                host=server_host,
                port=server_port,
                reload=True,
                log_level="info"
            )
        else:
            # Use app object for non-reload mode
            uvicorn.run(
                app,
                host=server_host,
                port=server_port,
                reload=False,
                log_level="info"
            )
    except KeyboardInterrupt:
        console.print("\n👋 Server stopped.")
    except Exception as e:
        console.print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

@cli.command()
@click.option('--port', '-p', type=int, help='Server port to stop (overrides config)')
@click.option('--host', '-h', help='Server host to stop (overrides config)')
@click.option('--force', '-f', is_flag=True, help='Force stop without confirmation')
def stop(port: Optional[int], host: Optional[str], force: bool):
    """Stop the TalkShow web server."""
    console.print(Panel.fit(
        "[bold red]🛑 TalkShow Server Stop[/bold red]\n"
        "Stopping the web server...",
        border_style="red"
    ))
    
    # Load configuration
    config = load_config(None)
    if not config:
        console.print("[red]❌ Failed to load configuration![/red]")
        return 1
    
    # Get server settings
    # Check both 'server' and 'web' keys for compatibility
    server_config = config.get("server", {})
    web_config = config.get("web", {})
    
    server_host = host or server_config.get("host") or web_config.get("host", "127.0.0.1")
    server_port = port or server_config.get("port") or web_config.get("port", 8000)
    
    console.print(f"🔍 Looking for server at {server_host}:{server_port}")
    
    try:
        import psutil
        import signal
        
        # Find processes using the port
        found_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                connections = proc.connections()
                for conn in connections:
                    if conn.laddr.port == server_port and conn.laddr.ip == server_host:
                        found_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not found_processes:
            console.print(f"[yellow]⚠️  No server found running on {server_host}:{server_port}[/yellow]")
            return 0
        
        # Show found processes
        console.print(f"📋 Found {len(found_processes)} process(es) using port {server_port}:")
        for proc in found_processes:
            console.print(f"  PID: {proc.pid}, Name: {proc.name()}")
        
        # Confirm stop if not forced
        if not force:
            response = input(f"\nStop server on {server_host}:{server_port}? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                console.print("❌ Operation cancelled.")
                return 0
        
        # Stop processes
        stopped_count = 0
        for proc in found_processes:
            try:
                console.print(f"🛑 Stopping process {proc.pid}...")
                proc.terminate()
                proc.wait(timeout=5)  # Wait up to 5 seconds
                stopped_count += 1
                console.print(f"✅ Process {proc.pid} stopped successfully.")
            except psutil.TimeoutExpired:
                console.print(f"⚠️  Process {proc.pid} didn't stop gracefully, forcing...")
                proc.kill()
                stopped_count += 1
            except psutil.NoSuchProcess:
                console.print(f"✅ Process {proc.pid} already stopped.")
                stopped_count += 1
            except Exception as e:
                console.print(f"❌ Error stopping process {proc.pid}: {e}")
        
        if stopped_count > 0:
            console.print(f"\n[green]✅ Successfully stopped {stopped_count} server process(es).[/green]")
        else:
            console.print("\n[yellow]⚠️  No processes were stopped.[/yellow]")
        
        return 0
        
    except ImportError:
        console.print("[red]❌ psutil not available. Please install it: pip install psutil[/red]")
        console.print("Alternatively, you can manually stop the server using:")
        console.print(f"  lsof -ti:{server_port} | xargs kill")
        return 1
    except Exception as e:
        console.print(f"❌ Error stopping server: {e}")
        return 1

@cli.command()
def config():
    """Show configuration information."""
    console.print(Panel.fit(
        "[bold yellow]⚙️  TalkShow Configuration[/bold yellow]\n"
        "Displaying current configuration settings...",
        border_style="yellow"
    ))
    
    config_manager.print_config_info()
    
    # Show current configuration
    config = config_manager.load_config()
    if config:
        console.print("\n[bold]Current Configuration:[/bold]")
        # Check both 'server' and 'web' keys for compatibility
        server_config = config.get("server", {})
        web_config = config.get("web", {})
        
        console.print(f"  Web Host: {server_config.get('host') or web_config.get('host', '127.0.0.1')}")
        console.print(f"  Web Port: {server_config.get('port') or web_config.get('port', 8000)}")
        console.print(f"  History Dir: {config.get('parser', {}).get('history_directory', '.specstory/history')}")
        console.print(f"  Data File: {config.get('storage', {}).get('json', {}).get('file_path', '.specstory/data/sessions.json')}")
        console.print(f"  Summarizer Enabled: {config.get('summarizer', {}).get('enabled', True)}")
        console.print(f"  LLM Enabled: {config.get('summarizer', {}).get('llm', {}).get('enabled', False)}")

def main():
    """Main entry point for the talkshow command."""
    cli()

if __name__ == "__main__":
    main() 