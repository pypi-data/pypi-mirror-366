# backend/gradio_livelog/utils.py

import logging
import queue
import time
from contextlib import contextmanager
from typing import Callable, List, Iterator, Dict, Any

class _QueueLogHandler(logging.Handler):
    """A private logging handler that directs log records into a queue."""
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord):
        self.log_queue.put(record)

@contextmanager
def capture_logs(disable_console: bool = False) -> Iterator[Callable[[], List[logging.LogRecord]]]:
    """
    A context manager to capture logs from the root logger.

    Temporarily attaches a handler to the root logger to intercept all log
    messages. If `disable_console` is True, it will also temporarily remove
    other console-based StreamHandlers to prevent duplicate output.

    Args:
        disable_console: If True, prevents logs from also being printed to the console.

    Yields:
        A function that, when called, returns a list of all log records captured
        since the last call.
    """
    log_queue = queue.Queue()
    queue_handler = _QueueLogHandler(log_queue)
    root_logger = logging.getLogger()

    original_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    removed_handlers = []
    if disable_console:
        for handler in root_logger.handlers[:]: # Iterate over a copy
            if isinstance(handler, logging.StreamHandler) and handler is not queue_handler:
                removed_handlers.append(handler)
                root_logger.removeHandler(handler)

    all_captured = [] 
    last_returned = 0 

    try:
        def get_captured_records():
            nonlocal last_returned
            while True:
                try:
                    all_captured.append(log_queue.get_nowait()) 
                except queue.Empty:
                    break
            new_records = all_captured[last_returned:]
            last_returned = len(all_captured)
            return new_records
        yield get_captured_records
    finally:
        root_logger.removeHandler(queue_handler)
        root_logger.setLevel(original_level)
        for handler in removed_handlers:
            root_logger.addHandler(handler)

class ProgressTracker:
    """
    A helper class to track and format progress updates for the LiveLog component.

    This class mimics some of the behavior of `tqdm`, calculating the rate of
    iterations per second and providing a structured dictionary for easy use
    with Gradio's `yield` mechanism.
    """
    def __init__(self, total: int, description: str = "Processing..."):
        """
        Initializes the progress tracker.

        Args:
            total: The total number of iterations for the process.
            description: A short, fixed description of the task being performed.
        """
        self.total = total
        self.description = description
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_update_item = 0
        self.rate = 0.0

    def update(self, advance: int = 1, status: str = "running", logs: List[Dict] = None, log_content: str = None) -> Dict[str, Any]:
        """
        Advances the progress and returns a dictionary formatted for the LiveLog component.

        Args:
            advance: The number of steps to advance the progress by (default is 1).
            status: The current status of the process ("running", "success", "error").
            logs: An optional list of all log dictionaries generated so far. If provided,
                  this list will be passed to the frontend, allowing the log view to be
                  updated simultaneously with the progress bar.
            log_content: An optional string to use as the progress bar's description for this
                         specific update, overriding the fixed description. This is useful
                         for showing the most recent log message as the progress description.

        Returns:
            A dictionary formatted for the LiveLog component's frontend.
        """
        self.current += advance
        self.current = min(self.current, self.total)

        now = time.time()
        delta_time = now - self.last_update_time
        delta_items = self.current - self.last_update_item

        # Stabilize the rate calculation by updating it periodically or at the very end.
        if delta_time > 0.1 or self.current == self.total:
            self.rate = delta_items / delta_time if delta_time > 0 else 0.0
            self.last_update_time = now
            self.last_update_item = self.current
        
        desc = log_content if log_content is not None else self.description
        
        return {
            "type": "progress",
            "current": self.current,
            "total": self.total,
            "desc": desc,
            "rate": self.rate,
            "status": status,
            "logs": logs or [],
        }