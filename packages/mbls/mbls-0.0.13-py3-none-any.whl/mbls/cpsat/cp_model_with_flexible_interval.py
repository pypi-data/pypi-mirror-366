from typing import Hashable

from ortools.sat.python.cp_model import IntVar

from .cp_model_with_fixed_interval import CpModelWithFixedInterval


class CpModelWithFlexibleInterval(CpModelWithFixedInterval):
    # Variables

    var_op_lth: dict[Hashable, IntVar]
    """
    Dictionary to store length variables for each operation in a job.
    The keys are job names, stage names, and machine names.
    """

    var_op_intvl_flex_name_set: set[str]
    """
    Set to store names of flexible interval variables.
    """

    def __init__(self, horizon: int):
        """Initialize the CpModelWithFlexibleInterval class.

        Args:
            horizon (int): The horizon for the scheduling problem,
                           which is the maximum time that any operation can end.
        """
        super().__init__(horizon)

        # Initialize dictionaries to store variables
        self.var_op_lth = {}

        # Initialize the set to store interval variable names
        self.var_op_intvl_flex_name_set = set()

    def define_flexible_interval_var(self, name: Hashable, p_lb: int, p_ub: int):
        """Define a flexible interval variable for an operation.

        Args:
            name (Hashable): The name of the operation.
            p_lb (int): The lower bound of the processing time.
            p_ub (int): The upper bound of the processing time.
        """
        # If name is tuple, use "_".join(name) as the suffix
        if isinstance(name, tuple):
            suffix = "_".join(map(str, name))
        else:
            suffix = str(name)

        var_name = f"intvl_flex_{suffix}"
        # Check if the interval variable name already exists
        if var_name in self.var_op_intvl_flex_name_set:
            raise ValueError(
                f"Flexible interval variable name '{var_name}' already exists."
            )

        # Create a flexible interval variable with the specified lower and upper bounds
        start_var = self.new_int_var(0, self.horizon, f"start_{suffix}")
        end_var = self.new_int_var(0, self.horizon, f"end_{suffix}")
        lth_var = self.new_int_var(p_lb, p_ub, f"lth_{suffix}")
        intvl_var = self.new_interval_var(start_var, lth_var, end_var, var_name)

        # Add each variable to the corresponding dictionaries
        self.var_op_start[name] = start_var
        self.var_op_end[name] = end_var
        self.var_op_lth[name] = lth_var
        self.var_op_intvl[name] = intvl_var

        # Add name of the new variable to the set
        self.var_op_intvl_flex_name_set.add(var_name)
