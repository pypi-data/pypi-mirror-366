import inspect
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Sequence

from dora import Node


def on_event(event_type: str, event_id: str | Sequence[str] | set[str] | None, run_async: bool = False) -> Callable:
    """Decorator to mark a method as an event handler.

    Args:
        event_type: The type of event to handle, e.g., "INPUT" or "OUTPUT".
        event_id: The ID or IDs of the event(s) to handle. Either a string or some set/sequence of strings can be used.
        run_async: Whether to run the handler async. If True, the method will be dispatched on a background thread.
    """
    if isinstance(event_id, str) or event_id is None:
        event_ids = {event_id}
    else:
        event_ids = set(event_id)

    def decorator(method: Callable) -> Callable:
        method.__event_handler__ = (event_type, event_ids)
        method.__run_async__ = run_async  # mark async execution
        return method

    return decorator


class DoraNode:
    """Convenience wrapper for a `dora-rs` Node that cleans up event handling."""

    def __init__(self, node_id: str | None = None, max_workers: int | None = None) -> None:
        """Initialize the DoraNode.

        Args:
            node_id: The node ID.
            max_workers: The maximum number of workers for the node. If None, no async callbacks are used.
        """
        self.node = Node(node_id=node_id)
        self.dispatch_table: dict[tuple[str, str], Callable] = {}
        if max_workers is None:
            self.executor = None  # no async callbacks
        else:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)  # thread pool for async callbacks
        self._register_event_handlers()

    def cleanup(self) -> None:
        """Clean up the node and executor."""
        sys.exit(0)

    def _register_event_handlers(self) -> None:
        """Introspect on the node to find all decorated callbacks and register them."""
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "__event_handler__"):
                event_type, event_ids = method.__event_handler__
                for eid in event_ids:
                    self.dispatch_table[(event_type, eid)] = method

    def handle(self, event: dict) -> None:
        """Executes a registered callback by looking up the appropriate function."""
        event_type, event_id = event.get("type"), event.get("id")
        if event_type == "STOP":
            # Handle shutdown behavior.
            self.cleanup()
        handler = self.dispatch_table.get((event_type, event_id))
        if handler:
            # If marked to run asynchronously, submit it to the thread pool.
            if getattr(handler, "__run_async__", False):
                self.executor.submit(handler, event)
            else:
                handler(event)
        else:
            self.default_handler(event)

    def parse_messages(self) -> None:
        """Parses all currently available messages."""
        event = self.node.next(timeout=1e-3)
        while event["type"] != "ERROR":
            self.handle(event)
            event = self.node.next(timeout=1e-3)

    def default_handler(self, event: dict) -> None:
        """Default handler that does nothing."""

    def spin(self) -> None:
        """Main loop for node. Iterates over events and handles them."""
        for event in self.node:
            self.handle(event)
