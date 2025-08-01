# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from collections.abc import Callable

import pytest
from _pytest.fixtures import FixtureFunctionMarker
from invenio_app.factory import create_api as _create_api


@pytest.fixture(scope="module")
def app_config(app_config: FixtureFunctionMarker) -> FixtureFunctionMarker:
    """Application config."""
    app_config["ALMA_API_KEY"] = "test-token"
    app_config["ALMA_API_HOST"] = "test-host"
    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path: FixtureFunctionMarker) -> Callable:
    """Application factory fixture."""
    return _create_api
