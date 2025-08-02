import pytest

from mbls.cpsat.solver_report import CpsatSolverReport
from mbls.cpsat.status import CpsatStatus


@pytest.fixture
def dummy_report():
    return CpsatSolverReport(
        status=CpsatStatus.OPTIMAL,
        elapsed_time=1.23,
        obj_value=42.0,
        obj_bound=40.0,
        obj_value_records=[(0.0, 10.0), (1.0, 12.0)],
        obj_bound_records=[(0.0, 8.0), (1.0, 11.0)],
    )


def test_to_string_dict(dummy_report):
    d = dummy_report.to_string_dict()
    assert d["status"] == "OPTIMAL"
    assert d["obj_value_records"].startswith('"[(0.0, 10.0),')
    assert d["obj_bound_records"].startswith('"[(0.0, 8.0),')


def test_is_feasible(dummy_report):
    assert dummy_report.is_feasible is True


def test_str_and_repr(dummy_report):
    s = str(dummy_report)
    r = repr(dummy_report)
    assert "SolverReport" in s
    assert "SolverReport" in r
    assert "status=OPTIMAL" in s or "status=CpsatStatus.OPTIMAL" in s
    assert "obj_value_records" in s
    assert "obj_bound_records" in s
