from abc import ABC

from routix import ElapsedTimer

from mbls.time_stamped_recorder import RecordValT, TimeStampedRecorder

from .base_solution_callback import BaseSolutionCallback


class ByCallbackRecorder(BaseSolutionCallback, TimeStampedRecorder[RecordValT], ABC):
    """
    For solver callbacks (e.g. CP-SAT on_solution_callback).
    Subclasses only need to call self.record(...) in on_solution_callback().
    """

    def __init__(self, e_timer: ElapsedTimer | None = None, **kwargs) -> None:
        super().__init__(e_timer=e_timer, **kwargs)
