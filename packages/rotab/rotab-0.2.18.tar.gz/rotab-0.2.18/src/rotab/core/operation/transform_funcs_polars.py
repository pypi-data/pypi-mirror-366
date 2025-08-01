import polars as pl
from typing import List, Dict, Any
from datetime import date
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Tuple


def normalize_dtype(dtype: str):
    mapping = {
        "int": pl.Int64,
        "float": pl.Float64,
        "str": pl.String,
        "string": pl.String,
        "bool": pl.Boolean,
        "datetime": pl.Datetime,
        "datetime[ns]": pl.Datetime,
        "object": pl.String,
    }
    return mapping.get(dtype, dtype)


def validate_table_schema(df: pl.DataFrame, columns: List[dict]) -> bool:
    supported_dtypes = {pl.Int64, pl.Float64, pl.String, pl.Boolean, pl.Datetime}

    if not isinstance(columns, list) or not all(isinstance(c, dict) for c in columns):
        raise ValueError("Invalid schema: 'columns' must be a list of dicts")

    for col_def in columns:
        col_name = col_def["name"]
        expected = normalize_dtype(col_def["dtype"])

        if expected not in supported_dtypes:
            raise ValueError(f"Unsupported type in schema: {col_def['dtype']} for column: {col_name}")

        if col_name not in df.columns:
            raise ValueError(f"Missing required column: {col_name}")

        actual = df.schema[col_name]

        if actual != expected:
            raise ValueError(
                f"Type mismatch for column '{col_name}': expected {expected.__class__.__name__}, got {actual.__class__.__name__}"
            )

    return True


def sort_by(table: pl.DataFrame, column: str, ascending: bool = True) -> pl.DataFrame:
    return table.sort(by=column, descending=not ascending)


from typing import Dict, List, Union

import polars as pl


def groupby_agg(
    table: pl.DataFrame,
    by: Union[str, List[str]],
    aggregations: Dict[str, str],
) -> pl.DataFrame:
    aggs = [getattr(pl.col(col), agg)().alias(col) for col, agg in aggregations.items()]
    return table.group_by(by).agg(aggs)


def drop_duplicates(table: pl.DataFrame, subset: List[str] = None) -> pl.DataFrame:
    return table.unique(subset=subset)


def merge(left: pl.DataFrame, right: pl.DataFrame, on: Union[str, List[str]], how: str = "inner") -> pl.DataFrame:
    if isinstance(on, str):
        on = [on]
    return left.join(right, on=on, how=how)


def reshape(
    table: pl.DataFrame,
    column_to: str = None,
    columns_from: List[str] = None,
    column_value: str = None,
    agg: str = None,
) -> pl.DataFrame:
    if agg:
        if columns_from is None or column_value is None:
            raise ValueError("columns_from and column_value must be specified for pivot with aggregation.")
        pivoted = table.pivot(values=column_value, index=column_to, columns=columns_from[0], aggregate_function=agg)
        return pivoted

    elif column_value and columns_from:
        pivoted = table.pivot(values=column_value, index=column_to, columns=columns_from[0])
        return pivoted

    elif column_value and not columns_from:
        melted = table.melt(
            id_vars=[column_to], value_vars=[column_value], variable_name="variable", value_name="melted_value"
        )
        return melted

    else:
        raise ValueError("Invalid combination of parameters for reshape.")


def fillna(table: pl.DataFrame, mapping: Dict[str, Any]) -> pl.DataFrame:
    return table.with_columns([pl.col(k).fill_null(v) for k, v in mapping.items()])


def sample(table: pl.DataFrame, frac: float) -> pl.DataFrame:
    return table.sample(fraction=frac)


def concat(tables: List[pl.DataFrame]) -> pl.DataFrame:
    return pl.concat(tables, how="vertical")


def drop_na(table: pl.DataFrame, subset: List[str] = None) -> pl.DataFrame:
    return table.drop_nulls(subset=subset)


def replace(table: pl.DataFrame, columns: List[str], old: Any, new: Any) -> pl.DataFrame:
    table_copy = table.clone()
    for col in columns:
        table_copy = table_copy.with_columns(pl.col(col).replace(old, new).alias(col))
    return table_copy


def unique(df: pl.DataFrame, group_keys: list[str], sort_by: str, ascending: bool = True) -> pl.DataFrame:
    return df.sort(group_keys + [sort_by], descending=not ascending).group_by(group_keys, maintain_order=True).first()


def _parse_date_column(column: pl.Expr, fmt: str) -> pl.Expr:
    if "%d" not in fmt:
        last_char = fmt[-1]
        is_delimited = not last_char.isalpha()

        if is_delimited:
            column = column + f"{last_char}01"
            fmt += f"{last_char}%d"
        else:
            column = column + "01"
            fmt += "%d"

    return column.str.strptime(pl.Datetime, fmt)


def month_window(
    df_base: pl.LazyFrame,
    df_data: pl.LazyFrame,
    date_col: str,
    date_format: str,
    value_cols: List[str],
    months_list: List[int],
    new_col_name_prefix: str = "future_value",
    metrics: List[str] = ["mean", "sum", "max"],
    keys: List[str] = [],
) -> pl.LazyFrame:
    _base_date = "__mw_base_date__"
    _data_date = "__mw_data_date__"
    _row_id = "__mw_row_id__"
    _window_start = "__mw_window_start__"
    _window_end = "__mw_window_end__"
    _join_key = "__mw_join_key__"

    def dbg(label, df):
        print(f"\n🟡 DEBUG: {label}")
        try:
            print(df.schema)
        except Exception as e:
            print(f"❌ schema error: {e}")
        return df

    df_base_processed = df_base.with_columns(
        [
            pl.col(date_col)
            .str.strptime(pl.Datetime, date_format, strict=False)
            .cast(pl.Datetime("us"))
            .alias(_base_date),
            (
                pl.concat_str([pl.col(k) for k in keys], separator="|").alias(_join_key)
                if keys
                else pl.lit("").alias(_join_key)
            ),
        ]
    )
    df_base_processed = dbg("after with_columns (base)", df_base_processed)

    df_base_processed = df_base_processed.with_row_index(_row_id)
    df_base_processed = dbg("after with_row_index", df_base_processed)

    results = []

    for m in months_list:
        suffix = f"_{abs(m)}m"
        direction = "past" if m < 0 else "future"
        join_strategy = "forward" if m < 0 else "backward"

        df_data_corrected = df_data.with_columns(
            [
                (
                    pl.col(date_col).str.strptime(pl.Datetime, date_format, strict=False)
                    + (pl.duration(microseconds=1) if m < 0 else pl.duration(microseconds=0))
                ).alias(_data_date),
                (
                    pl.concat_str([pl.col(k) for k in keys], separator="|").alias(_join_key)
                    if keys
                    else pl.lit("").alias(_join_key)
                ),
            ]
        ).sort([_join_key, _data_date])
        df_data_corrected = dbg(f"data_corrected (m={m})", df_data_corrected)

        df_base_sorted = df_base_processed.sort([_join_key, _base_date])
        df_base_sorted = dbg(f"base_sorted (m={m})", df_base_sorted)

        df_joined = df_data_corrected.join_asof(
            df_base_sorted,
            left_on=_data_date,
            right_on=_base_date,
            by=_join_key,
            strategy=join_strategy,
        )
        df_joined = dbg(f"joined (m={m})", df_joined)

        df_joined = df_joined.with_columns(
            [
                (
                    (pl.col(_base_date).dt.offset_by(f"{m}mo")).alias(_window_start)
                    if m < 0
                    else pl.col(_base_date).alias(_window_start)
                ),
                (
                    (pl.col(_base_date)).alias(_window_end)
                    if m < 0
                    else pl.col(_base_date).dt.offset_by(f"{m}mo").alias(_window_end)
                ),
            ]
        )
        df_joined = dbg(f"window_applied (m={m})", df_joined)

        df_filtered = df_joined.filter(
            (pl.col(_data_date) >= pl.col(_window_start)) & (pl.col(_data_date) < pl.col(_window_end))
        )
        df_filtered = dbg(f"filtered (m={m})", df_filtered)

        aggs = []
        for col in value_cols:
            for metric in metrics:
                alias_name = f"{new_col_name_prefix}_{col}_{metric}_{direction}{suffix}"
                aggs.append(getattr(pl.col(col), metric)().alias(alias_name))

        df_agg = df_filtered.group_by(keys + [_row_id]).agg(aggs)
        df_agg = dbg(f"aggregated (m={m})", df_agg)

        results.append(df_agg)

    final_df = df_base_processed
    for i, res_df in enumerate(results):
        final_df = final_df.join(res_df, on=keys + [_row_id], how="left")
        final_df = dbg(f"after join result[{i}]", final_df)

    final_df = final_df.drop(_row_id).drop(_base_date).drop(_join_key)
    final_df = dbg("final before return", final_df)

    return final_df


def is_date_column(series: pl.Series, fmt: str = "%Y-%m-%d") -> bool:
    if series.is_empty() or series.null_count() == len(series):
        return True

    non_null_str_series = series.drop_nulls().cast(str)

    if non_null_str_series.is_empty():
        return True

    try:
        parsed = non_null_str_series.str.strptime(pl.Date, fmt=fmt, strict=False)
    except TypeError:
        try:
            parsed = non_null_str_series.str.strptime(pl.Date, format=fmt, strict=False)
        except Exception:
            return False
    except Exception:
        return False

    return parsed.drop_nulls().len() == len(non_null_str_series)


def is_float_column(series: pl.Series) -> bool:
    try:
        temp_series = series.drop_nulls().cast(str)
        if temp_series.is_empty():
            return True
        return temp_series.cast(pl.Float64, strict=False).null_count() == 0
    except Exception:
        return False


def is_int_column(series: pl.Series) -> bool:
    try:
        temp_series = series.drop_nulls().cast(str)
        if temp_series.is_empty():
            return True
        return temp_series.cast(pl.Int64, strict=False).null_count() == 0
    except Exception:
        return False


def _get_item_or_scalar(polars_result: Any) -> Any:
    """Safely extracts item from Polars Series or returns scalar directly."""
    if isinstance(polars_result, pl.Series):
        if polars_result.len() == 1 and not polars_result.is_null()[0]:
            return polars_result.item()
        return None  # Series is empty or contains null, return None
    return polars_result  # Already a scalar


def describe(df: pl.DataFrame, date_format: str = None) -> pl.DataFrame:
    summaries = []

    full_summary_keys = {
        "column",
        "dtype",
        "mean",
        "std",
        "min",
        "max",
        "Q1",
        "median",
        "Q3",
        "zeros",
        "infinite",
        "top",
        "top_freq",
        "top_ratio",
        "min_cat",
        "min_freq",
        "min_ratio",
        "avg_length",
        "min_length",
        "max_length",
        "n_unique",
        "n_nulls",
        "min_year",
        "max_year",
        "min_month",
        "max_month",
        "mode",
        "mode_freq",
        "mode_ratio",
        "range_days",
    }

    for col in df.columns:
        series = df[col]
        nulls = series.null_count()
        n_unique = series.n_unique()

        current_summary_data = {"column": col, "n_unique": n_unique, "n_nulls": nulls}
        for key in full_summary_keys:
            if key not in current_summary_data:
                current_summary_data[key] = None

        summarized = False

        if is_date_column(series, date_format):
            parsed_series_dt = None

            formats_to_try = []
            if date_format:
                formats_to_try.append(date_format)
            formats_to_try.extend(["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m", "%Y/%m", "%Y"])

            seen = set()
            unique_formats = []
            for fmt in formats_to_try:
                if fmt not in seen:
                    unique_formats.append(fmt)
                    seen.add(fmt)

            for fmt in unique_formats:
                temp_series_str = series.cast(pl.String).str.strip_chars()
                temp_parsed = _parse_date_column(temp_series_str, fmt)

                if (series.len() - nulls) > 0 and temp_parsed.drop_nulls().len() / (series.len() - nulls) >= 0.8:
                    parsed_series_dt = temp_parsed
                    break

            if parsed_series_dt is not None:
                # min/max/modeの値をPythonのdateオブジェクトとして取得し、strftimeでフォーマット
                min_date_obj = _get_item_or_scalar(parsed_series_dt.min())
                max_date_obj = _get_item_or_scalar(parsed_series_dt.max())

                current_summary_data.update(
                    {
                        "dtype": "date",
                        "min": min_date_obj.strftime("%Y-%m-%d") if min_date_obj is not None else None,
                        "max": max_date_obj.strftime("%Y-%m-%d") if max_date_obj is not None else None,
                        "min_year": (
                            str(_get_item_or_scalar(parsed_series_dt.dt.year().min()))
                            if not parsed_series_dt.drop_nulls().is_empty()
                            else None
                        ),
                        "max_year": (
                            str(_get_item_or_scalar(parsed_series_dt.dt.year().max()))
                            if not parsed_series_dt.drop_nulls().is_empty()
                            else None
                        ),
                        "min_month": (
                            str(_get_item_or_scalar(parsed_series_dt.dt.month().min()))
                            if not parsed_series_dt.drop_nulls().is_empty()
                            else None
                        ),
                        "max_month": (
                            str(_get_item_or_scalar(parsed_series_dt.dt.month().max()))
                            if not parsed_series_dt.drop_nulls().is_empty()
                            else None
                        ),
                    }
                )

                date_only_series = parsed_series_dt.drop_nulls()
                mode_counts = date_only_series.value_counts().sort("count", descending=True)
                if not mode_counts.is_empty():
                    mode_val_date_obj = _get_item_or_scalar(mode_counts[0, date_only_series.name])
                    mode_freq = _get_item_or_scalar(mode_counts[0, "count"])

                    mode_ratio = float(mode_freq) / len(date_only_series) if len(date_only_series) > 0 else 0.0

                    current_summary_data.update(
                        {
                            "mode": mode_val_date_obj.strftime("%Y-%m-%d") if mode_val_date_obj is not None else None,
                            "mode_freq": str(mode_freq),
                            "mode_ratio": str(mode_ratio),
                        }
                    )
                else:
                    current_summary_data.update({"mode": None, "mode_freq": None, "mode_ratio": None})

                if current_summary_data["min"] is not None and current_summary_data["max"] is not None:
                    try:
                        # ここではすでにYYYY-MM-DD形式の文字列になっているので、date.fromisoformatで安全に変換できる
                        temp_min_date = date.fromisoformat(current_summary_data["min"])
                        temp_max_date = date.fromisoformat(current_summary_data["max"])
                        range_days_val = (temp_max_date - temp_min_date).days
                        current_summary_data["range_days"] = str(range_days_val)
                    except ValueError:
                        current_summary_data["range_days"] = None
                else:
                    current_summary_data["range_days"] = None

                summarized = True
            else:
                current_summary_data["dtype"] = "error"
                summarized = True

            if summarized:
                summaries.append(current_summary_data)
                continue

        elif is_float_column(series):
            series_float = series.cast(pl.String).cast(pl.Float64, strict=False)

            current_summary_data.update(
                {
                    "mean": str(_get_item_or_scalar(series_float.mean())),
                    "std": str(_get_item_or_scalar(series_float.std())),
                    "min": str(_get_item_or_scalar(series_float.min())),
                    "max": str(_get_item_or_scalar(series_float.max())),
                    "Q1": str(_get_item_or_scalar(series_float.quantile(0.25, "nearest"))),
                    "median": str(_get_item_or_scalar(series_float.median())),
                    "Q3": str(_get_item_or_scalar(series_float.quantile(0.75, "nearest"))),
                    "zeros": str(_get_item_or_scalar((series_float == 0).sum())),
                    "infinite": str(_get_item_or_scalar(series_float.is_infinite().sum())),
                }
            )

            if is_int_column(series):
                current_summary_data["dtype"] = "int"
            else:
                current_summary_data["dtype"] = "float"
            summarized = True
            if summarized:
                summaries.append(current_summary_data)
                continue

        else:
            series_str = series.drop_nulls().cast(pl.String)
            vc = series_str.value_counts().sort("count", descending=True)

            top = top_freq = min_cat = min_freq = None
            if not vc.is_empty():
                top = str(_get_item_or_scalar(vc[0, series_str.name]))
                top_freq = str(_get_item_or_scalar(vc[0, "count"]))

                if vc.height > 1:
                    min_cat = str(_get_item_or_scalar(vc[-1, series_str.name]))
                    min_freq = str(_get_item_or_scalar(vc[-1, "count"]))
                elif vc.height == 1:
                    min_cat = top
                    min_freq = top_freq

            lengths = series_str.str.len_chars()

            current_summary_data.update(
                {
                    "dtype": "string",
                    "top": top,
                    "top_freq": top_freq,
                    "top_ratio": (
                        str(float(top_freq) / len(series)) if top_freq is not None and len(series) > 0 else None
                    ),
                    "min_cat": min_cat,
                    "min_freq": min_freq,
                    "min_ratio": (
                        str(float(min_freq) / len(series)) if min_freq is not None and len(series) > 0 else None
                    ),
                    "avg_length": str(_get_item_or_scalar(lengths.mean())) if lengths.len() > 0 else None,
                    "min_length": str(_get_item_or_scalar(lengths.min())) if lengths.len() > 0 else None,
                    "max_length": str(_get_item_or_scalar(lengths.max())) if lengths.len() > 0 else None,
                }
            )
            summaries.append(current_summary_data)

    final_schema = {k: pl.String for k in full_summary_keys}
    final_summary_df = pl.DataFrame(summaries, schema=final_schema)

    return final_summary_df


def get_categorical_counts_table(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    if column_name not in df.columns:
        raise ValueError(f"Error: The specified column '{column_name}' does not exist in the DataFrame.")

    series = df[column_name]
    non_null_series = series.drop_nulls()

    if non_null_series.is_empty():
        print(
            f"Warning: Column '{column_name}' contains only null values or is empty, so aggregation cannot be performed."
        )
        return pl.DataFrame()

    # Sort by 'count' descending, then by the original column_name (categories) ascending for stable order
    counts_df = non_null_series.value_counts().sort(
        ["count", column_name], descending=[True, False]  # Added secondary sort
    )
    return counts_df


def plot_categorical_bar_chart(
    categories: np.ndarray, counts: np.ndarray, column_name: str, output_filename: str = None
):
    if categories.size == 0 or counts.size == 0:
        print(f"Warning: No data available for column '{column_name}' to create a chart.")
        return

    data_list = sorted(zip(categories, counts), key=lambda x: (-x[1], x[0]))
    sorted_categories = [item[0] for item in data_list]
    sorted_counts = [item[1] for item in data_list]

    bar_trace = go.Bar(y=sorted_categories, x=sorted_counts, orientation="h", marker_color="steelblue")

    fig = go.Figure(data=[bar_trace])

    fig.update_layout(
        title={
            "text": f"Frequency of Categories for Column: {column_name}",
            "font_size": 24,
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title={"text": "Count", "font_size": 18},
        yaxis_title={"text": "Category", "font_size": 18},
        xaxis=dict(tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=18), automargin=True),
        width=1200,
        height=800,
    )

    try:
        fig.write_html(output_filename, auto_open=False)
        print(f"Horizontal bar chart for '{column_name}' saved as '{output_filename}'.")
        print(f"Please open '{output_filename}' in your web browser to view the chart.")
    except Exception as e:
        print(f"An unexpected error occurred while saving the HTML file: {e}")


def plot_numerical_distribution(data: np.ndarray, column_name: str, output_filename: str = None):
    # Check for empty data
    if data.size == 0:
        print(f"Warning: No data available for column '{column_name}' to create a chart.")
        return

    # Create subplots: 2 rows, 1 column for histogram and boxplot
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,  # Share the X-axis for better comparison
        vertical_spacing=0.1,  # Space between subplots
        subplot_titles=(f"Histogram of {column_name}", f"Boxplot of {column_name}"),
    )

    # Add Histogram trace to the first subplot
    fig.add_trace(
        go.Histogram(
            x=data,
            name="Count",  # This name appears in the legend if multiple traces are used
            marker_color="steelblue",
            xbins=dict(size=None),  # Auto binning for histogram
        ),
        row=1,
        col=1,
    )

    # Add Boxplot trace to the second subplot
    fig.add_trace(
        go.Box(
            x=data,
            name="Distribution",  # This name appears in the legend
            marker_color="steelblue",
            boxpoints="outliers",  # Show all points and outliers
            jitter=0.3,  # Spread out points if boxpoints is set
            pointpos=-1.8,  # Position of the points
            line_width=2,
            orientation="h",  # Horizontal boxplot
        ),
        row=2,
        col=1,
    )

    # Customize overall layout
    fig.update_layout(
        title={
            "text": f"Distribution of Numerical Data for Column: {column_name}",
            "font_size": 24,  # Main title font size
            "x": 0.5,  # Center the main title
            "xanchor": "center",
        },
        height=800,  # Total height of the figure
        width=1200,  # Total width of the figure
        showlegend=False,  # No need for legend as traces are clear by subplot titles
    )

    # Customize axis titles and tick fonts for each subplot
    # Row 1 (Histogram)
    fig.update_xaxes(title_text="Value", title_font_size=18, tickfont_size=16, row=1, col=1)
    fig.update_yaxes(title_text="Frequency", title_font_size=18, tickfont_size=16, row=1, col=1)

    # Row 2 (Boxplot)
    fig.update_xaxes(title_text="Value", title_font_size=18, tickfont_size=16, row=2, col=1)
    # For a horizontal boxplot, y-axis is categorical (implicitly), no title needed
    fig.update_yaxes(visible=False, row=2, col=1)  # Hide y-axis for cleaner boxplot

    try:
        fig.write_html(output_filename, auto_open=False)
        print(f"Numerical distribution chart for '{column_name}' saved as '{output_filename}'.")
        print(f"Please open '{output_filename}' in your web browser to view the chart.")
    except Exception as e:
        print(f"An unexpected error occurred while saving the HTML file: {e}")


def plot_timeseries_histogram(dates: np.ndarray, column_name: str):
    # Ensure dates are in datetime format for proper Plotly handling
    # Convert various input types to datetime, handling potential errors
    try:
        # Attempt to convert to pandas Series of datetime, then to numpy array of datetimes
        # This handles datetime objects, strings, timestamps etc.
        processed_dates = pd.to_datetime(dates).to_numpy()
    except Exception as e:
        print(
            f"Error: Could not convert input 'dates' to datetime format. Please ensure data is convertible. Error: {e}"
        )
        return

    # Check for empty data after potential conversion
    if processed_dates.size == 0:
        print(f"Warning: No valid date data available for column '{column_name}' to create a time-series histogram.")
        return

    # Create histogram trace
    # Plotly automatically handles binning for date axes
    fig = go.Figure(data=[go.Histogram(x=processed_dates, marker_color="steelblue")])

    # Customize layout for a time-series histogram
    fig.update_layout(
        title={
            "text": f"Time-Series Histogram of {column_name}",
            "font_size": 24,
            "x": 0.5,  # Center the title
            "xanchor": "center",
        },
        xaxis_title_text="Date",
        yaxis_title_text="Frequency",
        xaxis=dict(type="date", tickfont_size=16, title_font_size=18),  # Ensure x-axis is treated as a date axis
        yaxis=dict(tickfont_size=16, title_font_size=18),
        height=600,  # Height of the figure
        width=1000,  # Width of the figure
        bargap=0.1,  # Gap between bars for better visualization
        showlegend=False,
    )

    # Define output directory and ensure it exists
    output_filename = f"./samples/{column_name}_timeseries_histogram.html"

    try:
        fig.write_html(output_filename, auto_open=False)
        print(f"Time-series histogram for '{column_name}' saved as '{output_filename}'.")
        print(f"Please open '{output_filename}' in your web browser to view the chart.")
    except Exception as e:
        print(f"An unexpected error occurred while saving the HTML file: {e}")


def profile(
    df: pl.DataFrame,
    output_filename: str = "./samples/all_columns_charts.html",
    date_format: str = "%Y-%m-%d %H:%M",
):
    if df.is_empty():
        print("Warning: Input DataFrame is empty. No charts will be generated.")
        return

    plot_info = []
    for col_name in df.columns:
        series = df.get_column(col_name)
        non_null_series = series.drop_nulls()

        if non_null_series.is_empty():
            print(
                f"Warning: Column '{col_name}' is empty after dropping nulls. Skipping chart generation for this column."
            )
            continue

        is_handled = False
        if non_null_series.dtype == pl.String:
            try:
                parsed_datetime_series = _parse_date_column(pl.lit(non_null_series), date_format).to_series()
                if parsed_datetime_series.dtype == pl.Datetime and parsed_datetime_series.drop_nulls().len() > 0:
                    plot_info.append(
                        {
                            "name": col_name,
                            "type": "datetime",
                            "rows": 1,
                            "data": parsed_datetime_series.drop_nulls().to_numpy(),
                        }
                    )
                    is_handled = True
            except Exception as e:
                print(f"Warning: Failed to parse datetime for column '{col_name}': {e}")

        if is_handled:
            continue

        if non_null_series.dtype.is_numeric():
            plot_info.append({"name": col_name, "type": "numerical", "rows": 2, "data": non_null_series.to_numpy()})
        elif non_null_series.dtype == pl.Datetime:
            plot_info.append({"name": col_name, "type": "datetime", "rows": 1, "data": non_null_series.to_numpy()})
        elif non_null_series.dtype == pl.String or non_null_series.dtype == pl.Categorical:
            counts_pl_df = non_null_series.value_counts()
            category_col_name = col_name
            count_col_name = "count"
            sorted_counts_pl_df = counts_pl_df.sort([count_col_name, category_col_name], descending=[True, False])
            sorted_categories = sorted_counts_pl_df[category_col_name].to_numpy()
            sorted_counts = sorted_counts_pl_df[count_col_name].to_numpy()
            plot_info.append(
                {
                    "name": col_name,
                    "type": "categorical",
                    "rows": 1,
                    "data": {"categories": sorted_categories, "counts": sorted_counts},
                }
            )
        else:
            print(
                f"Warning: Column '{col_name}' has an unhandled data type ({non_null_series.dtype}). Skipping chart generation."
            )
            continue

    if not plot_info:
        print("No suitable columns found for plotting. No chart will be generated.")
        return

    total_rows = sum(item["rows"] for item in plot_info)
    subplot_titles = []
    for item in plot_info:
        if item["type"] == "numerical":
            subplot_titles.append(f"Histogram of {item['name']}")
            subplot_titles.append(f"Boxplot of {item['name']}")
        elif item["type"] == "categorical":
            subplot_titles.append(f"Frequency of {item['name']}")
        elif item["type"] == "datetime":
            subplot_titles.append(f"Time-Series Histogram of {item['name']}")

    fig = make_subplots(
        rows=total_rows,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.03,
        subplot_titles=subplot_titles,
    )

    current_row = 1
    for item in plot_info:
        col_name = item["name"]
        col_type = item["type"]

        if col_type == "categorical":
            sorted_categories = item["data"]["categories"]
            sorted_counts = item["data"]["counts"]
            fig.add_trace(
                go.Bar(y=sorted_categories, x=sorted_counts, orientation="h", marker_color="steelblue", name=col_name),
                row=current_row,
                col=1,
            )
            fig.update_xaxes(title_text="Count", title_font_size=18, tickfont_size=16, row=current_row, col=1)
            fig.update_yaxes(
                title_text="Category", title_font_size=18, tickfont_size=16, automargin=True, row=current_row, col=1
            )
            current_row += 1

        elif col_type == "numerical":
            col_data = item["data"]
            min_val = np.min(col_data)
            max_val = np.max(col_data)
            x_range = [min_val - (max_val - min_val) * 0.05, max_val + (max_val - min_val) * 0.05]

            fig.add_trace(
                go.Histogram(x=col_data, name=col_name, marker_color="steelblue"),
                row=current_row,
                col=1,
            )
            fig.update_yaxes(title_text="Frequency", title_font_size=18, tickfont_size=16, row=current_row, col=1)
            fig.update_xaxes(
                title_text="Value", title_font_size=18, tickfont_size=16, range=x_range, row=current_row, col=1
            )
            current_row += 1

            fig.add_trace(
                go.Box(
                    x=col_data,
                    name=col_name,
                    marker_color="steelblue",
                    boxpoints="outliers",
                    jitter=0.3,
                    pointpos=-1.8,
                    line_width=2,
                    orientation="h",
                ),
                row=current_row,
                col=1,
            )
            fig.update_yaxes(visible=False, row=current_row, col=1)
            fig.update_xaxes(
                title_text="Value", title_font_size=18, tickfont_size=16, range=x_range, row=current_row, col=1
            )
            current_row += 1

        elif col_type == "datetime":
            col_data = item["data"]
            fig.add_trace(go.Histogram(x=col_data, name=col_name, marker_color="steelblue"), row=current_row, col=1)
            fig.update_xaxes(
                title_text="Date", title_font_size=18, tickfont_size=16, type="date", row=current_row, col=1
            )
            fig.update_yaxes(title_text="Frequency", title_font_size=18, tickfont_size=16, row=current_row, col=1)
            current_row += 1

    fig.update_layout(
        title={"text": "Comprehensive Data Distribution Analysis", "font_size": 28, "x": 0.5, "xanchor": "center"},
        height=400 * total_rows,
        width=1200,
        showlegend=False,
        margin=dict(t=100, b=50, l=50, r=50),
    )

    try:
        fig.write_html(output_filename, auto_open=False)
        print(f"All charts saved to: '{output_filename}'.")
        print(f"Please open '{output_filename}' in your web browser to view the combined report.")
    except Exception as e:
        print(f"An unexpected error occurred while saving the HTML file: {e}")


def profile_bivariate(
    df: pl.DataFrame,
    column_pairs: List[Tuple[str, str]],
    output_filename: str = "./samples/bivariate_report.html",
    date_format: str = "%Y-%m-%d %H:%M",
):
    if df.is_empty():
        print("Warning: Input DataFrame is empty. No bivariate charts will be generated.")
        return

    processed_df = df.clone()
    for col_name in df.columns:
        series = df.get_column(col_name)
        if series.dtype == pl.String:
            try:
                parsed = _parse_date_column(pl.lit(series), date_format).to_series()
                if parsed.dtype == pl.Datetime and parsed.drop_nulls().len() > 0:
                    processed_df = processed_df.with_columns(parsed.alias(col_name))
            except Exception:
                pass

    plots_to_add = []
    subplot_titles = []

    for col1_name, col2_name in column_pairs:
        if col1_name not in processed_df.columns or col2_name not in processed_df.columns:
            print(f"Warning: One or both columns '{col1_name}', '{col2_name}' not found in DataFrame. Skipping pair.")
            continue

        paired_df_cleaned = processed_df.select([col1_name, col2_name]).drop_nulls()
        if paired_df_cleaned.is_empty():
            print(f"Warning: Pair ({col1_name}, {col2_name}) is empty after dropping nulls. Skipping plot.")
            continue

        s1_cleaned = paired_df_cleaned.get_column(col1_name)
        s2_cleaned = paired_df_cleaned.get_column(col2_name)
        type1 = s1_cleaned.dtype
        type2 = s2_cleaned.dtype

        trace = None
        plot_type_key = ""

        if type1.is_numeric() and type2.is_numeric():
            trace = go.Scatter(
                x=s1_cleaned.to_numpy(),
                y=s2_cleaned.to_numpy(),
                mode="markers",
                marker=dict(color="steelblue", opacity=0.7, size=8),
                name=f"{col2_name} vs {col1_name}",
                showlegend=False,
            )
            plot_type_key = "num_num_scatter"
            subplot_titles.append(f"Scatter Plot: {col1_name} vs {col2_name}")

        elif (type1.is_numeric() and (type2 == pl.String or type2 == pl.Categorical)) or (
            (type1 == pl.String or type1 == pl.Categorical) and type2.is_numeric()
        ):
            num_s_cleaned = s1_cleaned if type1.is_numeric() else s2_cleaned
            cat_s_cleaned = s2_cleaned if type1.is_numeric() else s1_cleaned
            trace = go.Box(
                x=num_s_cleaned.to_numpy(),
                y=cat_s_cleaned.to_numpy(),
                orientation="h",
                marker_color="steelblue",
                name=f"{num_s_cleaned.name} by {cat_s_cleaned.name}",
                showlegend=False,
            )
            plot_type_key = "num_cat_box"
            subplot_titles.append(f"Box Plot: {num_s_cleaned.name} by {cat_s_cleaned.name}")

        elif (type1 == pl.String or type1 == pl.Categorical) and (type2 == pl.String or type2 == pl.Categorical):
            counts_df = processed_df.group_by(col1_name, col2_name).len().rename({"len": "count"})
            all_cat1 = processed_df.get_column(col1_name).unique().sort().to_numpy()
            all_cat2 = processed_df.get_column(col2_name).unique().sort().to_numpy()
            traces = []
            for cat2_val in all_cat2:
                subset = counts_df.filter(pl.col(col2_name) == cat2_val)
                full_cat1_df = pl.DataFrame({col1_name: all_cat1})
                merged = full_cat1_df.join(subset, on=col1_name, how="left").fill_null(0).sort(col1_name)
                traces.append(
                    go.Bar(
                        x=merged["count"].to_numpy(),
                        y=merged[col1_name].to_numpy(),
                        orientation="h",
                        name=str(cat2_val),
                        hoverinfo="x+y+name+text",
                        text=np.where(
                            merged["count"].to_numpy() > 0,
                            np.full(merged.height, str(cat2_val)),
                            "",
                        ),
                        textposition="auto",
                    )
                )
            trace = traces
            plot_type_key = "cat_cat_stacked_bar"
            subplot_titles.append(f"Stacked Bar Plot: {col1_name} by {col2_name} (Counts)")

        elif (type1 == pl.Datetime and type2.is_numeric()) or (type1.is_numeric() and type2 == pl.Datetime):
            dt_s = s1_cleaned if type1 == pl.Datetime else s2_cleaned
            num_s = s2_cleaned if type1 == pl.Datetime else s1_cleaned
            trace = go.Scatter(
                x=dt_s.to_numpy(),
                y=num_s.to_numpy(),
                mode="lines+markers",
                name=f"{num_s.name} over {dt_s.name}",
                marker_color="steelblue",
                showlegend=False,
            )
            plot_type_key = "dt_num_line"
            subplot_titles.append(f"Time Series: {num_s.name} over {dt_s.name}")

        elif (type1 == pl.Datetime and (type2 == pl.String or type2 == pl.Categorical)) or (
            (type1 == pl.String or type1 == pl.Categorical) and type2 == pl.Datetime
        ):
            dt_s = s1_cleaned if type1 == pl.Datetime else s2_cleaned
            cat_s = s2_cleaned if type1 == pl.Datetime else s1_cleaned
            trace = go.Box(
                x=dt_s.to_numpy(),
                y=cat_s.to_numpy(),
                orientation="h",
                name=f"Date Distribution by {cat_s.name}",
                marker_color="steelblue",
                showlegend=False,
            )
            plot_type_key = "dt_cat_box"
            subplot_titles.append(f"Date Distribution: {dt_s.name} by {cat_s.name}")

        elif type1 == pl.Datetime and type2 == pl.Datetime:
            trace = go.Scatter(
                x=s1_cleaned.to_numpy(),
                y=s2_cleaned.to_numpy(),
                mode="markers",
                marker=dict(color="steelblue", opacity=0.7, size=8),
                name=f"{col2_name} vs {col1_name}",
                showlegend=False,
            )
            plot_type_key = "dt_dt_scatter"
            subplot_titles.append(f"Scatter Plot: {col1_name} vs {col2_name}")

        else:
            print(f"Warning: Unhandled data type combination for pair ({col1_name}, {col2_name}). Skipping plot.")
            continue

        if trace:
            plots_to_add.append(
                {
                    "trace": trace,
                    "col1_name": col1_name,
                    "col2_name": col2_name,
                    "plot_type_key": plot_type_key,
                    "types": (type1, type2),
                }
            )

    if not plots_to_add:
        print("No suitable column pairs found for plotting. No chart will be generated.")
        return

    fig = make_subplots(
        rows=len(plots_to_add),
        cols=1,
        vertical_spacing=0.03,
        subplot_titles=subplot_titles,
    )

    for i, plot_info in enumerate(plots_to_add):
        trace_data = plot_info["trace"]
        col1_name = plot_info["col1_name"]
        col2_name = plot_info["col2_name"]
        plot_type_key = plot_info["plot_type_key"]
        type1, type2 = plot_info["types"]

        if isinstance(trace_data, list):
            for single_trace in trace_data:
                fig.add_trace(single_trace, row=i + 1, col=1)
        else:
            fig.add_trace(trace_data, row=i + 1, col=1)

        xaxis_title = col1_name
        yaxis_title = col2_name
        xaxis_type = None
        yaxis_type = None

        if plot_type_key == "num_cat_box":
            num_s_name = col1_name if type1.is_numeric() else col2_name
            cat_s_name = col2_name if type1.is_numeric() else col1_name
            xaxis_title = num_s_name
            yaxis_title = cat_s_name
            yaxis_type = "category"
        elif plot_type_key == "cat_cat_stacked_bar":
            xaxis_title = "Count"
            yaxis_title = col1_name
            xaxis_type = "linear"
            yaxis_type = "category"
        elif plot_type_key == "dt_num_line":
            dt_s_name = col1_name if type1 == pl.Datetime else col2_name
            num_s_name = col2_name if type1 == pl.Datetime else col1_name
            xaxis_title = dt_s_name
            yaxis_title = num_s_name
            xaxis_type = "date"
        elif plot_type_key == "dt_cat_box":
            dt_s_name = col1_name if type1 == pl.Datetime else col2_name
            cat_s_name = col2_name if type1 == pl.Datetime else col1_name
            xaxis_title = dt_s_name
            yaxis_title = cat_s_name
            xaxis_type = "date"
            yaxis_type = "category"
        elif plot_type_key == "dt_dt_scatter":
            xaxis_title = col1_name
            yaxis_title = col2_name
            xaxis_type = "date"
            yaxis_type = "date"

        fig.update_xaxes(
            title_text=xaxis_title, title_font_size=18, tickfont_size=16, type=xaxis_type, row=i + 1, col=1
        )
        fig.update_yaxes(
            title_text=yaxis_title,
            title_font_size=18,
            tickfont_size=16,
            automargin=True,
            type=yaxis_type,
            row=i + 1,
            col=1,
        )

    fig.update_layout(
        title={"text": "Bivariate Data Analysis Report", "font_size": 28, "x": 0.5, "xanchor": "center"},
        height=500 * len(plots_to_add),
        width=1200,
        showlegend=False,
        margin=dict(t=100, b=50, l=50, r=50),
        barmode="stack",
    )

    try:
        fig.write_html(output_filename, auto_open=False)
        print(f"Bivariate charts saved to: '{output_filename}'.")
        print(f"Please open '{output_filename}' in your web browser to view the report.")
    except Exception as e:
        print(f"An unexpected error occurred while saving the HTML file: {e}")
