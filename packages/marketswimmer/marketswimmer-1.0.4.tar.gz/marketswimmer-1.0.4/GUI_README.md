# MarketSwimmer GUI - User Guide

## 🏊‍♂️ MarketSwimmer Financial Analysis Tool

A user-friendly PyQt6 GUI for analyzing stock financials using Warren Buffett's Owner Earnings methodology.

## Features

### 🎯 Three Main Actions:

1. **🚀 Complete Analysis (One-Click Solution)**
   - Fully automated process
   - Runs: `get_xlsx.py` → `owner_earnings.py` → `visualize_owner_earnings.py`
   - Perfect for quick, comprehensive analysis

2. **📥 Download & Monitor (Step 1)**
   - Opens StockRow website in browser for manual data download
   - Monitors downloads folder for new XLSX files
   - Copies files to local `downloaded_files` folder

3. **📈 Process & Visualize (Steps 2-3)**
   - Processes existing XLSX files in `downloaded_files`
   - Calculates Owner Earnings using Buffett methodology
   - Creates professional waterfall charts and trend analysis

### 🎨 GUI Features:

- **Modern Interface**: Professional PyQt6 design with intuitive layout
- **Real-time Output**: Live console showing command progress and results
- **Threading**: Non-blocking operations - GUI stays responsive during analysis
- **Error Handling**: Clear error messages and status indicators
- **Progress Tracking**: Visual progress bars and status updates

## 🚀 Getting Started

### Method 1: Double-click launcher
```
start_gui.bat
```

### Method 2: PowerShell command line
```powershell
.\start_gui.bat
```

### Method 3: Alternative launcher
```powershell
.\launch_gui.bat
```

### Method 4: Direct Python execution
```powershell
& "C:/Users/jerem/AppData/Local/Programs/Python/Python312/python.exe" market_swimmer_gui.py
```

## 📊 How to Use

1. **Launch the GUI** using one of the methods above
2. **Select Ticker**: Click "📊 Select Ticker" and enter a stock symbol (e.g., AAPL, TSLA, BRK.B)
3. **Choose Analysis Method**:
   - For beginners: Use "🚀 Complete Analysis" (fully automated)
   - For manual control: Use "📥 Download & Monitor" then "📈 Process & Visualize"
4. **Monitor Progress**: Watch the output console for real-time updates
5. **View Results**: Generated charts will be saved as PNG files in the main folder

## 📁 Generated Files

After analysis, you'll find these files:
- `{ticker}_earnings_components_breakdown.png` - Waterfall chart showing Owner Earnings components
- `{ticker}_owner_earnings_comparison.png` - Trend analysis over time
- `{ticker}_volatility_analysis.png` - Risk and volatility metrics
- `owner_earnings_financials_annual.csv` - Annual financial data
- `owner_earnings_financials_quarterly.csv` - Quarterly financial data

## 🔧 Technical Requirements

- **Python 3.12+** with these packages:
  - PyQt6 (GUI framework)
  - pandas, numpy (data processing)
  - matplotlib, seaborn (visualization)
  - openpyxl (Excel file handling)
  - requests, beautifulsoup4 (web scraping)

## 💡 Tips for Best Results

1. **Use Complete Analysis** for most cases - it's fully automated
2. **Check output console** for detailed progress information
3. **Wait for completion** - financial analysis takes time for accurate results
4. **Use manual steps** if you need to customize the data download process
5. **Charts are automatically saved** - no need to manually save them

## 🛠️ Troubleshooting

**GUI won't start:**
- Ensure PyQt6 is installed: `pip install PyQt6`
- Check Python path is correct

**Analysis fails:**
- Verify ticker symbol exists (e.g., BRK.B for Berkshire Hathaway Class B)
- Check internet connection for data download
- Ensure XLSX files are in `downloaded_files` folder for manual processing

**No charts generated:**
- Check if CSV files were created first
- Verify matplotlib is installed: `pip install matplotlib seaborn`
- Look for error messages in output console

## 📞 Support

This GUI provides the same powerful financial analysis as the command-line scripts, but with an easy-to-use interface perfect for both beginners and experts.

For technical issues, check the output console for detailed error messages.
