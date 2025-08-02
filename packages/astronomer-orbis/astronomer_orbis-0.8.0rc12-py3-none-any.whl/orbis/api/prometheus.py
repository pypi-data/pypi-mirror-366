import asyncio
import logging
import sys
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any

import polars as pl
import requests

logger = logging.getLogger("root")


class PrometheusData:
    """Prometheus Data class to query data from Prometheus."""

    def __init__(self, organization_name: str, namespace: str, start_date: datetime, end_date: datetime, token: str, verify_ssl: bool = True) -> None:
        self.organization_name = organization_name
        self.namespace = namespace
        self.start_date = start_date
        self.end_date = end_date
        self.token = token
        self.verify_ssl = verify_ssl

    async def get_request(
        self,
        api_endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Make an asynchronous GET request to Prometheus API."""
        url = f"http://prometheus.{self.organization_name.replace('_', '.')}/{api_endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await asyncio.to_thread(requests.get, url, headers=headers, params=params, verify=self.verify_ssl)
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise requests.HTTPError("API token is missing, expired, or invalid. Exiting!")
        if not response.ok:
            raise ValueError(f"Prometheus API request failed: {response.text}")

        return response.json()

    async def query_over_range(self, query: str, step: int, period_hours: int = 6) -> pl.DataFrame:
        """Query Prometheus over the given date range.(Default period_hour is set to 6 which means 4 queries per day)"""
        api_endpoint = "api/v1/query_range"
        queries_to_execute = []
        total_duration = self.end_date - self.start_date
        total_periods = int(total_duration.total_seconds() / (period_hours * 3600)) + 1

        for period in range(total_periods):
            start_date = self.start_date + timedelta(hours=period * period_hours)
            end_date = min(start_date + timedelta(hours=period_hours), self.end_date)
            params = {
                "query": query,
                "start": datetime.timestamp(start_date),
                "end": datetime.timestamp(end_date),
                "step": step,
            }
            queries_to_execute.append(self.get_request(api_endpoint=api_endpoint, params=params))

        try:
            data = await asyncio.gather(*queries_to_execute)
        except requests.HTTPError as e:
            logger.error("Error querying Prometheus: %s", str(e))
            sys.exit(1)
        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error querying Prometheus: %s", str(e))
            sys.exit(1)
        except Exception as e:
            logger.error("Error querying Prometheus: %s", str(e))
            return pl.DataFrame({"Time Stamp": [], "Value": []})
        result = []
        for temp_data in data:
            results = temp_data.get("data", {}).get("result", [])
            for i in results:
                values = i.get("values", [])
                if values:
                    df = pl.DataFrame({"Time Stamp": [v[0] for v in values], "Value": [v[1] for v in values]})
                    result.append(df)

        if result:
            df = pl.concat(result)
            sorted_df = df.sort("Time Stamp").unique(subset=["Time Stamp"], keep="last")
            sorted_df = sorted_df.with_columns(pl.col("Value").cast(pl.Float64))
            return sorted_df
        else:
            logger.warning("No data returned from Prometheus query")
            return pl.DataFrame({"Time Stamp": [], "Value": []}, schema={"Time Stamp": pl.Datetime("us", "UTC"), "Value": pl.Float64})
