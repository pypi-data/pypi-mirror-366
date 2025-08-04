# PyPI Publishing Commands

## Fixed Issues in v1.0.3:
- ✅ CLI import errors resolved
- ✅ Typer dependency warnings fixed  
- ✅ GUI dependencies made optional (graceful fallback)
- ✅ Better error messages for missing dependencies

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
