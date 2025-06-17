# File: app/core/async_bridge.py
"""
Provides a robust, thread-safe bridge between the PySide6 (Qt) event loop
and the asyncio event loop. This prevents UI freezes during I/O-bound operations.
"""
import asyncio
import threading
from typing import Coroutine, Any, Callable, Optional
import inspect
import sys
from concurrent.futures import Future

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication

from app.core.exceptions import AsyncBridgeError

class AsyncWorker(QObject):
    """
    An object that lives in a QThread and runs an asyncio event loop.
    It accepts coroutines for execution and signals results back to the main thread.
    """
    # FIX: A new signal specifically to carry the callback and its results
    # This is the key to safe, cross-thread callback invocation.
    callback_ready = Signal(object, object, object)

    def __init__(self, loop: asyncio.AbstractEventLoop, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._loop = loop
        self._tasks = set()

    def stop(self, final_coro: Optional[Coroutine] = None):
        """Gracefully stops the asyncio event loop, optionally running one final coroutine."""
        if self._loop.is_running():
            async def _stop_coro():
                if final_coro:
                    try:
                        await final_coro
                    except Exception as e:
                        print(f"Error during final shutdown coroutine: {e}", file=sys.stderr)
                
                tasks = [task for task in self._tasks if not task.done()]
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                self._loop.stop()

            self._loop.call_soon_threadsafe(lambda: asyncio.create_task(_stop_coro()))

    def run_task(self, coro: Coroutine[Any, Any, Any], on_done_callback: Optional[Callable] = None):
        """Submits a fire-and-forget coroutine to be run on the event loop."""
        if not inspect.iscoroutine(coro):
            raise TypeError("Input must be a coroutine.")
        
        def _task_wrapper():
            task = self._loop.create_task(coro)
            self._tasks.add(task)
            task.add_done_callback(lambda fut: self._on_task_completed(fut, on_done_callback))
            task.add_done_callback(lambda fut: self._tasks.discard(fut))

        self._loop.call_soon_threadsafe(_task_wrapper)

    def run_task_and_wait(self, coro: Coroutine) -> Any:
        """Submits a coroutine and blocks until it returns a result."""
        if not self._loop.is_running():
            raise AsyncBridgeError("Cannot run task: event loop is not running.")
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def _on_task_completed(self, fut: asyncio.Future, on_done_callback: Optional[Callable]):
        result, error = None, None
        try:
            result = fut.result()
        except asyncio.CancelledError:
            error = AsyncBridgeError("Task was cancelled.")
        except Exception as e:
            error = e
        
        if on_done_callback:
            # FIX: Emit a signal containing the callback and its arguments.
            # This is thread-safe and lets the main thread execute the callback.
            self.callback_ready.emit(on_done_callback, result, error)

class AsyncWorkerThread(QThread):
    """A QThread that manages an asyncio event loop and an AsyncWorker."""
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.worker: Optional[AsyncWorker] = None
        self._thread_started_event = threading.Event()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.worker = AsyncWorker(self.loop)
        # The worker's signals will be connected from the main thread after it starts.
        self._thread_started_event.set()
        self.loop.run_forever()
        self.loop.close()

    def start_and_wait(self):
        if self.isRunning(): return
        self._thread_started_event.clear()
        self.start()
        if not self._thread_started_event.wait(timeout=5):
            raise AsyncBridgeError("AsyncWorkerThread failed to start event loop in time.")

    def stop_and_wait(self, final_coro: Optional[Coroutine] = None):
        if not self.isRunning() or not self.worker: return
        self.worker.stop(final_coro)
        if not self.wait(5000):
            print("Warning: AsyncWorkerThread did not terminate gracefully.", file=sys.stderr)
            self.terminate()
