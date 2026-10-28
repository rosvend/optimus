import hmac
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory

from config import API_KEY_HEADER
from orion import BackendError
from readings import ValidationError, parse_batch, parse_query

API_PATH = "/api/readings"


def create_app(orion, history, api_key, now=lambda: datetime.now(timezone.utc), static_dir=None):
    app = Flask(__name__, static_folder=static_dir, static_url_path="")

    @app.after_request
    def allow_cross_origin(response):
        # Lets a dashboard served from elsewhere (npm run dev) call the API
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = f"{API_KEY_HEADER}, content-type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST"
        return response

    @app.route(API_PATH, methods=["GET", "POST"])
    def readings():
        sent = request.headers.get(API_KEY_HEADER, "")
        if not hmac.compare_digest(sent.encode(), api_key.encode()):
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

    # The dashboard reads its API URL from here; it is served by this same app
    @app.get("/config.json")
    def dashboard_config():
        return jsonify(apiUrl=API_PATH.lstrip("/"))

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
    return create_app(orion, history, os.environ["API_KEY"], static_dir=os.environ.get("STATIC_DIR"))
