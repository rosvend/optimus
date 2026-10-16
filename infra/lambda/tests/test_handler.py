import base64
import json
from datetime import datetime, timezone

from handler import handle

KEY = "secret-key"
NOW = datetime(2026, 10, 14, 15, 0, 0, tzinfo=timezone.utc)
READING = {"temperature": 22.5, "humidity": 60, "lat": 6.24, "lon": -75.58}


class FakeStore:
    def __init__(self):
        self.items = []
        self.queries = []

    def put_many(self, items):
        self.items.extend(items)

    def query(self, query):
        self.queries.append(query)
        matches = [i for i in self.items if i["sensor"] == query.sensor and query.start <= i["ts"] <= query.end]
        return sorted(matches, key=lambda i: i["ts"], reverse=True)[:query.limit]


def event(method, body=None, params=None, key=KEY, base64_body=False):
    headers = {"x-api-key": key} if key is not None else {}
    raw = json.dumps(body) if isinstance(body, dict) else body
    if base64_body and raw is not None:
        raw = base64.b64encode(raw.encode()).decode()
    return {
        "requestContext": {"http": {"method": method}},
        "headers": headers,
        "queryStringParameters": params,
        "body": raw,
        "isBase64Encoded": base64_body,
    }


def call(evt, store=None):
    response = handle(evt, store or FakeStore(), KEY, NOW)
    return response["statusCode"], json.loads(response["body"])


def test_post_stores_every_sensor_item():
    store = FakeStore()

    status, body = call(event("POST", {"readings": [READING]}), store)

    assert status == 200
    assert body == {"stored": 3}
    assert len(store.items) == 3


def test_missing_key_is_unauthorized():
    store = FakeStore()

    status, _ = call(event("POST", {"readings": [READING]}, key=None), store)

    assert status == 401
    assert store.items == []


def test_wrong_key_is_unauthorized():
    status, _ = call(event("GET", params={"sensor": "gps"}, key="nope"))

    assert status == 401


def test_header_name_is_case_insensitive():
    evt = event("GET", params={"sensor": "gps"})
    evt["headers"] = {"X-Api-Key": KEY}

    status, _ = call(evt)

    assert status == 200


def test_invalid_post_returns_validation_status():
    status, body = call(event("POST", "not json"))

    assert status == 400
    assert "error" in body


def test_base64_body_is_decoded():
    status, body = call(event("POST", {"readings": [READING]}, base64_body=True))

    assert (status, body) == (200, {"stored": 3})


def test_get_returns_stored_items_newest_first():
    store = FakeStore()
    call(event("POST", {"readings": [{"lat": 1, "lon": 2, "age_ms": 1000}, {"lat": 3, "lon": 4}]}), store)

    status, body = call(event("GET", params={"sensor": "gps"}), store)

    assert status == 200
    assert [(i["lat"], i["lon"]) for i in body["items"]] == [(3, 4), (1, 2)]
    assert body["items"][0]["ts"] == "2026-10-14T15:00:00.000Z"
    assert "sensor" not in body["items"][0]


def test_get_unknown_sensor_is_bad_request():
    status, _ = call(event("GET", params={"sensor": "pressure"}))

    assert status == 400


def test_other_methods_are_not_allowed():
    status, _ = call(event("DELETE"))

    assert status == 405
