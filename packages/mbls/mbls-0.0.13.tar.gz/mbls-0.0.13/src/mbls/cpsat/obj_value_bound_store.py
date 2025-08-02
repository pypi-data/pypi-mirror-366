from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from routix.metric_time_series import MetricTimeSeries, NamedTimeSeriesStore
from routix.type_defs import NumericT


class ObjValueBoundStore(NamedTimeSeriesStore[NumericT]):
    """A store for objective value and bound time series data.

    This class extends NamedTimeSeriesStore to specifically handle
    objective values and bounds in a time series format.
    """

    def __init__(self) -> None:
        super().__init__()

        self.obj_value_series: MetricTimeSeries[NumericT] = self.get_or_create(
            "obj_value"
        )
        """MetricTimeSeries for objective values."""
        self.obj_bound_series: MetricTimeSeries[NumericT] = self.get_or_create(
            "obj_bound"
        )
        """MetricTimeSeries for objective bounds."""

    # Setters

    def add_obj_value(
        self, timestamp: float, value: NumericT, is_maximize: bool | None = False
    ) -> None:
        """Add an objective value to the store.

        Args:
            timestamp (float): _timestamp_ of the objective value.
            value (NumericT): the objective _value_.
            is_maximize (bool | None, optional):
                - If True, add if the value is greater than the last value.
                - If False, add if the value is less than the last value.
                - If None, add the value without any condition.
                - Defaults to False.
        """
        if is_maximize is None:
            self.obj_value_series.add(timestamp, value)
        elif is_maximize:
            self.obj_value_series.add_if_value_stg_last(timestamp, value)
        else:
            self.obj_value_series.add_if_value_stl_last(timestamp, value)

    def add_obj_bound(
        self, timestamp: float, value: NumericT, is_maximize: bool | None = False
    ) -> None:
        """Add an objective bound to the store.

        Args:
            timestamp (float): _timestamp_ of the objective value.
            value (NumericT): _value_ of the objective bound.
            is_maximize (bool | None, optional):
                - If True, add if the bound is less than the last bound.
                - If False, add if the bound is greater than the last bound.
                - If None, add the bound without any condition.
                - Defaults to False.
        """
        if is_maximize is None:
            self.obj_bound_series.add(timestamp, value)
        elif is_maximize:
            self.obj_bound_series.add_if_value_stl_last(timestamp, value)
        else:
            self.obj_bound_series.add_if_value_stg_last(timestamp, value)

    def add_last_timestamp_note(
        self,
        note: Any,
        do_overwrite: bool = False,
        obj_value_is_valid: bool = False,
        obj_bound_is_valid: bool = False,
    ) -> None:
        """
        Add a note to the last timestamp of the objective value and bound series.
        This method checks the last timestamps of both the objective value and bound
        series to determine where to add the note. If both series have valid last
        timestamps, the note is added to both. If only one series has a valid last
        timestamp, the note is added to that series.

        Args:
            note (Any): Note to be added to the last timestamp.
            overwrite (bool, optional): If True, overwrite the last value with the note.
                Defaults to False.
            obj_value_is_valid (bool, optional): True if the last objective value is valid.
                Defaults to False.
            obj_bound_is_valid (bool, optional): True if the last objective bound is valid.
                Defaults to False.
        """
        obj_value_last_timestamp: float | None = self.obj_value_series.last_timestamp
        obj_bound_last_timestamp: float | None = self.obj_bound_series.last_timestamp

        # True if the last objective value is valid
        obj_value_note_cond = (
            obj_value_is_valid and obj_value_last_timestamp is not None
        )
        # True if the last objective bound is valid
        obj_bound_note_cond = (
            obj_bound_is_valid and obj_bound_last_timestamp is not None
        )
        # If both values are invalid, we have nothing to do
        if not (obj_value_note_cond or obj_bound_note_cond):
            return

        # Determine the last timestamp to use for adding the note
        # If both are None, we have no data to add a note to
        if obj_value_note_cond and obj_bound_note_cond:
            # If both are valid, we use the maximum of the two
            assert obj_value_last_timestamp is not None
            assert obj_bound_last_timestamp is not None
            last_timestamp = max(obj_value_last_timestamp, obj_bound_last_timestamp)
            self.obj_value_series.repeat_last_value(
                last_timestamp, note=note, overwrite_note=do_overwrite
            )
            self.obj_bound_series.repeat_last_value(
                last_timestamp, note=note, overwrite_note=do_overwrite
            )
        # If one is None, we use the other
        elif obj_value_note_cond:
            assert obj_value_last_timestamp is not None
            self.obj_value_series.repeat_last_value(
                obj_value_last_timestamp, note=note, overwrite_note=do_overwrite
            )
        elif obj_bound_note_cond:
            assert obj_bound_last_timestamp is not None
            self.obj_bound_series.repeat_last_value(
                obj_bound_last_timestamp, note=note, overwrite_note=do_overwrite
            )

    # I/O from/to dict

    def to_dict(self) -> dict[str, dict[str, Any]]:
        return super().to_dict()

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, Any]]) -> ObjValueBoundStore:
        """Create an ObjValueBoundStore from a dictionary."""
        # obj_value_series and obj_bound_series will be initialized in __init__
        store = cls()
        store.clear()  # Clear existing data before loading new data

        for name, ts_data in data.items():
            store._store[name] = MetricTimeSeries.from_dict(ts_data)

        # Ensure obj_value_series and obj_bound_series are initialized or binded
        store.obj_value_series = store.get_or_create("obj_value")
        store.obj_bound_series = store.get_or_create("obj_bound")
        return store

    # I/O from/to YAML

    def save_yaml(self, file_path: Path | str, encoding: str = "utf-8") -> None:
        """Save to a YAML file.

        Args:
            file_path (str): Path to the YAML file where the store will be saved.
            encoding (str, optional): Encoding to use when writing the file. Defaults to "utf-8".
        """
        super().save_yaml(file_path, encoding=encoding)

    @classmethod
    def load_yaml(
        cls, file_path: Path | str, encoding: str = "utf-8"
    ) -> ObjValueBoundStore:
        """Load an ObjValueBoundStore from a YAML file.

        Args:
            file_path (str): Path to the YAML file from which the store will be loaded.
            encoding (str, optional): Encoding to use when writing the file. Defaults to "utf-8".

        Returns:
            ObjValueBoundStore[NumericT]: An instance of ObjValueBoundStore populated with the data.
        """
        with open(file_path, "r", encoding=encoding) as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data)
