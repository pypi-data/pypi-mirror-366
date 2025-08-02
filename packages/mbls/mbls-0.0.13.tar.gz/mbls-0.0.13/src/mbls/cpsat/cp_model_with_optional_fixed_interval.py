from typing import Hashable

from ortools.sat.python.cp_model import IntVar

from .cp_model_with_fixed_interval import CpModelWithFixedInterval


class CpModelWithOptionalFixedInterval(CpModelWithFixedInterval):
    # Variables

    var_op_is_present: dict[Hashable, IntVar]
    """
    Dictionary to store presence indicator variables for each operation in a job.
    """

    var_op_intvl_opt_fixed_name_set: set[str]
    """
    Set to store names of optional fixed interval variables.
    """

    def __init__(self, horizon: int):
        """Initialize the CpModelWithOptionalFixedInterval class.

        Args:
            horizon (int): The horizon for the scheduling problem,
                           which is the maximum time that any operation can end.
        """
        super().__init__(horizon)

        # Initialize dictionaries to store variables
        self.var_op_is_present = {}

        # Initialize the set to store interval variable names
        self.var_op_intvl_opt_fixed_name_set = set()

    def define_optional_fixed_interval_var(self, name: Hashable, processing_time: int):
        """Define an optional interval variable with fixed processing time
        for an operation.

        Args:
            name (Hashable): The name of the operation.
            processing_time (int): The processing time of the operation.
        """
        # method var_optional_casts on line 184 in constraint_program_model.py

        suffix = self._from_name_to_var_name_suffix(name)
        var_name = f"intvlOptFixed_{suffix}"
        # Check if the interval variable name already exists
        if var_name in self.var_op_intvl_opt_fixed_name_set:
            raise ValueError(
                f"Optional fixed interval variable name '{var_name}' already exists."
            )

        # Create an optional interval variable with the specified processing time
        start_var = self.new_int_var(0, self.horizon, f"start_{suffix}")
        end_var = self.new_int_var(0, self.horizon, f"end_{suffix}")
        is_present_var = self.new_bool_var(f"isPresent_{suffix}")
        intvl_var = self.new_optional_interval_var(
            start_var, processing_time, end_var, is_present_var, var_name
        )

        # Add each variable to the corresponding dictionaries
        self.var_op_start[name] = start_var
        self.var_op_end[name] = end_var
        self.var_op_is_present[name] = is_present_var
        self.var_op_intvl[name] = intvl_var

        # Add name of the new variable to the set
        self.var_op_intvl_opt_fixed_name_set.add(var_name)
