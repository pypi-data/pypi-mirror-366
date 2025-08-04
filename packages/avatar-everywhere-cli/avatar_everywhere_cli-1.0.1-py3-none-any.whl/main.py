#!/usr/bin/env python3
"""
Avatar Everywhere CLI - Portable Sandbox Identity Toolkit
Milestone 1: NFT Ownership Verification + Avatar Export to VRM

Main entry point for the CLI application.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.syntax import Syntax
from rich.traceback import install as install_traceback

from cli import app

# Install rich traceback handler for better error display
install_traceback()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()

def show_banner():
    """Display a professional banner"""
    banner_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   █████╗ ██╗   ██╗ █████╗ ████████╗ ██████╗    ██████╗██╗     ██╗          ║
║  ██╔══██╗██║   ██║██╔══██╗╚══██╔══╝██╔═══██╗   ██╔══██╗██║     ██║         ║
║  ███████║██║   ██║███████║   ██║   ██║   ██║   ██████╔╝██║     ██║         ║
║  ██╔══██║██║   ██║██╔══██║   ██║   ██║   ██║   ██╔══██╗██║     ██║         ║
║  ██║  ██║╚██████╔╝██║  ██║   ██║   ╚██████╔╝   ██║  ██║███████╗███████╗    ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝    ╚═╝  ╚═╝╚══════╝╚══════╝    ║
║                                                                              ║
║                Avatar Everywhere CLI - Identity Toolkit                      ║
║                                                                              ║
║  NFT Verification • VRM Conversion • Cross-Platform Compatibility            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    console.print(Panel(
        Align.center(Text(banner_text, style="bold cyan")),
        border_style="bright_blue",
        padding=(1, 2)
    ))

def show_version_info():
    """Display version and system information"""
    version_info = [
        ("Version", "1.0.0", "bright_green"),
        ("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", "bright_blue"),
        ("Platform", sys.platform, "bright_yellow"),
        ("Status", "Ready", "bright_green")
    ]
    
    columns = []
    for label, value, color in version_info:
        columns.append(f"[{color}]{label}:[/{color}] {value}")
    
    console.print(Columns(columns, equal=True, expand=True))
    console.print()

def show_quick_start():
    """Display quick start guide"""
    quick_start_text = Text()
    quick_start_text.append("Quick Start Guide:\n", style="bold cyan")
    quick_start_text.append("\n")
    quick_start_text.append("1. Verify NFT Ownership:\n", style="bold green")
    quick_start_text.append("   python3 main.py verify --contract 0x... --token 123\n")
    quick_start_text.append("\n")
    quick_start_text.append("2. Convert Avatar:\n", style="bold green")
    quick_start_text.append("   python3 main.py convert avatar.glb --output avatar.vrm\n")
    quick_start_text.append("\n")
    quick_start_text.append("3. Get File Info:\n", style="bold green")
    quick_start_text.append("   python3 main.py info avatar.glb\n")
    quick_start_text.append("\n")
    quick_start_text.append("4. Check Requirements:\n", style="bold green")
    quick_start_text.append("   python3 main.py list-requirements\n")
    console.print(Panel(
        quick_start_text,
        title="[bold cyan]Quick Start[/bold cyan]",
        border_style="bright_blue",
        padding=(1, 2)
    ))

def main():
    """Main entry point for the Avatar Everywhere CLI"""
    try:
        # Show banner if no arguments or if --help is present
        if len(sys.argv) == 1 or "--help" in sys.argv:
            show_banner()
            show_version_info()
            show_quick_start()
            console.print(Rule(style="bright_blue"))
        # Run the CLI
        app()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user[/bold yellow]")
        console.print("[dim]Press Ctrl+C again to exit immediately[/dim]")
        sys.exit(0)
    except typer.Exit as e:
        sys.exit(e.exit_code)
    except ImportError as e:
        console.print("\n[bold red]Import Error[/bold red]")
        console.print(f"[red]Missing dependency: {e}[/red]")
        console.print("\n[dim]Please install required dependencies: pip install -r requirements.txt[/dim]")
        logger.error(f"Import error: {e}")
        sys.exit(1)
    except PermissionError as e:
        console.print("\n[bold red]Permission Error[/bold red]")
        console.print(f"[red]Access denied: {e}[/red]")
        console.print("\n[dim]Please check file permissions or run with appropriate privileges[/dim]")
        logger.error(f"Permission error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        console.print("\n[bold red]File Not Found[/bold red]")
        console.print(f"[red]File not found: {e}[/red]")
        console.print("\n[dim]Please check the file path and try again[/dim]")
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except OSError as e:
        console.print("\n[bold red]System Error[/bold red]")
        console.print(f"[red]System error: {e}[/red]")
        console.print("\n[dim]Please check your system configuration[/dim]")
        logger.error(f"OS error: {e}")
        sys.exit(1)
    except MemoryError as e:
        console.print("\n[bold red]Memory Error[/bold red]")
        console.print(f"[red]Insufficient memory: {e}[/red]")
        console.print("\n[dim]Please close other applications and try again[/dim]")
        logger.error(f"Memory error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print("\n[bold red]Unexpected Error[/bold red]")
        console.print(f"[red]Error: {e}[/red]")
        console.print("\n[dim]For help, run: python3 main.py --help[/dim]")
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()