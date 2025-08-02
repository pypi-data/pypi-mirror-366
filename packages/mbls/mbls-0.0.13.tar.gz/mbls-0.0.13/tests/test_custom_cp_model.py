import pytest
from routix import ElapsedTimer

from mbls.cpsat.custom_cp_model import CustomCpModel
from mbls.cpsat.status import CpsatStatus


@pytest.fixture
def model():
    """Fixture to create a CustomCpModel instance."""
    return CustomCpModel()


def test_init_solver(model: CustomCpModel):
    model.init_solver(computational_time=10.0, num_workers=4)
    assert model.solver.parameters.max_time_in_seconds == 10.0
    assert model.solver.parameters.num_workers == 4


def test_solve_and_get_status(model: CustomCpModel):
    model.init_solver(computational_time=10.0, num_workers=4)
    status, elapsed_time, ub, lb = model.solve_and_get_status(
        computational_time=10.0, num_workers=4
    )
    assert isinstance(status, CpsatStatus)
    assert isinstance(elapsed_time, float)
    assert isinstance(ub, float)
    assert isinstance(lb, float)


def test_change_domain(model: CustomCpModel):
    var = model.new_int_var(0, 10, "test_var")
    model.change_domain(var, [5, 15])
    assert var.Proto().domain == [5, 15]


def test_is_maximize(model: CustomCpModel):
    assert model.is_maximize() is False


def test_set_num_base_constraints(model: CustomCpModel):
    # Create integer variables
    x = model.new_int_var(0, 10, "x")
    y = model.new_int_var(0, 10, "y")

    # Add a constraint
    model.add(x + y <= 15)

    # Set the number of base constraints
    model.set_num_base_constraints()

    # Assert that the number of base constraints is updated correctly
    assert model.num_base_constraints == 1


def test_delete_added_constraints(model: CustomCpModel):
    # Create integer variables
    x = model.new_int_var(0, 10, "x")
    y = model.new_int_var(0, 10, "y")

    # Add base constraints
    model.add(x >= 0)
    model.add(x + y <= 15)
    model.set_num_base_constraints()

    # Add additional constraints
    model.add(x - y >= 5)  # Added constraint 1
    model.add(x + 2 * y == 20)  # Added constraint 2

    # Delete added constraints
    model.delete_added_constraints()

    # Assert that only the base constraints remain
    assert model.get_next_constr_idx() == model.num_base_constraints


def test_solve_with_callbacks(model: CustomCpModel):
    timer = ElapsedTimer()
    model.init_solver(computational_time=10.0, num_workers=4)

    # Example CP model by Google
    num_vals = 3
    x = model.new_int_var(0, num_vals - 1, "x")
    y = model.new_int_var(0, num_vals - 1, "y")
    z = model.new_int_var(0, num_vals - 1, "z")
    model.add(x != y)

    status, elapsed_time, ub, lb = model.solve_with_callbacks(
        computational_time=10.0, num_workers=4, e_timer=timer
    )
    assert isinstance(status, CpsatStatus)
    assert isinstance(elapsed_time, float)
    assert isinstance(ub, float)
    assert isinstance(lb, float)
    if status.is_feasible:
        print(f"x = {model.solver.value(x)}")
        print(f"y = {model.solver.value(y)}")
        print(f"z = {model.solver.value(z)}")
    else:
        print("No solution found.")


def test_obj_value_and_bound_records(model: CustomCpModel):
    model.init_solver(computational_time=10.0, num_workers=4)
    # Setup: add some dummy records
    model.obj_value_recorder.entries.extend(
        [
            (0.0, 10.0),
            (1.0, 12.0),
            (2.0, 15.0),
        ]
    )
    model.obj_bound_recorder.entries.extend(
        [
            (0.0, 8.0),
            (1.0, 11.0),
            (2.0, 14.0),
        ]
    )
    # Test get_obj_value_records
    value_records = model.get_obj_value_records()
    assert value_records == [(0.0, 10.0), (1.0, 12.0), (2.0, 15.0)]
    # Test get_obj_bound_records
    bound_records = model.get_obj_bound_records()
    assert bound_records == [(0.0, 8.0), (1.0, 11.0), (2.0, 14.0)]
