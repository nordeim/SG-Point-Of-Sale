# File: app/core/async_bridge.py
"""
Provides a robust, thread-safe bridge between the PySide6 (Qt) event loop
and the asyncio event loop. This prevents UI freezes during I/O-bound operations.
"""
import asyncio
import threading
from typing import Coroutine, Any, Callable, Optional, Union
import inspect
import sys # Import sys for sys.exc_info()

from PySide6.QtCore import QObject, QThread, Signal, Slot, QMetaObject, Qt, QCoreApplication
from PySide6.QtWidgets import QApplication

from app.core.exceptions import AsyncBridgeError

class AsyncWorker(QObject):
    """
    An object that lives in a QThread and runs an asyncio event loop.
    It accepts coroutines for execution and signals results back to the main thread.
    """
    # Signal emitted when an async task finishes (result, error)
    # The result and error can be anything, so we use object for broad typing.
    task_finished = Signal(object, object)

    def __init__(self, loop: asyncio.AbstractEventLoop, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._loop = loop
        self._tasks = set()
        self._running = True # Flag to control loop.run_forever()

    def stop(self):
        """Gracefully stops the asyncio loop."""
        self._running = False
        # Schedule loop stop and task cancellation in its own thread
        if self._loop.is_running():
            # Cancel all pending tasks, then stop the loop.
            # This must be done via call_soon_threadsafe from another thread.
            async def _stop_coro():
                for task in list(self._tasks):
                    task.cancel()
                # Wait for tasks to finish cancelling or timeout
                await asyncio.gather(*self._tasks, return_exceptions=True) # Gather ensures all tasks are attempted to be cancelled
                self._loop.stop()

            self._loop.call_soon_threadsafe(lambda: asyncio.create_task(_stop_coro()))
        else:
            # If loop is not running (e.g. already stopped or not yet started fully), just close.
            if not self._loop.is_closed():
                self._loop.close()

    def run_task(self, coro: Coroutine[Any, Any, Any], on_done_callback: Optional[Callable[[Any, Optional[Exception]], None]] = None):
        """
        Submits a coroutine to be run on the asyncio event loop in the worker thread.
        
        Args:
            coro: The awaitable (coroutine) to run.
            on_done_callback: An optional callable that will be invoked on the main UI thread
                              with the result or exception when the task completes.
                              Signature: `callback(result, error_or_none)`.
            This callback is in addition to the `task_finished` signal.
        """
        if not inspect.iscoroutine(coro):
            raise TypeError("Input must be a coroutine.")
        
        # Check if the loop is running. It might not be ready right after start_and_wait if tasks are submitted too quickly.
        if not self._loop.is_running() and not self._loop.is_closed():
            # If the loop is not yet running, schedule a startup task.
            # This covers the edge case where tasks are submitted right after start() but before loop.run_forever() fully kicks in.
            # This is primarily for robustness; usually, initialize() in ApplicationCore would ensure it's running.
            pass # No specific action, create_task in lambda below handles scheduling on self._loop

        def _create_and_run_task():
            task = self._loop.create_task(coro)
            self._tasks.add(task)

            def _done_callback(fut: asyncio.Future):
                self._tasks.discard(fut)
                result = None
                error = None
                try:
                    result = fut.result() # This will re-raise the exception if one occurred
                except asyncio.CancelledError:
                    error = AsyncBridgeError("Task cancelled.")
                except Exception as e:
                    # Capture original exception details
                    error = e
                
                # Use QMetaObject.invokeMethod to safely call the signal emission on the main thread
                # This ensures the signal is emitted from the correct thread.
                # Q_ARG is from PySide6.QtCore, but explicitly defining it here for clarity or if needed.
                QMetaObject.invokeMethod(self.task_finished, "emit",
                                         Qt.ConnectionType.QueuedConnection,
                                         QGenericArgument(object.__name__, result), # Use QGenericArgument
                                         QGenericArgument(object.__name__, error)) # Use QGenericArgument
                
                # Also invoke the direct callback if provided, on the main thread
                if on_done_callback:
                    QMetaObject.invokeMethod(QApplication.instance(), on_done_callback.__name__, # Call by name for safety
                                             Qt.ConnectionType.QueuedConnection,
                                             QGenericArgument(object.__name__, result),
                                             QGenericArgument(object.__name__, error))

            task.add_done_callback(_done_callback)

        # Schedule the task creation on the worker thread's event loop
        # This is safe because _create_and_run_task operates within the target loop.
        self._loop.call_soon_threadsafe(_create_and_run_task)


class AsyncWorkerThread(QThread):
    """
    A QThread that manages an asyncio event loop and an AsyncWorker.
    This is the actual thread that the asyncio loop runs on.
    """
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.worker: Optional[AsyncWorker] = None
        self._thread_started_event = threading.Event()
        self.finished.connect(self._cleanup_on_exit) # Connect to QThread's finished signal

    def run(self):
        """Entry point for the thread. Initializes and runs the asyncio event loop."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Initialize the AsyncWorker with the new loop and move it to this thread
        self.worker = AsyncWorker(self.loop)
        self.worker.moveToThread(self) # Ensure the worker's parentage is correct

        # Signal that the thread and loop are ready
        self._thread_started_event.set()

        # Run the event loop until stop() is called or tasks are done
        self.loop.run_forever() # Blocks until self.loop.stop() is called

        # After loop stops, perform final cleanup
        self.loop.close() # Close the event loop
        self.worker = None # Dereference worker
        self.loop = None # Dereference loop
        print(f"AsyncWorkerThread {threading.current_thread().name} loop closed.")


    def start_and_wait(self):
        """Starts the thread and waits until the event loop is ready."""
        if self.isRunning():
            print("AsyncWorkerThread is already running.", file=sys.stderr)
            return

        self._thread_started_event.clear() # Clear event before starting
        self.start() # Start the QThread, which calls self.run()
        if not self._thread_started_event.wait(timeout=5): # Wait up to 5 seconds for thread.run() to set event
            raise AsyncBridgeError("AsyncWorkerThread failed to start event loop in time.")
        if self.worker is None:
            raise AsyncBridgeError("AsyncWorker not initialized within the thread.")


    def stop_and_wait(self):
        """Stops the worker and the thread gracefully."""
        if not self.isRunning():
            print("AsyncWorkerThread is not running, nothing to stop.", file=sys.stderr)
            return

        if self.worker:
            self.worker.stop() # Signal the worker to stop its loop gracefully
        
        if not self.wait(timeout=10000): # Wait for the thread to actually finish (timeout 10s)
            # If thread doesn't terminate, consider logging a warning or forceful termination
            print("Warning: AsyncWorkerThread did not terminate gracefully.", file=sys.stderr)
            self.terminate() # Forceful termination if not graceful (not recommended)
            self.wait() # Wait for termination

    @Slot()
    def _cleanup_on_exit(self):
        """Slot connected to QThread.finished for final cleanup. This runs on the main thread."""
        print("AsyncWorkerThread finished signal received. Final cleanup on main thread.")
        # Any main thread cleanup related to this thread can go here.


# Q_ARG helper for invokeMethod
# Note: For complex types or custom classes, `Q_ARG` might not serialize correctly across threads
# for `Qt.QueuedConnection`. Simple Python primitives, lists, dicts, and dataclasses work well.
# It's generally safer to pass raw Python objects and let the slot handle them.
from PySide6.QtCore import QGenericArgument # Renamed to QGenericArgument
