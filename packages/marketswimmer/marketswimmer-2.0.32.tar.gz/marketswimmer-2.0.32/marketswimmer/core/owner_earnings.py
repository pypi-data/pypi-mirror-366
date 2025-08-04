import pandas as pd
import os
import sys
import glob
from pathlib import Path

class OwnerEarningsCalculator:
    """
    Calculate Warren Buffett's Owner Earnings from financial statement data.
    
    Owner Earnings = Net Income + Depreciation/Amortization - Capital Expenditures - Working Capital Changes
    """
    
    def __init__(self, xlsx_file_path=None):
        """
        Initialize the calculator.
        
        Args:
            xlsx_file_path (str, optional): Path to the XLSX file with financial data
        """
        self.file_path = xlsx_file_path
        self.company_name = None
        self.income_statement = None
        self.balance_sheet = None
        self.cash_flow = None
        self.owner_earnings_data = {}
        
        # If file path provided, load immediately for backward compatibility
        if xlsx_file_path:
            self.load_financial_data(xlsx_file_path)
    
    def load_financial_data(self, xlsx_file_path):
        """
        Load financial data from an XLSX file.
        
        Args:
            xlsx_file_path (str): Path to the XLSX file with financial data
        """
        self.file_path = xlsx_file_path
        self.company_name = os.path.basename(xlsx_file_path).split('_')[0] if '_' in os.path.basename(xlsx_file_path) else "Unknown"
        return self.load_financial_statements()
        
    def load_financial_statements(self):
        """Load all financial statement tabs from the XLSX file."""
        try:
            print(f"[DATA] Loading financial data from: {os.path.basename(self.file_path)}")
            
            # Get all sheet names
            xl_file = pd.ExcelFile(self.file_path)
            sheet_names = xl_file.sheet_names
            print(f"[INFO] Available sheets: {sheet_names}")
            
            # Try to identify sheets by common names - prefer Annual (A) over Quarterly (Q)
            # Look for annual data first, then fall back to quarterly
            income_sheet = (self._find_sheet(sheet_names, ['Income Statement, A']) or 
                           self._find_sheet(sheet_names, ['Income Statement, Q']) or
                           self._find_sheet(sheet_names, ['income', 'profit', 'earnings', 'statement']))
            
            balance_sheet = (self._find_sheet(sheet_names, ['Balance Sheet, A']) or 
                            self._find_sheet(sheet_names, ['Balance Sheet, Q']) or
                            self._find_sheet(sheet_names, ['balance', 'position', 'sheet']))
            
            cashflow_sheet = (self._find_sheet(sheet_names, ['Cash Flow, A']) or 
                             self._find_sheet(sheet_names, ['Cash Flow, Q']) or
                             self._find_sheet(sheet_names, ['cash', 'flow', 'cashflow']))
            
            # Load the sheets
            if income_sheet:
                self.income_statement = pd.read_excel(self.file_path, sheet_name=income_sheet)
                print(f"[OK] Loaded Income Statement: {income_sheet}")
                print(f"   [DATA] Shape: {self.income_statement.shape}")
                data_type = "Annual" if ", A" in income_sheet else "Quarterly" if ", Q" in income_sheet else "Unknown"
                print(f"   [DATE] Data type: {data_type}")
            
            if balance_sheet:
                self.balance_sheet = pd.read_excel(self.file_path, sheet_name=balance_sheet)
                print(f"[OK] Loaded Balance Sheet: {balance_sheet}")
                print(f"   [DATA] Shape: {self.balance_sheet.shape}")
                data_type = "Annual" if ", A" in balance_sheet else "Quarterly" if ", Q" in balance_sheet else "Unknown"
                print(f"   [DATE] Data type: {data_type}")
            
            if cashflow_sheet:
                self.cash_flow = pd.read_excel(self.file_path, sheet_name=cashflow_sheet)
                print(f"[OK] Loaded Cash Flow Statement: {cashflow_sheet}")
                print(f"   [DATA] Shape: {self.cash_flow.shape}")
                data_type = "Annual" if ", A" in cashflow_sheet else "Quarterly" if ", Q" in cashflow_sheet else "Unknown"
                print(f"   [DATE] Data type: {data_type}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading financial statements: {e}")
            return False
    
    def load_financial_statements_by_type(self, data_type):
        """Load financial statements of a specific type (Annual or Quarterly)."""
        try:
            print(f"[DATA] Loading {data_type.lower()} financial data from: {os.path.basename(self.file_path)}")
            
            # Get all sheet names
            xl_file = pd.ExcelFile(self.file_path)
            sheet_names = xl_file.sheet_names
            
            # Map data type to sheet suffix
            suffix = ', A' if data_type == 'Annual' else ', Q'
            
            # Look for sheets with the specific suffix
            income_sheet = self._find_sheet(sheet_names, [f'Income Statement{suffix}'])
            balance_sheet = self._find_sheet(sheet_names, [f'Balance Sheet{suffix}'])
            cashflow_sheet = self._find_sheet(sheet_names, [f'Cash Flow{suffix}'])
            
            # Fallback to any income/balance/cashflow sheet if specific type not found
            if not income_sheet:
                income_sheet = self._find_sheet(sheet_names, ['income', 'profit', 'earnings', 'statement'])
            if not balance_sheet:
                balance_sheet = self._find_sheet(sheet_names, ['balance', 'position', 'sheet'])
            if not cashflow_sheet:
                cashflow_sheet = self._find_sheet(sheet_names, ['cash', 'flow', 'cashflow'])
            
            # Load the sheets
            sheets_loaded = 0
            
            if income_sheet:
                self.income_statement = pd.read_excel(self.file_path, sheet_name=income_sheet)
                print(f"[OK] Loaded Income Statement: {income_sheet}")
                print(f"   [DATA] Shape: {self.income_statement.shape}")
                sheets_loaded += 1
            
            if balance_sheet:
                self.balance_sheet = pd.read_excel(self.file_path, sheet_name=balance_sheet)
                print(f"[OK] Loaded Balance Sheet: {balance_sheet}")
                print(f"   [DATA] Shape: {self.balance_sheet.shape}")
                sheets_loaded += 1
            
            if cashflow_sheet:
                self.cash_flow = pd.read_excel(self.file_path, sheet_name=cashflow_sheet)
                print(f"[OK] Loaded Cash Flow Statement: {cashflow_sheet}")
                print(f"   [DATA] Shape: {self.cash_flow.shape}")
                sheets_loaded += 1
            
            return sheets_loaded >= 2  # Need at least 2 statements for analysis
            
        except Exception as e:
            print(f"[ERROR] Error loading {data_type.lower()} financial statements: {e}")
            return False
    
    def _find_sheet(self, sheet_names, keywords):
        """Find sheet name that contains any of the keywords."""
        for sheet in sheet_names:
            for keyword in keywords:
                if keyword.lower() in sheet.lower():
                    return sheet
        return None
    
    def _quarter_to_number(self, month_name):
        """Convert month name to quarter number."""
        if month_name.startswith('Dec'):
            return 4
        elif month_name.startswith('Sep'):
            return 3
        elif month_name.startswith('Jun'):
            return 2
        elif month_name.startswith('Mar'):
            return 1
        else:
            return 1  # Default fallback
    
    def debug_financial_data(self):
        """Print available financial line items for debugging."""
        print(f"\n[SEARCH] DEBUG: Available financial line items...")
        
        if self.income_statement is not None:
            print(f"\n[DATA] INCOME STATEMENT ({self.income_statement.shape}):")
            print(f"   Columns: {list(self.income_statement.columns)}")
            print(f"   First few rows of first column:")
            try:
                first_col = self.income_statement.iloc[:, 0]
                for i, item in enumerate(first_col.head(15)):
                    if pd.notna(item):
                        print(f"   {i}: {item}")
            except Exception as e:
                print(f"   Error reading income statement: {e}")
        
        if self.cash_flow is not None:
            print(f"\n[MONEY] CASH FLOW STATEMENT ({self.cash_flow.shape}):")
            print(f"   Columns: {list(self.cash_flow.columns)}")
            print(f"   First few rows of first column:")
            try:
                first_col = self.cash_flow.iloc[:, 0]
                for i, item in enumerate(first_col.head(15)):
                    if pd.notna(item):
                        print(f"   {i}: {item}")
            except Exception as e:
                print(f"   Error reading cash flow: {e}")
        
        if self.balance_sheet is not None:
            print(f"\n[INFO] BALANCE SHEET ({self.balance_sheet.shape}):")
            print(f"   Columns: {list(self.balance_sheet.columns)}")
            print(f"   First few rows of first column:")
            try:
                first_col = self.balance_sheet.iloc[:, 0]
                for i, item in enumerate(first_col.head(15)):
                    if pd.notna(item):
                        print(f"   {i}: {item}")
            except Exception as e:
                print(f"   Error reading balance sheet: {e}")

    def _find_financial_item(self, df, search_terms, years_to_extract=40):
        """
        Find a financial line item in a dataframe and extract values for recent years.
        
        Args:
            df: DataFrame to search
            search_terms: List of terms to search for in the first column
            years_to_extract: Number of recent periods to extract (40 for ~10 years quarterly)
        
        Returns:
            dict: Period -> Value mapping
        """
        if df is None or df.empty:
            return {}
        
        print(f"   [SEARCH] Searching for: {search_terms}")
        
        # Try different approaches to find the data
        # Approach 1: Use first column as index
        try:
            search_df = df.copy()
            if len(search_df.columns) > 0:
                search_df = search_df.set_index(search_df.columns[0])
        except:
            search_df = df.copy()
        
        # Search for the item
        for search_term in search_terms:
            print(f"      Looking for: '{search_term}'")
            
            # Try exact match first
            for idx in search_df.index:
                if pd.notna(idx) and search_term.lower() in str(idx).lower():
                    print(f"      [OK] Found match: '{idx}'")
                    
                    # Found the row, extract recent years
                    row_data = search_df.loc[idx]
                    
                    # Get year columns - handle quarterly data like "Jun '25", "Dec '24", etc.
                    year_cols = []
                    for col in search_df.columns:
                        col_str = str(col)
                        try:
                            # Handle StockRow quarterly format like "Dec '24", "Jun '25", etc.
                            if "'" in col_str:
                                parts = col_str.split("'")
                                if len(parts) == 2:
                                    month_part = parts[0].strip()
                                    year_str = parts[1].strip()
                                    
                                    if len(year_str) == 2 and year_str.isdigit():
                                        # Convert 2-digit year to 4-digit
                                        year_int = int(year_str)
                                        if year_int <= 30:  # Assume 00-30 means 2000-2030
                                            year = 2000 + year_int
                                        else:  # 31-99 means 1931-1999
                                            year = 1900 + year_int
                                        
                                        # For quarterly data, we'll use the year-end quarters (Dec) 
                                        # as the primary annual data points, but include all quarters
                                        quarter_priority = 0
                                        if month_part.startswith('Dec'):
                                            quarter_priority = 4  # Highest priority for year-end
                                        elif month_part.startswith('Sep'):
                                            quarter_priority = 3  # Q3
                                        elif month_part.startswith('Jun'):
                                            quarter_priority = 2  # Q2
                                        elif month_part.startswith('Mar'):
                                            quarter_priority = 1  # Q1
                                        
                                        year_cols.append((col, year, quarter_priority, month_part))
                                        continue
                            
                            # Handle other year formats
                            if any(char.isdigit() for char in col_str):
                                # Extract 4-digit year from column name
                                year_match = None
                                for part in col_str.split():
                                    if len(part) == 4 and part.isdigit():
                                        year = int(part)
                                        if 2010 <= year <= 2030:
                                            year_match = year
                                            break
                                
                                if year_match:
                                    year_cols.append((col, year_match, 5, "Annual"))  # Highest priority for annual
                                    continue
                                
                                # Try to extract year from beginning of string
                                if len(col_str) >= 4 and col_str[:4].isdigit():
                                    year = int(col_str[:4])
                                    if 2010 <= year <= 2030:
                                        year_cols.append((col, year, 5, "Annual"))
                                        continue
                        except:
                            continue
                    
                    # Sort by year (most recent first), then by quarter priority (Dec quarters first)
                    year_cols.sort(key=lambda x: (x[1], x[2]), reverse=True)
                    
                    print(f"      [DATES] Found year columns: {[(f'{col}({year}-{quarter})' if len(col_data) > 3 else f'{col}({year})') for col_data in year_cols[:10] for col, year, priority, quarter in [col_data]]}")
                    
                    # Extract values for recent years/quarters
                    result = {}
                    processed_periods = set()
                    
                    for col, year, priority, period in year_cols:
                        try:
                            value = row_data[col]
                            if pd.notna(value):
                                # Convert to float if possible
                                if isinstance(value, str):
                                    # Clean up the value - remove commas, parentheses, etc.
                                    clean_value = value.replace(',', '').replace('$', '').strip()
                                    
                                    # Handle negative values in parentheses
                                    if clean_value.startswith('(') and clean_value.endswith(')'):
                                        clean_value = '-' + clean_value[1:-1]
                                    
                                    # Try to convert to float
                                    try:
                                        numeric_value = float(clean_value)
                                    except ValueError:
                                        continue
                                else:
                                    # Already numeric
                                    numeric_value = float(value)
                                
                                # Create proper period key
                                if hasattr(self, 'preferred_data_type') and self.preferred_data_type == 'Quarterly':
                                    # For quarterly data, use full quarter identifier
                                    period_key = f"{year}Q{self._quarter_to_number(period)}" if period != "Annual" else year
                                else:
                                    # For annual data, use just the year
                                    period_key = year
                                
                                if period_key not in processed_periods:
                                    result[period_key] = numeric_value
                                    processed_periods.add(period_key)
                                    
                                    # Stop after we have enough periods
                                    if len(processed_periods) >= years_to_extract:
                                        break
                                        
                        except Exception as e:
                            print(f"      [WARNING]  Error processing {col}: {e}")
                            continue
                    
                    if result:
                        print(f"      [CHART] Extracted data: {result}")
                        return result
                    else:
                        print(f"      [ERROR] No valid numeric data found")
        
        print(f"      [ERROR] No matches found for any search terms")
        return {}
    
    def extract_shares_outstanding(self):
        """Extract shares outstanding data for fair value calculation."""
        print(f"\n[SEARCH] Extracting shares outstanding for {self.company_name}...")
        
        # Determine how many periods to extract based on data type
        if hasattr(self, 'preferred_data_type') and self.preferred_data_type == 'Quarterly':
            periods_to_extract = 40  # About 10 years of quarterly data
        else:
            periods_to_extract = 10  # 10 years of annual data
        
        # Search terms for shares outstanding
        shares_terms = [
            'shares outstanding', 'common shares outstanding', 'basic shares outstanding',
            'weighted average shares outstanding', 'diluted shares outstanding',
            'common stock outstanding', 'shares issued and outstanding',
            'weighted average common shares', 'basic common shares outstanding',
            'diluted weighted average shares'
        ]
        
        # Try to find shares outstanding in income statement first (usually weighted average)
        shares_outstanding = self._find_financial_item(self.income_statement, shares_terms, periods_to_extract)
        
        # If not found in income statement, try balance sheet
        if not shares_outstanding and self.balance_sheet is not None:
            shares_outstanding = self._find_financial_item(self.balance_sheet, shares_terms, periods_to_extract)
        
        # If still not found, try cash flow statement
        if not shares_outstanding and self.cash_flow is not None:
            shares_outstanding = self._find_financial_item(self.cash_flow, shares_terms, periods_to_extract)
        
        print(f"   [RESULT] Found shares outstanding for {len(shares_outstanding)} periods")
        return shares_outstanding

    def extract_owner_earnings_components(self):
        """Extract all components needed for owner earnings calculation."""
        print(f"\n[SEARCH] Extracting Owner Earnings components for {self.company_name}...")
        
        # Determine how many periods to extract based on data type
        if hasattr(self, 'preferred_data_type') and self.preferred_data_type == 'Quarterly':
            periods_to_extract = 40  # About 10 years of quarterly data
        else:
            periods_to_extract = 10  # 10 years of annual data
        
        # Net Income (from Income Statement)
        net_income_terms = [
            'net income', 'net earnings', 'profit after tax', 'net profit',
            'income from continuing operations', 'earnings'
        ]
        net_income = self._find_financial_item(self.income_statement, net_income_terms, periods_to_extract)
        
        # Depreciation & Amortization (from Cash Flow Statement or Income Statement)
        depreciation_terms = [
            'depreciation', 'amortization', 'depreciation and amortization',
            'depletion', 'depreciation & amortization'
        ]
        depreciation = self._find_financial_item(self.cash_flow, depreciation_terms, periods_to_extract)
        if not depreciation:
            depreciation = self._find_financial_item(self.income_statement, depreciation_terms, periods_to_extract)
        
        # Capital Expenditures (from Cash Flow Statement)
        capex_terms = [
            'capital expenditures', 'capex', 'capital expenditure',
            'purchase of property', 'investments in property', 'additions to property'
        ]
        capex = self._find_financial_item(self.cash_flow, capex_terms, periods_to_extract)
        
        # Working Capital Changes - try multiple approaches
        working_capital_change = {}
        
        # Method 1: Direct working capital line item
        working_capital_terms = [
            'working capital', 'change in working capital', 'changes in working capital',
            'working capital changes', 'change in net working capital'
        ]
        working_capital_change = self._find_financial_item(self.cash_flow, working_capital_terms, periods_to_extract)
        
        # Method 2: Calculate from balance sheet (more accurate)
        if not working_capital_change and self.balance_sheet is not None:
            print(f"   [TIP] Calculating working capital changes from balance sheet...")
            working_capital_change = self._calculate_working_capital_from_balance_sheet(periods_to_extract)
        
        # Method 3: If still not found, calculate from cash flow components
        if not working_capital_change:
            print(f"   [TIP] Direct working capital not found, calculating from cash flow components...")
            
            # Get individual working capital components
            receivables_change = self._find_financial_item(self.cash_flow, 
                ['accounts receivable', 'receivables change', 'change in receivables'], periods_to_extract)
            
            inventory_change = self._find_financial_item(self.cash_flow, 
                ['inventory', 'change in inventory', 'change in inventories', 'inventories'], periods_to_extract)
            
            payables_change = self._find_financial_item(self.cash_flow, 
                ['accounts payable', 'payables change', 'change in payables', 'change in payables and accrued'], periods_to_extract)
            
            # Calculate working capital change if we have the components
            if receivables_change or inventory_change or payables_change:
                print(f"   [DATA] Found working capital components:")
                if receivables_change:
                    print(f"      - Receivables changes: {receivables_change}")
                if inventory_change:
                    print(f"      - Inventory changes: {inventory_change}")
                if payables_change:
                    print(f"      - Payables changes: {payables_change}")
                
                # Calculate combined working capital change
                # Note: Increases in receivables/inventory are negative for cash flow
                # Increases in payables are positive for cash flow
                all_years = set()
                if receivables_change:
                    all_years.update(receivables_change.keys())
                if inventory_change:
                    all_years.update(inventory_change.keys())
                if payables_change:
                    all_years.update(payables_change.keys())
                
                for year in all_years:
                    wc_change = 0
                    components = []
                    
                    if receivables_change and year in receivables_change:
                        wc_change += receivables_change[year]
                        components.append(f"Receivables: {receivables_change[year]:,.0f}")
                    
                    if inventory_change and year in inventory_change:
                        wc_change += inventory_change[year]
                        components.append(f"Inventory: {inventory_change[year]:,.0f}")
                    
                    if payables_change and year in payables_change:
                        wc_change += payables_change[year]
                        components.append(f"Payables: {payables_change[year]:,.0f}")
                    
                    working_capital_change[year] = wc_change
                    print(f"      [YEAR] {year}: {' + '.join(components)} = ${wc_change:,.0f}")
        
        # Store the components
        self.owner_earnings_data = {
            'net_income': net_income,
            'depreciation': depreciation,
            'capex': capex,
            'working_capital_change': working_capital_change
        }
        
        return self.owner_earnings_data
    
    def _calculate_working_capital_from_balance_sheet(self, periods_to_extract=40):
        """
        Calculate working capital changes from balance sheet data.
        Working Capital = Current Assets - Current Liabilities
        """
        print(f"   [DATA] Extracting working capital components from balance sheet...")
        
        # Find current assets and current liabilities
        current_assets = self._find_financial_item(self.balance_sheet, 
            ['total current assets', 'current assets'], periods_to_extract)
        
        current_liabilities = self._find_financial_item(self.balance_sheet, 
            ['total current liabilities', 'current liabilities'], periods_to_extract)
        
        if not current_assets and not current_liabilities:
            print(f"   [ERROR] Could not find current assets or liabilities in balance sheet")
            return {}
        
        # Calculate working capital for each year
        working_capital_levels = {}
        all_years = set()
        
        if current_assets:
            all_years.update(current_assets.keys())
            print(f"   [CHART] Current Assets: {current_assets}")
        
        if current_liabilities:
            all_years.update(current_liabilities.keys())
            print(f"   [DECLINE] Current Liabilities: {current_liabilities}")
        
        # Calculate working capital level for each year
        for year in all_years:
            assets = current_assets.get(year, 0) if current_assets else 0
            liabilities = current_liabilities.get(year, 0) if current_liabilities else 0
            working_capital_levels[year] = assets - liabilities
        
        print(f"   [MONEY] Working Capital Levels: {working_capital_levels}")
        
        # Also extract long-term debt to check for debt restructuring
        print(f"\n   [SEARCH] DEBT ANALYSIS FOR RESTRUCTURING CHECK:")
        debt_search_terms = ['long term debt', 'long-term debt', 'total debt', 'debt total']
        
        debt_data = None
        for search_term in debt_search_terms:
            debt_data = self._find_financial_item(self.balance_sheet, [search_term], periods_to_extract)
            if debt_data:
                print(f"   [DATA] Long-term Debt Levels: {debt_data}")
                # Calculate debt changes (limit display to avoid clutter)
                debt_periods = sorted(debt_data.keys())
                for i in range(1, min(len(debt_periods), 8)):  # Show max 7 periods to avoid clutter
                    prev_period = debt_periods[i-1]
                    curr_period = debt_periods[i]
                    debt_change = debt_data[curr_period] - debt_data[prev_period]
                    print(f"   [CREDIT] {curr_period}: Debt change from ${debt_data[prev_period]:,.0f} to ${debt_data[curr_period]:,.0f} = ${debt_change:,.0f}")
                break
        
        if not debt_data:
            print("   [ERROR] Could not find long-term debt information")
        
        print(f"\n   [DATA] WORKING CAPITAL CHANGES:")
        working_capital_changes = {}
        sorted_years = sorted(working_capital_levels.keys())
        
        for i in range(1, len(sorted_years)):
            current_year = sorted_years[i]
            previous_year = sorted_years[i-1]
            
            current_wc = working_capital_levels[current_year]
            previous_wc = working_capital_levels[previous_year]
            
            # Change in working capital (increase is negative for cash flow)
            wc_change = -(current_wc - previous_wc)  # Negative because increase uses cash
            working_capital_changes[current_year] = wc_change
            
            print(f"   [YEAR] {current_year}: WC change from ${previous_wc:,.0f} to ${current_wc:,.0f} = ${wc_change:,.0f}")
        
        return working_capital_changes

    def calculate_owner_earnings(self):
        """Calculate owner earnings for each available year."""
        if not self.owner_earnings_data:
            self.extract_owner_earnings_components()
        
        print(f"\n[MONEY] Calculating Owner Earnings for {self.company_name}...")
        
        # Get all available years
        all_years = set()
        for component in self.owner_earnings_data.values():
            all_years.update(component.keys())
        
        owner_earnings = {}
        
        for year in sorted(all_years, reverse=True):
            try:
                # Get components for this year
                net_income = self.owner_earnings_data.get('net_income', {}).get(year, 0)
                depreciation = self.owner_earnings_data.get('depreciation', {}).get(year, 0)
                capex = self.owner_earnings_data.get('capex', {}).get(year, 0)
                wc_change = self.owner_earnings_data.get('working_capital_change', {}).get(year, 0)
                
                # Calculate owner earnings
                # Note: CapEx is usually negative in cash flow, so we add it (which subtracts it from earnings)
                # Working capital increase is negative for cash flow, so we add it
                owner_earnings_value = net_income + depreciation + capex + wc_change
                
                owner_earnings[year] = {
                    'net_income': net_income,
                    'depreciation': depreciation,
                    'capex': capex,
                    'working_capital_change': wc_change,
                    'owner_earnings': owner_earnings_value
                }
                
            except Exception as e:
                print(f"[WARNING]  Error calculating owner earnings for {year}: {e}")
                continue
        
        return owner_earnings
    
    def calculate_fair_value_estimate(self, owner_earnings_data, shares_outstanding_data):
        """
        Calculate estimated fair stock price based on owner earnings per share.
        
        Args:
            owner_earnings_data: Dict of period -> owner earnings values
            shares_outstanding_data: Dict of period -> shares outstanding values
            
        Returns:
            dict: Fair value analysis including price estimate and metrics
        """
        if not owner_earnings_data or not shares_outstanding_data:
            return None
        
        print(f"\n[VALUATION] Calculating fair value estimate...")
        
        # Find common periods between owner earnings and shares data
        common_periods = set(owner_earnings_data.keys()) & set(shares_outstanding_data.keys())
        
        if not common_periods:
            print(f"   [WARNING] No matching periods found between earnings and shares data")
            return None
        
        # Calculate owner earnings per share for each period
        earnings_per_share = {}
        valid_periods = []
        
        for period in common_periods:
            oe = owner_earnings_data[period]['owner_earnings'] if isinstance(owner_earnings_data[period], dict) else owner_earnings_data[period]
            shares = shares_outstanding_data[period]
            
            # Skip periods with invalid data
            if shares > 0 and pd.notna(oe) and pd.notna(shares):
                eps = oe / shares
                earnings_per_share[period] = eps
                valid_periods.append(period)
                print(f"   [CALC] {period}: ${oe:,.0f} ÷ {shares:,.0f} shares = ${eps:.2f}/share")
        
        if not earnings_per_share:
            print(f"   [WARNING] No valid earnings per share calculations possible")
            return None
        
        # Calculate average owner earnings per share
        avg_eps = sum(earnings_per_share.values()) / len(earnings_per_share)
        
        # Calculate basic fair value estimates using common P/E-like multiples
        # Since owner earnings are more conservative than reported earnings,
        # we can use slightly higher multiples than traditional P/E
        fair_value_estimates = {
            'conservative_10x': avg_eps * 10,   # Very conservative 
            'moderate_15x': avg_eps * 15,       # Moderate valuation
            'growth_20x': avg_eps * 20,         # Growth company multiple
            'aggressive_25x': avg_eps * 25      # Aggressive/high-growth multiple
        }
        
        return {
            'periods_analyzed': len(valid_periods),
            'years_of_data': len(valid_periods),
            'avg_owner_earnings_per_share': avg_eps,
            'earnings_per_share_by_period': earnings_per_share,
            'fair_value_estimates': fair_value_estimates,
            'methodology': 'Average Owner Earnings Per Share × Valuation Multiple'
        }

    def calculate_annual_owner_earnings(self):
        """Calculate owner earnings using annual financial data."""
        # Load annual data specifically
        self.load_financial_statements_by_type('Annual')
        owner_earnings = self.calculate_owner_earnings()
        
        # Convert to DataFrame for consistency with workflow expectations
        if owner_earnings:
            df_data = []
            for year, data in owner_earnings.items():
                row = {
                    'Period': year,
                    'Net Income': data['net_income'],
                    'Depreciation': data['depreciation'],
                    'CapEx': data['capex'],
                    'Working Capital Change': data['working_capital_change'],
                    'Owner Earnings': data['owner_earnings']
                }
                df_data.append(row)
            
            import pandas as pd
            return pd.DataFrame(df_data)
        else:
            import pandas as pd
            return pd.DataFrame()
    
    def calculate_quarterly_owner_earnings(self):
        """Calculate owner earnings using quarterly financial data."""
        # Load quarterly data specifically  
        self.load_financial_statements_by_type('Quarterly')
        owner_earnings = self.calculate_owner_earnings()
        
        # Convert to DataFrame for consistency with workflow expectations
        if owner_earnings:
            df_data = []
            for year, data in owner_earnings.items():
                row = {
                    'Period': year,
                    'Net Income': data['net_income'],
                    'Depreciation': data['depreciation'],
                    'CapEx': data['capex'],
                    'Working Capital Change': data['working_capital_change'],
                    'Owner Earnings': data['owner_earnings']
                }
                df_data.append(row)
            
            import pandas as pd
            return pd.DataFrame(df_data)
        else:
            import pandas as pd
            return pd.DataFrame()
    
    def print_analysis_report(self):
        """Print a comprehensive analysis report."""
        owner_earnings = self.calculate_owner_earnings()
        
        if not owner_earnings:
            print("[ERROR] No owner earnings data could be calculated.")
            return
        
        print(f"\n" + "=" * 60)
        print(f"[DATA] OWNER EARNINGS ANALYSIS - {self.company_name.upper()}")
        print("=" * 60)
        
        print(f"\n[TIP] Owner Earnings Formula:")
        print(f"   Net Income + Depreciation/Amortization - CapEx - Working Capital Changes")
        
        print(f"\n[CHART] DETAILED BREAKDOWN BY YEAR:")
        print("-" * 60)
        
        for year in sorted(owner_earnings.keys(), reverse=True):
            data = owner_earnings[year]
            print(f"\n[YEAR] {year}:")
            print(f"   Net Income:           ${data['net_income']:>15,.0f}")
            print(f"   + Depreciation:       ${data['depreciation']:>15,.0f}")
            print(f"   + CapEx:              ${data['capex']:>15,.0f}")
            print(f"   + WC Change:          ${data['working_capital_change']:>15,.0f}")
            print(f"   = Owner Earnings:     ${data['owner_earnings']:>15,.0f}")
            
            # Calculate margin
            if data['net_income'] != 0:
                margin = (data['owner_earnings'] / data['net_income']) * 100
                print(f"   Owner Earnings/NI:    {margin:>15.1f}%")
        
        # Calculate trends
        years_list = sorted(owner_earnings.keys(), reverse=True)
        if len(years_list) >= 2:
            recent_oe = owner_earnings[years_list[0]]['owner_earnings']
            older_oe = owner_earnings[years_list[1]]['owner_earnings']
            
            if older_oe != 0:
                growth = ((recent_oe - older_oe) / abs(older_oe)) * 100
                print(f"\n[DATA] YEAR-OVER-YEAR GROWTH:")
                print(f"   {years_list[1]} to {years_list[0]}: {growth:+.1f}%")
        
        # Calculate average
        oe_values = [data['owner_earnings'] for data in owner_earnings.values()]
        avg_oe = sum(oe_values) / len(oe_values)
        print(f"\n[DATA] SUMMARY STATISTICS:")
        print(f"   Average Owner Earnings: ${avg_oe:,.0f}")
        
        # Show correct period type based on data type
        period_type = "Quarters" if hasattr(self, 'preferred_data_type') and self.preferred_data_type == 'Quarterly' else "Years"
        print(f"   {period_type} analyzed: {len(owner_earnings)}")
        
        # Add fair value estimation based on owner earnings per share
        try:
            shares_outstanding = self.extract_shares_outstanding()
            if shares_outstanding:
                fair_value_analysis = self.calculate_fair_value_estimate(owner_earnings, shares_outstanding)
                
                if fair_value_analysis:
                    print(f"\n[VALUATION] ESTIMATED FAIR STOCK PRICE:")
                    print("-" * 60)
                    print(f"   Based on {fair_value_analysis['years_of_data']} years of data")
                    print(f"   Average Owner Earnings/Share: ${fair_value_analysis['avg_owner_earnings_per_share']:.2f}")
                    print(f"   Methodology: {fair_value_analysis['methodology']}")
                    
                    print(f"\n[PRICE] Fair Value Estimates:")
                    estimates = fair_value_analysis['fair_value_estimates']
                    print(f"   Conservative (10x):   ${estimates['conservative_10x']:>8.2f}")
                    print(f"   Moderate (15x):       ${estimates['moderate_15x']:>8.2f}")
                    print(f"   Growth (20x):         ${estimates['growth_20x']:>8.2f}")
                    print(f"   Aggressive (25x):     ${estimates['aggressive_25x']:>8.2f}")
                    
                    print(f"\n[DETAIL] Owner Earnings Per Share by Period:")
                    for period in sorted(fair_value_analysis['earnings_per_share_by_period'].keys(), reverse=True):
                        eps = fair_value_analysis['earnings_per_share_by_period'][period]
                        print(f"   {period}: ${eps:.2f}/share")
                    
                    print(f"\n[NOTE] These estimates use Owner Earnings (more conservative than")
                    print(f"       reported earnings) with traditional P/E-style multiples.")
                    print(f"       Consider market conditions, growth prospects, and risk factors.")
                else:
                    print(f"\n[VALUATION] Could not calculate fair value - insufficient matching data")
            else:
                print(f"\n[VALUATION] Fair value calculation skipped - shares outstanding not found")
                print(f"   [TIP] Ensure financial statements include shares outstanding data")
        except Exception as e:
            print(f"\n[VALUATION] Fair value calculation error: {e}")
        
        return owner_earnings

def find_recent_xlsx_file(directory="./downloaded_files"):
    """Find the most recently modified XLSX file in the directory."""
    if not os.path.exists(directory):
        return None
    
    xlsx_files = glob.glob(os.path.join(directory, "*.xlsx"))
    if not xlsx_files:
        return None
    
    # Sort by modification time (most recent first)
    xlsx_files.sort(key=os.path.getmtime, reverse=True)
    return xlsx_files[0]

def find_ticker_xlsx_file(ticker, directory="./downloaded_files"):
    """Find the most recent XLSX file for a specific ticker."""
    if not os.path.exists(directory):
        return None
    
    # Clean ticker (remove dots, make lowercase)
    clean_ticker = ticker.replace('.', '').lower()
    
    # Look for files matching the ticker pattern
    pattern = os.path.join(directory, f"*{clean_ticker}*.xlsx")
    xlsx_files = glob.glob(pattern)
    
    if not xlsx_files:
        print(f"[ERROR] No XLSX files found for ticker '{ticker}' in {directory}")
        print(f"[SEARCH] Looked for pattern: *{clean_ticker}*.xlsx")
        return None
    
    # Sort by modification time (most recent first) 
    xlsx_files.sort(key=os.path.getmtime, reverse=True)
    print(f"[FOUND] Using ticker-specific file: {os.path.basename(xlsx_files[0])}")
    return xlsx_files[0]

def main():
    """Main function to run the owner earnings analysis."""
    print("Warren Buffett Owner Earnings Calculator")
    print("=" * 45)
    
    # Get XLSX file path
    xlsx_file = None
    
    if len(sys.argv) > 1:
        # Check if argument is a ticker or file path
        arg = sys.argv[1]
        
        if arg.endswith('.xlsx') and os.path.exists(arg):
            # Direct file path provided
            xlsx_file = arg
            print(f"[FILE] Using specified file: {os.path.basename(xlsx_file)}")
        else:
            # Treat as ticker symbol
            ticker = arg.upper()
            print(f"[TICKER] Looking for files for ticker: {ticker}")
            xlsx_file = find_ticker_xlsx_file(ticker)
            
            if not xlsx_file:
                print(f"[FALLBACK] No ticker-specific files found, using most recent file...")
                xlsx_file = find_recent_xlsx_file()
    else:
        # Look for recent file in downloaded_files directory
        xlsx_file = find_recent_xlsx_file()
        if not xlsx_file:
            print("[ERROR] No XLSX files found in ./downloaded_files directory")
            print("[TIP] Usage: python owner_earnings_fixed.py <TICKER_SYMBOL>")
            print("[TIP] Usage: python owner_earnings_fixed.py <path_to_xlsx_file>")
            print("[TIP] Or place XLSX files in ./downloaded_files directory")
            return
        
        print(f"[FILE] Using most recent file: {os.path.basename(xlsx_file)}")
    
    if not xlsx_file:
        print("[ERROR] No suitable XLSX file found")
        return
    # Process both Annual and Quarterly data
    data_types = ['Annual', 'Quarterly']
    
    for data_type in data_types:
        print(f"\n{'='*60}")
        print(f"[DATA] PROCESSING {data_type.upper()} DATA")
        print(f"{'='*60}")
        
        # Create calculator and configure for specific data type
        calculator = OwnerEarningsCalculator(xlsx_file)
        calculator.preferred_data_type = data_type
        
        if calculator.load_financial_statements_by_type(data_type):
            # Show debug info to understand the data structure
            if data_type == 'Annual':  # Only show debug for first run
                calculator.debug_financial_data()
            
            owner_earnings = calculator.print_analysis_report()
            
            # Save results to CSV
            if owner_earnings:
                # Create data directory if it doesn't exist
                data_dir = "data"
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                
                suffix = 'annual' if data_type == 'Annual' else 'quarterly'
                output_file = os.path.join(data_dir, f"owner_earnings_{calculator.company_name}_{suffix}.csv")
                
                # Convert to DataFrame for easy CSV export
                df_data = []
                for year, data in owner_earnings.items():
                    row = {'Period': year}
                    row.update(data)
                    df_data.append(row)
                
                df = pd.DataFrame(df_data)
                df.to_csv(output_file, index=False)
                print(f"\n[SAVE] Results saved to: {output_file}")
        else:
            print(f"[ERROR] Failed to load {data_type.lower()} financial statements")

if __name__ == "__main__":
    main()
