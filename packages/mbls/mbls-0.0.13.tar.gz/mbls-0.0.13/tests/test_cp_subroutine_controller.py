from routix import DynamicDataObject, StoppingCriteria

from mbls.cpsat import CpSubroutineController
from mbls.cpsat.status import CpsatStatus

from .fake_cp_model import FakeCpModel


class DummyProblem:
    name = "test-problem"


class DummyCpController(
    CpSubroutineController[DummyProblem, FakeCpModel, StoppingCriteria]
):
    def is_stopping_condition(self) -> bool:
        return False

    def post_run_process(self):
        pass

    def create_base_cp_model(self) -> FakeCpModel:
        return FakeCpModel(maximize=False)


def test_solve_cp_model_triggers_logging():
    controller = DummyCpController(
        instance=DummyProblem(),
        shared_param_dict={},
        cp_model_class=FakeCpModel,
        subroutine_flow=DynamicDataObject({}),
        stopping_criteria=StoppingCriteria({}),
    )

    output = controller.solve_current_cp_model(
        computational_time=10.0,
        num_workers=1,
        obj_value_is_valid=True,
        obj_bound_is_valid=True,
    )

    assert output.status == CpsatStatus.OPTIMAL
    assert output.elapsed_time == 3.0
    assert output.obj_value == 85.0
    assert output.obj_bound == 70.0

    assert controller.obj_value_log[-1] == (2.0, 85.0)
    assert controller.obj_bound_log[-1] == (1.0, 70.0)
