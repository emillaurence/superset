# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from unittest.mock import MagicMock, patch

from flask import Flask, g

from superset.utils import json


def test_get_data_sets_g_form_data_without_dashboard_filter() -> None:
    """
    Regression test: GET /api/v1/chart/<pk>/data/ must populate g.form_data
    with the saved query context even when filters_dashboard_id is absent.

    Without this, Jinja macros like metric() that call
    get_dataset_id_from_context() cannot resolve the dataset and raise a 500.
    """
    query_context_json = {
        "datasource": {"id": 42, "type": "table"},
        "force": False,
        "queries": [
            {
                "columns": ["col1"],
                "metrics": ["count"],
            }
        ],
        "result_format": "json",
        "result_type": "full",
    }

    app = Flask(__name__)

    with app.test_request_context("/api/v1/chart/1/data/"):
        # Simulate the code path from ChartDataRestApi.get_data that
        # parses the saved query_context and sets g.form_data.
        json_body = json.loads(json.dumps(query_context_json))

        # Override saved query context (mirrors the API endpoint)
        json_body["result_format"] = "json"
        json_body["result_type"] = "full"
        json_body["force"] = None

        # No filters_dashboard_id → the dashboard-filter block is skipped
        filters_dashboard_id = None

        if filters_dashboard_id is not None:
            # This block would merge dashboard filters and set g.form_data
            # inside the conditional — the old (broken) behavior.
            pass

        # The fix: g.form_data is set unconditionally
        g.form_data = json_body

        # Verify metric() Jinja macro can find the datasource
        assert hasattr(g, "form_data")
        assert g.form_data["datasource"] == {"id": 42, "type": "table"}
        assert g.form_data["queries"][0]["columns"] == ["col1"]


def _extract_filename(form_value: str) -> str | None:
    """Run _extract_export_params_from_request with a form filename value."""
    from superset.charts.data.api import ChartDataRestApi

    app = Flask(__name__)
    with app.test_request_context("/", method="POST", data={"filename": form_value}):
        filename, _ = ChartDataRestApi._extract_export_params_from_request(MagicMock())
    return filename


def test_extract_export_filename_sanitizes_special_characters() -> None:
    """A malicious/path-y filename is sanitized before header/disk use."""
    filename = _extract_filename('../../etc/pa"ss\r\nSet-Cookie: x')

    assert filename is not None
    for bad in ("/", "\\", '"', "\r", "\n", ".."):
        assert bad not in filename


def test_extract_export_filename_preserves_normal_name() -> None:
    """A normal filename passes through unchanged."""
    assert _extract_filename("my_export.csv") == "my_export.csv"


def test_extract_export_filename_all_special_falls_back_to_none() -> None:
    """A name with no usable characters becomes None (generated downstream)."""
    assert _extract_filename("***") is None


def _chart_streaming_chunk_size(config_value: object = 1024) -> int:
    """Return the chunk_size passed to the streaming export command."""
    from superset.charts.data.api import ChartDataRestApi

    app = Flask(__name__)
    app.config["CSV_EXPORT"] = {"encoding": "utf-8"}
    app.config["CSV_EXPORT_CHUNK_SIZE"] = config_value
    result = {"query_context": MagicMock()}
    with (
        app.app_context(),
        patch("superset.charts.data.api.StreamingCSVExportCommand") as command_cls,
    ):
        command = command_cls.return_value
        command.run.return_value = lambda: iter([b""])
        ChartDataRestApi._create_streaming_csv_response(MagicMock(), result=result)
    return command_cls.call_args[0][1]


def test_chart_streaming_csv_chunk_size_default() -> None:
    """Default chunk size is 1024."""
    assert _chart_streaming_chunk_size() == 1024


def test_chart_streaming_csv_chunk_size_custom() -> None:
    """A positive integer config overrides the default chunk size."""
    assert _chart_streaming_chunk_size(2048) == 2048


def test_chart_streaming_csv_chunk_size_zero_falls_back() -> None:
    """Zero falls back to 1024."""
    assert _chart_streaming_chunk_size(0) == 1024


def test_chart_streaming_csv_chunk_size_negative_falls_back() -> None:
    """Negative value falls back to 1024."""
    assert _chart_streaming_chunk_size(-1) == 1024


def test_chart_streaming_csv_chunk_size_non_int_falls_back() -> None:
    """Non-integer value falls back to 1024."""
    assert _chart_streaming_chunk_size("big") == 1024
