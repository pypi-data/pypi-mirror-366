from abc import ABC, abstractmethod

from mbls.time_stamped_recorder import RecordValT, TimeStampedRecorder


class ByCallRecorder(TimeStampedRecorder[RecordValT], ABC):
    """
    For simple callables (e.g. best_bound_callback, log_callback).
    Subclasses implement __call__(value) and call self.record(value).
    """

    @abstractmethod
    def __call__(self, value: RecordValT) -> None: ...
