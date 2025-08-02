import logging
from datetime import datetime
from typing import Any, cast

import pendulum
import polars as pl

logger = logging.getLogger("root")


def adaptive_downsample(df: pl.DataFrame, column: str, window_size: int, threshold: float, max_rows: int = 7_800_000) -> pl.DataFrame:
    """Adaptive downsampling of data points based on rate of change."""
    if df.is_empty() or df.height <= max_rows:
        return df

    while True:
        downsampled_data = []
        time_stamps = []

        for i in range(0, df.height, window_size):
            window = df.slice(i, window_size)
            rate_of_change_raw = window[column].diff().abs().mean()

            # Handle None case - if no valid rate of change, default to downsampling
            rate_of_change: float = 0.0 if rate_of_change_raw is None else cast(float, rate_of_change_raw)

            if rate_of_change > threshold:
                downsampled_data.extend(window[column].to_list())
                time_stamps.extend(window["Time Stamp"].to_list())
            else:
                downsampled_data.append(window[column].mean())
                time_stamps.append(window["Time Stamp"][0])

        downsampled_df = pl.DataFrame({"Time Stamp": time_stamps, "Value": downsampled_data})

        if downsampled_df.height <= max_rows:
            return downsampled_df

        threshold *= 1.1


def normalize_timestamp(ts: Any) -> pl.Series:
    if isinstance(ts, str):
        parsed = pendulum.parse(ts)
        # Only DateTime objects have timestamp() method
        if isinstance(parsed, pendulum.DateTime):
            return pl.from_epoch([int(parsed.timestamp())]).cast(pl.Datetime("us", "UTC"))
        else:
            raise ValueError(f"Parsed timestamp '{parsed}' is not a datetime")
    elif isinstance(ts, (int, float)):
        ts_int = int(ts)  # Convert to int for pl.from_epoch
        if ts_int < 10_000_000_000:  # seconds
            return pl.from_epoch([ts_int], time_unit="s").cast(pl.Datetime("us", "UTC"))
        return pl.from_epoch([ts_int], time_unit="ms").cast(pl.Datetime("us", "UTC"))
    elif isinstance(ts, (datetime, pendulum.DateTime)):
        return pl.from_epoch([int(ts.timestamp())]).cast(pl.Datetime("us", "UTC"))
    raise ValueError(f"Unsupported timestamp format: {type(ts)}")


def process_metric_data(df: pl.DataFrame, start_date, end_date) -> pl.DataFrame:
    """Process metric data, handling empty dataframes and type conversions."""
    schema = {"Time Stamp": pl.Datetime("us", "UTC"), "Value": pl.Float64}
    if df.is_empty():
        logger.warning("Empty DataFrame received")
        return pl.DataFrame({"Time Stamp": pl.concat([normalize_timestamp(start_date), normalize_timestamp(end_date)]), "Value": pl.Series([0.0, 0.0])}).with_columns([
            pl.col("Time Stamp").cast(schema["Time Stamp"]),
            pl.col("Value").cast(schema["Value"]),
        ])
    df = df.sort("Time Stamp")
    first_timestamp = df["Time Stamp"][0]
    if isinstance(first_timestamp, (int, float)):
        time_unit = "s" if first_timestamp < 10000000000 else "ms"
        df = df.with_columns(pl.from_epoch("Time Stamp", time_unit=time_unit).cast(schema["Time Stamp"]))
    else:
        df = df.with_columns(pl.col("Time Stamp").cast(schema["Time Stamp"]))
    return df.with_columns(pl.col("Value").cast(schema["Value"]))


def calculate_scheduler_resources(scheduler_resources: dict[str, float]) -> str:
    """Calculate resources for software."""
    if scheduler_resources["memory"] % 384 == 0 and scheduler_resources["cpu"] % 100 == 0:
        if scheduler_resources["cpu"] / 100 == scheduler_resources["memory"] / 384:
            return str(scheduler_resources["cpu"] / 100)
    res = {
        "Memory": str(scheduler_resources["memory"] / 1024) + " GiB",
        "CPU": str(scheduler_resources["cpu"] / 1000) + " vCPU",
    }
    res_str = "{}, {}".format(res["CPU"], res["Memory"])
    return res_str


def calculate_worker_concurrency(env_vars: list[dict]) -> int:
    """Calculate worker concurrency for software."""
    concurrency = 16
    for env_var in env_vars:
        if env_var["key"] == "AIRFLOW__CELERY__WORKER_CONCURRENCY":
            return int(env_var["value"])
    return concurrency


def calculate_worker_type(worker_resources: dict) -> dict:
    """Calculate worker type for software."""
    worker_type = {
        "machinetype": "",  # Software doesn't have machine type
        "Memory": str(worker_resources["memory"] / 1024) + " GiB",
        "CPU": str(worker_resources["cpu"] / 1000) + " vCPU",
    }
    return worker_type
