"""Weerlive models."""
# pylint: disable=too-many-instance-attributes

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .helpers import str_to_datetime, time_to_datetime


@dataclass
class Response(DataClassORJSONMixin):
    """Weerlive API response."""

    live: LiveWeather = field(metadata=field_options(alias="liveweer"))
    daily_forecast: list[DailyForecast] = field(metadata=field_options(alias="wk_verw"))
    hourly_forecast: list[HourlyForecast] = field(metadata=field_options(alias="uur_verw"))
    api: ApiInfo

    @classmethod
    def __pre_deserialize__(cls, d: dict[Any, Any]) -> dict[Any, Any]:
        """Extract single items from lists for live and api fields."""
        result = d.copy()

        # Extract first item from liveweer list
        if "liveweer" in result and isinstance(result["liveweer"], list) and result["liveweer"]:
            result["liveweer"] = result["liveweer"][0]

        # Extract first item from api list
        if "api" in result and isinstance(result["api"], list) and result["api"]:
            result["api"] = result["api"][0]

        return result


@dataclass
class LiveWeather(DataClassORJSONMixin):
    """Live weather data."""

    city: str = field(metadata=field_options(alias="plaats"))
    timestamp: int
    time: datetime = field(metadata=field_options(deserialize=lambda time: str_to_datetime(time, "%d-%m-%Y %H:%M:%S")))
    temperature: float = field(metadata=field_options(alias="temp"))
    feels_like_temperature: float = field(metadata=field_options(alias="gtemp"))
    summary: str = field(metadata=field_options(alias="samenv"))
    humidity: int = field(metadata=field_options(alias="lv"))
    wind_direction: str = field(metadata=field_options(alias="windr"))
    wind_direction_degree: float = field(metadata=field_options(alias="windrgr"))
    wind_speed_mps: float = field(metadata=field_options(alias="windms"))
    wind_speed_bft: int = field(metadata=field_options(alias="windbft"))
    wind_speed_knots: float = field(metadata=field_options(alias="windknp"))
    wind_speed_kmh: float = field(metadata=field_options(alias="windkmh"))
    air_pressure: float = field(metadata=field_options(alias="luchtd"))
    air_pressure_mm_hg: int = field(metadata=field_options(alias="ldmmhg"))
    dew_point: float = field(metadata=field_options(alias="dauwp"))
    visibility: int = field(metadata=field_options(alias="zicht"))
    solar_irradiance: int = field(metadata=field_options(alias="gr"))
    forecast: str = field(metadata=field_options(alias="verw"))
    sunrise: datetime = field(metadata=field_options(alias="sup", deserialize=time_to_datetime))
    sunset: datetime = field(metadata=field_options(alias="sunder", deserialize=time_to_datetime))
    image: str = field(metadata=field_options(alias="image"))
    alert: int = field(metadata=field_options(alias="alarm"))
    alert_title: str = field(metadata=field_options(alias="lkop"))
    alert_text: str = field(metadata=field_options(alias="ltekst"))
    weather_code: str = field(metadata=field_options(alias="wrschklr"))
    next_alert_date: str = field(metadata=field_options(alias="wrsch_g", deserialize=lambda date: str_to_datetime(date, "%d-%m-%Y %H:%M")))
    next_alert_timestamp: int = field(metadata=field_options(alias="wrsch_gts"))
    next_alert_weather_code: str = field(metadata=field_options(alias="wrsch_gc", deserialize=lambda code: None if code == "-" else code))

    @property
    def is_sun_up(self) -> bool:
        """Check if the sun is up based on sunrise and sunset times."""
        if not self.sunrise or not self.sunset:
            return False

        return self.sunrise <= datetime.now(tz=self.sunrise.tzinfo) <= self.sunset


@dataclass
class DailyForecast(DataClassORJSONMixin):
    """Daily weather forecast data."""

    day: datetime = field(metadata=field_options(alias="dag", deserialize=lambda day: str_to_datetime(day, "%d-%m-%Y")))
    image: str = field(metadata=field_options(alias="image"))
    max_temperature: float = field(metadata=field_options(alias="max_temp"))
    min_temperature: float = field(metadata=field_options(alias="min_temp"))
    wind_speed_bft: int = field(metadata=field_options(alias="windbft"))
    wind_speed_kmh: float = field(metadata=field_options(alias="windkmh"))
    wind_speed_knots: float = field(metadata=field_options(alias="windknp"))
    wind_speed_mps: float = field(metadata=field_options(alias="windms"))
    wind_direction_degree: float = field(metadata=field_options(alias="windrgr"))
    wind_direction: str = field(metadata=field_options(alias="windr"))
    precipitation_probability: int = field(metadata=field_options(alias="neersl_perc_dag"))
    sunshine_probability: int = field(metadata=field_options(alias="zond_perc_dag"))


@dataclass
class HourlyForecast(DataClassORJSONMixin):
    """Hourly weather forecast data."""

    time: datetime = field(metadata=field_options(alias="uur", deserialize=lambda time: str_to_datetime(time, "%d-%m-%Y %H:%M")))
    timestamp: int
    image: str = field(metadata=field_options(alias="image"))
    temperature: float = field(metadata=field_options(alias="temp"))
    wind_speed_bft: int = field(metadata=field_options(alias="windbft"))
    wind_speed_kmh: float = field(metadata=field_options(alias="windkmh"))
    wind_speed_knots: float = field(metadata=field_options(alias="windknp"))
    wind_speed_mps: float = field(metadata=field_options(alias="windms"))
    wind_direction_degree: float = field(metadata=field_options(alias="windrgr"))
    wind_direction: str = field(metadata=field_options(alias="windr"))
    precipitation: float = field(metadata=field_options(alias="neersl"))
    solar_irradiance: int = field(metadata=field_options(alias="gr"))


@dataclass
class ApiInfo(DataClassORJSONMixin):
    """API information."""

    source: str = field(metadata=field_options(alias="bron"))
    max_requests: int = field(metadata=field_options(alias="max_verz"))
    remaining_requests: int = field(metadata=field_options(alias="rest_verz"))
