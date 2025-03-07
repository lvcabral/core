"""The tests for light recorder."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components import light
from homeassistant.components.light import (
    ATTR_EFFECT,
    ATTR_MAX_COLOR_TEMP_KELVIN,
    ATTR_MAX_MIREDS,
    ATTR_MIN_COLOR_TEMP_KELVIN,
    ATTR_MIN_MIREDS,
    ATTR_SUPPORTED_COLOR_MODES,
)
from homeassistant.components.recorder import Recorder
from homeassistant.components.recorder.history import get_significant_states
from homeassistant.const import ATTR_FRIENDLY_NAME
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

from tests.common import async_fire_time_changed
from tests.components.recorder.common import async_wait_recording_done


async def test_exclude_attributes(recorder_mock: Recorder, hass: HomeAssistant) -> None:
    """Test light registered attributes to be excluded."""
    now = dt_util.utcnow()
    await async_setup_component(
        hass, light.DOMAIN, {light.DOMAIN: {"platform": "demo"}}
    )
    await hass.async_block_till_done()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=5))
    await hass.async_block_till_done()
    await async_wait_recording_done(hass)

    states = await hass.async_add_executor_job(get_significant_states, hass, now)
    assert len(states) >= 1
    for entity_states in states.values():
        for state in entity_states:
            assert ATTR_MIN_MIREDS not in state.attributes
            assert ATTR_MAX_MIREDS not in state.attributes
            assert ATTR_SUPPORTED_COLOR_MODES not in state.attributes
            assert ATTR_EFFECT not in state.attributes
            assert ATTR_FRIENDLY_NAME in state.attributes
            assert ATTR_MAX_COLOR_TEMP_KELVIN not in state.attributes
            assert ATTR_MIN_COLOR_TEMP_KELVIN not in state.attributes
