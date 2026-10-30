import json

from signaling import Relay


class FakePeer:
    def __init__(self, gone=False):
        self.sent = []
        self.gone = gone

    def send(self, data):
        if self.gone:
            raise ConnectionError("closed")
        self.sent.append(data)


def join(relay, peer, role, room="ROOM"):
    relay.receive(peer, json.dumps({"roomId": room, "clientType": role}))


def test_join_remembers_the_role():
    relay, robot, browser = Relay(), FakePeer(), FakePeer()

    join(relay, robot, "robot")
    join(relay, browser, "browser")

    assert relay.role(robot) == "robot"
    assert relay.role(browser) == "browser"


def test_join_without_client_type_is_a_browser():
    relay, peer = Relay(), FakePeer()

    relay.receive(peer, json.dumps({"roomId": "ROOM"}))

    assert relay.role(peer) == "browser"


def test_messages_are_relayed_to_the_other_role_in_the_room():
    relay, robot, browser, elsewhere = Relay(), FakePeer(), FakePeer(), FakePeer()
    join(relay, robot, "robot")
    join(relay, browser, "browser")
    join(relay, elsewhere, "browser", room="OTHER")
    offer = json.dumps({"status": {"WEB_RTC_EVENT": "{}"}, "roomId": "ROOM"})

    relay.receive(robot, offer)

    assert browser.sent == [offer]
    assert robot.sent == elsewhere.sent == []


def test_a_message_with_room_id_and_payload_is_relayed_not_treated_as_a_join():
    relay, robot, browser = Relay(), FakePeer(), FakePeer()
    join(relay, robot, "robot")
    join(relay, browser, "browser")

    relay.receive(robot, json.dumps({"roomId": "ROOM", "status": {"VIDEO_COMMAND": "START"}}))

    assert relay.role(robot) == "robot"
    assert len(browser.sent) == 1


def test_messages_from_connections_outside_a_room_are_dropped():
    relay, robot, stranger = Relay(), FakePeer(), FakePeer()
    join(relay, robot, "robot")

    relay.receive(stranger, json.dumps({"webrtc_event": {}}))

    assert robot.sent == []


def test_gone_peers_are_forgotten():
    relay, robot, browser = Relay(), FakePeer(), FakePeer(gone=True)
    join(relay, robot, "robot")
    join(relay, browser, "browser")

    relay.receive(robot, json.dumps({"status": {}}))

    assert relay.role(browser) is None


def test_non_json_and_non_object_messages_are_ignored():
    relay, robot, browser = Relay(), FakePeer(), FakePeer()
    join(relay, robot, "robot")
    join(relay, browser, "browser")

    relay.receive(robot, "not json")
    relay.receive(robot, "[1, 2]")

    assert browser.sent == []


def test_leave_forgets_the_connection():
    relay, robot = Relay(), FakePeer()
    join(relay, robot, "robot")

    relay.leave(robot)

    assert relay.role(robot) is None
