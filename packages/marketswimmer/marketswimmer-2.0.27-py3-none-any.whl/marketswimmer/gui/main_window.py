import sys
import os
import subprocess
import threading
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QInputDialog, QTextEdit, 
                             QMessageBox, QProgressBar, QFrame, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor

# Optional logging - only import if available
try:
    from logger_config import setup_logger, log_function_entry, log_gui_event, log_subprocess_call, log_function_exit
    LOGGING_ENABLED = True
    logger = setup_logger()
except ImportError:
    # Fallback dummy functions if logging not available
    def log_function_entry(*args, **kwargs): pass
    def log_gui_event(*args, **kwargs): pass
    def log_subprocess_call(*args, **kwargs): pass
    def log_function_exit(*args, **kwargs): pass
    
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def debug(self, msg): pass
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
    
    LOGGING_ENABLED = False
    logger = DummyLogger()

class WorkerThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        log_function_entry(f"WorkerThread.run() args=[{self.command}]")
        logger.info(f"Starting subprocess: {self.command}")
        
        if LOGGING_ENABLED:
            log_subprocess_call()
        
        try:
            # Keep the original working directory instead of changing to GUI directory
            # This ensures files are created where the user expects them
            original_cwd = os.getcwd()
            logger.debug(f"Using working directory: {original_cwd}")
            
            # Create the subprocess
            logger.debug(f"Creating subprocess: {self.command}")
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=original_cwd  # Explicitly set working directory
            )
            
            logger.info(f"Subprocess PID: {process.pid}")
            
            # Read output in real-time
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.output_signal.emit(line.rstrip())
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                logger.info(f"Subprocess completed successfully with return code: {process.returncode}")
                self.finished_signal.emit()
            else:
                error_msg = f"Process failed with return code: {process.returncode}"
                logger.error(error_msg)
                self.error_signal.emit(error_msg)
                
        except Exception as e:
            error_msg = f"Error running subprocess: {str(e)}"
            logger.error(error_msg)
            self.error_signal.emit(error_msg)

class MarketSwimmerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        log_function_entry("MarketSwimmerGUI.__init__()")
        log_gui_event("GUI_INIT_START")
        
        self.setWindowTitle("MarketSwimmer - Financial Analysis Tool")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: #fafafa;
            }
            QLabel {
                font-size: 12px;
                color: #333;
            }
        """)

        # Initialize UI
        self.init_ui()
        
        # Current ticker
        self.current_ticker = ""
        
        logger.info("GUI window created successfully")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("MarketSwimmer Financial Analysis")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Ticker input section
        ticker_group = QGroupBox("Stock Ticker Selection")
        ticker_layout = QHBoxLayout(ticker_group)
        
        self.ticker_label = QLabel("Selected Ticker: None")
        self.ticker_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2980b9;")
        
        self.select_ticker_button = QPushButton("Select Ticker")
        self.select_ticker_button.clicked.connect(self.select_ticker)
        
        ticker_layout.addWidget(self.ticker_label)
        ticker_layout.addStretch()
        ticker_layout.addWidget(self.select_ticker_button)
        
        main_layout.addWidget(ticker_group)
        
        # Analysis buttons section
        analysis_group = QGroupBox("Analysis Options")
        analysis_layout = QGridLayout(analysis_group)
        
        # Individual analysis buttons
        self.download_button = QPushButton("Download Financial Data")
        self.download_button.clicked.connect(self.download_data)
        self.download_button.setEnabled(False)
        
        self.earnings_button = QPushButton("Calculate Owner Earnings")
        self.earnings_button.clicked.connect(self.calculate_earnings)
        self.earnings_button.setEnabled(False)
        
        self.visualize_button = QPushButton("Create Visualizations")
        self.visualize_button.clicked.connect(self.create_visualizations)
        self.visualize_button.setEnabled(False)
        
        self.complete_button = QPushButton("Complete Analysis")
        self.complete_button.clicked.connect(self.run_full_analysis)
        self.complete_button.setEnabled(False)
        self.complete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                font-size: 16px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Arrange buttons in grid
        analysis_layout.addWidget(self.download_button, 0, 0)
        analysis_layout.addWidget(self.earnings_button, 0, 1)
        analysis_layout.addWidget(self.visualize_button, 1, 0)
        analysis_layout.addWidget(self.complete_button, 1, 1)
        
        main_layout.addWidget(analysis_group)
        
        # Console output section
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout(console_group)
        
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(300)
        console_layout.addWidget(self.console_output)
        
        # Clear console button
        clear_button = QPushButton("Clear Console")
        clear_button.clicked.connect(self.clear_console)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        console_layout.addWidget(clear_button)
        
        main_layout.addWidget(console_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select a ticker to begin analysis")

    def select_ticker(self):
        log_gui_event("BUTTON_CLICK", "Select Ticker button clicked")
        
        ticker, ok = QInputDialog.getText(self, 'Select Ticker', 'Enter stock ticker symbol:')
        
        if ok and ticker:
            ticker = ticker.upper().strip()
            self.current_ticker = ticker
            self.ticker_label.setText(f"Selected Ticker: {ticker}")
            
            # Enable analysis buttons
            self.download_button.setEnabled(True)
            self.earnings_button.setEnabled(True)
            self.visualize_button.setEnabled(True)
            self.complete_button.setEnabled(True)
            
            self.console_output.append(f">> Ticker selected: {ticker}")
            self.statusBar().showMessage(f"Ticker selected: {ticker} - Ready for analysis")
            
            logger.info(f"Ticker selected: {ticker}")

    def download_data(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Download Data button clicked")
        logger.info(f"Starting data download for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Starting data download for {self.current_ticker}...")
        self.disable_buttons()
        self.show_progress()
        
        # Use the modern CLI for data analysis
        # Fix: Use the correct Python installation path instead of sys.executable
        python_exe = r"C:\Users\jerem\AppData\Local\Programs\Python\Python312\python.exe"
        command = f'"{python_exe}" -m marketswimmer analyze {self.current_ticker} --force'
        self.run_command(command)

    def calculate_earnings(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Calculate Earnings button clicked")
        logger.info(f"Starting earnings calculation for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Calculating owner earnings for {self.current_ticker}...")
        self.disable_buttons()
        self.show_progress()
        
        # Fix: Use the correct Python installation path instead of sys.executable
        python_exe = r"C:\Users\jerem\AppData\Local\Programs\Python\Python312\python.exe"
        command = f'"{python_exe}" owner_earnings_fixed.py'
        self.run_command(command)

    def create_visualizations(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Create Visualizations button clicked")
        logger.info(f"Starting visualization creation for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Creating visualizations for {self.current_ticker}...")
        self.disable_buttons()
        self.show_progress()
        
        # Use the MarketSwimmer visualization command instead of a standalone script
        # Fix: Use the correct Python installation path instead of sys.executable
        python_exe = r"C:\Users\jerem\AppData\Local\Programs\Python\Python312\python.exe"
        command = f'"{python_exe}" -m marketswimmer visualize --ticker {self.current_ticker}'
        self.run_command(command)

    def run_full_analysis(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Complete Analysis button clicked")
        logger.info(f"Starting complete analysis for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Starting complete analysis for {self.current_ticker}...")
        self.console_output.append("This will run the full analysis pipeline:")
        self.console_output.append("  1. Download financial data")
        self.console_output.append("  2. Calculate owner earnings")  
        self.console_output.append("  3. Create visualizations")
        self.console_output.append("Please wait...\n")
        
        self.disable_buttons()
        self.show_progress()
        
        # Use the new MarketSwimmer CLI automation
        # Fix: Use the correct Python installation path instead of sys.executable
        python_exe = r"C:\Users\jerem\AppData\Local\Programs\Python\Python312\python.exe"
        command = f'"{python_exe}" -m marketswimmer analyze {self.current_ticker}'
        logger.info(f"Full analysis command: {command}")
        
        self.run_command(command)

    def run_command(self, command):
        """Run a command in a separate thread"""
        self.worker_thread = WorkerThread(command)
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_process_finished)
        self.worker_thread.error_signal.connect(self.on_process_error)
        self.worker_thread.start()

    def update_console(self, text):
        """Update console output with new text"""
        self.console_output.append(text)
        
        # Auto-scroll to bottom
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console_output.setTextCursor(cursor)

    def on_process_finished(self):
        """Handle process completion"""
        self.console_output.append("\n>> Process completed successfully!")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage(f"Analysis completed for {self.current_ticker}")
        
        logger.info("Process completed successfully")

    def on_process_error(self, error_msg):
        """Handle process error"""
        self.console_output.append(f"\nERROR: {error_msg}")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Error occurred during analysis")
        
        logger.error(f"Process error: {error_msg}")

    def disable_buttons(self):
        """Disable all analysis buttons during processing"""
        self.download_button.setEnabled(False)
        self.earnings_button.setEnabled(False)
        self.visualize_button.setEnabled(False)
        self.complete_button.setEnabled(False)

    def enable_buttons(self):
        """Enable all analysis buttons after processing"""
        if self.current_ticker:
            self.download_button.setEnabled(True)
            self.earnings_button.setEnabled(True)
            self.visualize_button.setEnabled(True)
            self.complete_button.setEnabled(True)

    def show_progress(self):
        """Show indeterminate progress bar"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)

    def clear_console(self):
        """Clear the console output"""
        self.console_output.clear()
        self.console_output.append("Console cleared.")
        
        logger.info("Console cleared by user")

def main():
    log_function_entry("main()")
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("MarketSwimmer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MarketSwimmer Analytics")
    
    # Create and show the main window
    window = MarketSwimmerGUI()
    window.show()
    
    logger.info("MarketSwimmer GUI started successfully")
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
