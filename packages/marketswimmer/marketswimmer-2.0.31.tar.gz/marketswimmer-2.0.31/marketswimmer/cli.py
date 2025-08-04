"""
MarketSwimmer CLI - A modern command-line interface for financial analysis
Built with Typer for an excellent user experience
"""

import typer
from typing import Optional
from pathlib import Path
import os
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, TextColumn
import time

# Initialize Rich console for beautiful output
console = Console()

# Create the main Typer app
app = typer.Typer(
    name="marketswimmer",
    help="🏊 MarketSwimmer - Warren Buffett's Owner Earnings Analysis Tool",
    epilog="For more help on a specific command, use: marketswimmer COMMAND --help",
    rich_markup_mode="rich"
)

def check_python_executable():
    """Find the best Python executable to use."""
    python_paths = [
        r"C:\Users\jerem\AppData\Local\Programs\Python\Python312\python.exe",
        "python",
        "python3",
        "py"
    ]
    
    for python_path in python_paths:
        try:
            result = subprocess.run([python_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return python_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return "python"  # fallback

def run_python_script(script_name: str, args: list = None):
    """Run a Python script with the best available Python executable."""
    python_exe = check_python_executable()
    cmd = [python_exe, script_name]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        console.print(f"[red]Error running {script_name}: {e}[/red]")
        return False

@app.command()
def gui(
    safe_mode: bool = typer.Option(False, "--safe", "-s", help="Check for existing processes before launching"),
    test_mode: bool = typer.Option(False, "--test", "-t", help="Launch in test mode (no logging)")
):
    """
    Launch the MarketSwimmer GUI application
    
    The GUI provides an intuitive interface for:
    - Downloading financial data
    - Calculating owner earnings
    - Generating beautiful charts
    """
    with console.status("[bold green]Launching MarketSwimmer GUI...", spinner="dots"):
        time.sleep(1)  # Brief delay for visual feedback
    
    if safe_mode:
        console.print("[yellow]🔍 Checking for existing GUI processes...[/yellow]")
        # Check for existing processes (simplified)
        try:
            result = subprocess.run(['tasklist', '/FI', 'WINDOWTITLE eq MarketSwimmer*'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                console.print("[red]WARNING: MarketSwimmer GUI is already running![/red]")
                console.print("Please close existing windows before starting a new one.")
                raise typer.Exit(1)
        except:
            pass  # Continue if check fails
    
    console.print("[green]>> Starting MarketSwimmer GUI...[/green]")
    
    try:
        # Import and run the GUI module
        from .gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        console.print(f"[red]ERROR: Failed to import GUI module: {e}[/red]")
        console.print("[yellow]NOTE: Make sure PyQt6 is installed: pip install PyQt6[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]ERROR: Failed to launch GUI: {e}[/red]")
        raise typer.Exit(1)
    
    console.print("[green]>> GUI closed successfully.[/green]")

@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., BRK.B, AAPL, TSLA)"),
    charts_only: bool = typer.Option(False, "--charts-only", "-c", help="Only generate charts from existing data"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-download even if data exists")
):
    """
    Analyze a stock ticker using Warren Buffett's Owner Earnings method
    
    This command will:
    1. Download the latest financial data
    2. Calculate owner earnings (annual & quarterly)
    3. Generate comprehensive charts and analysis
    4. Save results to organized directories
    
    Examples:
    - marketswimmer analyze BRK.B
    - marketswimmer analyze AAPL --charts-only
    - marketswimmer analyze TSLA --force
    """
    ticker = ticker.upper()
    
    # Handle special cases
    if ticker == "BRKB":
        ticker = "BRK.B"
    
    console.print(f"[bold blue]>> Analyzing {ticker}...[/bold blue]")
    
    if charts_only:
        console.print("[yellow]>> Generating charts from existing data...[/yellow]")
        from .core.analysis import visualize_existing_data
        success = visualize_existing_data()
    else:
        console.print(f"[cyan]>> Running complete analysis for {ticker}...[/cyan]")
        from .core.analysis import analyze_ticker_workflow
        success = analyze_ticker_workflow(ticker, force)
    
    if success is True:
        console.print("\n[green]>> Analysis complete![/green]")
        console.print("Check these directories for results:")
        console.print("  >> [bold]data/[/bold] - CSV files with financial analysis")
        console.print("  >> [bold]charts/[/bold] - PNG charts and visualizations")
        console.print("  >> [bold]downloaded_files/[/bold] - Raw Excel data")
    elif success == "guidance_provided":
        console.print("\n[blue]>> Guidance provided above. Follow the steps to complete your analysis.[/blue]")
    else:
        console.print("[red]ERROR: Analysis failed. Check the output above for details.[/red]")
        raise typer.Exit(1)

@app.command()
def status():
    """
    Show MarketSwimmer project status and health check
    """
    console.print("[bold blue]MarketSwimmer Project Status[/bold blue]\n")
    
    # Check directories
    directories = ["data", "charts", "downloaded_files", "logs", "scripts"]
    dir_table = Table(title=">> Directory Structure")
    dir_table.add_column("Directory", style="cyan")
    dir_table.add_column("Status", style="green")
    dir_table.add_column("Files", justify="right")
    
    for directory in directories:
        if Path(directory).exists():
            file_count = len(list(Path(directory).glob("*")))
            dir_table.add_row(directory, ">> Exists", str(file_count))
        else:
            dir_table.add_row(directory, ">> Missing", "0")
    
    console.print(dir_table)
    console.print()
    
    # Check Python installation
    python_exe = check_python_executable()
    console.print(f">> Python executable: [cyan]{python_exe}[/cyan]")
    
    try:
        result = subprocess.run([python_exe, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f">> Python version: [green]{result.stdout.strip()}[/green]")
        else:
            console.print("[red]ERROR: Python check failed[/red]")
    except:
        console.print("[red]ERROR: Python not accessible[/red]")
    
    # Check for package modules
    console.print("\n>> Package Modules:")
    modules_to_check = [
        ("marketswimmer.core.owner_earnings", "OwnerEarningsCalculator"),
        ("marketswimmer.core.analysis", "analyze_ticker_workflow"),
        ("marketswimmer.visualization", "OwnerEarningsVisualizer"),
        ("marketswimmer.gui.main_window", "MarketSwimmerGUI"),
    ]
    
    for module_name, class_name in modules_to_check:
        try:
            __import__(module_name)
            console.print(f"  >> {module_name}")
        except ImportError as e:
            console.print(f"  ERROR: {module_name} [red](import error: {e})[/red]")

@app.command()
def quick_start():
    """
    >> Quick start guide for new users
    """
    console.print(Panel.fit(
        "[bold blue]>> Welcome to MarketSwimmer![/bold blue]\n\n"
        "MarketSwimmer analyzes stocks using Warren Buffett's 'Owner Earnings' method.\n"
        "This approach focuses on the actual cash a business generates for its owners.",
        title="Welcome",
        border_style="blue"
    ))
    
    console.print("\n[bold green]>> Quick Start Steps:[/bold green]")
    
    steps = [
        ("1.", "Launch GUI", "marketswimmer gui", "Start with the user-friendly interface"),
        ("2.", "Analyze a Stock", "marketswimmer analyze AAPL", "Analyze Apple's owner earnings"),
        ("3.", "View Results", "Check data/ and charts/ folders", "See your analysis results"),
        ("4.", "Try More", "marketswimmer analyze BRK.B", "Analyze Berkshire Hathaway")
    ]
    
    for step, title, command, description in steps:
        console.print(f"\n{step} [bold]{title}[/bold]")
        console.print(f"   Command: [cyan]{command}[/cyan]")
        console.print(f"   {description}")
    
    console.print("\n[bold yellow]>> Pro Tips:[/bold yellow]")
    console.print("• Use [cyan]--help[/cyan] with any command for detailed options")
    console.print("• Check [cyan]marketswimmer status[/cyan] if you encounter issues")
    console.print("• The GUI is perfect for beginners, CLI for power users")
    console.print("• All data is saved locally - no cloud dependencies")

@app.command()
def examples():
    """
    >> Show practical examples and use cases
    """
    console.print("[bold blue]>> MarketSwimmer Examples & Use Cases[/bold blue]\n")
    
    # Create examples table
    examples_table = Table(title=">> Common Commands")
    examples_table.add_column("Use Case", style="cyan", width=25)
    examples_table.add_column("Command", style="green", width=35)
    examples_table.add_column("Description", width=30)
    
    examples = [
        ("First-time user", "marketswimmer quick-start", "Get oriented with the tool"),
        ("Launch GUI", "marketswimmer gui", "Use the visual interface"),
        ("Safe GUI launch", "marketswimmer gui --safe", "Check for existing processes"),
        ("Test mode GUI", "marketswimmer gui --test", "Launch without logging"),
        ("Analyze Berkshire", "marketswimmer analyze BRK.B", "Warren Buffett's company"),
        ("Analyze Apple", "marketswimmer analyze AAPL", "Tech giant analysis"),
        ("Analyze Tesla", "marketswimmer analyze TSLA", "EV company analysis"),
        ("Charts only", "marketswimmer analyze AAPL -c", "Skip download, make charts"),
        ("Force refresh", "marketswimmer analyze AAPL -f", "Re-download all data"),
        ("Check health", "marketswimmer status", "Verify installation"),
        ("Get help", "marketswimmer --help", "Show all commands"),
    ]
    
    for use_case, command, description in examples:
        examples_table.add_row(use_case, command, description)
    
    console.print(examples_table)
    
    console.print("\n[bold green]>> Recommended Workflow:[/bold green]")
    workflow = [
        "Start with the GUI to get familiar: [cyan]marketswimmer gui[/cyan]",
        "Try analyzing a well-known stock: [cyan]marketswimmer analyze BRK.B[/cyan]", 
        "Check the generated files in [bold]data/[/bold] and [bold]charts/[/bold]",
        "Use the CLI for batch processing multiple stocks",
        "Run [cyan]marketswimmer status[/cyan] if you encounter any issues"
    ]
    
    for i, step in enumerate(workflow, 1):
        console.print(f"{i}. {step}")

@app.command()
def version():
    """
    >> Show version and system information
    """
    console.print("[bold blue]>> MarketSwimmer Version Information[/bold blue]\n")
    
    console.print("Version: [green]2.0.0[/green] (CLI Edition)")
    console.print("Built with: [cyan]Typer + Rich[/cyan]")
    console.print("Purpose: [yellow]Warren Buffett's Owner Earnings Analysis[/yellow]")
    console.print(f"Working Directory: [blue]{Path.cwd()}[/blue]")
    
    # System info
    console.print(f"\nSystem: [cyan]{sys.platform}[/cyan]")
    console.print(f"Python: [cyan]{sys.version.split()[0]}[/cyan]")
    
    # Check for key dependencies
    try:
        import pandas
        console.print(f"Pandas: [green]{pandas.__version__}[/green]")
    except ImportError:
        console.print("Pandas: [red]Not installed[/red]")
    
    try:
        import matplotlib
        console.print(f"Matplotlib: [green]{matplotlib.__version__}[/green]")
    except ImportError:
        console.print("Matplotlib: [red]Not installed[/red]")

@app.command()
def calculate(
    ticker: str = typer.Option(..., "--ticker", "-t", help="Stock ticker symbol"),
    force: bool = typer.Option(False, "--force", "-f", help="Force recalculation")
):
    """
    🧮 Calculate owner earnings for a specific ticker
    
    This command calculates Warren Buffett's owner earnings from financial data.
    Requires financial data to be available in the data/ directory.
    """
    console.print(f"[bold blue]🧮 Calculating owner earnings for {ticker.upper()}...[/bold blue]")
    
    try:
        from .core.owner_earnings import OwnerEarningsCalculator
        
        # This is a placeholder - would need to implement the full calculation workflow
        console.print(f"[yellow]WARNING: Owner earnings calculation not yet fully implemented.[/yellow]")
        console.print(f"[yellow]NOTE: To calculate owner earnings for {ticker.upper()}:[/yellow]")
        console.print("  1. Ensure you have downloaded financial data")
        console.print("  2. Place Excel files in downloaded_files/ directory")
        console.print("  3. The calculation module is available for development")
        
        console.print(f"[green]NOTE: Module loaded: OwnerEarningsCalculator available[/green]")
        
    except ImportError as e:
        console.print(f"[red]ERROR: Cannot import OwnerEarningsCalculator: {e}[/red]")

@app.command()
def visualize(
    ticker: str = typer.Option(None, "--ticker", "-t", help="Stock ticker symbol"),
    all_data: bool = typer.Option(False, "--all", "-a", help="Visualize all available data")
):
    """
    Create visualizations from calculated owner earnings data
    
    This command generates charts and graphs from owner earnings calculations.
    Requires calculated data to be available in the data/ directory.
    """
    if ticker:
        console.print(f"[bold blue]>> Creating visualizations for {ticker.upper()}...[/bold blue]")
    else:
        console.print("[bold blue]>> Creating visualizations from available data...[/bold blue]")
    
    try:
        # Check if visualization module is available
        try:
            from .visualization.charts import main as visualization_main
            visualization_available = True
        except ImportError:
            visualization_available = False
            
        if not visualization_available:
            console.print(f"[red]ERROR: Visualization dependencies not available[/red]")
            console.print(f"[yellow]NOTE: Install with: pip install matplotlib PyQt6[/yellow]")
            return
            
        console.print(f"[green]>> Running visualization for {ticker or 'available data'}...[/green]")
        
        # Ensure we're in the right directory for data files
        import os
        original_dir = os.getcwd()
        
        try:
            # Call the visualization main function
            visualization_main()
            
            console.print(f"[green]>> Visualization completed successfully![/green]")
            console.print("Check the charts/ directory for generated visualizations")
        finally:
            # Always restore original directory
            os.chdir(original_dir)
        
    except Exception as e:
        console.print(f"[red]ERROR: Error during visualization: {e}[/red]")

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    app()
