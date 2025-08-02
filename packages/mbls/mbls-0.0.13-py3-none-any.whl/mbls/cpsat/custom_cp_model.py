import warnings
from typing import TypeVar, Union

from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from ortools.sat.cp_model_pb2 import ConstraintProto  # type: ignore
from ortools.sat.python.cp_model import CpModel, CpSolver, IntVar
from routix import ElapsedTimer

from .callbacks import (
    ImprovTimeoutCallback,
    ImprovTimeoutValueRecorder,
    ObjectiveBoundRecorder,
    ObjectiveValueRecorder,
)
from .status import CpsatStatus


class CustomCpModel(CpModel):
    """A custom CpModel class that extends the OR-Tools CpModel class."""

    solver: CpSolver
    """CpSolver object for solving the model."""
    solution_callback: ObjectiveValueRecorder
    """Recorder for objective values during search."""
    obj_bound_recorder: ObjectiveBoundRecorder
    """Recorder for objective bounds during search."""
    improv_timeout_cb: ImprovTimeoutCallback | None = None
    """Improvement timeout callback to halt search after a timeout."""

    def __init__(self) -> None:
        super().__init__()
        self.num_base_constraints: int = 0
        """Number of base constraints in the model."""

    def solve_and_get_status(
        self, computational_time: float, num_workers: int
    ) -> tuple[CpsatStatus, float, float, float]:
        """Solve the CP model.

        Args:
            computational_time (float): The maximum computational time in seconds.
            num_workers (int): The number of parallel workers (i.e. threads) to use during search.

        Returns:
            tuple[CpsatStatus, float, float, float]: A tuple containing
                - the solver status,
                - elapsed time,
                - the value of the objective, and
                - the best lower (upper) bound of the objective function.
        """
        self.init_solver(computational_time, num_workers)

        cp_solver_status = self.solver.solve(self)
        cpsat_status = CpsatStatus.from_cp_solver_status(cp_solver_status)
        elapsed_time = self.solver.wall_time

        if cpsat_status.is_feasible:
            obj_value = self.solver.objective_value
            obj_bound = self.solver.best_objective_bound
        else:
            obj_value, obj_bound = CpsatStatus.get_obj_value_and_bound_for_infeasible(
                self.is_maximize()
            )

        return cpsat_status, elapsed_time, obj_value, obj_bound

    def init_solver(
        self,
        computational_time: float,
        num_workers: int,
        random_seed: int | None = None,
        no_improvement_timelimit: float | None = None,
        e_timer: ElapsedTimer | None = None,
        print_on_obj_value_update: bool = False,
        print_on_obj_bound_update: bool = False,
        log_level_obj_value: int | None = None,
        log_level_obj_bound: int | None = None,
    ) -> None:
        """Initializes the solver, together with callbacks.

        - obj_value_recorder: CpSolverSolutionCallback for objective value updates.
        - obj_bound_recorder: Callable for objective bound updates.

        Args:
            computational_time (float): The maximum computational time in seconds.
            num_workers (int): The number of parallel workers (i.e. threads) to use during search.
            random_seed (int | None, optional): Random seed for reproducibility.
                Defaults to None.
            no_improvement_timelimit (float | None, optional): If there is no improvement in this
                amount of time, the search will be stopped. If None, no timeout is set.
                Defaults to None.
            e_timer (ElapsedTimer | None, optional): ElapsedTimer for callbacks.
                Defaults to None.
            print_on_obj_value_update (bool, optional): Print on objective value update.
                Defaults to False.
            print_on_obj_bound_update (bool, optional): Print on objective bound update.
                Defaults to False.
            log_level_obj_value (int | None, optional): Log level for value updates.
                Defaults to None.
            log_level_obj_bound (int | None, optional): Log level for bound updates.
                Defaults to None.
        """
        self.solver = CpSolver()
        self.solver.parameters.max_time_in_seconds = computational_time
        self.solver.parameters.num_workers = num_workers
        if random_seed is not None:
            self.solver.parameters.random_seed = random_seed

        # Define solution callback for objective value updates
        if no_improvement_timelimit is not None and no_improvement_timelimit > 0:
            # If no_improvement_timelimit is set, use ImprovTimeoutValueRecorder
            self.solution_callback = ImprovTimeoutValueRecorder(
                no_improvement_timelimit,
                is_maximize=self.is_maximize(),
                e_timer=e_timer,
                print_on_record=print_on_obj_value_update,
                log_level_on_record=log_level_obj_value,
            )
        else:
            # Otherwise, use ObjectiveValueRecorder
            self.solution_callback = ObjectiveValueRecorder(
                e_timer,
                print_on_record=print_on_obj_value_update,
                log_level_on_record=log_level_obj_value,
            )

        # Define objective bound recorder as a separate callback
        self.obj_bound_recorder = ObjectiveBoundRecorder(
            e_timer,
            print_on_record=print_on_obj_bound_update,
            log_level_on_record=log_level_obj_bound,
        )
        self.solver.best_bound_callback = self.obj_bound_recorder

    def solve_with_callbacks(
        self,
        computational_time: float,
        num_workers: int,
        random_seed: int | None = None,
        no_improvement_timelimit: float | None = None,
        e_timer: ElapsedTimer | None = None,
        print_on_obj_value_update: bool = False,
        print_on_obj_bound_update: bool = False,
        log_level_obj_value: int | None = None,
        log_level_obj_bound: int | None = None,
    ) -> tuple[CpsatStatus, float, float, float]:
        """Solve the CP model with progress recorders for objective value and bound.

        Args:
            computational_time (float): The maximum computational time in seconds.
            num_workers (int): The number of parallel workers (i.e. threads) to use during search.
            random_seed (int | None, optional): Random seed for reproducibility.
                Defaults to None.
            no_improvement_timelimit (float | None, optional): If there is no improvement in this
                amount of time, the search will be stopped. If None, no timeout is set.
                Defaults to None.
            e_timer (ElapsedTimer | None, optional): ElapsedTimer for callbacks.
                Defaults to None.
            print_on_obj_value_update (bool, optional): Whether to print/log on each objective value update.
                Defaults to False.
            print_on_obj_bound_update (bool, optional): Whether to print/log on each objective bound update.
                Defaults to False.
            log_level_obj_value (int | None, optional): Log level for objective value updates.
                Defaults to None.
            log_level_obj_bound (int | None, optional): Log level for objective bound updates.
                Defaults to None.

        Returns:
            tuple[CpsatStatus, float, float, float]: A tuple containing
                - the solver status,
                - elapsed time,
                - the value of the objective, and
                - the best lower (upper) bound of the objective function.
        """  # noqa: E501
        self.init_solver(
            computational_time,
            num_workers,
            random_seed=random_seed,
            no_improvement_timelimit=no_improvement_timelimit,
            e_timer=e_timer,
            print_on_obj_value_update=print_on_obj_value_update,
            print_on_obj_bound_update=print_on_obj_bound_update,
            log_level_obj_value=log_level_obj_value,
            log_level_obj_bound=log_level_obj_bound,
        )

        cp_solver_status = self.solver.solve(
            self, solution_callback=self.solution_callback
        )

        cpsat_status = CpsatStatus.from_cp_solver_status(cp_solver_status)
        elapsed_time = self.solver.wall_time
        if cpsat_status.is_feasible:
            obj_value = self.solver.objective_value
            obj_bound = self.solver.best_objective_bound
        else:
            obj_value, obj_bound = CpsatStatus.get_obj_value_and_bound_for_infeasible(
                self.is_maximize()
            )
        return cpsat_status, elapsed_time, obj_value, obj_bound

    @property
    def obj_value_recorder(
        self,
    ) -> Union[ObjectiveValueRecorder, ImprovTimeoutValueRecorder]:
        """Returns the objective value recorder."""
        return self.solution_callback

    def get_obj_value_records(self) -> list[tuple[float, float]]:
        """Returns the recorded objective values and elapsed times.

        Returns:
            list[tuple[float, float]]: A list of tuples containing (elapsed time, objective value).
        """
        return self.obj_value_recorder.elapsed_time_and_value

    def get_obj_bound_records(self) -> list[tuple[float, float]]:
        """Returns the recorded objective bounds and elapsed times.

        Returns:
            list[tuple[float, float]]: A list of tuples containing (elapsed time, objective bound).
        """
        return self.obj_bound_recorder.elapsed_time_and_bound

    # variable functions

    def change_domain(self, var: IntVar, domain: list[int]) -> None:
        """Changes the domain of a variable.

        Args:
            var (IntVar)
            domain (list[int]): A list of two integers representing the new domain.
        """
        assert len(domain) == 2, (
            f"Domain must be a list of two integers; {domain} given."
        )

        var.Proto().domain[:] = domain

    # objective functions

    def is_maximize(self) -> bool:
        """
        Returns:
            bool: True if the objective is maximize, False if minimize.
        """
        proto = self.Proto()
        # If the objective is not set to maximize, it defaults to minimize
        # in OR-Tools, so we return False if maximize is not set.
        return getattr(proto.objective, "maximize", False)

    # constraint functions

    def _get_constraints(self) -> RepeatedCompositeFieldContainer[ConstraintProto]:
        proto = self.Proto()
        if not hasattr(proto, "constraints") or proto.constraints is None:
            raise RuntimeError("No constraints defined in the model.")
        return proto.constraints

    def get_next_constr_idx(self) -> int:
        """Returns the index of the next constraint.

        Returns:
            int: The index of the next constraint.
        """
        return len(self._get_constraints())

    def set_num_base_constraints(self) -> None:
        """Sets the base number of constraints to the current number of constraints."""
        self.num_base_constraints = self.get_next_constr_idx()

    def freeze_base_constraints(self) -> None:
        warnings.warn(
            "freeze_base_constraints() is deprecated and will be removed in a future version. "
            "Use set_num_base_constraints() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.set_num_base_constraints()

    # methods to delete constraints

    def delete_constraints(self, idx_start: int, idx_end: int) -> None:
        del self._get_constraints()[idx_start:idx_end]

    def delete_added_constraints(self):
        """Deletes all constraints added after base model was built.

        Raises:
            ValueError: If no constraints were added after the base model was built.
        """

        if self.num_base_constraints == 0:
            raise ValueError("No base model constraints defined.")
        current_num_constraints = self.get_next_constr_idx()
        if current_num_constraints > self.num_base_constraints:
            self.delete_constraints(self.num_base_constraints, current_num_constraints)


CustomCpModelT = TypeVar("CustomCpModelT", bound=CustomCpModel)
"""
Type variable for CustomCpModel, allowing methods to specify
that they return or accept an instance of CustomCpModel or its subclasses.
"""
