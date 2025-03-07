"""Queries for logbook."""
from __future__ import annotations

from collections.abc import Collection
from datetime import datetime as dt

from sqlalchemy.sql.lambdas import StatementLambdaElement

from homeassistant.components.recorder.filters import Filters
from homeassistant.components.recorder.models import ulid_to_bytes_or_none
from homeassistant.helpers.json import json_dumps
from homeassistant.util import dt as dt_util

from .all import all_stmt
from .devices import devices_stmt
from .entities import entities_stmt
from .entities_and_devices import entities_devices_stmt


def statement_for_request(
    start_day_dt: dt,
    end_day_dt: dt,
    event_types: tuple[str, ...],
    entity_ids: list[str] | None = None,
    states_metadata_ids: Collection[int] | None = None,
    device_ids: list[str] | None = None,
    filters: Filters | None = None,
    context_id: str | None = None,
) -> StatementLambdaElement:
    """Generate the logbook statement for a logbook request."""
    start_day = dt_util.utc_to_timestamp(start_day_dt)
    end_day = dt_util.utc_to_timestamp(end_day_dt)
    # No entities: logbook sends everything for the timeframe
    # limited by the context_id and the yaml configured filter
    if not entity_ids and not device_ids:
        context_id_bin = ulid_to_bytes_or_none(context_id)
        states_entity_filter = (
            filters.states_metadata_entity_filter() if filters else None
        )
        events_entity_filter = filters.events_entity_filter() if filters else None
        return all_stmt(
            start_day,
            end_day,
            event_types,
            states_entity_filter,
            events_entity_filter,
            context_id_bin,
        )

    # sqlalchemy caches object quoting, the
    # json quotable ones must be a different
    # object from the non-json ones to prevent
    # sqlalchemy from quoting them incorrectly

    # entities and devices: logbook sends everything for the timeframe for the entities and devices
    if entity_ids and device_ids:
        return entities_devices_stmt(
            start_day,
            end_day,
            event_types,
            states_metadata_ids or [],
            [json_dumps(entity_id) for entity_id in entity_ids],
            [json_dumps(device_id) for device_id in device_ids],
        )

    # entities: logbook sends everything for the timeframe for the entities
    if entity_ids:
        return entities_stmt(
            start_day,
            end_day,
            event_types,
            states_metadata_ids or [],
            [json_dumps(entity_id) for entity_id in entity_ids],
        )

    # devices: logbook sends everything for the timeframe for the devices
    assert device_ids is not None
    return devices_stmt(
        start_day,
        end_day,
        event_types,
        [json_dumps(device_id) for device_id in device_ids],
    )
