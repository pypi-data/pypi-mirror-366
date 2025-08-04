"""
Avatar Everywhere CLI - Core Commands
Handles wallet verification and avatar conversion workflows
"""

import logging
import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.syntax import Syntax
from rich.traceback import install as install_traceback

from converters.sandbox_to_vrm import SandboxToVRMConverter

# Install rich traceback handler for better error display
install_traceback()

# Configure logging
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="avatar-everywhere",
    help="Convert Sandbox avatars to VRM format with NFT ownership verification",
    add_completion=False
)

console = Console()

def show_success(message: str):
    """Display success message"""
    console.print(f"[bold green]SUCCESS: {message}[/bold green]")

def show_error(message: str):
    """Display error message"""
    console.print(f"[bold red]ERROR: {message}[/bold red]")

def show_warning(message: str):
    """Display warning message"""
    console.print(f"[bold yellow]WARNING: {message}[/bold yellow]")

def show_info(message: str):
    """Display info message"""
    console.print(f"[bold blue]INFO: {message}[/bold blue]")

def show_step(step: int, total: int, message: str):
    """Display step progress"""
    console.print(f"[bold cyan]Step {step}/{total}:[/bold cyan] {message}")

def validate_contract_address(address: str) -> bool:
    """Validate Ethereum contract address format"""
    if not address:
        return False
    
    # Check if it's a valid hex string
    if not address.startswith('0x'):
        return False
    
    if len(address) != 42:  # 0x + 40 hex characters
        return False
    
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False

def validate_token_id(token_id: str) -> bool:
    """Validate token ID format"""
    try:
        int(token_id)
        return True
    except ValueError:
        return False

def validate_file_path(file_path: Path) -> bool:
    """Validate file path and permissions"""
    try:
        # Check if file exists
        if not file_path.exists():
            return False
        
        # Check if it's a file (not directory)
        if not file_path.is_file():
            return False
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return False
        
        # Check file size (prevent processing extremely large files)
        file_size = file_path.stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB limit
        if file_size > max_size:
            return False
        
        return True
    except (OSError, PermissionError):
        return False

def check_node_installation() -> bool:
    """Check if Node.js is installed and accessible"""
    try:
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False

def check_npm_installation() -> bool:
    """Check if npm is installed and accessible"""
    try:
        result = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False

def check_wallet_script_exists() -> bool:
    """Check if the wallet verification script exists"""
    script_path = Path("wallet/verify_owner.js")
    return script_path.exists() and script_path.is_file()

@app.command()
def verify(
    contract_address: str = typer.Option(..., "--contract", "-c", help="NFT contract address on Polygon"),
    token_id: str = typer.Option(..., "--token", "-t", help="NFT token ID"),
    wallet_address: Optional[str] = typer.Option(None, "--wallet", "-w", help="Wallet address (optional, will prompt for WalletConnect if not provided)")
):
    """Verify NFT ownership on Polygon network
    
    Examples:
        # Verify ownership with specific wallet
        avatar-everywhere verify --contract 0x1234... --token 123 --wallet 0xabcd...
        
        # Verify ownership using WalletConnect
        avatar-everywhere verify --contract 0x1234... --token 123
        
        # Using short options
        avatar-everywhere verify -c 0x1234... -t 123 -w 0xabcd...
    """
    
    console.print(Panel(
        Align.center("[bold cyan]NFT Ownership Verification[/bold cyan]"),
        border_style="bright_blue"
    ))
    
    # Validate inputs
    if not validate_contract_address(contract_address):
        show_error("Invalid contract address format")
        console.print("[dim]Contract address must be a valid Ethereum address (0x...)[/dim]")
        raise typer.Exit(1)
    
    if not validate_token_id(token_id):
        show_error("Invalid token ID format")
        console.print("[dim]Token ID must be a valid number[/dim]")
        raise typer.Exit(1)
    
    # Check Node.js installation
    if not check_node_installation():
        show_error("Node.js not found")
        console.print("[dim]Please install Node.js from: https://nodejs.org/[/dim]")
        raise typer.Exit(1)
    
    # Check wallet script
    if not check_wallet_script_exists():
        show_error("Wallet verification script not found")
        console.print("[dim]Please ensure wallet/verify_owner.js exists[/dim]")
        raise typer.Exit(1)
    
    # Display verification details
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Contract Address", contract_address)
    info_table.add_row("Token ID", token_id)
    if wallet_address:
        info_table.add_row("Wallet Address", wallet_address)
    else:
        info_table.add_row("Wallet Address", "[dim]Will use WalletConnect[/dim]")
    
    console.print(info_table)
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Checking NFT ownership...", total=100)
        
        try:
            # Simulate progress
            for i in range(0, 101, 20):
                progress.update(task, completed=i)
                progress.advance(task)
            
            # Run the Node.js verification script
            cmd = ["node", "wallet/verify_owner.js", contract_address, token_id]
            if wallet_address:
                cmd.append(wallet_address)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=Path.cwd(),
                timeout=60  # 60 second timeout
            )
            
            progress.update(task, completed=100)
            
            if result.returncode == 0:
                response = result.stdout.strip()
                if response == "true":
                    show_success("NFT ownership verified successfully")
                    console.print(Panel(
                        "[bold green]Verification Complete[/bold green]\n"
                        "Your wallet owns this NFT and you can proceed with conversion.",
                        border_style="bright_green"
                    ))
                    return True
                else:
                    show_error("NFT ownership verification failed")
                    console.print(Panel(
                        "[bold red]Verification Failed[/bold red]\n"
                        "Your wallet does not own this NFT. Please check the contract address and token ID.",
                        border_style="bright_red"
                    ))
                    return False
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                show_error(f"Verification error: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            show_error("Verification timeout - operation took too long")
            console.print("[dim]Please check your internet connection and try again[/dim]")
            return False
        except FileNotFoundError:
            show_error("Node.js not found")
            console.print("\n[dim]Install Node.js from: https://nodejs.org/[/dim]")
            return False
        except PermissionError:
            show_error("Permission denied when running verification script")
            console.print("[dim]Please check file permissions[/dim]")
            return False
        except OSError as e:
            show_error(f"System error during verification: {e}")
            return False
        except Exception as e:
            logger.error(f"Verification error: {e}")
            show_error(f"Unexpected error: {e}")
            return False

@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input avatar file (.glb or .vox)"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output VRM file path"),
    contract_address: Optional[str] = typer.Option(None, "--contract", "-c", help="NFT contract address for ownership verification"),
    token_id: Optional[str] = typer.Option(None, "--token", "-t", help="NFT token ID for ownership verification"),
    skip_verification: bool = typer.Option(False, "--skip-verify", help="Skip NFT ownership verification")
):
    """Convert Sandbox avatar to VRM format
    
    Examples:
        # Convert GLB file to VRM
        avatar-everywhere convert avatar.glb
        
        # Convert with custom output path
        avatar-everywhere convert avatar.glb --output my_avatar.vrm
        
        # Convert with NFT verification
        avatar-everywhere convert avatar.glb --contract 0x1234... --token 123
        
        # Convert VOX file to VRM
        avatar-everywhere convert model.vox --output model.vrm
        
        # Skip verification for testing
        avatar-everywhere convert avatar.glb --skip-verify
        
        # Using short options
        avatar-everywhere convert avatar.glb -o my_avatar.vrm -c 0x1234... -t 123
    """
    
    console.print(Panel(
        Align.center("[bold cyan]Avatar Conversion[/bold cyan]"),
        border_style="bright_blue"
    ))
    
    # Validate input file
    if not validate_file_path(input_file):
        show_error(f"Input file '{input_file}' is invalid or inaccessible")
        console.print("\n[dim]Please check the file path, permissions, and file size[/dim]")
        raise typer.Exit(1)
    
    if input_file.suffix.lower() not in ['.glb', '.vox']:
        show_error(f"Unsupported file format '{input_file.suffix}'. Use .glb or .vox files.")
        console.print("\n[dim]Supported formats: .glb, .vox[/dim]")
        raise typer.Exit(1)
    
    # Set default output file
    if output_file is None:
        output_file = input_file.with_suffix('.vrm')
    
    # Check output directory permissions
    output_dir = output_file.parent
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            show_error(f"Cannot write to output directory: {output_dir}")
            raise typer.Exit(1)
    except (OSError, PermissionError) as e:
        show_error(f"Cannot create output directory: {e}")
        raise typer.Exit(1)
    
    # Display conversion details
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Input File", str(input_file))
    info_table.add_row("Output File", str(output_file))
    info_table.add_row("File Format", input_file.suffix.upper())
    info_table.add_row("File Size", f"{input_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    console.print(info_table)
    console.print()
    
    # NFT ownership verification
    if not skip_verification:
        if contract_address and token_id:
            show_step(1, 2, "Verifying NFT Ownership")
            if not validate_contract_address(contract_address):
                show_error("Invalid contract address format")
                raise typer.Exit(1)
            if not validate_token_id(token_id):
                show_error("Invalid token ID format")
                raise typer.Exit(1)
            
            if not verify(contract_address, token_id, wallet_address=None):
                if not Confirm.ask("NFT verification failed. Continue anyway?"):
                    raise typer.Exit(1)
        else:
            show_warning("NFT verification skipped (no contract/token provided)")
            if not Confirm.ask("Continue without NFT verification?"):
                raise typer.Exit(1)
    else:
        show_info("NFT verification skipped")
    
    # Avatar conversion
    show_step(2, 2, "Converting Avatar")
    
    try:
        converter = SandboxToVRMConverter()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Converting avatar...", total=100)
            
            # Simulate conversion progress
            for i in range(0, 101, 25):
                progress.update(task, completed=i)
                progress.advance(task)
            
            success = converter.convert(input_file, output_file)
            
            progress.update(task, completed=100)
            
            if success:
                show_success(f"Avatar successfully converted to {output_file}")
                
                # Display file info
                if output_file.exists():
                    file_size = output_file.stat().st_size / 1024 / 1024  # MB
                    console.print(f"[dim]Output file size: {file_size:.2f} MB[/dim]")
                
                console.print(Panel(
                    "[bold green]Conversion Complete[/bold green]\n"
                    "Your VRM file is ready to import into Unity with UniVRM.",
                    border_style="bright_green"
                ))
                
            else:
                show_error("Avatar conversion failed")
                raise typer.Exit(1)
                
    except ImportError as e:
        show_error(f"Missing dependency: {e}")
        console.print("\n[dim]Please install required dependencies: pip install -r requirements.txt[/dim]")
        raise typer.Exit(1)
    except PermissionError as e:
        show_error(f"Permission denied: {e}")
        console.print("\n[dim]Please check file permissions[/dim]")
        raise typer.Exit(1)
    except OSError as e:
        show_error(f"System error during conversion: {e}")
        raise typer.Exit(1)
    except MemoryError as e:
        show_error("Insufficient memory for conversion")
        console.print("\n[dim]Please close other applications and try again[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Error during conversion: {e}")
        console.print("\n[dim]Please check the input file and try again[/dim]")
        raise typer.Exit(1)

@app.command()
def info(
    file_path: Path = typer.Argument(..., help="Avatar file to analyze")
):
    """Show information about an avatar file
    
    Examples:
        # Analyze a GLB file
        avatar-everywhere info avatar.glb
        
        # Analyze a VOX file
        avatar-everywhere info model.vox
        
        # Analyze with full path
        avatar-everywhere info /path/to/avatar.glb
    """
    
    console.print(Panel(
        Align.center("[bold cyan]File Analysis[/bold cyan]"),
        border_style="bright_blue"
    ))
    
    if not validate_file_path(file_path):
        show_error(f"File '{file_path}' is invalid or inaccessible")
        raise typer.Exit(1)
    
    # Basic file info
    file_info = Table(title="File Information", show_header=True, header_style="bold cyan")
    file_info.add_column("Property", style="cyan")
    file_info.add_column("Value", style="white")
    
    try:
        stat = file_path.stat()
        file_info.add_row("File Path", str(file_path))
        file_info.add_row("File Format", file_path.suffix.upper())
        file_info.add_row("File Size", f"{stat.st_size / 1024 / 1024:.2f} MB")
        file_info.add_row("Last Modified", str(stat.st_mtime))
        
        console.print(file_info)
        console.print()
        
        # Additional format-specific info
        if file_path.suffix.lower() == '.glb':
            try:
                converter = SandboxToVRMConverter()
                info = converter.analyze_glb(file_path)
                
                if info:
                    analysis_table = Table(title="GLB Analysis", show_header=True, header_style="bold cyan")
                    analysis_table.add_column("Property", style="cyan")
                    analysis_table.add_column("Value", style="white")
                    
                    analysis_table.add_row("Mesh Count", str(info.get('mesh_count', 'Unknown')))
                    analysis_table.add_row("Material Count", str(info.get('material_count', 'Unknown')))
                    analysis_table.add_row("Has Skeleton", "Yes" if info.get('has_skeleton') else "No")
                    analysis_table.add_row("Texture Count", str(info.get('texture_count', 'Unknown')))
                    analysis_table.add_row("Node Count", str(info.get('node_count', 'Unknown')))
                    
                    console.print(analysis_table)
            except ImportError as e:
                show_warning(f"Missing dependency for GLB analysis: {e}")
            except Exception as e:
                show_warning(f"Could not analyze GLB file: {e}")
        
        elif file_path.suffix.lower() == '.vox':
            console.print(Panel(
                "[bold yellow]VOX Analysis[/bold yellow]\n"
                "VOX file analysis is experimental. Basic file information shown above.",
                border_style="bright_yellow"
            ))
            
    except OSError as e:
        show_error(f"Error reading file: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Unexpected error during analysis: {e}")
        raise typer.Exit(1)

@app.command()
def list_requirements():
    """List system requirements and dependencies
    
    Examples:
        # Check all requirements
        avatar-everywhere list-requirements
        
        # Check requirements status
        avatar-everywhere list-requirements
    """
    
    console.print(Panel(
        Align.center("[bold cyan]System Requirements[/bold cyan]"),
        border_style="bright_blue"
    ))
    
    # System requirements table
    requirements = [
        ("Python", "3.11+", "OK" if sys.version_info >= (3, 11) else "FAIL"),
        ("Node.js", "16+", "OK" if check_node_installation() else "FAIL"),
        ("npm", "Latest", "OK" if check_npm_installation() else "FAIL"),
        ("UniVRM", "0.121+", "Install in Unity"),
        ("Unity", "2022 LTS", "For testing VRM files")
    ]
    
    req_table = Table(title="System Requirements", show_header=True, header_style="bold cyan")
    req_table.add_column("Component", style="cyan")
    req_table.add_column("Version", style="white")
    req_table.add_column("Status", style="white")
    
    for name, version, status in requirements:
        req_table.add_row(name, version, status)
    
    console.print(req_table)
    console.print()
    
    # Python dependencies
    console.print("[bold cyan]Python Dependencies:[/bold cyan]")
    deps = [
        "typer",
        "rich", 
        "pygltflib",
        "trimesh",
        "numpy",
        "pillow"
    ]
    
    for dep in deps:
        console.print(f"  • {dep}")
    
    console.print()
    
    # Node.js dependencies
    console.print("[bold cyan]Node.js Dependencies:[/bold cyan]")
    node_deps = [
        "ethers",
        "@walletconnect/client"
    ]
    
    for dep in node_deps:
        console.print(f"  • {dep}")
    
    console.print()
    
    # Installation instructions
    console.print(Panel(
        "[bold green]Installation Tips:[/bold green]\n"
        "• Install Python dependencies: pip install -r requirements.txt\n"
        "• Install Node.js dependencies: npm install\n"
        "• For Unity testing, install UniVRM 0.121+",
        border_style="bright_green"
    ))

if __name__ == "__main__":
    app()