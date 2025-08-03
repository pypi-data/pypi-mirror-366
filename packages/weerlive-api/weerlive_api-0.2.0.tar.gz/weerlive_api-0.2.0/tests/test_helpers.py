"""Helpers tests."""

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from weerlive.const import API_TIMEZONE
from weerlive.helpers import str_to_datetime, time_to_datetime


@pytest.mark.parametrize(
    ("date_str", "format_str", "expected_result"),
    [
        # Valid date strings
        ("2023-12-25", "%Y-%m-%d", datetime(2023, 12, 25, tzinfo=ZoneInfo(API_TIMEZONE))),
        ("25/12/2023", "%d/%m/%Y", datetime(2023, 12, 25, tzinfo=ZoneInfo(API_TIMEZONE))),
        ("2023-12-25 14:30", "%Y-%m-%d %H:%M", datetime(2023, 12, 25, 14, 30, tzinfo=ZoneInfo(API_TIMEZONE))),
        ("Dec 25, 2023", "%b %d, %Y", datetime(2023, 12, 25, tzinfo=ZoneInfo(API_TIMEZONE))),
        # Edge cases that should return None
        ("", "%Y-%m-%d", None),
        ("-", "%Y-%m-%d", None),
        (None, "%Y-%m-%d", None),
    ],
)
def test_str_to_datetime(date_str: str, format_str: str, expected_result: datetime | None) -> None:
    """Test str_to_datetime function with various inputs."""
    result = str_to_datetime(date_str, format_str)
    assert result == expected_result


def test_str_to_datetime_invalid_format() -> None:
    """Test str_to_datetime with invalid format raises ValueError."""
    with pytest.raises(ValueError):  # noqa: PT011
        str_to_datetime("2023-12-25", "%d/%m/%Y")


@pytest.mark.parametrize(
    ("time_str", "expected_hour", "expected_minute"),
    [
        ("14:30", 14, 30),
        ("09:15", 9, 15),
        ("23:59", 23, 59),
        ("00:00", 0, 0),
    ],
)
def test_time_to_datetime_valid(time_str: str, expected_hour: int, expected_minute: int) -> None:
    """Test time_to_datetime with valid time strings."""
    with patch("weerlive.helpers.datetime") as mock_datetime:
        mock_now = datetime(2023, 12, 25, 12, 0, 0, tzinfo=ZoneInfo(API_TIMEZONE))
        mock_datetime.now.return_value = mock_now

        result = time_to_datetime(time_str)

        assert result is not None
        assert result.hour == expected_hour
        assert result.minute == expected_minute
        assert result.second == 0
        assert result.microsecond == 0
        assert result.tzinfo == ZoneInfo(API_TIMEZONE)


@pytest.mark.parametrize(
    "time_str",
    [
        "",  # Empty string
        None,  # None value
        "14",  # Missing minute part
        "14:30:45",  # Too many parts
        "25:30",  # Invalid hour
        "14:60",  # Invalid minute
        "abc:30",  # Non-numeric hour
        "14:xyz",  # Non-numeric minute
        "14-30",  # Wrong separator
    ],
)
def test_time_to_datetime_invalid(time_str: str) -> None:
    """Test time_to_datetime with invalid inputs."""
    result = time_to_datetime(time_str)
    assert result is None


def test_time_to_datetime_preserves_date() -> None:
    """Test that time_to_datetime preserves the current date."""
    test_date = datetime(2023, 6, 15, 10, 20, 30, 123456, tzinfo=ZoneInfo(API_TIMEZONE))

    with patch("weerlive.helpers.datetime") as mock_datetime:
        mock_datetime.now.return_value = test_date

        result = time_to_datetime("14:30")

        assert result is not None
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 0
        assert result.microsecond == 0
