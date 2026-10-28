import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from config import (
    DEFAULT_DEVICE,
    DEFAULT_QUERY_LIMIT,
    DEVICE_PATTERN,
    MAX_QUERY_LIMIT,
    MAX_READINGS_PER_BATCH,
    RANGES,
    SENSORS,
)


class ValidationError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class Query:
    sensor: str
    start: Optional[str]
    end: Optional[str]
    limit: int


def format_ts(moment):
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def parse_batch(body, received_at):
    """Validates a POST body into readings like {"device", "ts", "temperature"?, "humidity"?, "lat"?, "lon"?}."""
    try:
        batch = json.loads(body or "")
    except json.JSONDecodeError:
        raise ValidationError("body must be JSON")
    if not isinstance(batch, dict):
        raise ValidationError("body must be a JSON object")

    device = batch.get("device", DEFAULT_DEVICE)
    if not isinstance(device, str) or not re.fullmatch(DEVICE_PATTERN, device):
        raise ValidationError("device must be 1-64 letters, digits, _ or -")

    readings = batch.get("readings")
    if not isinstance(readings, list) or not readings:
        raise ValidationError("readings must be a non-empty list")
    if len(readings) > MAX_READINGS_PER_BATCH:
        raise ValidationError(f"at most {MAX_READINGS_PER_BATCH} readings per request", status=413)

    return [_parse_reading(reading, index, device, received_at) for index, reading in enumerate(readings)]


def _parse_reading(reading, index, device, received_at):
    if not isinstance(reading, dict):
        raise ValidationError(f"reading {index} must be an object")

    age_ms = reading.get("age_ms", 0)
    if not _is_int(age_ms) or age_ms < 0:
        raise ValidationError(f"reading {index}: age_ms must be a non-negative integer")

    values = {}
    for sensor in ("temperature", "humidity"):
        if sensor in reading:
            values[sensor] = _in_range(reading, sensor, index)

    if ("lat" in reading) != ("lon" in reading):
        raise ValidationError(f"reading {index}: lat and lon must be sent together")
    if "lat" in reading:
        values["lat"] = _in_range(reading, "lat", index)
        values["lon"] = _in_range(reading, "lon", index)

    if not values:
        raise ValidationError(f"reading {index} has no sensor values")
    return {"device": device, "ts": format_ts(received_at - timedelta(milliseconds=age_ms)), **values}


def _in_range(reading, field, index):
    value = reading[field]
    low, high = RANGES[field]
    if not _is_number(value) or not low <= value <= high:
        raise ValidationError(f"reading {index}: {field} must be a number between {low} and {high}")
    return value


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def parse_query(params):
    params = params or {}

    sensor = params.get("sensor")
    if sensor not in SENSORS:
        raise ValidationError(f"sensor must be one of {', '.join(SENSORS)}")

    try:
        limit = int(params.get("limit", DEFAULT_QUERY_LIMIT))
    except ValueError:
        raise ValidationError("limit must be an integer")
    if limit < 1:
        raise ValidationError("limit must be at least 1")

    return Query(
        sensor=sensor,
        start=_parse_time(params.get("from")),
        end=_parse_time(params.get("to")),
        limit=min(limit, MAX_QUERY_LIMIT),
    )


def _parse_time(value):
    if value is None:
        return None
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        raise ValidationError(f"invalid ISO-8601 time: {value}")
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return format_ts(moment)
