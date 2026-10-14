import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from config import (
    DEFAULT_DEVICE,
    DEFAULT_QUERY_LIMIT,
    MAX_QUERY_LIMIT,
    MAX_READINGS_PER_BATCH,
    QUERY_MAX_TS,
    QUERY_MIN_TS,
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
    start: str
    end: str
    limit: int


def format_ts(moment):
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def parse_batch(body, received_at):
    """Validates a POST body and fans each reading out into one item per sensor."""
    try:
        batch = json.loads(body or "")
    except json.JSONDecodeError:
        raise ValidationError("body must be JSON")
    if not isinstance(batch, dict):
        raise ValidationError("body must be a JSON object")

    device = batch.get("device", DEFAULT_DEVICE)
    if not isinstance(device, str) or not device:
        raise ValidationError("device must be a non-empty string")

    readings = batch.get("readings")
    if not isinstance(readings, list) or not readings:
        raise ValidationError("readings must be a non-empty list")
    if len(readings) > MAX_READINGS_PER_BATCH:
        raise ValidationError(f"at most {MAX_READINGS_PER_BATCH} readings per request", status=413)

    items = []
    for index, reading in enumerate(readings):
        items.extend(_reading_items(reading, index, device, received_at))
    return items


def _reading_items(reading, index, device, received_at):
    if not isinstance(reading, dict):
        raise ValidationError(f"reading {index} must be an object")

    age_ms = reading.get("age_ms", 0)
    if not _is_int(age_ms) or age_ms < 0:
        raise ValidationError(f"reading {index}: age_ms must be a non-negative integer")
    base = {"device": device, "ts": format_ts(received_at - timedelta(milliseconds=age_ms))}

    items = []
    for sensor in ("temperature", "humidity"):
        if sensor in reading:
            items.append({**base, "sensor": sensor, "value": _in_range(reading, sensor, index)})

    if ("lat" in reading) != ("lon" in reading):
        raise ValidationError(f"reading {index}: lat and lon must be sent together")
    if "lat" in reading:
        items.append({**base, "sensor": "gps", "lat": _in_range(reading, "lat", index), "lon": _in_range(reading, "lon", index)})

    if not items:
        raise ValidationError(f"reading {index} has no sensor values")
    return items


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
        start=_parse_time(params.get("from"), QUERY_MIN_TS),
        end=_parse_time(params.get("to"), QUERY_MAX_TS),
        limit=min(limit, MAX_QUERY_LIMIT),
    )


def _parse_time(value, default):
    if value is None:
        return default
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        raise ValidationError(f"invalid ISO-8601 time: {value}")
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return format_ts(moment)
