"""SimpleBroker - A lightweight message queue backed by SQLite."""

__version__ = "2.0.0"

# Import main components
# Import BrokerDB for backward compatibility (but don't export it)
from .db import BrokerDB as _BrokerDB  # noqa: F401
from .queue import Queue
from .watcher import QueueMoveWatcher, QueueWatcher

# Only export the new API
__all__ = ["Queue", "QueueWatcher", "QueueMoveWatcher", "__version__"]
