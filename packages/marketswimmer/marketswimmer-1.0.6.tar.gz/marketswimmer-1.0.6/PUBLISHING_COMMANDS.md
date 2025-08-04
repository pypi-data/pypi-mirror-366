# PyPI Publishing Commands

## Fixed Issues in v1.0.5:
- ✅ CLI import errors resolved
- ✅ Typer dependency warnings fixed  
- ✅ GUI dependencies made optional (graceful fallback)
- ✅ Better error messages for missing dependencies
- ✅ Missing script errors fixed (analyze_ticker_gui.py, etc.)
- ✅ Added missing `calculate` and `visualize` commands
- ✅ Complete CLI workflow now functional
- ✅ Consistent user experience with helpful guidance

## Current CLI Commands:
- `ms analyze TICKER` - Full analysis workflow (with guidance)
- `ms calculate --ticker TICKER` - Owner earnings calculation
- `ms visualize --ticker TICKER` - Create charts and visualizations
- `ms gui` - Launch GUI application
- `ms status` - Check package health
- `ms --help` - Show all available commands

# 1. Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# 2. Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ marketswimmer

# 3. If everything works, upload to production PyPI
python -m twine upload dist/*

# 4. Install from production PyPI
pip install marketswimmer

# 5. For GUI functionality, install additional dependencies:
pip install matplotlib PyQt6
