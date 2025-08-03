"""Conftest for the tests."""

from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import patch

import pytest
from aiohttp import ClientSession
from aresponses import ResponsesMockServer

from weerlive import WeerliveApi


@pytest.fixture(name="mock_session")
def fixture_mock_session() -> Generator[ClientSession]:
    """Fixture for mock session."""
    with patch("aiohttp.client.ClientSession", autospec=True) as mock:
        yield mock.return_value


@pytest.fixture(name="weerlive_api")
async def fixture_weerlive_api() -> AsyncGenerator[WeerliveApi]:
    """Fixture for WeerliveApi."""
    async with WeerliveApi("demo") as weerlive:
        yield weerlive


def load_json(filename: str) -> str:
    """Load a fixture."""
    path = Path(__package__) / "fixtures" / filename
    return path.read_text(encoding="utf-8")


@pytest.fixture(name="json_response")
def fixture_json_response(request: pytest.FixtureRequest, aresponses: ResponsesMockServer) -> None:
    """Fixture for adding the aresponses response with a configurable JSON file."""
    fixture_filename = request.param
    aresponses.add(
        response=aresponses.Response(
            status=200,
            text=load_json(fixture_filename),
        ),
    )
