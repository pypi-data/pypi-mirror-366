"""
Core analysis functions for MarketSwimmer.
This module provides the main analysis workflow that replaces the standalone scripts.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()

def clean_ticker_for_filename(ticker: str) -> str:
    """Clean ticker symbol for use in filenames."""
    return ticker.replace('.', '_').upper()

def analyze_ticker_workflow(ticker: str, force: bool = False) -> bool:
    """
    Run the complete analysis workflow for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        force: Force re-download even if data exists
        
    Returns:
        bool: True if analysis completed successfully
    """
    try:
        console.print(f"🚀 Starting complete analysis for {ticker}...")
        console.print("This will run the full analysis pipeline:")
        console.print("  1. Download financial data")
        console.print("  2. Calculate owner earnings")
        console.print("  3. Create visualizations")
        console.print("Please wait...")
        
        # For now, let's provide a helpful message until we implement the full workflow
        console.print(f"[yellow]⚠️ Full analysis workflow not yet implemented in package version.[/yellow]")
        console.print(f"[yellow]📝 To analyze {ticker}, please:[/yellow]")
        console.print(f"  1. Visit: https://stockrow.com/vector/exports/financials/{ticker.upper()}")
        console.print(f"  2. Download the Excel file")
        console.print(f"  3. Run: ms calculate --ticker {ticker}")
        console.print(f"  4. Run: ms visualize --ticker {ticker}")
        
        # Return a special status to indicate "guidance provided" rather than "failed"
        return "guidance_provided"  # Not implemented yet, but guidance given
        
    except Exception as e:
        console.print(f"[red]❌ Error during analysis: {e}[/red]")
        return False

def visualize_existing_data() -> bool:
    """
    Generate visualizations from existing data.
    
    Returns:
        bool: True if visualization completed successfully
    """
    try:
        console.print("📊 Generating charts from existing data...")
        
        # For now, provide a helpful message
        console.print("[yellow]⚠️ Visualization from existing data not yet implemented in package version.[/yellow]")
        console.print("[yellow]📝 To create visualizations:[/yellow]")
        console.print("  1. Ensure you have data files in the data/ directory")
        console.print("  2. Run: ms visualize")
        
        return "guidance_provided"  # Not implemented yet, but guidance given
        
    except Exception as e:
        console.print(f"[red]❌ Error during visualization: {e}[/red]")
        return False
