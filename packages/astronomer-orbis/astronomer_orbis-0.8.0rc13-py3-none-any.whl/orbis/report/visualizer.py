import json
import logging
import os
import urllib.parse

import pendulum
import plotly.graph_objects as go
import polars as pl
from pendulum import DateTime

from orbis.config import COLORS
from orbis.data.models import Figure, Metric, ReportMetadata
from orbis.data.transform import adaptive_downsample
from orbis.utils.fileio import compress_img

logger = logging.getLogger("root")


class Visualizer:
    def __init__(self, namespace: str, organization_name: str, release_name: str | None = None, resume: bool = False, metadata: ReportMetadata | None = None):
        self.namespace = namespace
        self.release_name = release_name
        self.organization_name = organization_name
        self.output_folder = f"output/{self.organization_name}"
        self.namespace_folder = f"{self.output_folder}/{self.namespace}"
        self.resume = resume
        self.resume_file = f"output/{organization_name}/.resume"
        self.metadata = metadata

        self.create_folders()

    def create_folders(self):
        import os

        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.namespace_folder, exist_ok=True)

    def _get_unique_identifier(self, metric: Metric) -> str:
        components = [metric.metric_name, self.namespace]
        return ".".join(components)

    def _load_figure(self, metric: Metric) -> Figure:
        unique_id = self._get_unique_identifier(metric)
        logger.debug(f"Loading figure from checkpoint: {unique_id}")
        with open(self.resume_file) as f:
            generated_metrics = json.load(f)

        figure_dict = generated_metrics.get(unique_id, {})
        return Figure.from_dict(figure_dict)

    def _is_graph_generated(self, metric: Metric) -> bool:
        if os.path.exists(self.resume_file):
            with open(self.resume_file) as f:
                generated_metrics = json.load(f)
            unique_id = self._get_unique_identifier(metric)
            return unique_id in generated_metrics
        return False

    def _save_figure(self, figure: Figure):
        logger.debug(f"Saving figure in checkpoint: {figure.metric.metric_identifier}")
        if not os.path.exists(self.resume_file):
            generated_metrics = {}
        else:
            with open(self.resume_file) as f:
                generated_metrics = json.load(f)

        unique_id = self._get_unique_identifier(figure.metric)
        generated_metrics[unique_id] = figure.to_dict()

        with open(self.resume_file, "w") as f:
            json.dump(generated_metrics, f, indent=4)

    def get_figure_if_resume(self, metric: Metric) -> Figure | None:
        if self.resume and self._is_graph_generated(metric):
            return self._load_figure(metric)
        return None

    def generate_combined_graph(self, dataframes: list[pl.DataFrame], metrics: list[Metric]) -> Figure:
        primary_metric = metrics[0]
        logger.info("Generating Combined Graph: %s", primary_metric.metric_name)

        fig = go.Figure()
        total_dfs = []
        y_axis = self.get_y_axis_label(primary_metric.metric_name)

        for metric, df in zip(metrics, dataframes):
            df = self.downsample_if_needed(df)
            total_dfs.append(df)

            if "small" in metric.metric_identifier:
                name = "Small Pods (<=0.25 vCPU)" if "cpu" in metric.metric_name.lower() else "Small Pods (<=0.5 GiB)"
                fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Value"].to_list(), mode="lines", name=name, line=dict(color=COLORS[0], width=1)))
            elif "large" in metric.metric_identifier:
                name = "Large Pods (>0.25 vCPU)" if "cpu" in metric.metric_name.lower() else "Large Pods (>0.5 GiB)"
                fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Value"].to_list(), mode="lines", name=name, line=dict(color=COLORS[1], width=1)))

        # Add statistics
        total_stats = self._calculate_stats(total_dfs) if total_dfs else None

        # Plot mean/median
        if total_stats and total_dfs:
            df = total_dfs[0].with_columns([pl.lit(total_stats["mean_value"]).alias("Mean"), pl.lit(total_stats["median_value"]).alias("Median")])
            fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Mean"].to_list(), mode="lines", name="Mean", line=dict(color="grey", width=2, dash="dash")))
            fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Median"].to_list(), mode="lines", name="Median", line=dict(color="magenta", width=2, dash="dashdot")))

        self.update_layout(fig, y_axis)

        image_path = f"{self.namespace_folder}/{primary_metric.file_name}"
        try:
            fig.write_image(image_path, scale=6)
            image_path = compress_img(image_path)
        except Exception as e:
            if "Chrome" in str(e) or "ChromeNotFoundError" in str(e):
                logger.warning(f"Skipping image generation for combined graph {primary_metric.metric_name} - Chrome not available: {e}")
                # Create a placeholder file to avoid breaking the report
                placeholder_path = image_path.replace(".png", "_placeholder.txt")
                with open(placeholder_path, "w") as f:
                    f.write(f"Image generation skipped - Chrome not available\nMetric: {primary_metric.metric_name}")
                image_path = placeholder_path
            else:
                raise

        figure = Figure(
            image_path=image_path,
            metric=primary_metric,
            statistics=total_stats or {},
            namespace=self.namespace,
            release_name=self.release_name,
            worker_queue_stats=primary_metric.worker_queues if "celery" in primary_metric.metric_name.lower() else None,
            url=get_prometheus_url(
                queries=primary_metric.queries,
                namespace=self.namespace,
                start_date=self.metadata.start_date if self.metadata else "",
                end_date=self.metadata.end_date if self.metadata else "",
                organization_name=self.organization_name,
                release_name=self.release_name,
            ),
        )
        self._save_figure(figure)
        return figure

    def generate_graph(self, dataframes: list[pl.DataFrame], metric: Metric) -> Figure:
        if self.resume and self._is_graph_generated(metric):
            return self._load_figure(metric)

        logger.info("Generating Graph: %s", metric.metric_name)
        fig = go.Figure()
        y_axis = self.get_y_axis_label(metric.metric_name)
        total_dfs = []

        for idx, df in enumerate(dataframes):
            try:
                df = self.downsample_if_needed(df)
                total_dfs.append(df)
                self._add_trace(fig, df, metric, idx)
            except Exception as e:
                logger.error(f"Error adding trace {idx}: {str(e)}")
                continue

        total_stats = self._calculate_stats(total_dfs) if total_dfs else None
        df = self._prepare_dataframe(total_dfs, total_stats or {})

        try:
            stats = self._calculate_statistics(df, metric)
            if total_stats:
                self._add_mean_median_traces(fig, df)

            self.update_layout(fig, y_axis)
            image_path = self._save_image(fig, metric)
            figure = self._create_figure(image_path, metric, stats)
            self._save_figure(figure)
            return figure
        except Exception as e:
            logger.error(f"Error generating figure: {str(e)}")
            raise

    def _save_image(self, fig: go.Figure, metric: Metric) -> str:
        image_path = f"{self.namespace_folder}/{metric.file_name}"
        try:
            fig.write_image(image_path, scale=6)
            return compress_img(image_path)
        except Exception as e:
            if "Chrome" in str(e) or "ChromeNotFoundError" in str(e):
                logger.warning(f"Skipping image generation for {metric.metric_name} - Chrome not available: {e}")
                # Create a placeholder file to avoid breaking the report
                placeholder_path = image_path.replace(".png", "_placeholder.txt")
                with open(placeholder_path, "w") as f:
                    f.write(f"Image generation skipped - Chrome not available\nMetric: {metric.metric_name}")
                return placeholder_path
            raise

    def _add_trace(self, fig: go.Figure, df: pl.DataFrame, metric: Metric, idx: int):
        if metric.metric_name == "Tasks Trend":
            name = "Successful Tasks" if idx == 0 else "Failed Tasks"
            fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Value"].to_list(), mode="lines", name=name, line=dict(color=COLORS[idx], width=1)))
        elif metric.pod_stats and idx < len(metric.pod_stats):
            pod_stat = metric.pod_stats[idx]
            if "cpu" in metric.metric_identifier:
                name = f"{'Small' if pod_stat.pod_type == 'small' else 'Large'} Pods {'(<=0.25 vCPU)' if pod_stat.pod_type == 'small' else '(>0.25 vCPU)'}"
            else:
                name = f"{'Small' if pod_stat.pod_type == 'small' else 'Large'} Pods {'(<=0.5 GiB)' if pod_stat.pod_type == 'small' else '(>0.5 GiB)'}"
            color = COLORS[0] if pod_stat.pod_type == "small" else COLORS[1]
            fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Value"].to_list(), mode="lines", name=name, line=dict(color=color, width=1)))
        elif metric.worker_queues and idx < len(metric.worker_queues):
            name = self.get_queue_y_axis(metric, idx, self.get_y_axis_label(metric.metric_name))
            fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Value"].to_list(), mode="lines", name=name, line=dict(color=COLORS[idx % len(COLORS)], width=1)))
        else:
            name = metric.metric_name
            fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df["Value"].to_list(), mode="lines", name=name, line=dict(color=COLORS[idx % len(COLORS)], width=1)))

    def _get_trace_name(self, metric: Metric, idx: int) -> str:
        if metric.metric_name == "Tasks Trend":
            return "Successful Tasks" if idx == 0 else "Failed Tasks"

        if metric.worker_queues and idx < len(metric.worker_queues):
            if "memory" in metric.metric_name.lower():
                return f"{metric.worker_queues[idx].queue_name} (GiB)"
            elif "cpu" in metric.metric_name.lower():
                return f"{metric.worker_queues[idx].queue_name} (vCPU)"
            return f"{metric.worker_queues[idx].queue_name}"

        if metric.pod_stats and idx < len(metric.pod_stats):
            pod_stat = metric.pod_stats[idx]
            is_small = pod_stat.pod_type == "small"
            if "kpo" in metric.metric_identifier.lower() or "ke" in metric.metric_identifier.lower():
                if "cpu" in metric.metric_identifier:
                    return f"{'Small' if is_small else 'Large'} Pods {'(<=0.25 vCPU)' if is_small else '(>0.25 vCPU)'}"
                return f"{'Small' if is_small else 'Large'} Pods {'(<=0.5 GiB)' if is_small else '(>0.5 GiB)'}"

        return metric.metric_name

    def _get_trace_color(self, metric: Metric, idx: int) -> str:
        if metric.pod_stats and idx < len(metric.pod_stats):
            return COLORS[0] if metric.pod_stats[idx].pod_type == "small" else COLORS[1]
        return COLORS[idx % len(COLORS)]

    def _prepare_dataframe(self, total_dfs: list[pl.DataFrame], total_stats: dict) -> pl.DataFrame:
        if not total_dfs:
            return pl.DataFrame({"Time Stamp": [], "Value": []}, schema={"Time Stamp": pl.Datetime("us", "UTC"), "Value": pl.Float64})

        df = total_dfs[0]
        if total_stats and not df.is_empty():
            df = df.with_columns([pl.lit(total_stats["mean_value"]).alias("Mean"), pl.lit(total_stats["median_value"]).alias("Median")])
        return df

    def _calculate_statistics(self, df: pl.DataFrame, metric: Metric) -> dict:
        if df.is_empty():
            return dict.fromkeys(["mean_value", "median_value", "max_value", "min_value", "p90_value", "last_value"], 0)

        stats = {
            "mean_value": df["Value"].mean() or 0,
            "median_value": df["Value"].median() or 0,
            "max_value": df["Value"].max() or 0,
            "min_value": df["Value"].min() or 0,
            "p90_value": df["Value"].quantile(0.9) or 0,
        }

        stats["last_value"] = self._calculate_task_total(df) if "Total Task" in metric.metric_name else df.sort("Time Stamp").select("Value").row(-1)[0] if "Time Stamp" in df.columns else 0

        return stats

    def _calculate_task_total(self, df: pl.DataFrame) -> float:
        try:
            if df.is_empty():
                return 0

            df = df.sort("Time Stamp")
            values = df["Value"].to_list()
            total = 0
            last_value = values[0]
            initial_value = values[0]
            last_peak = values[0]

            for val in values[1:]:
                # If there is a significant drop (50%) then add the last peak to the total and start a new peak
                if val < last_value * 0.5:
                    total += last_peak
                    last_peak = val
                elif val > last_peak:
                    last_peak = val
                last_value = val

            total += last_peak
            return total - initial_value
        except Exception as e:
            logger.error(f"Error calculating task total: {str(e)}")
            return 0

    def _add_mean_median_traces(self, fig: go.Figure, df: pl.DataFrame):
        trace_configs = [("Mean", "grey", "dash"), ("Median", "magenta", "dashdot")]

        for name, color, dash in trace_configs:
            try:
                fig.add_trace(go.Scatter(x=df["Time Stamp"].to_list(), y=df[name].to_list(), mode="lines", name=name, line=dict(color=color, width=2, dash=dash)))
            except Exception as e:
                logger.error(f"Error adding {name} trace: {str(e)}")

    def _create_figure(self, image_path: str, metric: Metric, stats: dict) -> Figure:
        is_pod_metric = len(metric.queries) > 1 and ("ke" in metric.metric_name.lower() or "kpo" in metric.metric_name.lower())

        url_kwargs = {
            "queries": metric.queries,
            "namespace": self.namespace,
            "start_date": self.metadata.start_date if self.metadata else "",
            "end_date": self.metadata.end_date if self.metadata else "",
            "organization_name": self.organization_name,
            "release_name": self.release_name,
        }

        return Figure(
            image_path=image_path,
            metric=metric,
            statistics=stats,
            namespace=self.namespace,
            release_name=self.release_name,
            worker_queue_stats=(metric.worker_queues if "celery" in metric.metric_name.lower() else None),
            pod_stats=(metric.pod_stats if (is_pod_metric and metric.pod_stats) else None),
            url=get_prometheus_url(**url_kwargs),
        )

    def get_y_axis_label(self, metric_name: str) -> str:
        if "memory" in metric_name.lower():
            return "Value (GiB)"
        elif "cpu" in metric_name.lower():
            return "Value (vCPU)"
        else:
            return "Value"

    def get_queue_y_axis(self, metric: Metric, idx: int, y_axis: str) -> str:
        if idx >= len(metric.worker_queues):
            return y_axis
        if "memory" in metric.metric_name.lower():
            return f"{metric.worker_queues[idx].queue_name} (GiB)"
        elif "cpu" in metric.metric_name.lower():
            return f"{metric.worker_queues[idx].queue_name} (vCPU)"
        elif "pod" in metric.metric_name.lower():
            return f"{metric.worker_queues[idx].queue_name}"
        else:
            return y_axis

    def downsample_if_needed(self, df: pl.DataFrame) -> pl.DataFrame:
        rows, _ = df.shape
        if rows > 3500000:
            try:
                mean_val = df["Value"].mean()
                if mean_val is not None and isinstance(mean_val, (int, float)):
                    threshold = float(mean_val) * 1.25
                else:
                    threshold = 0.0
            except Exception:
                threshold = 0.0
            return adaptive_downsample(df=df, column="Value", window_size=100, threshold=threshold)
        return df

    def _calculate_stats(self, dataframes: list[pl.DataFrame]) -> dict:
        default_stats = {"mean_value": 0, "median_value": 0, "max_value": 0, "min_value": 0, "p90_value": 0, "last_value": 0}

        if not dataframes:
            logger.warning("No dataframes provided for statistics calculation")
            return default_stats

        try:
            combined_df = pl.concat(dataframes) if len(dataframes) > 1 else dataframes[0]
            if combined_df.is_empty():
                logger.warning("Empty dataframe after combination")
                return default_stats

            combined_df = combined_df.sort("Time Stamp")

            stats = {
                "mean_value": combined_df["Value"].mean(),
                "median_value": combined_df["Value"].median(),
                "max_value": combined_df["Value"].max(),
                "min_value": combined_df["Value"].min(),
                "p90_value": combined_df["Value"].quantile(0.9),
                "last_value": combined_df.tail(1)["Value"][0],
            }

            # Replace None/NaN with 0
            return {k: v if v is not None else 0 for k, v in stats.items()}

        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return default_stats

    def update_layout(self, fig: go.Figure, y_axis_name: str):
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title=y_axis_name,
            width=780,
            height=390,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            margin=dict(l=50, r=50, t=50, b=50),
            plot_bgcolor="black",
            xaxis=dict(
                showgrid=True,
                gridwidth=0.5,
                gridcolor="lightgrey",
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=0.5,
                gridcolor="lightgrey",
                autorange=True,
            ),
        )


def get_prometheus_url(queries: list[str], namespace: str, start_date, end_date, organization_name: str, release_name: str | None = None) -> str:
    if isinstance(start_date, str):
        parsed_start = pendulum.parse(start_date)
        if not isinstance(parsed_start, DateTime):
            raise ValueError(f"Expected DateTime, got {type(parsed_start)}")
        start_date = parsed_start

    if isinstance(end_date, str):
        parsed_end = pendulum.parse(end_date)
        if not isinstance(parsed_end, DateTime):
            raise ValueError(f"Expected DateTime, got {type(parsed_end)}")
        end_date = parsed_end

    period = (end_date - start_date).in_days()
    params = {}
    count = 0
    end_date_str = end_date.to_datetime_string()
    for query in queries:
        params.update({
            f"g{count}.expr": query.format(namespace=namespace, release_name=release_name),
            f"g{count}.tab": 0,
            f"g{count}.stacked": 0,
            f"g{count}.show_exemplars": 0,
            f"g{count}.range_input": f"{period}d",
            f"g{count}.end_input": end_date_str,
        })
        count += 1
    org_domain = organization_name.replace("_", ".")
    host = f"https://prometheus.{org_domain}/graph"
    params_str = urllib.parse.urlencode(params)
    url = f"{host}?orgId=1&{params_str}"
    return url
