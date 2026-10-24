import json

from handler import Gone, handle

KEY = "secret-key"
NOW = 1_000_000


class FakeStore:
    def __init__(self):
        self.connections = {}

    def put(self, connection_id, room_id, role, expires):
        self.connections[connection_id] = {"connectionId": connection_id, "roomId": room_id, "role": role, "expires": expires}

    def get(self, connection_id):
        return self.connections.get(connection_id)

    def delete(self, connection_id):
        self.connections.pop(connection_id, None)

    def in_room(self, room_id):
        return [c for c in self.connections.values() if c["roomId"] == room_id]


class FakeNotifier:
    def __init__(self, gone=()):
        self.sent = []
        self.gone = set(gone)

    def send(self, connection_id, data):
        if connection_id in self.gone:
            raise Gone(connection_id)
        self.sent.append((connection_id, data))


def event(route, connection_id="c1", body=None, params=None):
    return {
        "requestContext": {"routeKey": route, "connectionId": connection_id},
        "queryStringParameters": params,
        "body": json.dumps(body) if isinstance(body, dict) else body,
    }


def call(evt, store=None, notifier=None):
    return handle(evt, store or FakeStore(), notifier or FakeNotifier(), KEY, NOW)["statusCode"]


def joined(*members):
    store = FakeStore()
    for connection_id, role in members:
        store.put(connection_id, "ROOM", role, NOW + 1)
    return store


def test_connect_requires_the_api_key():
    assert call(event("$connect", params={"key": KEY})) == 200
    assert call(event("$connect", params={"key": "wrong"})) == 401
    assert call(event("$connect")) == 401


def test_join_stores_the_connection_with_its_role_and_expiry():
    store = FakeStore()

    call(event("$default", "robot", {"roomId": "ROOM", "clientType": "robot"}), store)
    call(event("$default", "browser", {"roomId": "ROOM", "clientType": "browser"}), store)

    assert store.get("robot")["role"] == "robot"
    assert store.get("browser")["role"] == "browser"
    assert store.get("robot")["expires"] > NOW


def test_join_without_client_type_is_a_browser():
    store = FakeStore()

    call(event("$default", "c1", {"roomId": "ROOM"}), store)

    assert store.get("c1")["role"] == "browser"


def test_messages_are_relayed_to_the_other_role_in_the_room():
    store = joined(("robot", "robot"), ("browser", "browser"))
    store.put("elsewhere", "OTHER", "browser", NOW + 1)
    notifier = FakeNotifier()
    offer = {"status": {"WEB_RTC_EVENT": "{}"}, "roomId": "ROOM"}

    assert call(event("$default", "robot", offer), store, notifier) == 200

    assert notifier.sent == [("browser", json.dumps(offer))]


def test_a_message_with_room_id_and_payload_is_relayed_not_treated_as_a_join():
    store = joined(("robot", "robot"), ("browser", "browser"))
    notifier = FakeNotifier()

    call(event("$default", "robot", {"roomId": "ROOM", "status": {"VIDEO_COMMAND": "START"}}), store, notifier)

    assert store.get("robot")["role"] == "robot"
    assert len(notifier.sent) == 1


def test_messages_from_connections_outside_a_room_are_dropped():
    notifier = FakeNotifier()

    assert call(event("$default", "stranger", {"webrtc_event": {}}), joined(("robot", "robot")), notifier) == 200

    assert notifier.sent == []


def test_gone_peers_are_forgotten():
    store = joined(("robot", "robot"), ("browser", "browser"))

    call(event("$default", "robot", {"status": {}}), store, FakeNotifier(gone={"browser"}))

    assert store.get("browser") is None


def test_non_json_bodies_are_ignored():
    assert call(event("$default", body="not json")) == 400


def test_disconnect_forgets_the_connection():
    store = joined(("robot", "robot"))

    call(event("$disconnect", "robot"), store)

    assert store.get("robot") is None
