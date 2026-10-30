# Relays OpenBot WebRTC signaling between the robot and the dashboard in the same room,
# like OpenBot's controller/web-server. The video itself flows directly between phone and browser.
import json
import logging
import threading

from config import BROWSER_ROLE, JOIN_KEYS, ROBOT_ROLE

log = logging.getLogger(__name__)


class Relay:
    """Who is in which room. Connections are kept in memory: the api runs as a single process."""

    def __init__(self):
        self._lock = threading.Lock()
        self._members = {}  # connection -> (room id, role)

    def receive(self, connection, text):
        try:
            message = json.loads(text)
        except json.JSONDecodeError:
            return
        if not isinstance(message, dict):
            return

        if message.get("roomId") and set(message) <= JOIN_KEYS:
            role = ROBOT_ROLE if message.get("clientType") == ROBOT_ROLE else BROWSER_ROLE
            with self._lock:
                self._members[connection] = (message["roomId"], role)
                count = sum(1 for member in self._members.values() if member[0] == message["roomId"])
            log.info("%s joined room %r (%d in the room)", role, message["roomId"], count)
            return

        with self._lock:
            sender = self._members.get(connection)
            peers = [c for c, member in self._members.items() if sender and member[0] == sender[0] and member[1] != sender[1]]
        for peer in peers:
            try:
                peer.send(text)
            except Exception:  # The peer's socket is gone; its own thread will also call leave()
                self.leave(peer)

    def leave(self, connection):
        with self._lock:
            member = self._members.pop(connection, None)
        if member:
            log.info("%s left room %r", member[1], member[0])

    def role(self, connection):
        with self._lock:
            member = self._members.get(connection)
        return member and member[1]
