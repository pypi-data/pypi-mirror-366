"""Client for the Weerlive API."""

from __future__ import annotations

import asyncio
import logging
import socket
from json import JSONDecodeError
from types import TracebackType
from typing import Self

from aiohttp.client import ClientError, ClientResponseError, ClientSession
from yarl import URL

from .const import API_ENDPOINT, API_TIMEOUT
from .exceptions import (
    WeerliveAPIConnectionError,
    WeerliveAPIKeyError,
    WeerliveAPIRateLimitError,
    WeerliveAPIRequestTimeoutError,
    WeerliveDecodeError,
)
from .models import Response

logger = logging.getLogger(__name__)


class WeerliveApi:
    """Weerlive HTTP client."""

    _session: ClientSession
    _close_session: bool
    api_key: str

    def __init__(self: Self, api_key: str, session: ClientSession | None = None) -> None:
        """Initialize the Weerlive client."""
        self.api_key = api_key
        if session is None:
            self._session = ClientSession()
            self._close_session = True
        else:
            self._session = session
            self._close_session = False

    async def latitude_longitude(self: Self, latitude: float, longitude: float) -> Response:
        """Get weather data for a specific latitude and longitude."""
        return await self._request(URL(API_ENDPOINT.format(self.api_key, f"{latitude},{longitude}")))

    async def city(self: Self, city_name: str) -> Response:
        """Get weather data for a specific city."""
        return await self._request(URL(API_ENDPOINT.format(self.api_key, city_name)))

    async def _request(self: Self, url: URL) -> Response:
        """Make a request to the Weerlive service."""
        try:
            async with asyncio.timeout(API_TIMEOUT):
                response = await self._session.request("GET", url)
                logger.info("GET request for url: %s responded with status %s", url, response.status)
                response.raise_for_status()

                response_text = await response.text()

                # The API has no proper error handling for a wrong API key or rate limit.
                # Instead a 200 with a message is returned, try to detect that here.
                if "Vraag eerst een API-key op" in response_text:
                    msg = "The given API key is invalid"
                    raise WeerliveAPIKeyError(msg)
                if "Dagelijkse limiet" in response_text:
                    msg = "API key daily limit exceeded, try again tomorrow"
                    raise WeerliveAPIRateLimitError(msg)

                return Response.from_json(response_text)
        except JSONDecodeError as exception:
            msg = "Error decoding JSON response from the API"
            raise WeerliveDecodeError(msg) from exception

        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the API"
            raise WeerliveAPIRequestTimeoutError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with the API"
            raise WeerliveAPIConnectionError(msg) from exception

    async def close(self: Self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self: Self) -> Self:
        """Async enter."""
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async exit."""
        await self.close()
