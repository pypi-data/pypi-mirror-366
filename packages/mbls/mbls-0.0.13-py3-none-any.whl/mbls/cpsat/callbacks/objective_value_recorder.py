import logging

from routix import ElapsedTimer

from .by_callback_recorder import ByCallbackRecorder


class ObjectiveValueRecorder(ByCallbackRecorder[float]):
    """
    Solution callback that records (elapsed time, objective value) pairs
    at each solution found during the CP-SAT search.

    Args:
        e_timer (ElapsedTimer | None): Timer for measuring elapsed time.
            If None, a new ElapsedTimer is created and started.
        print_on_record (bool): If True, prints progress at each solution callback.
        log_level_on_record (int | None): If set, logs progress at the specified logging level.

    Attributes:
        elapsed_time_and_value (list[tuple[float, float]]): List of (elapsed time, objective value) pairs.
    """

    def __init__(
        self,
        e_timer: ElapsedTimer | None = None,
        print_on_record: bool = False,
        log_level_on_record: int | None = None,
        **kwargs,
    ) -> None:
        """
        Args:
            e_timer (ElapsedTimer | None, optional): Timer for measuring elapsed time.
                If None, a new ElapsedTimer is created and started.
            print_on_record (bool, optional): If True, prints progress at each solution callback.
                Defaults to False.
            log_level_on_record (int | None, optional): If set to a valid logging level,
                logs the progress message at that level.
                Defaults to None.
        """
        super().__init__(e_timer=e_timer, **kwargs)

        self.print_on_record = print_on_record
        """If True, prints progress on each solution callback."""

        self.log_level_on_record = log_level_on_record
        """If set, logs progress at the specified logging level."""

    # Start abstract method implementation

    def on_record(self, timestamp: float, value: float) -> None:
        """Hook called after a new (timestamp, value) is added.

        - Prints progress if print_on_record is True.
        - Logs progress if log_level_on_record is set to a valid logging level.

        Args:
            timestamp (float): The elapsed time in seconds.
            value (float): The objective value.
        """
        obj_bound = self.best_objective_bound
        info_str = (
            f"Elapsed: {timestamp:.2f} sec, "
            f"Obj. value: {value}, "
            f"Obj. bound: {obj_bound}"
        )
        if self.print_on_record:
            print(info_str)
        if (
            self.log_level_on_record is not None
            and 10 <= self.log_level_on_record <= 50
            and self.log_level_on_record in logging._levelToName
        ):
            logging.log(self.log_level_on_record, info_str)

    def on_solution_callback(self) -> None:
        """
        Called by the solver at each solution.

        - Records the current objective value and elapsed time.
        - Prints progress if print_on_record is True.
        - Logs progress if log_level_on_record is set to a valid logging level.
        """
        self.record(self.objective_value)

    # End abstract method implementation
    # Start getter

    @property
    def elapsed_time_and_value(self) -> list[tuple[float, float]]:
        """
        Returns:
            list[tuple[float, float]]: A list of (elapsed time, objective value) pairs
            collected during the search.
        """
        return self.entries.copy()

    # End getter
