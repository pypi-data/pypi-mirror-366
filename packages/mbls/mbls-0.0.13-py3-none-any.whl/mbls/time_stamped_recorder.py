from abc import ABC, abstractmethod
from typing import Generic, List, Tuple, TypeVar

from routix import ElapsedTimer

RecordValT = TypeVar("RecordValT")
"""
Type of the metric being recorded (objective value, bound, etc.).
"""


class TimeStampedRecorder(ABC, Generic[RecordValT]):
    """
    Abstract base for recording timestamped metric values.

    Maintains a list of (elapsed_time, value) pairs.
    Subclasses should integrate `self.record(value)` into their solver-specific callback,
    and override `on_record()` if they need custom side-effects
    (e.g. printing or logging).
    """

    def __init__(self, e_timer: ElapsedTimer | None = None, **kwargs) -> None:
        """
        Args:
            e_timer (ElapsedTimer | None, optional): Timer for measuring elapsed time.
                If None, a new ElapsedTimer is created and started.
        """
        if e_timer is None:
            e_timer = ElapsedTimer()
            e_timer.set_start_time_as_now()
        self.e_timer = e_timer
        """Elapsed timer to track the time. If None, a new ElapsedTimer is created and started."""

        # the master list of (time, value) pairs
        self.entries: List[Tuple[float, RecordValT]] = []
        """A list of tuples containing (elapsed time, value)."""

    def record(self, value: RecordValT) -> None:
        """Append a new record with the current elapsed time, then invoke the on_record hook.

        Args:
            value (T): The recorded value.
        """
        t = self.e_timer.elapsed_sec
        self.entries.append((t, value))
        self.on_record(t, value)

    @abstractmethod
    def on_record(self, timestamp: float, value: RecordValT) -> None:
        """
        Hook called after a new (timestamp, value) is added.
        Subclasses can override to print, log, or trigger other side-effects.

        Args:
            timestamp (float): The time at which the value was recorded.
            value (T): The recorded value.
        """
