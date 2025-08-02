from abc import ABC, ABCMeta, abstractmethod

from ortools.sat.python.cp_model import CpSolverSolutionCallback


# Suppress the dynamic-base-class warning: we're combining two metaclasses.
class _CombinedMeta(ABCMeta, type(CpSolverSolutionCallback)):  # type: ignore[misc]
    """Combine ABCMeta with CpSolverSolutionCallback's SWIG metaclass."""

    pass


class BaseSolutionCallback(ABC, CpSolverSolutionCallback, metaclass=_CombinedMeta):
    def __init__(self, **kwargs) -> None:
        # 1) explicitly initialize the C++ wrapper
        CpSolverSolutionCallback.__init__(self)
        # 2) then delegate up the Python MRO
        super().__init__(**kwargs)

    @abstractmethod
    def on_solution_callback(self) -> None: ...

    def StopSearch(self) -> None:
        return super().StopSearch()
