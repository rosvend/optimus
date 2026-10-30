import pytest
import requests

from config import SUBSCRIPTION_DESCRIPTION
from orion import BackendError, OrionClient, to_entity

NOTIFY = "http://quantumleap:8668/v2/notify"


class FakeResponse:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = body

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, subscriptions=(), fail=False):
        self.calls = []
        self.subscriptions = list(subscriptions)
        self.fail = fail

    def request(self, method, url, **kwargs):
        if self.fail:
            raise requests.ConnectionError("refused")
        self.calls.append((method, url, kwargs))
        if method == "GET":
            return FakeResponse(body=self.subscriptions)
        return FakeResponse(201)

    def posts(self, path):
        return [kwargs["json"] for method, url, kwargs in self.calls if method == "POST" and url.endswith(path)]


def reading(ts, **values):
    return {"device": "optimus", "ts": ts, **values}


def test_entity_carries_only_the_sent_sensors():
    entity = to_entity(reading("2026-10-14T15:00:00.000Z", temperature=22.5))

    assert entity == {
        "id": "urn:ngsi-ld:Robot:optimus",
        "type": "Robot",
        "TimeInstant": {"type": "DateTime", "value": "2026-10-14T15:00:00.000Z"},
        "temperature": {"type": "Number", "value": 22.5},
    }


def test_position_is_a_geo_point_lat_first():
    entity = to_entity(reading("2026-10-14T15:00:00.000Z", lat=6.24, lon=-75.58))

    assert entity["location"] == {"type": "geo:point", "value": "6.24, -75.58"}


def test_publish_sends_oldest_first_with_upsert():
    session = FakeSession()

    OrionClient("http://orion:1026/", NOTIFY, session).publish([
        reading("2026-10-14T15:00:02.000Z", humidity=60),
        reading("2026-10-14T15:00:01.000Z", humidity=59),
    ])

    updates = [kwargs for method, url, kwargs in session.calls if url == "http://orion:1026/v2/entities"]
    assert [u["json"]["humidity"]["value"] for u in updates] == [59, 60]
    assert updates[0]["params"] == {"options": "upsert,forcedUpdate"}


def test_subscription_is_created_once():
    session = FakeSession()
    orion = OrionClient("http://orion:1026", NOTIFY, session)

    orion.publish([reading("2026-10-14T15:00:00.000Z", temperature=20)])
    orion.publish([reading("2026-10-14T15:00:01.000Z", temperature=21)])

    [created] = session.posts("/v2/subscriptions")
    assert created["description"] == SUBSCRIPTION_DESCRIPTION
    assert created["notification"]["http"]["url"] == NOTIFY
    assert created["notification"]["onlyChangedAttrs"] is True


def test_existing_subscription_is_reused():
    session = FakeSession(subscriptions=[{"description": SUBSCRIPTION_DESCRIPTION}])

    OrionClient("http://orion:1026", NOTIFY, session).publish([reading("2026-10-14T15:00:00.000Z", temperature=20)])

    assert session.posts("/v2/subscriptions") == []


def test_unreachable_orion_is_a_backend_error():
    with pytest.raises(BackendError):
        OrionClient("http://orion:1026", NOTIFY, FakeSession(fail=True)).publish([reading("2026-10-14T15:00:00.000Z", temperature=20)])
