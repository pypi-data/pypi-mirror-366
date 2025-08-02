from pathlib import Path
from typing import Any

from mbls.cpsat import ObjValueBoundStore

from .time_series_plotter import TimeSeriesPlotter


class ObjValueBoundPlotter:
    """
    Plot the objective value and bound stored in ObjValueBoundStore.
    It utilizes TimeSeriesPlotter to render time series plots.
    """

    @staticmethod
    def plot(
        store: ObjValueBoundStore,
        save_path: Path,
        show_markers: bool = True,
        label_y_offset: float = 10.0,
        drop_first_values_percent: float = 0.0,
        title: str = "Objective Value and Bound Over Time",
        xlabel: str = "Elapsed Time (seconds)",
        ylabel: str = "Objective",
        legend_loc: str = "upper right",
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        show: bool = False,
        dpi: int = 300,
        obj_value_label: str | None = None,
        obj_bound_label: str | None = None,
        obj_value_linestyle: str = "-",
        obj_bound_linestyle: str = "--",
    ):
        """Plot the objective value and bound from the given store.

        Args:
            store (ObjValueBoundStore): The store containing the time series.
            save_path (Path): File path to save the plot image.
            show_markers (bool, optional): Whether to show dots on step points.
                Defaults to True.
            label_y_offset (float, optional): Vertical offset for labels.
                Defaults to 10.0.
            drop_first_values_percent (float, optional): Drop early fraction of values (e.g. 0.01 for 1%).
                Defaults to 0.0.
            title (str, optional): Plot title.
                Defaults to "Objective Value and Bound Over Time".
            xlabel (str, optional): X-axis label.
                Defaults to "Elapsed Time (seconds)".
            ylabel (str, optional): Y-axis label.
                Defaults to "Objective".
            legend_loc (str, optional): Legend location.
                Defaults to "upper right".
            xlim (tuple[float, float] | None, optional): X-axis limits.
                Defaults to None.
            ylim (tuple[float, float] | None, optional): Y-axis limits.
                Defaults to None.
            show (bool, optional): Whether to display the plot interactively.
                Defaults to False.
            dpi (int, optional): DPI for saved figure.
                Defaults to 300.
            obj_value_label (str, optional): Label for objective value line.
                If not specified, it uses the name from the store.
            obj_bound_label (str, optional): Label for objective bound line.
                If not specified, it uses the name from the store.
            obj_value_linestyle (str, optional): Line style for objective value.
                Defaults to "-".
            obj_bound_linestyle (str, optional): Line style for objective bound.
                Defaults to "--".
        """
        # Get time series
        obj_bound_log = store.obj_bound_series.items()
        obj_value_log = store.obj_value_series.items()

        lists_of_time_and_val = []
        labels: list[str] = []
        linestyles: list[str] = []
        maps_of_time_to_note: list[dict[float, Any]] = []

        if obj_bound_log:
            lists_of_time_and_val.append(obj_bound_log)
            if obj_bound_label is None:
                labels.append(store.obj_bound_series.name)
            else:
                labels.append(obj_bound_label)
            linestyles.append(obj_bound_linestyle)
            maps_of_time_to_note.append(store.obj_bound_series.timestamp_note_map)

        if obj_value_log:
            lists_of_time_and_val.append(obj_value_log)
            if obj_value_label is None:
                labels.append(store.obj_value_series.name)
            else:
                labels.append(obj_value_label)
            linestyles.append(obj_value_linestyle)
            maps_of_time_to_note.append(store.obj_value_series.timestamp_note_map)

        TimeSeriesPlotter.plot_lists_of_time_and_val(
            lists_of_time_and_val=lists_of_time_and_val,
            save_path=save_path,
            maps_of_time_to_note=maps_of_time_to_note,
            linestyles=linestyles,
            show_markers=show_markers,
            labels=labels,
            label_y_offset=label_y_offset,
            drop_first_values_percent=drop_first_values_percent,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend_loc=legend_loc,
            xlim=xlim,
            ylim=ylim,
            show=show,
            dpi=dpi,
        )
