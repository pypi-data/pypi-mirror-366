# MarketSwimmer v2.0.4 Release Notes

## 🚀 Release Date: August 3, 2025

### ✅ What's New in v2.0.4:

#### 📧 Contact Information Updated
- **Author Email**: Updated to `jeremyevans@hey.com`
- **Package Metadata**: All configuration files updated with new contact information

#### 🧹 Repository Maintenance  
- **Repository Cleaned**: Removed all development bloat including:
  - 2 virtual environments (`marketswimmer_clean_test/`, `marketswimmer_test_env/`)
  - Build artifacts (`build/`, `dist/`, `*.egg-info/`)
  - 20+ legacy script files and test files
  - Log directories and temporary files
  - Duplicate GUI variants and development debris
- **Size Reduction**: Repository went from 70+ files to 15 essential files
- **Professional Structure**: Clean, maintainable codebase ready for continued development

### ✅ Preserved Functionality:
All features from v2.0.3 are preserved and working:
- **Complete End-to-End Automation**: `python -m marketswimmer analyze TICKER`
- **GUI Integration**: `python -m marketswimmer gui` with proper CLI command execution
- **Owner Earnings Calculation**: Real calculations with CSV output
- **Professional CLI**: Rich progress bars, error handling, helpful commands
- **Module Execution**: Proper `python -m marketswimmer` support

### 📦 Installation:
```bash
pip install marketswimmer==2.0.4
```

### 🎯 Key Commands:
```bash
# Complete analysis workflow
python -m marketswimmer analyze TSLA

# Launch GUI
python -m marketswimmer gui

# Calculate owner earnings
python -m marketswimmer calculate --ticker AAPL

# Generate visualizations  
python -m marketswimmer visualize --ticker MSFT

# Check package status
python -m marketswimmer status

# Show help
python -m marketswimmer --help
```

### 🔗 Links:
- **PyPI**: https://pypi.org/project/marketswimmer/2.0.4/
- **GitHub**: https://github.com/jeremevans/MarketSwimmer
- **Contact**: jeremyevans@hey.com

### 💭 Technical Notes:
- No breaking changes from v2.0.3
- Same dependency requirements
- Maintained backward compatibility
- Clean repository structure for future development

---
*MarketSwimmer - Warren Buffett's Owner Earnings Analysis Tool*
