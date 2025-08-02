from abc import abstractmethod
from datetime import datetime
from typing import Any, Generic

from routix import (
    DynamicDataObject,
    ElapsedTimer,
    StoppingCriteriaT,
    SubroutineController,
)
from routix.type_defs import ParametersT

from .custom_cp_model import CustomCpModelT
from .obj_value_bound_store import ObjValueBoundStore
from .solver_report import CpsatSolverReport


class CpSubroutineController(
    SubroutineController, Generic[ParametersT, CustomCpModelT, StoppingCriteriaT]
):
    """
    Subroutine controller utilizing OR-Tools CP model.
    This controller manages the execution of a CP model subroutine,
    including the creation of the model, solving it, and logging results.
    """

    def __init__(
        self,
        instance: ParametersT,
        shared_param_dict: dict,
        cp_model_class: type[CustomCpModelT],
        subroutine_flow: DynamicDataObject,
        stopping_criteria: StoppingCriteriaT,
        start_dt: datetime | None = None,
        expr_name: str | None = None,
    ):
        """
        Initialize the CpSubroutineController.
        - Set up the subroutine controller with algorithm data.
        - Create an instance of base CP model using the provided instance and shared parameters.
        - Set the number of base constraints of the CP model.

        Args:
            instance (ParametersT): Instance-specific parameters for the CP model.
            shared_param_dict (dict): Shared parameters for the CP model.
            cp_model_class (type[CustomCpModelT]): The class of the CP model to be used.
            subroutine_flow (DynamicDataObject): The flow of the subroutine to be executed.
            stopping_criteria (StoppingCriteriaT): Stopping criteria for the controller.
            start_dt (datetime | None, optional): Start date and time for the controller.
                If not provided, the current time is used.
            expr_name (str | None, optional): Name of the experiment.
                If not provided, defaults to the name of the instance or "CP Subroutine Controller".
        """
        _expr_name = expr_name or str(
            getattr(instance, "name", "CP Subroutine Controller")
        )
        super().__init__(
            name=_expr_name,
            subroutine_flow=subroutine_flow,
            stopping_criteria=stopping_criteria,
            start_dt=start_dt,
        )

        self.instance = instance
        """Instance-specific parameters for the CP model."""
        self.shared_param_dict = shared_param_dict
        """Shared parameters for the CP model."""
        self.cp_model_class = cp_model_class
        """The class of the CP model to be used."""

        self.obj_store = ObjValueBoundStore[float]()
        """Store for objective value and bound time series."""

        self.cp_model = self.create_base_cp_model()
        self.cp_model.set_num_base_constraints()

    @abstractmethod
    def create_base_cp_model(self) -> CustomCpModelT:
        """Initialize and return a CP model instance.

        Returns:
            CustomCpModelT: An instance of the CP model that corresponds to the target problem.
        """
        ...

    @property
    def obj_value_log(self) -> list[tuple[float, float]]:
        """Get the objective value log.

        Returns:
            list[tuple[float, float]]: List of tuples containing (elapsed time, objective value).
        """
        return self.obj_store.obj_value_series.items()

    def add_obj_value_log(
        self, elapsed: float, value: float, is_maximize: bool | None = False
    ) -> None:
        """Add a single objective value log entry.

        Args:
            elapsed (float): Elapsed time.
            value (float): Objective value.
            is_maximize (bool, optional): If True, indicates maximization problem.
                Defaults to False.
        """
        self.obj_store.add_obj_value(elapsed, value, is_maximize=is_maximize)

    def extend_obj_value_log(
        self, value_log: list[tuple[float, float]], is_maximize: bool | None = False
    ) -> None:
        """Add a list of objective value log entries.

        Args:
            value_log (list[tuple[float, float]]): List of (elapsed, value) tuples.
            is_maximize (bool, optional): If True, indicates maximization problem.
                Defaults to False.
        """
        for elapsed, value in value_log:
            self.add_obj_value_log(elapsed, value, is_maximize=is_maximize)

    @property
    def obj_bound_log(self) -> list[tuple[float, float]]:
        """Get the objective bound log.

        Returns:
            list[tuple[float, float]]: List of tuples containing (elapsed time, objective bound).
        """
        return self.obj_store.obj_bound_series.items()

    def add_obj_bound_log(
        self, elapsed: float, bound: float, is_maximize: bool | None = False
    ) -> None:
        """Add a single objective bound log entry.

        Args:
            elapsed (float): Elapsed time.
            bound (float): Objective bound.
            is_maximize (bool, optional): If True, indicates maximization problem.
                Defaults to False.
        """
        self.obj_store.add_obj_bound(elapsed, bound, is_maximize=is_maximize)

    def extend_obj_bound_log(
        self, bound_log: list[tuple[float, float]], is_maximize: bool | None = False
    ) -> None:
        """Add a list of objective bound log entries.

        Args:
            bound_log (list[tuple[float, float]]): List of (elapsed, bound) tuples.
            is_maximize (bool, optional): If True, indicates maximization problem.
                Defaults to False.
        """
        for elapsed, bound in bound_log:
            self.add_obj_bound_log(elapsed, bound, is_maximize=is_maximize)

    def solve_cp_model(
        self,
        cp_model: CustomCpModelT,
        computational_time: float,
        num_workers: int,
        random_seed: int | None = None,
        no_improvement_timelimit: float | None = None,
        e_timer: ElapsedTimer | None = None,
        print_on_obj_value_update: bool = False,
        print_on_obj_bound_update: bool = False,
        log_level_obj_value: int | None = None,
        log_level_obj_bound: int | None = None,
        obj_value_is_valid: bool = False,
        obj_bound_is_valid: bool = False,
        last_timestamp_note: Any | None = None,
    ) -> CpsatSolverReport:
        """Solve the given CP model.

        Args:
            cp_model (CpModelT): The CP model to be solved.
            computational_time (float): The maximum computational time in seconds.
            num_workers (int): The number of parallel workers (i.e. threads) to use during search.
            random_seed (int | None, optional): Random seed for reproducibility.
                Defaults to None.
            no_improvement_timelimit (float | None, optional): If there is no improvement in this
                amount of time, the search will be stopped. If None, no timeout is set.
                Defaults to None.
            e_timer (ElapsedTimer | None, optional): Timer to be passed to solver callback.
                Defaults to None.
            print_on_obj_value_update (bool, optional): If True, prints updates on objective value.
                Defaults to False.
            print_on_obj_bound_update (bool, optional): If True, prints updates on objective bound.
                Defaults to False.
            log_level_obj_value (int | None, optional): Log level for objective value updates.
                Defaults to None.
            log_level_obj_bound (int | None, optional): Log level for objective bound updates.
                Defaults to None.
            obj_value_is_valid (bool, optional): If True, adds the objective value log.
                Defaults to False.
            obj_bound_is_valid (bool, optional): If True, adds the objective bound log.
                Defaults to False.
            last_timestamp_note (Any | None, optional): Note for the last timestamp.
                Defaults to None.

        Raises:
            AttributeError: If self.cp_model is not initialized.

        Returns:
            CpsatSolverReport: A summary of the solver output, including status,
                elapsed time, objective value, best objective bound, and progress log.
        """
        (solver_status, elapsed_time, obj_value, obj_bound) = (
            cp_model.solve_with_callbacks(
                computational_time=computational_time,
                num_workers=num_workers,
                random_seed=random_seed,
                no_improvement_timelimit=no_improvement_timelimit,
                e_timer=e_timer,
                print_on_obj_value_update=print_on_obj_value_update,
                print_on_obj_bound_update=print_on_obj_bound_update,
                log_level_obj_value=log_level_obj_value,
                log_level_obj_bound=log_level_obj_bound,
            )
        )
        last_timestamp = self.timer.elapsed_sec

        # Store the objective value and bound logs

        if obj_value_is_valid:
            obj_value_records = cp_model.get_obj_value_records()
            self.extend_obj_value_log(
                obj_value_records, is_maximize=cp_model.is_maximize()
            )
            if (last_timestamp, obj_value) not in obj_value_records:
                self.add_obj_value_log(last_timestamp, obj_value, is_maximize=None)
        else:
            obj_value_records = []

        if obj_bound_is_valid:
            obj_bound_records = cp_model.get_obj_bound_records()
            self.extend_obj_bound_log(
                obj_bound_records, is_maximize=cp_model.is_maximize()
            )
            if (last_timestamp, obj_bound) not in obj_bound_records:
                self.add_obj_bound_log(last_timestamp, obj_bound, is_maximize=None)
        else:
            obj_bound_records = []

        _last_timestamp_note = (
            last_timestamp_note or self._get_call_context_of_current_method()
        )
        self.obj_store.add_last_timestamp_note(
            _last_timestamp_note,
            obj_value_is_valid=obj_value_is_valid,
            obj_bound_is_valid=obj_bound_is_valid,
        )

        return CpsatSolverReport(
            status=solver_status,
            elapsed_time=elapsed_time,
            obj_value=obj_value,
            obj_bound=obj_bound,
            obj_value_records=obj_value_records,
            obj_bound_records=obj_bound_records,
        )

    def solve_current_cp_model(
        self,
        computational_time: float,
        num_workers: int,
        random_seed: int | None = None,
        e_timer: ElapsedTimer | None = None,
        print_on_obj_value_update: bool = False,
        print_on_obj_bound_update: bool = False,
        log_level_obj_value: int | None = None,
        log_level_obj_bound: int | None = None,
        obj_value_is_valid: bool = False,
        obj_bound_is_valid: bool = False,
        last_timestamp_note: Any | None = None,
    ) -> CpsatSolverReport:
        """Solve the current CP model.

        Args:
            computational_time (float): The maximum computational time in seconds.
            num_workers (int): The number of parallel workers (i.e. threads) to use during search.
            random_seed (int | None, optional): Random seed for reproducibility.
                Defaults to None.
            e_timer (ElapsedTimer | None, optional): Timer to be passed to solver callback.
                Defaults to None.
            print_on_obj_value_update (bool, optional): If True, prints updates on objective value.
                Defaults to False.
            print_on_obj_bound_update (bool, optional): If True, prints updates on objective bound.
                Defaults to False.
            log_level_obj_value (int | None, optional): Log level for objective value updates.
                Defaults to None.
            log_level_obj_bound (int | None, optional): Log level for objective bound updates.
                Defaults to None.
            obj_value_is_valid (bool, optional): If True, adds the objective value log.
                Defaults to False.
            obj_bound_is_valid (bool, optional): If True, adds the objective bound log.
                Defaults to False.
            last_timestamp_note (Any | None, optional): Note for the last timestamp.
                Defaults to None.

        Raises:
            AttributeError: If self.cp_model is not initialized.

        Returns:
            CpsatSolverReport: A summary of the solver output, including status,
                elapsed time, objective value, best objective bound, and progress log.
        """
        if not hasattr(self, "cp_model"):
            raise AttributeError("CP model is not initialized.")
        return self.solve_cp_model(
            cp_model=self.cp_model,
            computational_time=computational_time,
            num_workers=num_workers,
            random_seed=random_seed,
            e_timer=e_timer,
            print_on_obj_value_update=print_on_obj_value_update,
            print_on_obj_bound_update=print_on_obj_bound_update,
            log_level_obj_value=log_level_obj_value,
            log_level_obj_bound=log_level_obj_bound,
            obj_value_is_valid=obj_value_is_valid,
            obj_bound_is_valid=obj_bound_is_valid,
            last_timestamp_note=last_timestamp_note,
        )
