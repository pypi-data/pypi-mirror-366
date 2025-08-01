# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2023-2025 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alma Resources configuration."""

from types import MappingProxyType

from flask_resources import ResourceConfig, ResponseHandler
from flask_resources.serializers import JSONSerializer
from marshmallow.fields import Raw, Str


class AlmaResourceConfig(ResourceConfig):
    """Marc21 Record resource configuration."""

    blueprint_name: str = "alma_records"
    url_prefix: str = "/alma"

    routes = MappingProxyType(
        {
            "item": "/<any({types}):type>/<record_id>",
        },
    )

    response_handlers = MappingProxyType(
        {
            "application/json": ResponseHandler(JSONSerializer()),
        },
    )

    record_id_search_key = MappingProxyType(
        {
            "ac_number": "local_control_field_009",
            "mmsid": "mms_id",
        },
    )

    # Request parsing
    request_read_args = MappingProxyType({})
    request_view_args = MappingProxyType(
        {
            "type": Str(),
            "record_id": Raw(),
        },
    )
