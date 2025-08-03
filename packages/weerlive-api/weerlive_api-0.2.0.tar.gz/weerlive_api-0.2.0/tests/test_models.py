"""Model tests."""

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from weerlive.const import API_TIMEZONE
from weerlive.models import ApiInfo, DailyForecast, LiveWeather, Response


@pytest.fixture(name="mock_live_weather")
def fixture_mock_live_weather() -> LiveWeather:
    """Fixture to mock the LiveWeather."""
    return LiveWeather(
        city="Test City",
        timestamp=1696156800,
        time=datetime(2023, 10, 1, 12, 0, tzinfo=ZoneInfo(API_TIMEZONE)),
        temperature=20.0,
        feels_like_temperature=18.0,
        summary="Sunny",
        humidity=50,
        wind_direction="N",
        wind_direction_degree=0.0,
        wind_speed_mps=5.0,
        wind_speed_bft=3,
        wind_speed_knots=9.0,
        wind_speed_kmh=18.0,
        air_pressure=1013.0,
        air_pressure_mm_hg=760,
        dew_point=10.0,
        visibility=10000,
        solar_irradiance=800,
        forecast="Clear",
        sunrise=datetime(2023, 10, 1, 6, 30, tzinfo=ZoneInfo(API_TIMEZONE)),
        sunset=datetime(2023, 10, 1, 18, 30, tzinfo=ZoneInfo(API_TIMEZONE)),
        image="sunny.png",
        alert=0,
        alert_title="No Alerts",
        alert_text="",
        weather_code="groen",
        next_alert_date="-",
        next_alert_timestamp=0,
        next_alert_weather_code="-",
    )


@pytest.mark.parametrize(
    ("now", "result"),
    [
        (datetime(2023, 10, 1, 12, 0, tzinfo=ZoneInfo(API_TIMEZONE)), True),
        (datetime(2023, 10, 1, 6, 30, tzinfo=ZoneInfo(API_TIMEZONE)), True),
        (datetime(2023, 10, 1, 18, 30, tzinfo=ZoneInfo(API_TIMEZONE)), True),
        (datetime(2023, 10, 1, 18, 31, tzinfo=ZoneInfo(API_TIMEZONE)), False),
        (datetime(2023, 10, 1, 20, 0, tzinfo=ZoneInfo(API_TIMEZONE)), False),
    ],
)
async def test_is_sun_up_property(mock_live_weather: LiveWeather, now: datetime, result: bool) -> None:  # noqa: FBT001
    """Test the is_sun_up property."""
    with patch("weerlive.models.datetime") as mock_datetime:
        mock_datetime.now.return_value = now

        assert mock_live_weather.is_sun_up is result


async def test_missing_sunrise_time(mock_live_weather: LiveWeather) -> None:
    """Test is_sun_up when sunrise time is missing."""
    mock_live_weather.sunrise = None  # type:ignore[assignment]
    mock_live_weather.sunset = datetime(2023, 10, 1, 18, 30, tzinfo=ZoneInfo(API_TIMEZONE))

    with patch("weerlive.models.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 1, 12, 0, tzinfo=ZoneInfo(API_TIMEZONE))

        assert not mock_live_weather.is_sun_up


async def test_response_pre_deserialize(mock_live_weather: LiveWeather) -> None:
    """Test the __pre_deserialize__ method."""
    mock_daily_forecast = DailyForecast(
        day=datetime(2023, 10, 2, tzinfo=ZoneInfo(API_TIMEZONE)),
        image="cloudy.png",
        max_temperature=22.0,
        min_temperature=15.0,
        wind_speed_bft=2,
        wind_speed_kmh=12.0,
        wind_speed_knots=6.5,
        wind_speed_mps=3.3,
        wind_direction_degree=180.0,
        wind_direction="S",
        precipitation_probability=20,
        sunshine_probability=70,
    )

    mock_api_info = ApiInfo(
        source="weerlive",
        max_requests=300,
        remaining_requests=250,
    )

    data = {"liveweer": [mock_live_weather], "wk_verw": [mock_daily_forecast], "api": [mock_api_info]}

    result = Response.__pre_deserialize__(data)

    assert result["liveweer"] == mock_live_weather
    assert result["wk_verw"] == data["wk_verw"]  # Should remain unchanged
    assert result["api"] == mock_api_info
