from routix import ElapsedTimer

from .improv_timeout_callback import ImprovTimeoutCallback
from .objective_value_recorder import ObjectiveValueRecorder


class ImprovTimeoutValueRecorder(ObjectiveValueRecorder, ImprovTimeoutCallback):
    """A class that combines ObjectiveValueRecorder and ImprovTimeoutCallback.

    This class is used to record objective values and also to stop the search
    after a specified timeout if no improvement is found.
    """

    def __init__(
        self,
        no_improvement_timelimit: float,
        is_maximize: bool,
        e_timer: ElapsedTimer | None = None,
        print_on_record: bool = False,
        log_level_on_record: int | None = None,
    ) -> None:
        super().__init__(
            no_improvement_timelimit=no_improvement_timelimit,
            is_maximize=is_maximize,
            e_timer=e_timer,
            print_on_record=print_on_record,
            log_level_on_record=log_level_on_record,
        )

    def on_solution_callback(self) -> None:
        ObjectiveValueRecorder.on_solution_callback(self)
        ImprovTimeoutCallback.on_solution_callback(self)
