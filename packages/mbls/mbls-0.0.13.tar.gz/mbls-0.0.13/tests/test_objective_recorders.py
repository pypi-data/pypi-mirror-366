from ortools.sat.python import cp_model
from routix import ElapsedTimer

from mbls.cpsat.callbacks.objective_bound_recorder import ObjectiveBoundRecorder
from mbls.cpsat.callbacks.objective_value_recorder import ObjectiveValueRecorder


def test_objective_value_and_bound_recorders():
    # Arrange
    model = cp_model.CpModel()
    x = model.NewIntVar(0, 2, "x")
    y = model.NewIntVar(0, 2, "y")
    model.Add(x != y)
    model.Maximize(x + y)

    timer = ElapsedTimer()
    value_recorder = ObjectiveValueRecorder(e_timer=timer, print_on_record=False)
    bound_recorder = ObjectiveBoundRecorder(e_timer=timer, print_on_record=False)

    # Act
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    solver.solve(model, solution_callback=value_recorder)
    # Simulate bound recording (in real use, attach to best bound callback if available)
    for _, obj_val in value_recorder.elapsed_time_and_value:
        bound_recorder(obj_val)  # For demonstration, record obj_val as bound

    value_log = value_recorder.elapsed_time_and_value
    bound_log = bound_recorder.elapsed_time_and_bound

    # Assert
    assert isinstance(value_log, list)
    assert len(value_log) >= 1  # At least one solution is found
    for entry in value_log:
        elapsed, objective = entry
        assert isinstance(elapsed, float)
        assert isinstance(objective, float)
    elapsed_times = [entry[0] for entry in value_log]
    assert elapsed_times == sorted(elapsed_times)  # should be increasing

    assert isinstance(bound_log, list)
    assert len(bound_log) == len(value_log)
    for entry in bound_log:
        elapsed, bound = entry
        assert isinstance(elapsed, float)
        assert isinstance(bound, float)
