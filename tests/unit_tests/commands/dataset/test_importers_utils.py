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
import pytest

from superset.commands.dataset.importers.v1.utils import redact_url_query


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "https://example.com/data.csv?token=abc123&expires=123",
            "https://example.com/data.csv?[redacted]",
        ),
        (
            "https://example.com/data.csv",
            "https://example.com/data.csv",
        ),
        (
            "https://example.com/data.csv?",
            "https://example.com/data.csv?",
        ),
        (
            "https://example.com/data.csv#frag",
            "https://example.com/data.csv?[redacted]",
        ),
        (
            "https://example.com/data.csv?token=abc#frag",
            "https://example.com/data.csv?[redacted]",
        ),
        (
            "https://example.com/path/to/file.csv.gz?sig=xyz",
            "https://example.com/path/to/file.csv.gz?[redacted]",
        ),
        (
            "/local/path/data.csv",
            "/local/path/data.csv",
        ),
    ],
)
def test_redact_url_query(url: str, expected: str) -> None:
    assert redact_url_query(url) == expected
