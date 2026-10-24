# Relays OpenBot WebRTC signaling between the robot and the dashboard in the same room,
# like OpenBot's controller/web-server but on API Gateway WebSockets.
import hmac
import json
import os
import time

from config import API_KEY_PARAM, BROWSER_ROLE, CONNECTION_TTL_S, JOIN_KEYS, ROBOT_ROLE

_store = None


class Gone(Exception):
    pass


def lambda_handler(event, context):
    global _store
    if _store is None:
        from store import DynamoConnections
        _store = DynamoConnections(os.environ["TABLE_NAME"])
    from store import ApiGatewayNotifier
    notifier = ApiGatewayNotifier(event["requestContext"], Gone)
    return handle(event, _store, notifier, os.environ["API_KEY"], int(time.time()))


def handle(event, store, notifier, api_key, now):
    context = event["requestContext"]
    route = context["routeKey"]
    connection_id = context["connectionId"]

    if route == "$connect":
        sent = (event.get("queryStringParameters") or {}).get(API_KEY_PARAM, "")
        return _status(200 if hmac.compare_digest(sent.encode(), api_key.encode()) else 401)
    if route == "$disconnect":
        store.delete(connection_id)
        return _status(200)

    try:
        message = json.loads(event.get("body") or "")
    except json.JSONDecodeError:
        return _status(400)
    if not isinstance(message, dict):
        return _status(400)

    if message.get("roomId") and set(message) <= JOIN_KEYS:
        role = ROBOT_ROLE if message.get("clientType") == ROBOT_ROLE else BROWSER_ROLE
        store.put(connection_id, message["roomId"], role, now + CONNECTION_TTL_S)
        return _status(200)

    sender = store.get(connection_id)
    if sender:
        _relay(store, notifier, sender, event["body"])
    return _status(200)


def _relay(store, notifier, sender, data):
    for peer in store.in_room(sender["roomId"]):
        if peer["role"] == sender["role"]:
            continue
        try:
            notifier.send(peer["connectionId"], data)
        except Gone:
            store.delete(peer["connectionId"])


def _status(code):
    return {"statusCode": code}
