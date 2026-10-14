import base64
import hmac
import json
import os
from datetime import datetime, timezone

from config import API_KEY_HEADER
from readings import ValidationError, parse_batch, parse_query

_store = None


def lambda_handler(event, context):
    global _store
    if _store is None:
        from store import DynamoStore
        _store = DynamoStore(os.environ["TABLE_NAME"])
    return handle(event, _store, os.environ["API_KEY"], datetime.now(timezone.utc))


def handle(event, store, api_key, now):
    if not _authorized(event, api_key):
        return _response(401, {"error": "unauthorized"})

    method = event.get("requestContext", {}).get("http", {}).get("method")
    try:
        if method == "POST":
            items = parse_batch(_body(event), now)
            store.put_many(items)
            return _response(200, {"stored": len(items)})
        if method == "GET":
            items = store.query(parse_query(event.get("queryStringParameters")))
            return _response(200, {"items": [_public(item) for item in items]})
    except ValidationError as error:
        return _response(error.status, {"error": str(error)})
    return _response(405, {"error": "method not allowed"})


def _authorized(event, api_key):
    headers = {name.lower(): value for name, value in (event.get("headers") or {}).items()}
    sent = headers.get(API_KEY_HEADER, "")
    return hmac.compare_digest(sent.encode(), api_key.encode())


def _body(event):
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()
    return body


def _public(item):
    return {key: value for key, value in item.items() if key != "sensor"}


def _response(status, payload):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload, default=float),
    }
