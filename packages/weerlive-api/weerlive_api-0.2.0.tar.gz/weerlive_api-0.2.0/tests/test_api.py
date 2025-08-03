"""API tests."""
# pylint: disable=protected-access

import asyncio
import datetime
import socket
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from aiohttp.client import ClientError, ClientResponseError, ClientSession

from weerlive import WeerliveApi
from weerlive.const import API_TIMEZONE
from weerlive.exceptions import (
    WeerliveAPIConnectionError,
    WeerliveAPIKeyError,
    WeerliveAPIRateLimitError,
    WeerliveAPIRequestTimeoutError,
    WeerliveDecodeError,
)


async def test_weerlive_initialization_without_session() -> None:
    """Test client initialization."""
    weerlive = WeerliveApi("demo")
    assert isinstance(weerlive._session, ClientSession)
    assert weerlive._close_session is True


async def test_weerlive_initialization_with_session(mock_session: ClientSession) -> None:
    """Test client initialization with session."""
    weerlive = WeerliveApi("demo", session=mock_session)
    assert weerlive._session is mock_session
    assert weerlive._close_session is False


@pytest.mark.usefixtures("json_response")
@pytest.mark.parametrize("json_response", ["amsterdam.json"], indirect=True)
async def test_deserialization_amsterdam(weerlive_api: WeerliveApi) -> None:
    """Test deserialization of Amsterdam weather data."""
    response = await weerlive_api.city("Test")
    assert response.live.city == "Amsterdam"
    assert response.live.temperature == 19.1
    assert response.live.summary == "Zwaar bewolkt"

    assert response.daily_forecast[0].max_temperature == 20
    assert response.daily_forecast[0].min_temperature == 15

    assert response.hourly_forecast[0].temperature == 20
    assert response.hourly_forecast[0].solar_irradiance == 704

    assert response.api.max_requests == 300
    assert response.api.remaining_requests == 0


@pytest.mark.usefixtures("json_response")
@pytest.mark.parametrize("json_response", ["groningen.json"], indirect=True)
async def test_deserialization_groningen(weerlive_api: WeerliveApi) -> None:
    """Test deserialization of Groningen weather data."""
    response = await weerlive_api.latitude_longitude(latitude=53.21917, longitude=6.56667)
    assert response.live.city == "Groningen"
    assert response.live.temperature == 18.5
    assert response.live.summary == "Zwaar bewolkt"

    assert response.daily_forecast[0].max_temperature == 18
    assert response.daily_forecast[0].min_temperature == 14

    assert response.hourly_forecast[0].temperature == 18
    assert response.hourly_forecast[0].solar_irradiance == 404

    assert response.api.max_requests == 300
    assert response.api.remaining_requests == 299


@pytest.mark.usefixtures("json_response")
@pytest.mark.parametrize("json_response", ["alarm.json"], indirect=True)
async def test_deserialization_alarm(weerlive_api: WeerliveApi) -> None:
    """Test deserialization of alarm data."""
    response = await weerlive_api.city("Test")
    assert response.live.next_alert_date == datetime.datetime(2024, 2, 22, 18, 0, tzinfo=ZoneInfo(API_TIMEZONE))
    assert response.live.next_alert_timestamp == 1708621200
    assert response.live.next_alert_weather_code == "geel"


@pytest.mark.usefixtures("json_response")
@pytest.mark.parametrize("json_response", ["invalid-api-key.txt"], indirect=True)
async def test_invalid_api_key(weerlive_api: WeerliveApi) -> None:
    """Test invalid API key."""
    with pytest.raises(WeerliveAPIKeyError):
        await weerlive_api.city("Test")


@pytest.mark.usefixtures("json_response")
@pytest.mark.parametrize("json_response", ["rate-limit.txt"], indirect=True)
async def test_rate_limit(weerlive_api: WeerliveApi) -> None:
    """Test rate limit."""
    with pytest.raises(WeerliveAPIRateLimitError):
        await weerlive_api.city("Test")


@pytest.mark.usefixtures("json_response")
@pytest.mark.parametrize("json_response", ["invalid.json"], indirect=True)
async def test_invalid_json(weerlive_api: WeerliveApi) -> None:
    """Test deserialization of invalid weather data."""
    with pytest.raises(WeerliveDecodeError):
        await weerlive_api.city("Test")


async def test_timeout_error(weerlive_api: WeerliveApi) -> None:
    """Test timeout error."""
    with (
        patch("asyncio.timeout", side_effect=asyncio.TimeoutError),
        pytest.raises(WeerliveAPIRequestTimeoutError),
    ):
        await weerlive_api.city("Test")


@pytest.mark.parametrize(
    ("side_effect"),
    [
        (ClientError("Connection error")),
        (ClientResponseError(request_info=None, history=None, status=500, message="Server error")),  # type:ignore[arg-type]
        (socket.gaierror("Name resolution error")),
    ],
)
async def test_connection_error(weerlive_api: WeerliveApi, side_effect: type[Exception]) -> None:
    """Test connection errors."""
    with (
        patch.object(
            weerlive_api._session,
            "request",
            side_effect=side_effect,
        ),
        pytest.raises(WeerliveAPIConnectionError),
    ):
        await weerlive_api.city("Test")
