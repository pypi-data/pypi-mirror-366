@echo off
echo ========================================
echo MarketSwimmer v2.0.3 Clean Installation
echo ========================================

echo.
echo 1. Uninstalling any existing MarketSwimmer installations...
pip uninstall marketswimmer -y

echo.
echo 2. Creating fresh virtual environment...
python -m venv marketswimmer_clean_test

echo.
echo 3. Installing MarketSwimmer v2.0.3 in virtual environment...
marketswimmer_clean_test\Scripts\python.exe -m pip install --upgrade pip
marketswimmer_clean_test\Scripts\python.exe -m pip install marketswimmer==2.0.3

echo.
echo 4. Verifying installation...
marketswimmer_clean_test\Scripts\python.exe -c "import marketswimmer; print('✅ MarketSwimmer imported successfully')"

echo.
echo 5. Testing CLI availability...
marketswimmer_clean_test\Scripts\python.exe -m marketswimmer --help

echo.
echo 6. Testing GUI launch...
echo Starting GUI in 3 seconds... (Close the GUI window to continue)
timeout /t 3
marketswimmer_clean_test\Scripts\python.exe -m marketswimmer gui

echo.
echo ========================================
echo Installation and testing complete!
echo ========================================
echo.
echo To use MarketSwimmer in this clean environment:
echo   marketswimmer_clean_test\Scripts\python.exe -m marketswimmer gui
echo   marketswimmer_clean_test\Scripts\python.exe -m marketswimmer analyze TICKER
echo.
pause
