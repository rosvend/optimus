# Relays OpenBot WebRTC signaling between the robot and the dashboard in the same room,
# like OpenBot's controller/web-server. The video itself flows directly between phone and browser.
import json
import threading

from config import BROWSER_ROLE, JOIN_KEYS, ROBOT_ROLE


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
            self._members.pop(connection, None)

    def role(self, connection):
        with self._lock:
            member = self._members.get(connection)
        return member and member[1]
