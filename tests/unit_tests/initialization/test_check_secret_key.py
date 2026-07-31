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
from unittest.mock import MagicMock, patch

import pytest

from superset.constants import CHANGE_ME_SECRET_KEY, TEST_NON_DEV_SECRET_KEY
from superset.initialization import SupersetAppInitializer


def _make_initializer(
    secret_key: str,
    debug: bool = False,
    testing: bool = False,
) -> SupersetAppInitializer:
    app = MagicMock()
    app.debug = debug
    app.config = {
        "SECRET_KEY": secret_key,
        "TESTING": testing,
        "DATA_DIR": "/tmp/superset_test",  # noqa: S108
    }
    initializer = SupersetAppInitializer(app)
    return initializer


@patch("superset.initialization.is_test", return_value=False)
def test_docker_default_secret_exits_in_production(mock_is_test: MagicMock) -> None:
    """Non-debug startup with TEST_NON_DEV_SECRET must refuse to start."""
    initializer = _make_initializer(TEST_NON_DEV_SECRET_KEY, debug=False)
    with pytest.raises(SystemExit):
        initializer.check_secret_key()


@patch("superset.initialization.is_test", return_value=False)
def test_original_default_secret_exits_in_production(
    mock_is_test: MagicMock,
) -> None:
    """Non-debug startup with CHANGE_ME_SECRET_KEY must refuse to start."""
    initializer = _make_initializer(CHANGE_ME_SECRET_KEY, debug=False)
    with pytest.raises(SystemExit):
        initializer.check_secret_key()


@patch("superset.initialization.is_test", return_value=False)
def test_docker_default_secret_warns_in_debug(mock_is_test: MagicMock) -> None:
    """Debug mode should warn but not exit for the Docker default secret."""
    initializer = _make_initializer(TEST_NON_DEV_SECRET_KEY, debug=True)
    # Should not raise
    initializer.check_secret_key()


@patch("superset.initialization.is_test", return_value=True)
def test_docker_default_secret_warns_in_test(mock_is_test: MagicMock) -> None:
    """Test mode should warn but not exit for the Docker default secret."""
    initializer = _make_initializer(TEST_NON_DEV_SECRET_KEY, debug=False)
    # Should not raise
    initializer.check_secret_key()


@patch("superset.initialization.is_test", return_value=False)
def test_docker_default_secret_warns_with_testing_config(
    mock_is_test: MagicMock,
) -> None:
    """TESTING=True in config should warn but not exit."""
    initializer = _make_initializer(TEST_NON_DEV_SECRET_KEY, debug=False, testing=True)
    # Should not raise
    initializer.check_secret_key()


@patch("superset.initialization.is_test", return_value=False)
def test_secure_secret_does_not_exit(mock_is_test: MagicMock) -> None:
    """A custom secret key should pass without warning or exit."""
    initializer = _make_initializer(
        "a-truly-random-production-secret-key-here", debug=False
    )
    # Should not raise
    initializer.check_secret_key()
