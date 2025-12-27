"""Support for ESPHome water heater devices."""

from __future__ import annotations

from functools import partial
from typing import Any

from aioesphomeapi import (
    EntityInfo,
    WaterHeaterInfo,
    WaterHeaterState,
)

from homeassistant.components.water_heater import (
    ATTR_OPERATION_MODE,
    ATTR_TEMPERATURE,
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_GAS,
    STATE_HEAT_PUMP,
    STATE_HIGH_DEMAND,
    STATE_OFF,
    STATE_PERFORMANCE,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import (
    PRECISION_TENTHS,
    PRECISION_WHOLE,
    UnitOfTemperature,
)
from homeassistant.core import callback

from .entity import (
    EsphomeEntity,
    convert_api_error_ha_error,
    esphome_float_state_property,
    esphome_state_property,
    platform_async_setup_entry,
)

PARALLEL_UPDATES = 0


class EsphomeWaterHeaterEntity(
    EsphomeEntity[WaterHeaterInfo, WaterHeaterState], WaterHeaterEntity
):
    """A water heater implementation for ESPHome."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    @callback
    def _on_static_info_update(self, static_info: EntityInfo) -> None:
        """Set attrs from static info."""
        super()._on_static_info_update(static_info)
        static_info = self._static_info
        self._attr_precision = self._get_precision()
        self._attr_operation_list = static_info.supported_operation_modes
        self._attr_min_temp = static_info.min_temperature
        self._attr_max_temp = static_info.max_temperature

        features = WaterHeaterEntityFeature(0)
        features |= WaterHeaterEntityFeature.TARGET_TEMPERATURE
        if static_info.supports_away:
            features |= WaterHeaterEntityFeature.AWAY_MODE
        if self.operation_list:
            features |= WaterHeaterEntityFeature.OPERATION_MODE
        features |= WaterHeaterEntityFeature.ON_OFF
        self._attr_supported_features = features

    def _get_precision(self) -> float:
        """Return the precision of the water heater."""
        static_info = self._static_info
        step = static_info.temperature_step
        if step >= PRECISION_WHOLE:
            return PRECISION_WHOLE
        return PRECISION_TENTHS

    @property
    @esphome_float_state_property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._state.current_temperature

    @property
    @esphome_float_state_property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._state.target_temperature

    @property
    @esphome_state_property
    def current_operation(self) -> str | None:
        """Return current operation ie. eco, electric, performance, etc."""
        return self._state.mode

    @property
    @esphome_state_property
    def is_away_mode_on(self) -> bool | None:
        """Return if away mode is on."""
        return self._state.away

    @convert_api_error_ha_error
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        data: dict[str, Any] = {"key": self._key}
        if ATTR_TEMPERATURE in kwargs:
            data["target_temperature"] = kwargs[ATTR_TEMPERATURE]
        if ATTR_OPERATION_MODE in kwargs:
            data["mode"] = kwargs[ATTR_OPERATION_MODE]
        self._client.water_heater_command(**data, device_id=self._static_info.device_id)

    @convert_api_error_ha_error
    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        self._client.water_heater_command(
            key=self._key,
            mode=operation_mode,
            device_id=self._static_info.device_id,
        )

    @convert_api_error_ha_error
    async def async_turn_away_mode_on(self) -> None:
        """Turn away mode on."""
        self._client.water_heater_command(
            key=self._key,
            away=True,
            device_id=self._static_info.device_id,
        )

    @convert_api_error_ha_error
    async def async_turn_away_mode_off(self) -> None:
        """Turn away mode off."""
        self._client.water_heater_command(
            key=self._key,
            away=False,
            device_id=self._static_info.device_id,
        )

    @convert_api_error_ha_error
    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        self._client.water_heater_command(
            key=self._key,
            mode=STATE_ELECTRIC,
            device_id=self._static_info.device_id,
        )

    @convert_api_error_ha_error
    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        self._client.water_heater_command(
            key=self._key,
            mode=STATE_OFF,
            device_id=self._static_info.device_id,
        )


async_setup_entry = partial(
    platform_async_setup_entry,
    info_type=WaterHeaterInfo,
    entity_type=EsphomeWaterHeaterEntity,
    state_type=WaterHeaterState,
)
