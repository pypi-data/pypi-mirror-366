# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to connect InvenioRDM to Alma."""

from .ext import InvenioAlma
from .services import AlmaRESTService, AlmaSRUService

__version__ = "0.13.4"

__all__ = (
    "AlmaRESTService",
    "AlmaSRUService",
    "InvenioAlma",
    "__version__",
)
