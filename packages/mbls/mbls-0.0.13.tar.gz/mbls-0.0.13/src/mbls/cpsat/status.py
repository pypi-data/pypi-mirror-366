from __future__ import annotations

from enum import Enum

from ortools.sat.cp_model_pb2 import CpSolverStatus
from ortools.sat.python.cp_model import (
    FEASIBLE,
    INFEASIBLE,
    INT_MAX,
    INT_MIN,
    MODEL_INVALID,
    OPTIMAL,
    UNKNOWN,
)

from .. import SolverStatus


class CpsatStatus(Enum):
    UNKNOWN = UNKNOWN
    MODEL_INVALID = MODEL_INVALID
    FEASIBLE = FEASIBLE
    INFEASIBLE = INFEASIBLE
    OPTIMAL = OPTIMAL

    @classmethod
    def from_cp_solver_status(cls, cp_solver_status: CpSolverStatus) -> CpsatStatus:
        try:
            return CpsatStatus(cp_solver_status)
        except ValueError:
            raise ValueError(f"Unrecognized solver status value: {cp_solver_status}")

    @property
    def is_feasible(self) -> bool:
        """Returns True if the status indicates a feasible solution."""
        return self in (CpsatStatus.FEASIBLE, CpsatStatus.OPTIMAL)

    def to_solver_status_enum(self) -> SolverStatus:
        """Returns the SolverStatus Enum corresponding to the given status code."""
        return {
            CpsatStatus.UNKNOWN: SolverStatus.UNKNOWN,
            CpsatStatus.MODEL_INVALID: SolverStatus.MODEL_INVALID,
            CpsatStatus.FEASIBLE: SolverStatus.FEASIBLE,
            CpsatStatus.INFEASIBLE: SolverStatus.INFEASIBLE,
            CpsatStatus.OPTIMAL: SolverStatus.OPTIMAL,
        }[self]

    @staticmethod
    def get_obj_value_and_bound_for_infeasible(is_maximize: bool) -> tuple[int, int]:
        if is_maximize:
            return INT_MIN, INT_MIN
        else:
            return INT_MAX, INT_MAX
