import threading

import requests

from config import ENTITY_ID_PREFIX, ENTITY_TYPE, HTTP_TIMEOUT_S, SUBSCRIPTION_DESCRIPTION


class BackendError(Exception):
    """Orion, QuantumLeap or CrateDB failed; the client should retry later."""


def to_entity(reading):
    """NGSI v2 entity for one reading. Only the sensors it carries are sent, so QuantumLeap leaves the rest NULL."""
    entity = {
        "id": ENTITY_ID_PREFIX + reading["device"],
        "type": ENTITY_TYPE,
        # QuantumLeap uses TimeInstant as the row time, so buffered readings keep their capture time
        "TimeInstant": {"type": "DateTime", "value": reading["ts"]},
    }
    for sensor in ("temperature", "humidity"):
        if sensor in reading:
            entity[sensor] = {"type": "Number", "value": reading[sensor]}
    if "lat" in reading:
        entity["location"] = {"type": "geo:point", "value": f"{reading['lat']}, {reading['lon']}"}
    return entity


def subscription(notify_url):
    return {
        "description": SUBSCRIPTION_DESCRIPTION,
        "subject": {"entities": [{"idPattern": ".*", "type": ENTITY_TYPE}]},
        "notification": {
            "http": {"url": notify_url},
            # Without this every row would repeat the last temperature, humidity and location
            "onlyChangedAttrs": True,
            "metadata": ["dateCreated", "dateModified"],
        },
    }


class OrionClient:
    def __init__(self, orion_url, notify_url, session=None):
        self._url = orion_url.rstrip("/")
        self._notify_url = notify_url
        self._session = session or requests.Session()
        self._lock = threading.Lock()
        self._subscribed = False

    def publish(self, readings):
        try:
            self._ensure_subscription()
            # Oldest first, so Orion ends up holding the newest reading as the current state
            for reading in sorted(readings, key=lambda r: r["ts"]):
                # forcedUpdate notifies QuantumLeap even when a value repeats
                self._request("POST", "/v2/entities", params={"options": "upsert,forcedUpdate"}, json=to_entity(reading))
        except requests.RequestException as error:
            raise BackendError(f"Orion: {error}") from error

    def _ensure_subscription(self):
        with self._lock:
            if self._subscribed:
                return
            existing = self._request("GET", "/v2/subscriptions", params={"limit": 1000}).json()
            if not any(sub.get("description") == SUBSCRIPTION_DESCRIPTION for sub in existing):
                self._request("POST", "/v2/subscriptions", json=subscription(self._notify_url))
            self._subscribed = True

    def _request(self, method, path, **kwargs):
        response = self._session.request(method, self._url + path, timeout=HTTP_TIMEOUT_S, **kwargs)
        response.raise_for_status()
        return response
