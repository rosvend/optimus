import json
from datetime import datetime, timezone

import pytest

from config import MAX_READINGS_PER_BATCH, DEFAULT_QUERY_LIMIT, MAX_QUERY_LIMIT
from readings import ValidationError, parse_batch, parse_query

NOW = datetime(2026, 10, 14, 15, 0, 0, tzinfo=timezone.utc)


def body(*readings, device="optimus"):
    return json.dumps({"device": device, "readings": list(readings)})


def test_full_reading_keeps_every_sensor():
    [reading] = parse_batch(body({"temperature": 23.4, "humidity": 55.1, "lat": 6.24, "lon": -75.58}), NOW)

    assert reading == {
        "device": "optimus",
        "ts": "2026-10-14T15:00:00.000Z",
        "temperature": 23.4,
        "humidity": 55.1,
        "lat": 6.24,
        "lon": -75.58,
    }


def test_missing_fields_are_left_out():
    [reading] = parse_batch(body({"temperature": 20}), NOW)

    assert set(reading) == {"device", "ts", "temperature"}


def test_timestamp_is_received_time_minus_age():
    [reading] = parse_batch(body({"temperature": 20, "age_ms": 1500}), NOW)

    assert reading["ts"] == "2026-10-14T14:59:58.500Z"


def test_age_defaults_to_zero():
    [reading] = parse_batch(body({"temperature": 20}), NOW)

    assert reading["ts"] == "2026-10-14T15:00:00.000Z"


@pytest.mark.parametrize("reading", [
    {"temperature": -40.1},
    {"temperature": 125.1},
    {"humidity": -0.1},
    {"humidity": 100.1},
    {"lat": 90.1, "lon": 0},
    {"lat": 0, "lon": -180.1},
    {"temperature": "hot"},
    {"temperature": True},
    {"temperature": 20, "age_ms": -1},
    {"temperature": 20, "age_ms": 1.5},
    {"lat": 6.24},
    {},
    "not an object",
])
def test_invalid_readings_are_rejected(reading):
    with pytest.raises(ValidationError) as error:
        parse_batch(body(reading), NOW)
    assert error.value.status == 400


@pytest.mark.parametrize("reading", [
    {"temperature": -40, "humidity": 0, "lat": -90, "lon": -180},
    {"temperature": 125, "humidity": 100, "lat": 90, "lon": 180},
])
def test_range_limits_are_inclusive(reading):
    assert len(parse_batch(body(reading), NOW)) == 1


@pytest.mark.parametrize("raw", [
    "not json",
    "[]",
    json.dumps({"readings": []}),
    json.dumps({"readings": "nope"}),
    json.dumps({"device": "", "readings": [{"temperature": 1}]}),
    json.dumps({"device": 7, "readings": [{"temperature": 1}]}),
    json.dumps({"device": "has space", "readings": [{"temperature": 1}]}),
    json.dumps({"device": "x" * 65, "readings": [{"temperature": 1}]}),
])
def test_invalid_batches_are_rejected(raw):
    with pytest.raises(ValidationError) as error:
        parse_batch(raw, NOW)
    assert error.value.status == 400


def test_too_many_readings_is_payload_too_large():
    raw = body(*[{"temperature": 20}] * (MAX_READINGS_PER_BATCH + 1))

    with pytest.raises(ValidationError) as error:
        parse_batch(raw, NOW)
    assert error.value.status == 413


def test_max_batch_is_accepted():
    raw = body(*[{"temperature": 20, "age_ms": i} for i in range(MAX_READINGS_PER_BATCH)])

    assert len(parse_batch(raw, NOW)) == MAX_READINGS_PER_BATCH


def test_query_defaults():
    query = parse_query({"sensor": "gps"})

    assert query.sensor == "gps"
    assert query.limit == DEFAULT_QUERY_LIMIT
    assert query.start is None and query.end is None


def test_query_normalises_time_range():
    query = parse_query({"sensor": "temperature", "from": "2026-10-14T10:00:00Z", "to": "2026-10-14T11:00:00+00:00"})

    assert query.start == "2026-10-14T10:00:00.000Z"
    assert query.end == "2026-10-14T11:00:00.000Z"


def test_query_limit_is_capped():
    assert parse_query({"sensor": "gps", "limit": "100000"}).limit == MAX_QUERY_LIMIT


@pytest.mark.parametrize("params", [
    None,
    {},
    {"sensor": "pressure"},
    {"sensor": "gps", "limit": "0"},
    {"sensor": "gps", "limit": "ten"},
    {"sensor": "gps", "from": "yesterday"},
])
def test_invalid_queries_are_rejected(params):
    with pytest.raises(ValidationError) as error:
        parse_query(params)
    assert error.value.status == 400
