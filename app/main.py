# File: app/main.py
"""
SG-POS Application Entry Point.

This script initializes the core application components, sets up the asynchronous
bridge, creates the main UI window, and starts the Qt event loop.
"""
import sys
import asyncio
from PySide6.QtWidgets import QApplication

from app.core.config import settings
from app.core.application_core import ApplicationCore
from app.core.async_bridge import AsyncWorker # To be fully implemented later
from app.ui.main_window import MainWindow

def main():
    """Initializes and runs the SG-POS application."""
    # 1. Create the Qt Application instance
    app = QApplication(sys.argv)

    # 2. Initialize the Application Core with settings
    # This reads the .env.dev file and prepares the configuration
    core = ApplicationCore(settings)
    
    # 3. Asynchronous setup
    # In a real scenario, this would involve starting the async thread
    # and event loop managed by the async_bridge. For Stage 1, we can
    # defer the full implementation.
    
    # Run async initialization for the core (e.g., connect to DB)
    # A simple way to run an async function from a sync context
    try:
        asyncio.run(core.initialize())
    except Exception as e:
        # A proper UI should be shown here
        print(f"FATAL: Failed to initialize application core: {e}")
        sys.exit(1)

    # 4. Create and show the main window
    # The `core` object is passed to the main window, making it available
    # to all child UI components for dependency injection.
    main_window = MainWindow(core)
    main_window.show()

    # 5. Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
