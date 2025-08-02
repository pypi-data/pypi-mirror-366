import logging
import threading

from .base_solution_callback import BaseSolutionCallback


class ImprovTimeoutCallback(BaseSolutionCallback):
    """
    A solution callback that stops the search if no improvement in the
    objective value is made within a given time limit.

    This callback uses a background `threading.Timer` to track the time
    since the last improvement. The timer is started only after the first
    solution is found.

    Args:
        no_improvement_timelimit (float): The time limit in seconds.
            If no new best solution is found within this duration, the search is stopped.
        is_maximize (bool, optional): Set to True if the solver is maximizing the objective.
            Defaults to False (minimization).

    Raises:
        ValueError: If `no_improvement_timelimit` is not positive.
    """

    def __init__(
        self, no_improvement_timelimit: float, is_maximize: bool = False, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        if no_improvement_timelimit <= 0:
            raise ValueError("no_improvement_timelimit must be positive.")

        self.no_improvement_timelimit = no_improvement_timelimit
        self._is_maximize = is_maximize
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

        self.best_obj_value: float | None = None
        """
        The best objective value found so far.
        This is updated whenever a new best solution is found.
        If no solution has been found yet, it remains None.
        """

        self._timer_started = False
        self._stopped = False

    def on_solution_callback(self) -> None:
        """Called by the solver at each new solution."""
        if not self._timer_started:
            # Start the timer upon finding the first solution
            self._start_timer()
            self._timer_started = True
        self.refresh_timer()

    def refresh_timer(self) -> None:
        if self._refresh_best_objective_value():
            # If the best objective value is updated,
            # reset the timer to track the time since the last improvement
            self._start_timer()

    def _refresh_best_objective_value(self) -> bool:
        """
        Try updating the best objective value.
        If the current objective value is better than the best found so far,
        it updates the best objective value and returns True.
        If not updated, it returns False.

        Returns:
            bool: True if the best objective value has been updated, False otherwise.
        """
        current_obj = self.objective_value
        if current_obj is None:
            return False
        # current_obj is not None
        if self.best_obj_value is None:
            self.best_obj_value = current_obj
            return True
        # Compare current objective value with the best found so far
        if self._is_maximize:
            if current_obj > self.best_obj_value:
                self.best_obj_value = current_obj
                return True
        else:
            if current_obj < self.best_obj_value:
                self.best_obj_value = current_obj
                return True
        return False

    def _start_timer(self):
        """Cancels the existing timer and starts a new one."""

        def _on_timeout():
            """Called when the timer expires."""
            if not self._stopped:
                self._stopped = True
                logging.info(
                    "No improvement for %.2f seconds. Stopping search.",
                    self.no_improvement_timelimit,
                )
                self.StopSearch()
                if self._timer:
                    self._timer.cancel()
                    self._timer = None

        with self._lock:
            if self._stopped:
                return
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.no_improvement_timelimit, _on_timeout)
            self._timer.start()
