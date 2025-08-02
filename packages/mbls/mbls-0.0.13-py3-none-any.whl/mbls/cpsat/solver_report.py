from dataclasses import dataclass

from routix.report import SubroutineReport

from .status import CpsatStatus


@dataclass(frozen=True)
class CpsatSolverReport(SubroutineReport):
    """
    Immutable report summarizing the results of a CP-SAT solver run.

    Inherits from SubroutineReport and adds a solver status field.
    Provides structured access to status, elapsed time, objective values,
    and progress log, enabling downstream processing and standardized reporting.
    """

    status: CpsatStatus
    """Solver status as a CpsatStatus enum."""

    obj_value_records: list[tuple[float, float]]
    """
    List of (elapsed time, objective value)

    - Each entry records the state of the solver at a given time.
    - The list may not have the last entry.
    """

    obj_bound_records: list[tuple[float, float]]
    """
    List of (elapsed time, objective bound)

    - Each entry records the state of the solver at a given time.
    - The list may not have the last entry.
    """

    def to_string_dict(self) -> dict[str, str]:
        """
        Return a dictionary with string representations of each field, suitable for CSV export.

        - All values are converted to strings.
        - The status is exported as the standardized status string
          (e.g., "OPTIMAL"), not the enum representation.
        - Progress logs are wrapped in double quotes to ensure they are treated as strings in CSV.
          - If the log is empty, the string is empty.

        Returns:
            dict[str, str]: String representations of all report fields.
                - "elapsed_time"
                - "obj_value"
                - "obj_bound"
                - "status"
                - "obj_value_records"
                - "obj_bound_records"
        """
        d = super().to_string_dict()
        d["status"] = self.status.to_solver_status_enum().value
        d["obj_value_records"] = (
            f'"{self.obj_value_records}"' if self.obj_value_records else ""
        )
        d["obj_bound_records"] = (
            f'"{self.obj_bound_records}"' if self.obj_bound_records else ""
        )
        return d

    @property
    def is_feasible(self) -> bool:
        """Whether the report indicates a feasible solution.

        Returns:
            bool: True if the status corresponds to a feasible or optimal solution,
            False otherwise.
        """
        return self.status.is_feasible

    def __str__(self) -> str:
        return (
            f"CpsatSolverReport(elapsed_time={self.elapsed_time!s}, "
            f"obj_value={self.obj_value!s}, obj_bound={self.obj_bound!s}, "
            f"status={self.status!s}, "
            f"obj_value_records=[...{len(self.obj_value_records)} entries...]), "
            f"obj_bound_records=[...{len(self.obj_bound_records)} entries...])"
        )

    def __repr__(self) -> str:
        return (
            f"CpsatSolverReport(elapsed_time={self.elapsed_time!r}, "
            f"obj_value={self.obj_value!r}, obj_bound={self.obj_bound!r}, "
            f"status={self.status!r}, "
            f"obj_value_records=[...{len(self.obj_value_records)} entries...]), "
            f"obj_bound_records=[...{len(self.obj_bound_records)} entries...])"
        )
