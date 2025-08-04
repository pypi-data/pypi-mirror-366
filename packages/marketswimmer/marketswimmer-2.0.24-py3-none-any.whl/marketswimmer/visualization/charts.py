import pandas as pd
import matplotlib
# Set non-interactive backend for headless operation - must be before pyplot import
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Ensure matplotlib is in non-interactive mode
plt.ioff()
import seaborn as sns
import numpy as np
from datetime import datetime
import os
import glob

def setup_plotting_style():
    """Set up a professional plotting style."""
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9

def detect_ticker_symbol():
    """Detect the ticker symbol from the most recent XLSX file."""
    try:
        # Check downloaded_files folder for recent files
        xlsx_files = glob.glob("./downloaded_files/*.xlsx")
        if xlsx_files:
            # Get the most recent file
            latest_file = max(xlsx_files, key=os.path.getmtime)
            filename = os.path.basename(latest_file)
            
            # Extract ticker from filename like "financials_export_brkb_2025_08_02_221804.xlsx"
            if 'financials_export_' in filename:
                parts = filename.split('_')
                if len(parts) >= 3:
                    ticker = parts[2].upper()
                    # Handle special cases like BRK.B
                    if ticker == 'BRKB':
                        ticker = 'BRK.B'
                    return ticker
        
        # Fallback: try to detect from data patterns
        return "TICKER"
    except:
        return "TICKER"

def load_data(ticker=None):
    """Load both annual and quarterly CSV data for a specific ticker."""
    try:
        import glob
        import os
        
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        
        # Use provided ticker or detect it
        if not ticker:
            ticker = detect_ticker_symbol()
        print(f"[DEBUG] Using ticker: {ticker}")
        
        # Clean ticker for filename
        clean_ticker = ticker.lower().replace('.', '') if ticker and ticker != "TICKER" else None
        
        # Search for annual data files - prioritize specific ticker files
        annual_files = []
        if clean_ticker:
            specific_patterns = [
                f'data/owner_earnings_annual_{clean_ticker}.csv',
                f'owner_earnings_annual_{clean_ticker}.csv',
                f'./data/owner_earnings_annual_{clean_ticker}.csv',
                f'../data/owner_earnings_annual_{clean_ticker}.csv',
                f'marketswimmer/gui/data/owner_earnings_annual_{clean_ticker}.csv'
            ]
            
            for pattern in specific_patterns:
                files = glob.glob(pattern)
                if files:
                    annual_files.extend(files)
                    print(f"[DEBUG] Found ticker-specific files with pattern '{pattern}': {files}")
                    break  # Use first match for specific ticker
        
        # If no specific files found, search for any files
        if not annual_files:
            general_patterns = [
                'data/owner_earnings_annual_*.csv',
                'owner_earnings_annual_*.csv', 
                './data/owner_earnings_annual_*.csv',
                '../data/owner_earnings_annual_*.csv',
                'marketswimmer/gui/data/owner_earnings_annual_*.csv'
            ]
            
            for pattern in general_patterns:
                files = glob.glob(pattern)
                if files:
                    annual_files.extend(files)
                    print(f"[DEBUG] General pattern '{pattern}' found: {files}")
        
        # Remove duplicates and sort by modification time (most recent first)
        annual_files = list(set(annual_files))
        if annual_files:
            annual_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Fallback to old filename format
        if not annual_files:
            fallback_patterns = [
                'data/owner_earnings_financials_annual.csv',
                'owner_earnings_financials_annual.csv'
            ]
            for pattern in fallback_patterns:
                files = glob.glob(pattern)
                annual_files.extend(files)
        
        if not annual_files:
            print("[ERROR] No annual data files found in any location")
            print(f"[DEBUG] Current directory contents: {os.listdir('.')}")
            if os.path.exists('data'):
                print(f"[DEBUG] Data directory contents: {os.listdir('data')}")
            return None, None
        
        annual_path = annual_files[0]  # Use the most recent file
        print(f"[DEBUG] Found annual files: {annual_files}")
        print(f"[DEBUG] Using most recent annual file: {annual_path}")
        
        annual_df = pd.read_csv(annual_path)
        print(f"[OK] Loaded annual data: {len(annual_df)} years from {annual_path}")
        
        # Search for quarterly data files - prioritize specific ticker files
        quarterly_files = []
        if clean_ticker:
            specific_patterns = [
                f'data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'owner_earnings_quarterly_{clean_ticker}.csv',
                f'./data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'../data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'marketswimmer/gui/data/owner_earnings_quarterly_{clean_ticker}.csv'
            ]
            
            for pattern in specific_patterns:
                files = glob.glob(pattern)
                if files:
                    quarterly_files.extend(files)
                    print(f"[DEBUG] Found quarterly ticker-specific files with pattern '{pattern}': {files}")
                    break  # Use first match for specific ticker
        
        # If no specific files found, search for any quarterly files
        if not quarterly_files:
            general_patterns = [
                'data/owner_earnings_quarterly_*.csv',
                'owner_earnings_quarterly_*.csv',
                './data/owner_earnings_quarterly_*.csv',
                '../data/owner_earnings_quarterly_*.csv',
                'marketswimmer/gui/data/owner_earnings_quarterly_*.csv'
            ]
            
            for pattern in general_patterns:
                files = glob.glob(pattern)
                if files:
                    quarterly_files.extend(files)
                    print(f"[DEBUG] Quarterly general pattern '{pattern}' found: {files}")
        
        # Remove duplicates and sort by modification time
        quarterly_files = list(set(quarterly_files))
        if quarterly_files:
            quarterly_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Fallback to old filename format
        if not quarterly_files:
            fallback_patterns = [
                'data/owner_earnings_financials_quarterly.csv',
                'owner_earnings_financials_quarterly.csv'
            ]
            for pattern in fallback_patterns:
                files = glob.glob(pattern)
                quarterly_files.extend(files)
            
        if not quarterly_files:
            print("[ERROR] No quarterly data files found in any location")
            print(f"[DEBUG] Searched quarterly patterns for ticker: {clean_ticker}")
            return None, None
        
        quarterly_path = quarterly_files[0]  # Use the most recent file
        print(f"[DEBUG] Found quarterly files: {quarterly_files}")
        print(f"[DEBUG] Using most recent quarterly file: {quarterly_path}")
        quarterly_df = pd.read_csv(quarterly_path)
        print(f"[OK] Loaded quarterly data: {len(quarterly_df)} quarters from {quarterly_path}")
        
        return annual_df, quarterly_df
        
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return None, None
        print(f"[DEBUG] Found quarterly files: {quarterly_files}")
        print(f"[DEBUG] Using most recent quarterly file: {quarterly_path}")
        quarterly_df = pd.read_csv(quarterly_path)
        print(f"[OK] Loaded quarterly data: {len(quarterly_df)} quarters from {quarterly_path}")
        
        return annual_df, quarterly_df
    
    except FileNotFoundError as e:
        print(f"[ERROR] Error loading CSV files: {e}")
        print("[INFO] Make sure to run owner_earnings_fixed.py first to generate the CSV files")
        print("[INFO] CSV files should be in the 'data/' directory")
        return None, None

def prepare_quarterly_data(df):
    """Prepare quarterly data for plotting."""
    # Convert period to datetime for better plotting
    df = df.copy()
    
    print(f"[DEBUG] Raw quarterly data shape: {df.shape}")
    print(f"[DEBUG] Period column sample values: {df['Period'].head().tolist()}")
    print(f"[DEBUG] Period column data types: {df['Period'].dtype}")
    
    # Ensure Period column is string type for string operations
    df['Period'] = df['Period'].astype(str)
    print(f"[DEBUG] Period column after string conversion: {df['Period'].head().tolist()}")
    
    # Check if this is actually annual data masquerading as quarterly data
    period_values = df['Period'].unique()
    is_annual_data = all(len(p) == 4 and p.isdigit() for p in period_values)
    
    if is_annual_data:
        print(f"[WARNING] Detected annual data in quarterly file - treating as annual")
        # This is annual data, so just parse as years
        df['year'] = df['Period'].astype(int)
        df['quarter'] = 2  # Use Q2 as a middle-of-year approximation
        df['date'] = pd.to_datetime(df[['year']].assign(month=7, day=1))  # July 1st
        print(f"[DEBUG] Converted annual-as-quarterly data: {df['date'].head().tolist()}")
    else:
        # Extract year and quarter from Period (format should be like "2024Q1")
        try:
            # Handle different Period formats more robustly
            print(f"[DEBUG] Attempting to parse quarterly Period values: {df['Period'].unique()}")
            
            if df['Period'].str.contains('Q').any():
                # Format like "2024Q1"
                df['year'] = df['Period'].str[:4].astype(int)
                df['quarter'] = df['Period'].str[-1].astype(int)
            elif df['Period'].str.contains('-').any():
                # Format like "2024-Q1" or "Q1-2024"
                # Try to extract 4-digit year and 1-digit quarter
                year_pattern = df['Period'].str.extract(r'(\d{4})')
                quarter_pattern = df['Period'].str.extract(r'Q(\d)')
                df['year'] = year_pattern[0].astype(int)
                df['quarter'] = quarter_pattern[0].astype(int)
            else:
                # Fallback: try to parse as much as possible
                print(f"[WARNING] Unknown Period format, attempting generic parsing")
                # Try to extract any 4-digit number as year
                year_match = df['Period'].str.extract(r'(\d{4})')
                if not year_match[0].isna().all():
                    df['year'] = year_match[0].astype(int)
                else:
                    df['year'] = 2024  # Default year
                
                # Try to extract quarter number
                quarter_match = df['Period'].str.extract(r'(\d)')
                if not quarter_match[0].isna().all():
                    df['quarter'] = quarter_match[0].astype(int)
                else:
                    df['quarter'] = 1  # Default quarter
            
            print(f"[DEBUG] Extracted years: {df['year'].tolist()}")
            print(f"[DEBUG] Extracted quarters: {df['quarter'].tolist()}")
            
            # Validate extracted values
            if df['year'].isna().any() or df['quarter'].isna().any():
                raise ValueError("Failed to extract valid year/quarter values")
            if (df['quarter'] < 1).any() or (df['quarter'] > 4).any():
                print(f"[WARNING] Invalid quarter values found: {df['quarter'].unique()}")
                df['quarter'] = df['quarter'].clip(1, 4)  # Clamp to valid range
                
        except Exception as e:
            print(f"[ERROR] Failed to extract year/quarter: {e}")
            print(f"[DEBUG] Period values causing issues: {df['Period'].unique()}")
            # Create fallback values to prevent complete failure
            df['year'] = 2024
            df['quarter'] = 1
            print(f"[WARNING] Using fallback year/quarter values")
        
        # Create a proper date column
        try:
            df['date'] = pd.to_datetime(df[['year']].assign(month=(df['quarter']-1)*3+1, day=1))
            print(f"[DEBUG] Successfully created date column: {df['date'].head().tolist()}")
        except Exception as e:
            print(f"[ERROR] Failed to create date column: {e}")
            print(f"[DEBUG] Year values: {df['year'].tolist()}")
            print(f"[DEBUG] Quarter values: {df['quarter'].tolist()}")
            # Create a simple date column based on just the year
            df['date'] = pd.to_datetime(df['year'], format='%Y')
            print(f"[WARNING] Using year-only dates: {df['date'].head().tolist()}")
    
    # Convert to millions for better readability - use the actual CSV column names
    financial_cols_map = {
        'Net Income': 'net_income',
        'Depreciation': 'depreciation', 
        'CapEx': 'capex',
        'Working Capital Change': 'working_capital_change',
        'Owner Earnings': 'owner_earnings'
    }
    
    for csv_col, standard_col in financial_cols_map.items():
        if csv_col in df.columns:
            df[f'{standard_col}_millions'] = df[csv_col] / 1_000_000
    
    # Sort by date for proper chronological plotting
    df = df.sort_values('date')
    
    return df

def prepare_annual_data(df):
    """Prepare annual data for plotting with robust error handling."""
    df = df.copy()
    
    print(f"[DEBUG] Annual Period column: {df['Period'].head().tolist()}")
    print(f"[DEBUG] Annual Period dtypes: {df['Period'].dtype}")
    
    # Try different date parsing approaches
    try:
        # First try: assume it's just years like "2024"
        df['date'] = pd.to_datetime(df['Period'], format='%Y')
        print(f"[DEBUG] Successfully parsed annual dates as years")
    except ValueError as e:
        print(f"[DEBUG] Year format failed: {e}")
        try:
            # Second try: generic datetime parsing
            df['date'] = pd.to_datetime(df['Period'], errors='coerce')
            print(f"[DEBUG] Successfully parsed annual dates with generic parser")
        except Exception as e2:
            print(f"[ERROR] All annual date parsing failed: {e2}")
            print(f"[DEBUG] Problematic Period values: {df['Period'].unique()}")
            # Create a dummy date column to prevent crashes
            df['date'] = pd.to_datetime('2020-01-01')
            print(f"[WARNING] Using dummy dates for annual data")
    
    # Convert to millions for better readability - use the actual CSV column names
    financial_cols_map = {
        'Net Income': 'net_income',
        'Depreciation': 'depreciation', 
        'CapEx': 'capex',
        'Working Capital Change': 'working_capital_change',
        'Owner Earnings': 'owner_earnings'
    }
    
    for csv_col, standard_col in financial_cols_map.items():
        if csv_col in df.columns:
            df[f'{standard_col}_millions'] = df[csv_col] / 1_000_000
    
    return df

def create_owner_earnings_comparison(annual_df, quarterly_df, ticker):
    """Create a comparison chart of annual vs quarterly owner earnings."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Get date range for dynamic titles
    annual_start = annual_df['Period'].min()
    annual_end = annual_df['Period'].max()
    quarterly_start = quarterly_df['Period'].min() 
    quarterly_end = quarterly_df['Period'].max()
    
    # Annual chart
    annual_df.plot(x='date', y='owner_earnings_millions', kind='line', 
                   ax=ax1, marker='o', linewidth=2, markersize=6, color='#1f77b4')
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax1.set_title(f'{ticker} Annual Owner Earnings ({annual_start}-{annual_end})', fontweight='bold', fontsize=16)
    ax1.set_ylabel('Owner Earnings ($ Millions)')
    ax1.set_xlabel('Year')
    ax1.grid(True, alpha=0.3)
    ax1.legend(['Owner Earnings', 'Break-even'], loc='upper left')
    
    # Add annotations for key points
    max_annual = annual_df.loc[annual_df['owner_earnings_millions'].idxmax()]
    min_annual = annual_df.loc[annual_df['owner_earnings_millions'].idxmin()]
    
    ax1.annotate(f'Best: ${max_annual["owner_earnings_millions"]:.0f}M\n({max_annual["Period"]})', 
                xy=(max_annual['date'], max_annual['owner_earnings_millions']),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax1.annotate(f'Worst: ${min_annual["owner_earnings_millions"]:.0f}M\n({min_annual["Period"]})', 
                xy=(min_annual['date'], min_annual['owner_earnings_millions']),
                xytext=(10, -20), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # Quarterly chart
    quarterly_df.plot(x='date', y='owner_earnings_millions', kind='line', 
                      ax=ax2, marker='s', linewidth=1.5, markersize=4, color='#ff7f0e', alpha=0.8)
    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax2.set_title(f'{ticker} Quarterly Owner Earnings ({quarterly_start}-{quarterly_end})', fontweight='bold', fontsize=16)
    ax2.set_ylabel('Owner Earnings ($ Millions)')
    ax2.set_xlabel('Date')
    ax2.grid(True, alpha=0.3)
    ax2.legend(['Owner Earnings', 'Break-even'], loc='upper left')
    
    # Add annotations for quarterly extremes
    max_quarterly = quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmax()]
    min_quarterly = quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmin()]
    
    ax2.annotate(f'Best: ${max_quarterly["owner_earnings_millions"]:.0f}M\n({max_quarterly["Period"]})', 
                xy=(max_quarterly['date'], max_quarterly['owner_earnings_millions']),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax2.annotate(f'Worst: ${min_quarterly["owner_earnings_millions"]:.0f}M\n({min_quarterly["Period"]})', 
                xy=(min_quarterly['date'], min_quarterly['owner_earnings_millions']),
                xytext=(10, -20), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    return fig

def create_components_breakdown(annual_df, quarterly_df, ticker):
    """Create waterfall charts showing the components of owner earnings."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 14))
    
    # Annual components waterfall
    create_annual_waterfall_chart(ax1, annual_df, ticker)
    
    # Quarterly components (most recent 20 quarters for readability)
    # Sort by date to ensure we get the most recent quarters, then take the most recent 20
    quarterly_sorted = quarterly_df.sort_values('date', ascending=False)  # Most recent first
    quarterly_recent = quarterly_sorted.head(20).copy()  # Get 20 most recent quarters
    
    # Create waterfall chart for quarterly data
    create_waterfall_chart(ax2, quarterly_recent, ticker)
    
    # Rotate x-axis labels for better readability
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig

def create_annual_waterfall_chart(ax, df, ticker):
    """Create a waterfall chart showing annual owner earnings components."""
    
    # Get all years or the last 8 years for better visibility (show more recent data)
    # Sort by Period to ensure we get the most recent years
    df_sorted = df.sort_values('Period', ascending=False)  # Most recent first
    recent_years = df_sorted.head(8).copy()  # Get 8 most recent years
    
    # Keep the newest-first order for x-axis (reversed chronological)
    # recent_years is already in descending order (newest first)
    
    # Set up the chart dimensions
    n_years = len(recent_years)
    bar_width = 0.15
    
    # Create positions for each year
    year_positions = np.arange(n_years)
    
    # Colors for each component
    colors = {
        'Net Income': '#2E86AB',
        'Depreciation': '#A23B72', 
        'CapEx': '#F18F01',
        'WC Changes': '#C73E1D',
        'Owner Earnings': '#4CAF50'
    }
    
    # Create grouped waterfall charts for each year
    for i, (_, year) in enumerate(recent_years.iterrows()):
        period = year['Period']
        
        # Component values
        net_income = year['net_income_millions']
        depreciation = year['depreciation_millions']
        capex = year['capex_millions']
        wc_change = year['working_capital_change_millions']
        owner_earnings = year['owner_earnings_millions']
        
        # Calculate cumulative positions for waterfall
        cumulative = [0]
        cumulative.append(net_income)
        cumulative.append(cumulative[-1] + depreciation)
        cumulative.append(cumulative[-1] + capex)
        cumulative.append(cumulative[-1] + wc_change)
        
        # X position for this year's bars
        x_base = i
        
        # Net Income (starts from 0)
        ax.bar(x_base - 2*bar_width, net_income, bar_width, 
               bottom=0, color=colors['Net Income'], alpha=0.8, 
               edgecolor='black', linewidth=0.3,
               label='Net Income' if i == 0 else "")
        
        # Depreciation (stacks on Net Income)
        ax.bar(x_base - bar_width, depreciation, bar_width,
               bottom=cumulative[1], color=colors['Depreciation'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='+ Depreciation' if i == 0 else "")
        
        # CapEx (negative, stacks on previous)
        ax.bar(x_base, capex, bar_width,
               bottom=cumulative[2], color=colors['CapEx'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='- CapEx' if i == 0 else "")
        
        # Working Capital Changes (can be positive or negative)
        wc_color = colors['WC Changes'] if wc_change < 0 else '#90EE90'
        ax.bar(x_base + bar_width, wc_change, bar_width,
               bottom=cumulative[3], color=wc_color, alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='WC Changes' if i == 0 else "")
        
        # Owner Earnings (final result)
        oe_color = colors['Owner Earnings'] if owner_earnings >= 0 else '#F44336'
        ax.bar(x_base + 2*bar_width, owner_earnings, bar_width,
               bottom=0, color=oe_color, alpha=0.8,
               edgecolor='black', linewidth=0.5,
               label='Owner Earnings' if i == 0 else "")
        
        # Add value labels for Owner Earnings (in billions for annual)
        oe_billions = owner_earnings / 1000
        ax.text(x_base + 2*bar_width, owner_earnings/2, f'${oe_billions:.1f}B',
               ha='center', va='center', fontweight='bold', fontsize=9, rotation=90)
        
        # Add connecting line to show the flow to final result
        if owner_earnings >= 0:
            ax.plot([x_base + bar_width + bar_width/2, x_base + 2*bar_width - bar_width/2], 
                   [cumulative[4], owner_earnings/2], 'k--', alpha=0.3, linewidth=1)
    
    # Formatting
    ax.set_xticks(year_positions)
    ax.set_xticklabels([str(int(y['Period'])) for _, y in recent_years.iterrows()])
    ax.set_title(f'{ticker} Annual Owner Earnings Waterfall - Most Recent Years', fontweight='bold', fontsize=16)
    ax.set_ylabel('Amount ($ Millions)')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8)

def create_waterfall_chart(ax, df, ticker):
    """Create a waterfall chart showing owner earnings components for recent quarters."""
    
    # Get the most recent quarters and reverse order (newest first)
    # Sort by date to ensure we get the most recent quarters
    df_sorted = df.sort_values('date', ascending=False)  # Most recent first
    recent_quarters = df_sorted.head(12).copy()  # Get 12 most recent quarters (3 years)
    
    # Keep the newest-first order for x-axis (reversed chronological)
    
    # Set up the chart dimensions
    n_quarters = len(recent_quarters)
    n_components = 5  # Net Income, Depreciation, CapEx, WC Changes, Owner Earnings
    bar_width = 0.15
    
    # Create positions for each quarter
    quarter_positions = np.arange(n_quarters)
    
    # Colors for each component
    colors = {
        'Net Income': '#2E86AB',
        'Depreciation': '#A23B72', 
        'CapEx': '#F18F01',
        'WC Changes': '#C73E1D',
        'Owner Earnings': '#4CAF50'
    }
    
    # Create grouped waterfall charts for each quarter
    for i, (_, quarter) in enumerate(recent_quarters.iterrows()):
        period = quarter['Period']
        
        # Component values
        net_income = quarter['net_income_millions']
        depreciation = quarter['depreciation_millions']
        capex = quarter['capex_millions']
        wc_change = quarter['working_capital_change_millions']
        owner_earnings = quarter['owner_earnings_millions']
        
        # Calculate cumulative positions for waterfall
        cumulative = [0]
        cumulative.append(net_income)
        cumulative.append(cumulative[-1] + depreciation)
        cumulative.append(cumulative[-1] + capex)
        cumulative.append(cumulative[-1] + wc_change)
        
        # X position for this quarter's bars
        x_base = i
        
        # Net Income (starts from 0)
        ax.bar(x_base - 2*bar_width, net_income, bar_width, 
               bottom=0, color=colors['Net Income'], alpha=0.8, 
               edgecolor='black', linewidth=0.3,
               label='Net Income' if i == 0 else "")
        
        # Depreciation (stacks on Net Income)
        ax.bar(x_base - bar_width, depreciation, bar_width,
               bottom=cumulative[1], color=colors['Depreciation'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='+ Depreciation' if i == 0 else "")
        
        # CapEx (negative, stacks on previous)
        ax.bar(x_base, capex, bar_width,
               bottom=cumulative[2], color=colors['CapEx'], alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='- CapEx' if i == 0 else "")
        
        # Working Capital Changes (can be positive or negative)
        wc_color = colors['WC Changes'] if wc_change < 0 else '#90EE90'
        ax.bar(x_base + bar_width, wc_change, bar_width,
               bottom=cumulative[3], color=wc_color, alpha=0.8,
               edgecolor='black', linewidth=0.3,
               label='WC Changes' if i == 0 else "")
        
        # Owner Earnings (final result)
        oe_color = colors['Owner Earnings'] if owner_earnings >= 0 else '#F44336'
        ax.bar(x_base + 2*bar_width, owner_earnings, bar_width,
               bottom=0, color=oe_color, alpha=0.8,
               edgecolor='black', linewidth=0.5,
               label='Owner Earnings' if i == 0 else "")
        
        # Add value labels for Owner Earnings
        ax.text(x_base + 2*bar_width, owner_earnings/2, f'${owner_earnings:,.0f}M',
               ha='center', va='center', fontweight='bold', fontsize=8, rotation=90)
        
        # Add connecting line to show the flow to final result
        if owner_earnings >= 0:
            ax.plot([x_base + bar_width + bar_width/2, x_base + 2*bar_width - bar_width/2], 
                   [cumulative[4], owner_earnings/2], 'k--', alpha=0.3, linewidth=1)
    
    # Formatting
    ax.set_xticks(quarter_positions)
    ax.set_xticklabels([q['Period'] for _, q in recent_quarters.iterrows()], rotation=45, ha='right')
    ax.set_title(f'{ticker} Owner Earnings Waterfall - Most Recent Quarters', fontweight='bold', fontsize=14)
    ax.set_ylabel('Amount ($ Millions)')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8)

def create_volatility_analysis(quarterly_df, ticker):
    """Create charts showing the volatility and trends in owner earnings."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Check if we have enough data for volatility analysis
    if len(quarterly_df) < 4:
        # Not enough data for proper quarterly analysis
        ax1.text(0.5, 0.5, f'Insufficient data for volatility analysis\n({len(quarterly_df)} periods available)', 
                ha='center', va='center', transform=ax1.transAxes, fontsize=12)
        ax2.text(0.5, 0.5, 'Need at least 4 quarters\nfor meaningful analysis', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax3.text(0.5, 0.5, 'Quarterly data required', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=12)
        ax4.text(0.5, 0.5, 'Analysis not available', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title(f'{ticker} Volatility Analysis - Insufficient Data', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    # 1. Rolling average to show trend
    quarterly_df['rolling_4q'] = quarterly_df['owner_earnings_millions'].rolling(window=4, center=True).mean()
    quarterly_df['rolling_8q'] = quarterly_df['owner_earnings_millions'].rolling(window=8, center=True).mean()
    
    ax1.plot(quarterly_df['date'], quarterly_df['owner_earnings_millions'], 
             'o-', alpha=0.6, label='Quarterly', linewidth=1, markersize=3)
    ax1.plot(quarterly_df['date'], quarterly_df['rolling_4q'], 
             '-', linewidth=2, label='4Q Rolling Avg', color='red')
    ax1.plot(quarterly_df['date'], quarterly_df['rolling_8q'], 
             '-', linewidth=2, label='8Q Rolling Avg', color='green')
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.7)
    ax1.set_title(f'{ticker} Owner Earnings Trend Analysis', fontweight='bold')
    ax1.set_ylabel('Owner Earnings ($ Millions)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Year-over-year comparison (same quarter)
    quarterly_df['year'] = quarterly_df['date'].dt.year
    quarterly_df['quarter'] = quarterly_df['date'].dt.quarter
    
    # Create pivot for YoY comparison
    try:
        pivot_data = quarterly_df.pivot(index='quarter', columns='year', values='owner_earnings_millions')
        recent_years = [col for col in pivot_data.columns if col >= 2020]  # Focus on recent years
        
        # Check if we actually have quarterly data (not just annual data)
        unique_quarters = quarterly_df['quarter'].unique()
        if len(unique_quarters) == 1:
            # This is annual data masquerading as quarterly - show a different chart
            ax2.bar(quarterly_df['year'], quarterly_df['owner_earnings_millions'], alpha=0.7, color='skyblue')
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            ax2.set_title('Annual Owner Earnings (labeled as quarterly)', fontweight='bold')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Owner Earnings ($ Millions)')
            ax2.grid(True, alpha=0.3)
        else:
            # Real quarterly data - show quarters
            for year in recent_years:
                if year in pivot_data.columns:
                    quarters = [1,2,3,4]
                    values = [pivot_data.loc[q, year] if q in pivot_data.index else None for q in quarters]
                    # Filter out None values
                    valid_quarters = [q for q, v in zip(quarters, values) if v is not None]
                    valid_values = [v for v in values if v is not None]
                    if valid_quarters and valid_values:
                        ax2.plot(valid_quarters, valid_values, 'o-', label=f'{year}', linewidth=2, markersize=6)
            
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.7)
            ax2.set_title('Year-over-Year Quarterly Comparison', fontweight='bold')
            ax2.set_xlabel('Quarter')
            ax2.set_ylabel('Owner Earnings ($ Millions)')
            ax2.set_xticks([1,2,3,4])
            ax2.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
    except Exception as e:
        print(f"[WARNING] Error creating YoY chart: {e}")
        ax2.text(0.5, 0.5, f'YoY Analysis Error:\n{str(e)}', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=10)
        ax2.set_title('Year-over-Year Analysis - Error', fontweight='bold')
    
    # 3. Distribution histogram
    ax3.hist(quarterly_df['owner_earnings_millions'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.axvline(x=quarterly_df['owner_earnings_millions'].mean(), color='red', 
                linestyle='--', label=f"Mean: ${quarterly_df['owner_earnings_millions'].mean():.0f}M")
    ax3.axvline(x=quarterly_df['owner_earnings_millions'].median(), color='green', 
                linestyle='--', label=f"Median: ${quarterly_df['owner_earnings_millions'].median():.0f}M")
    ax3.set_title('Distribution of Quarterly Owner Earnings', fontweight='bold')
    ax3.set_xlabel('Owner Earnings ($ Millions)')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Positive vs Negative quarters
    positive_quarters = quarterly_df[quarterly_df['owner_earnings_millions'] > 0]
    negative_quarters = quarterly_df[quarterly_df['owner_earnings_millions'] <= 0]
    
    summary_data = {
        'Positive Quarters': [len(positive_quarters), positive_quarters['owner_earnings_millions'].mean() if len(positive_quarters) > 0 else 0],
        'Negative Quarters': [len(negative_quarters), negative_quarters['owner_earnings_millions'].mean() if len(negative_quarters) > 0 else 0]
    }
    
    categories = list(summary_data.keys())
    counts = [summary_data[cat][0] for cat in categories]
    avg_values = [summary_data[cat][1] for cat in categories]
    
    x_pos = np.arange(len(categories))
    
    bars1 = ax4.bar(x_pos - 0.2, counts, 0.4, label='Count', color='lightblue', alpha=0.8)
    ax4_twin = ax4.twinx()
    bars2 = ax4_twin.bar(x_pos + 0.2, avg_values, 0.4, label='Avg Value ($M)', color='lightcoral', alpha=0.8)
    
    ax4.set_title('Positive vs Negative Quarters Summary', fontweight='bold')
    ax4.set_xlabel('Quarter Type')
    ax4.set_ylabel('Number of Quarters', color='blue')
    ax4_twin.set_ylabel('Average Value ($ Millions)', color='red')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(categories)
    
    # Add value labels on bars
    for bar, count in zip(bars1, counts):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(count), ha='center', va='bottom')
    
    for bar, avg_val in zip(bars2, avg_values):
        ax4_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (20 if avg_val > 0 else -40), 
                     f'${avg_val:.0f}M', ha='center', va='bottom' if avg_val > 0 else 'top')
    
    plt.tight_layout()
    return fig

def create_investment_analysis(annual_df, quarterly_df, ticker):
    """Create comprehensive investment analysis charts including ROI, growth trends, and valuation metrics."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    
    # 1. Owner Earnings Growth Rate Analysis
    if len(annual_df) > 1:
        # Calculate year-over-year growth rates
        annual_sorted = annual_df.sort_values('Period')
        annual_sorted['oe_growth_rate'] = annual_sorted['owner_earnings_millions'].pct_change() * 100
        
        # Plot growth rates
        valid_growth = annual_sorted.dropna(subset=['oe_growth_rate'])
        if len(valid_growth) > 0:
            ax1.bar(valid_growth['Period'], valid_growth['oe_growth_rate'], 
                   color=['green' if x >= 0 else 'red' for x in valid_growth['oe_growth_rate']], 
                   alpha=0.7, edgecolor='black', linewidth=0.5)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.8)
            ax1.axhline(y=valid_growth['oe_growth_rate'].mean(), color='blue', linestyle='--', 
                       label=f'Avg: {valid_growth["oe_growth_rate"].mean():.1f}%', alpha=0.7)
            ax1.set_title(f'{ticker} Owner Earnings Growth Rate (YoY %)', fontweight='bold', fontsize=14)
            ax1.set_ylabel('Growth Rate (%)')
            ax1.set_xlabel('Year')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, (_, row) in enumerate(valid_growth.iterrows()):
                growth = row['oe_growth_rate']
                ax1.text(row['Period'], growth + (5 if growth >= 0 else -5), f'{growth:.1f}%',
                        ha='center', va='bottom' if growth >= 0 else 'top', fontweight='bold', fontsize=9)
        else:
            ax1.text(0.5, 0.5, 'Insufficient data for growth analysis', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title(f'{ticker} Owner Earnings Growth Rate - Insufficient Data', fontweight='bold')
    else:
        ax1.text(0.5, 0.5, 'Need at least 2 years for growth analysis', 
                ha='center', va='center', transform=ax1.transAxes, fontsize=12)
        ax1.set_title(f'{ticker} Owner Earnings Growth Rate - Insufficient Data', fontweight='bold')
    
    # 2. Cumulative Owner Earnings (Total Value Created)
    annual_sorted = annual_df.sort_values('Period')
    annual_sorted['cumulative_oe'] = annual_sorted['owner_earnings_millions'].cumsum()
    
    ax2.fill_between(annual_sorted['Period'], 0, annual_sorted['cumulative_oe'], 
                     alpha=0.6, color='lightblue', edgecolor='blue', linewidth=2)
    ax2.plot(annual_sorted['Period'], annual_sorted['cumulative_oe'], 
             'o-', color='darkblue', linewidth=2, markersize=6)
    ax2.set_title(f'{ticker} Cumulative Owner Earnings (Total Value Created)', fontweight='bold', fontsize=14)
    ax2.set_ylabel('Cumulative Owner Earnings ($ Millions)')
    ax2.set_xlabel('Year')
    ax2.grid(True, alpha=0.3)
    
    # Add final value annotation
    final_value = annual_sorted['cumulative_oe'].iloc[-1]
    final_year = annual_sorted['Period'].iloc[-1]
    ax2.annotate(f'Total: ${final_value:,.0f}M', 
                xy=(final_year, final_value),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # 3. Owner Earnings Consistency Analysis (Quarterly)
    if len(quarterly_df) > 4:
        # Calculate rolling standard deviation and coefficient of variation
        quarterly_sorted = quarterly_df.sort_values('date')
        quarterly_sorted['rolling_std'] = quarterly_sorted['owner_earnings_millions'].rolling(window=4).std()
        quarterly_sorted['rolling_mean'] = quarterly_sorted['owner_earnings_millions'].rolling(window=4).mean()
        quarterly_sorted['coefficient_of_variation'] = (quarterly_sorted['rolling_std'] / quarterly_sorted['rolling_mean'].abs()) * 100
        
        # Plot consistency metrics
        valid_cv = quarterly_sorted.dropna(subset=['coefficient_of_variation'])
        if len(valid_cv) > 0:
            ax3.plot(valid_cv['date'], valid_cv['coefficient_of_variation'], 
                    'o-', color='purple', linewidth=2, markersize=4, alpha=0.8)
            ax3.axhline(y=valid_cv['coefficient_of_variation'].mean(), color='red', linestyle='--', 
                       label=f'Avg CV: {valid_cv["coefficient_of_variation"].mean():.1f}%', alpha=0.7)
            ax3.set_title(f'{ticker} Earnings Consistency (4Q Rolling CV)', fontweight='bold', fontsize=14)
            ax3.set_ylabel('Coefficient of Variation (%)')
            ax3.set_xlabel('Date')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Add interpretation
            avg_cv = valid_cv['coefficient_of_variation'].mean()
            if avg_cv < 30:
                consistency = "High"
                color = "green"
            elif avg_cv < 60:
                consistency = "Moderate"
                color = "orange"
            else:
                consistency = "Low"
                color = "red"
            
            ax3.text(0.02, 0.98, f'Consistency: {consistency}', transform=ax3.transAxes,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7),
                    verticalalignment='top', fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'Insufficient quarterly data for consistency analysis', 
                    ha='center', va='center', transform=ax3.transAxes, fontsize=12)
            ax3.set_title(f'{ticker} Earnings Consistency - Insufficient Data', fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'Need at least 4 quarters for consistency analysis', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=12)
        ax3.set_title(f'{ticker} Earnings Consistency - Insufficient Data', fontweight='bold')
    
    # 4. Investment Quality Score Dashboard
    # Calculate various quality metrics
    scores = {}
    
    # Growth consistency (lower CV = higher score)
    if len(quarterly_df) > 4:
        quarterly_sorted = quarterly_df.sort_values('date')
        quarterly_sorted['rolling_std'] = quarterly_sorted['owner_earnings_millions'].rolling(window=4).std()
        quarterly_sorted['rolling_mean'] = quarterly_sorted['owner_earnings_millions'].rolling(window=4).mean()
        quarterly_sorted['coefficient_of_variation'] = (quarterly_sorted['rolling_std'] / quarterly_sorted['rolling_mean'].abs()) * 100
        avg_cv = quarterly_sorted['coefficient_of_variation'].mean()
        if not pd.isna(avg_cv):
            scores['Consistency'] = max(0, min(100, 100 - avg_cv))  # Invert CV for score
        else:
            scores['Consistency'] = 50
    else:
        scores['Consistency'] = 50
    
    # Profitability (percentage of positive quarters)
    positive_quarters = len(quarterly_df[quarterly_df['owner_earnings_millions'] > 0])
    total_quarters = len(quarterly_df)
    scores['Profitability'] = (positive_quarters / total_quarters) * 100 if total_quarters > 0 else 0
    
    # Growth trend (average annual growth)
    if len(annual_df) > 1:
        annual_sorted = annual_df.sort_values('Period')
        annual_sorted['oe_growth_rate'] = annual_sorted['owner_earnings_millions'].pct_change() * 100
        avg_growth = annual_sorted['oe_growth_rate'].mean()
        if not pd.isna(avg_growth):
            scores['Growth'] = max(0, min(100, avg_growth + 50))  # Scale growth to 0-100
        else:
            scores['Growth'] = 50
    else:
        scores['Growth'] = 50
    
    # Value creation (cumulative earnings relative to scale)
    total_oe = annual_df['owner_earnings_millions'].sum()
    if total_oe > 0:
        scores['Value Creation'] = min(100, (total_oe / 1000) * 10)  # Scale based on billions
    else:
        scores['Value Creation'] = 0
    
    # Create radar chart / score display
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Create bar chart for scores
    colors = ['green' if v >= 70 else 'orange' if v >= 40 else 'red' for v in values]
    bars = ax4.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    
    # Add score labels on bars
    for bar, value in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax4.set_ylim(0, 100)
    ax4.set_title(f'{ticker} Investment Quality Score', fontweight='bold', fontsize=14)
    ax4.set_ylabel('Score (0-100)')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add overall score
    overall_score = sum(values) / len(values)
    ax4.text(0.02, 0.98, f'Overall: {overall_score:.0f}/100', transform=ax4.transAxes,
            bbox=dict(boxstyle='round,pad=0.3', 
                     facecolor='green' if overall_score >= 70 else 'orange' if overall_score >= 40 else 'red', 
                     alpha=0.7),
            verticalalignment='top', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    return fig

def save_and_show_plots(figures, filenames, ticker):
    """Save plots to files and display them."""
    # Ensure we're using non-interactive backend
    matplotlib.use('Agg')
    plt.ioff()
    
    # Create charts directory if it doesn't exist
    charts_dir = "charts"
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        print(f"[DIR] Created directory: {charts_dir}/")
    
    for fig, filename in zip(figures, filenames):
        # Use the filename as-is since it's already properly formatted
        filepath = os.path.join(charts_dir, f"{filename}.png")
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"[CHART] Saved chart: {filepath}")
        # Close the figure to free memory
        plt.close(fig)
    
    # Don't show interactive plots in GUI mode - just save them
    # plt.show()
    print("\n[OK] All charts displayed and saved!")

def main(ticker=None):
    """Main function to create all visualizations."""
    # Use provided ticker or detect it
    if ticker is None:
        ticker = detect_ticker_symbol()
    
    print(f"{ticker} Owner Earnings Visualization Tool")
    print("=" * 50)
    
    # Set up plotting style
    setup_plotting_style()
    
    # Load data with specific ticker
    annual_df, quarterly_df = load_data(ticker)
    if annual_df is None or quarterly_df is None:
        return
    
    # Prepare data
    print("[ANALYSIS] Preparing data for visualization...")
    annual_df = prepare_annual_data(annual_df)
    quarterly_df = prepare_quarterly_data(quarterly_df)
    
    print(f"[CHARTS] Creating visualizations...")
    
    # Create all charts
    figures = []
    filenames = []
    
    # 1. Owner earnings comparison
    fig1 = create_owner_earnings_comparison(annual_df, quarterly_df, ticker)
    figures.append(fig1)
    filenames.append(f"{ticker.lower().replace('.', '')}_owner_earnings_comparison")
    
    # 2. Components breakdown
    fig2 = create_components_breakdown(annual_df, quarterly_df, ticker)
    figures.append(fig2)
    filenames.append(f"{ticker.lower().replace('.', '')}_earnings_components_breakdown")
    
    # 3. Volatility analysis
    fig3 = create_volatility_analysis(quarterly_df, ticker)
    figures.append(fig3)
    filenames.append(f"{ticker.lower().replace('.', '')}_volatility_analysis")
    
    # 4. Investment analysis (NEW!)
    fig4 = create_investment_analysis(annual_df, quarterly_df, ticker)
    figures.append(fig4)
    filenames.append(f"{ticker.lower().replace('.', '')}_investment_analysis")
    
    # Save and show all plots
    save_and_show_plots(figures, filenames, ticker)
    
    # Print summary statistics
    print(f"\n[SUMMARY] {ticker} SUMMARY STATISTICS:")
    print(f"Annual Data Range: {annual_df['Period'].min()} to {annual_df['Period'].max()}")
    print(f"Quarterly Data Range: {quarterly_df['Period'].min()} to {quarterly_df['Period'].max()}")
    print(f"Best Annual Owner Earnings: ${annual_df['owner_earnings_millions'].max():.0f}M ({annual_df.loc[annual_df['owner_earnings_millions'].idxmax(), 'Period']})")
    print(f"Worst Annual Owner Earnings: ${annual_df['owner_earnings_millions'].min():.0f}M ({annual_df.loc[annual_df['owner_earnings_millions'].idxmin(), 'Period']})")
    print(f"Best Quarterly Owner Earnings: ${quarterly_df['owner_earnings_millions'].max():.0f}M ({quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmax(), 'Period']})")
    print(f"Worst Quarterly Owner Earnings: ${quarterly_df['owner_earnings_millions'].min():.0f}M ({quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmin(), 'Period']})")
    
    positive_quarters = len(quarterly_df[quarterly_df['owner_earnings_millions'] > 0])
    total_quarters = len(quarterly_df)
    print(f"Positive Quarters: {positive_quarters}/{total_quarters} ({positive_quarters/total_quarters*100:.1f}%)")

if __name__ == "__main__":
    main()
