"""Test ESPHome water heaters."""

from unittest.mock import call

from aioesphomeapi import (
    APIClient,
    WaterHeaterInfo,
    WaterHeaterState,
)
import pytest

from homeassistant.components.water_heater import (
    ATTR_AWAY_MODE,
    ATTR_CURRENT_TEMPERATURE,
    ATTR_MAX_TEMP,
    ATTR_MIN_TEMP,
    ATTR_OPERATION_MODE,
    ATTR_TEMPERATURE,
    DOMAIN as WATER_HEATER_DOMAIN,
    SERVICE_SET_AWAY_MODE,
    SERVICE_SET_OPERATION_MODE,
    SERVICE_SET_TEMPERATURE,
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_OFF,
)
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from .conftest import MockGenericDeviceEntryType


async def test_water_heater_entity(
    hass: HomeAssistant,
    mock_client: APIClient,
    mock_generic_device_entry: MockGenericDeviceEntryType,
) -> None:
    """Test a generic water heater entity."""
    entity_info = [
        WaterHeaterInfo(
            object_id="mywaterheater",
            key=1,
            name="my water heater",
            min_temperature=30.0,
            max_temperature=80.0,
            temperature_step=1.0,
            supports_away=True,
            supported_operation_modes=[STATE_OFF, STATE_ELECTRIC, STATE_ECO],
        )
    ]
    states = [
        WaterHeaterState(
            key=1,
            mode=STATE_ELECTRIC,
            current_temperature=45.0,
            target_temperature=55.0,
            away=False,
        )
    ]
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        states=states,
    )
    state = hass.states.get("water_heater.test_my_water_heater")
    assert state is not None
    assert state.state == STATE_ELECTRIC
    assert state.attributes[ATTR_CURRENT_TEMPERATURE] == 45.0
    assert state.attributes[ATTR_TEMPERATURE] == 55.0
    assert state.attributes[ATTR_MIN_TEMP] == 30.0
    assert state.attributes[ATTR_MAX_TEMP] == 80.0
    assert state.attributes[ATTR_OPERATION_MODE] == STATE_ELECTRIC


async def test_water_heater_set_temperature(
    hass: HomeAssistant,
    mock_client: APIClient,
    mock_generic_device_entry: MockGenericDeviceEntryType,
) -> None:
    """Test setting water heater temperature."""
    entity_info = [
        WaterHeaterInfo(
            object_id="mywaterheater",
            key=1,
            name="my water heater",
            min_temperature=30.0,
            max_temperature=80.0,
            temperature_step=1.0,
            supports_away=True,
            supported_operation_modes=[STATE_OFF, STATE_ELECTRIC, STATE_ECO],
        )
    ]
    states = [
        WaterHeaterState(
            key=1,
            mode=STATE_ELECTRIC,
            current_temperature=45.0,
            target_temperature=55.0,
            away=False,
        )
    ]
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        states=states,
    )

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: "water_heater.test_my_water_heater", ATTR_TEMPERATURE: 60.0},
        blocking=True,
    )
    mock_client.water_heater_command.assert_has_calls(
        [call(key=1, target_temperature=60.0, device_id=0)]
    )
    mock_client.water_heater_command.reset_mock()


async def test_water_heater_set_operation_mode(
    hass: HomeAssistant,
    mock_client: APIClient,
    mock_generic_device_entry: MockGenericDeviceEntryType,
) -> None:
    """Test setting water heater operation mode."""
    entity_info = [
        WaterHeaterInfo(
            object_id="mywaterheater",
            key=1,
            name="my water heater",
            min_temperature=30.0,
            max_temperature=80.0,
            temperature_step=1.0,
            supports_away=True,
            supported_operation_modes=[STATE_OFF, STATE_ELECTRIC, STATE_ECO],
        )
    ]
    states = [
        WaterHeaterState(
            key=1,
            mode=STATE_ELECTRIC,
            current_temperature=45.0,
            target_temperature=55.0,
            away=False,
        )
    ]
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        states=states,
    )

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_SET_OPERATION_MODE,
        {ATTR_ENTITY_ID: "water_heater.test_my_water_heater", ATTR_OPERATION_MODE: STATE_ECO},
        blocking=True,
    )
    mock_client.water_heater_command.assert_has_calls(
        [call(key=1, mode=STATE_ECO, device_id=0)]
    )
    mock_client.water_heater_command.reset_mock()


async def test_water_heater_set_away_mode(
    hass: HomeAssistant,
    mock_client: APIClient,
    mock_generic_device_entry: MockGenericDeviceEntryType,
) -> None:
    """Test setting water heater away mode."""
    entity_info = [
        WaterHeaterInfo(
            object_id="mywaterheater",
            key=1,
            name="my water heater",
            min_temperature=30.0,
            max_temperature=80.0,
            temperature_step=1.0,
            supports_away=True,
            supported_operation_modes=[STATE_OFF, STATE_ELECTRIC, STATE_ECO],
        )
    ]
    states = [
        WaterHeaterState(
            key=1,
            mode=STATE_ELECTRIC,
            current_temperature=45.0,
            target_temperature=55.0,
            away=False,
        )
    ]
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        states=states,
    )

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_SET_AWAY_MODE,
        {ATTR_ENTITY_ID: "water_heater.test_my_water_heater", ATTR_AWAY_MODE: True},
        blocking=True,
    )
    mock_client.water_heater_command.assert_has_calls(
        [call(key=1, away=True, device_id=0)]
    )
    mock_client.water_heater_command.reset_mock()


async def test_water_heater_turn_on_off(
    hass: HomeAssistant,
    mock_client: APIClient,
    mock_generic_device_entry: MockGenericDeviceEntryType,
) -> None:
    """Test turning water heater on and off."""
    entity_info = [
        WaterHeaterInfo(
            object_id="mywaterheater",
            key=1,
            name="my water heater",
            min_temperature=30.0,
            max_temperature=80.0,
            temperature_step=1.0,
            supports_away=True,
            supported_operation_modes=[STATE_OFF, STATE_ELECTRIC, STATE_ECO],
        )
    ]
    states = [
        WaterHeaterState(
            key=1,
            mode=STATE_ELECTRIC,
            current_temperature=45.0,
            target_temperature=55.0,
            away=False,
        )
    ]
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        states=states,
    )

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "water_heater.test_my_water_heater"},
        blocking=True,
    )
    mock_client.water_heater_command.assert_has_calls(
        [call(key=1, mode=STATE_OFF, device_id=0)]
    )
    mock_client.water_heater_command.reset_mock()

    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "water_heater.test_my_water_heater"},
        blocking=True,
    )
    mock_client.water_heater_command.assert_has_calls(
        [call(key=1, mode=STATE_ELECTRIC, device_id=0)]
    )
