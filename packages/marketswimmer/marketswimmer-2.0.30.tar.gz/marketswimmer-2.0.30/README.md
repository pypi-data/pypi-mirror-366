# MarketSwimmer - Owner Earnings Analysis Tool

A comprehensive tool for analyzing Warren Buffett's "Owner Earnings" from financial statement data.

## 📁 Directory Structure

```
MarketSwimmer/
├── 📊 charts/                  # Generated visualization charts
├── 📈 data/                    # CSV output files and analysis results
├── 📥 downloaded_files/        # Financial data Excel files from StockRow
├── 📝 logs/                    # Application logs
├── 🛠️ scripts/                # Utility and test scripts
├── 🚀 Main Applications
│   ├── market_swimmer_gui_clean.py      # Main GUI application
│   ├── analyze_ticker_gui.py           # Complete analysis workflow
│   ├── owner_earnings_fixed.py         # Core analysis engine
│   └── visualize_owner_earnings.py     # Chart generation
├── 🔧 Utilities
│   ├── open_charts.py                  # Chart viewer
│   ├── monitor_downloads.py            # Download automation
│   ├── auto_download.py               # Download helper
│   └── logger_config.py               # Logging configuration
└── 📋 Batch Files
    ├── launch_clean_gui.bat           # Start GUI
    ├── start_gui_safe.bat             # Safe startup
    └── [other .bat files]
```

## 🚀 Quick Start

1. **Launch GUI**: Double-click `launch_clean_gui.bat`
2. **Select Ticker**: Choose a stock symbol (e.g., AAPL, MSFT, BRK.B)
3. **Download Data**: System opens StockRow page for data download
4. **Analyze**: Automatic calculation of Owner Earnings
5. **View Charts**: Generated visualizations open automatically

## 📊 Output Files

- **Charts**: `charts/[ticker]_*.png` - Visual analysis charts
- **Data**: `data/owner_earnings_*.csv` - Raw analysis data
- **Logs**: `logs/marketswimmer_*.log` - Application logs

## 💡 Owner Earnings Formula

```
Owner Earnings = Net Income + Depreciation/Amortization - CapEx - Working Capital Changes
```

## 🎯 Features

- ✅ Ticker-specific analysis
- ✅ Annual and quarterly data processing
- ✅ Professional visualizations
- ✅ Automated chart generation
- ✅ Clean directory organization
- ✅ Comprehensive logging

## 📋 Requirements

- Python 3.12+
- pandas, matplotlib, seaborn
- PyQt6 (for GUI)
- Internet connection (for data download)
