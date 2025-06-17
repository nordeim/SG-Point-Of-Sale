# File: app/main.py
"""
SG-POS Application Entry Point.

This script initializes the core application components, sets up the asynchronous
bridge, creates the main UI window, and starts the Qt event loop.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Optional
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import qRegisterMetaType

from app.core.application_core import ApplicationCore
from app.core.config import settings
from app.core.exceptions import CoreException
from app.ui.main_window import MainWindow

def main():
    """Initializes and runs the SG-POS application."""
    app = QApplication(sys.argv)
    
    # FIX: Register the generic 'object' type for use in queued signals/slots.
    # This must be done after QApplication is instantiated.
    qRegisterMetaType(object)

    core: Optional[ApplicationCore] = None
    exit_code = 0

    try:
        core = ApplicationCore(settings)
        core.initialize()

        main_window = MainWindow(core)
        main_window.show()

        exit_code = app.exec()

    except CoreException as e:
        QMessageBox.critical(None, "SG-POS Startup Error", f"A critical error occurred during startup:\n\n{e}\n\nThe application will now exit.")
        print(f"FATAL: {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        QMessageBox.critical(None, "SG-POS Unexpected Error", f"An unexpected error occurred:\n\n{e}\n\nThe application will now exit.")
        print(f"FATAL: Unexpected error: {e}", file=sys.stderr)
        exit_code = 1
    finally:
        if core:
            print("Shutting down core resources...")
            core.shutdown()
            print("Shutdown complete.")

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
