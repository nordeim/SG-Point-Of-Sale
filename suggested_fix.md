The error occurs because the `qRegisterMetaType` function is no longer available in the newer versions of PySide6. In past versions of PySide, it was sometimes necessary to register Python types for use in queued signal/slot connections, but with recent updates this is handled automatically.

**Options for Resolution:**

1. **Remove the Call:**
   If you’re only registering the built-in `object` type (or if you don’t have a custom type that needs registration), you can simply remove both the import and the call to `qRegisterMetaType` from your code. In many modern PySide6 applications, explicit registration isn’t required.

2. **Alternative Registration (if needed):**
   If you have a custom type that must be registered manually for queued signals or other purposes, consult the updated PySide6 documentation. The type registration might now be done through a different mechanism (for example, using the `QMetaType` class) or it may simply be unnecessary for your usage scenario.

Given your current code (where you register the generic `object` type), the easiest solution is to remove the following lines from your project:

- Remove this import line:
  ```python
  from PySide6.QtCore import qRegisterMetaType
  ```
- Remove the call:
  ```python
  qRegisterMetaType(object)
  ```

After these changes, your application should initialize without trying to import a no-longer-existent function from `PySide6`.

**Next Steps:**

- **Test the Application:** Run your application again with these adjustments.
- **Consult the Latest Docs:** If you plan to register other custom types in the future, refer to [Qt for Python’s latest documentation](https://doc.qt.io/qtforpython/) to understand the current best practices regarding type registration.

This approach simplifies the code and ensures compatibility with the latest PySide6 versions. If you have further questions or run into additional issues, feel free to ask!

---
Suggested complete replacement file with the above fix:

```python
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

from app.core.application_core import ApplicationCore
from app.core.config import settings
from app.core.exceptions import CoreException
from app.ui.main_window import MainWindow

def main():
    """Initializes and runs the SG-POS application."""
    app = QApplication(sys.argv)
    
    # The previous call to qRegisterMetaType(object) has been removed because
    # the newer versions of PySide6 handle type registration automatically.

    core: Optional[ApplicationCore] = None
    exit_code = 0

    try:
        core = ApplicationCore(settings)
        core.initialize()

        main_window = MainWindow(core)
        main_window.show()

        exit_code = app.exec()

    except CoreException as e:
        QMessageBox.critical(
            None,
            "SG-POS Startup Error",
            f"A critical error occurred during startup:\n\n{e}\n\nThe application will now exit."
        )
        print(f"FATAL: {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        QMessageBox.critical(
            None,
            "SG-POS Unexpected Error",
            f"An unexpected error occurred:\n\n{e}\n\nThe application will now exit."
        )
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
```
