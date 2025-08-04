# MarketSwimmer v2.0.3 Clean Installation Test
Write-Host "========================================" -ForegroundColor Green
Write-Host "MarketSwimmer v2.0.3 Clean Installation" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n1. Uninstalling any existing MarketSwimmer..." -ForegroundColor Yellow
pip uninstall marketswimmer -y

Write-Host "`n2. Creating fresh virtual environment..." -ForegroundColor Yellow
python -m venv marketswimmer_clean_test

Write-Host "`n3. Installing MarketSwimmer v2.0.3..." -ForegroundColor Yellow
& "marketswimmer_clean_test\Scripts\python.exe" -m pip install --upgrade pip
& "marketswimmer_clean_test\Scripts\python.exe" -m pip install marketswimmer==2.0.3

Write-Host "`n4. Testing installation..." -ForegroundColor Yellow
& "marketswimmer_clean_test\Scripts\python.exe" -c "import marketswimmer; print('✅ MarketSwimmer imported successfully')"

Write-Host "`n5. Testing CLI..." -ForegroundColor Yellow
& "marketswimmer_clean_test\Scripts\python.exe" -m marketswimmer --help

Write-Host "`n6. Ready to test GUI!" -ForegroundColor Green
Write-Host "Run this command to test the GUI:" -ForegroundColor Cyan
Write-Host "marketswimmer_clean_test\Scripts\python.exe -m marketswimmer gui" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Clean installation complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
