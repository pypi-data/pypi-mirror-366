# tests/fake_cp_model.py
from routix import ElapsedTimer

from mbls.cpsat.custom_cp_model import CustomCpModel
from mbls.cpsat.status import CpsatStatus


class FakeCpModel(CustomCpModel):
    def __init__(self, maximize=False):
        super().__init__()
        self._maximize = maximize
        self._obj_value_record = [
            (0.0, 100.0),
            (1.0, 90.0),
            (2.0, 85.0),
        ]
        self._obj_bound_record = [
            (0.0, 60.0),
            (1.0, 70.0),
            (2.0, 50.0),
        ]

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
    ):
        """
        Solve the fake CP model with a progress logger.

        Args:
            computational_time (float): The maximum computational time in seconds.
            num_workers (int): The number of parallel workers.
            random_seed (int | None, optional): Random seed for reproducibility. Defaults to None.
            no_improvement_timelimit (float | None, optional): If there is no improvement in this
                amount of time, the search will be stopped. If None, no timeout is set.
                Defaults to None.
            e_timer (ElapsedTimer | None, optional): Timer to be passed to solver callback. Defaults to None.
            print_on_obj_value_update (bool, optional): Print on objective value update. Defaults to False.
            print_on_obj_bound_update (bool, optional): Print on objective bound update. Defaults to False.
            log_level_obj_value (int | None, optional): Log level for value updates. Defaults to None.
            log_level_obj_bound (int | None, optional): Log level for bound updates. Defaults to None.
        """
        return (
            CpsatStatus.OPTIMAL,
            3.0,
            min(self._obj_value_record, key=lambda x: x[1])[1],
            max(self._obj_bound_record, key=lambda x: x[1])[1],
        )

    def get_obj_value_records(self) -> list[tuple[float, float]]:
        return self._obj_value_record

    def get_obj_bound_records(self) -> list[tuple[float, float]]:
        return self._obj_bound_record

    def is_maximize(self) -> bool:
        return self._maximize

    def set_num_base_constraints(self):
        pass
