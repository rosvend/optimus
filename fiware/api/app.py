import hmac
import os
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_sock import Sock

from config import (API_KEY_HEADER, DEFAULT_VIDEO_ROOM_ID, SIGNALING_KEY_PARAM, SIGNALING_PATH,
                    SIGNALING_PING_INTERVAL_S)
from orion import BackendError
from readings import ValidationError, parse_batch, parse_query
from signaling import Relay

API_PATH = "/api/readings"


def create_app(orion, history, api_key, now=lambda: datetime.now(timezone.utc), static_dir=None,
               room_id=DEFAULT_VIDEO_ROOM_ID, relay=None):
    app = Flask(__name__, static_folder=static_dir, static_url_path="")
    app.config["SOCK_SERVER_OPTIONS"] = {"ping_interval": SIGNALING_PING_INTERVAL_S}
    sock = Sock(app)
    relay = relay or Relay()

    def authorized(sent):
        return hmac.compare_digest(sent.encode(), api_key.encode())

    @app.after_request
    def allow_cross_origin(response):
        # Lets a dashboard served from elsewhere (npm run dev) call the API
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = f"{API_KEY_HEADER}, content-type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST"
        return response

    @app.route(API_PATH, methods=["GET", "POST"])
    def readings():
        if not authorized(request.headers.get(API_KEY_HEADER, "")):
            return jsonify(error="unauthorized"), 401
        try:
            if request.method == "POST":
                batch = parse_batch(request.get_data(as_text=True), now())
                orion.publish(batch)
                return jsonify(stored=len(batch))
            return jsonify(items=history.query(parse_query(request.args)))
        except ValidationError as error:
            return jsonify(error=str(error)), error.status
        except BackendError as error:
            app.logger.warning("%s", error)
            return jsonify(error="FIWARE backend unavailable"), 502

    # Refuses the WebSocket handshake itself, so the phone sees a failed connection and not an open one
    @app.before_request
    def check_signaling_key():
        if request.path == SIGNALING_PATH and not authorized(request.args.get(SIGNALING_KEY_PARAM, "")):
            return jsonify(error="unauthorized"), 401

    @sock.route(SIGNALING_PATH)
    def signaling(ws):
        peer = _Peer(ws)
        try:
            while True:
                relay.receive(peer, ws.receive())
        finally:
            relay.leave(peer)

    # The dashboard reads its API and signaling URLs from here; it is served by this same app
    @app.get("/config.json")
    def dashboard_config():
        scheme = "wss" if request.scheme == "https" else "ws"
        return jsonify(apiUrl=API_PATH.lstrip("/"), signalingUrl=f"{scheme}://{request.host}{SIGNALING_PATH}",
                       roomId=room_id)

    @app.get("/")
    def dashboard():
        if static_dir is None:
            return jsonify(error="dashboard not built"), 404
        return send_from_directory(static_dir, "index.html")

    return app


def from_env():
    from history import CrateHistory
    from orion import OrionClient

    orion = OrionClient(os.environ["ORION_URL"], os.environ["NOTIFY_URL"])
    history = CrateHistory(os.environ["CRATE_URL"])
    return create_app(orion, history, os.environ["API_KEY"], static_dir=os.environ.get("STATIC_DIR"),
                      room_id=os.environ.get("VIDEO_ROOM_ID") or DEFAULT_VIDEO_ROOM_ID)


class _Peer:
    """A signaling socket that other connections' threads can send to, one message at a time."""

    def __init__(self, ws):
        self._ws = ws
        self._lock = threading.Lock()

    def send(self, data):
        with self._lock:
            self._ws.send(data)
