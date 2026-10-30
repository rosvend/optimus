# Tunables for the telemetry API. Secrets and service URLs come from env vars set by docker-compose.

SENSORS = ("temperature", "humidity", "gps")

# Inclusive (min, max) accepted for each reading field
RANGES = {
    "temperature": (-40.0, 125.0),
    "humidity": (0.0, 100.0),
    "lat": (-90.0, 90.0),
    "lon": (-180.0, 180.0),
}

DEFAULT_DEVICE = "optimus"
# Orion entity ids can't contain spaces, quotes, <, >, =, ; or parentheses
DEVICE_PATTERN = r"[A-Za-z0-9_-]{1,64}"
MAX_READINGS_PER_BATCH = 50

DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 500

API_KEY_HEADER = "x-api-key"

# NGSI v2 model: one Robot entity per device; QuantumLeap stores it in CrateDB as doc.et<type>
ENTITY_TYPE = "Robot"
ENTITY_ID_PREFIX = "urn:ngsi-ld:Robot:"
HISTORY_TABLE = '"doc"."etrobot"'
# CrateDB column holding each sensor (QuantumLeap lowercases attribute names)
SENSOR_COLUMNS = {"temperature": "temperature", "humidity": "humidity", "gps": "location"}
# QuantumLeap stores Number attributes as 32-bit REAL; rounding hides the float noise
VALUE_DECIMALS = 2

SUBSCRIPTION_DESCRIPTION = "Optimus: Robot history to QuantumLeap"
HTTP_TIMEOUT_S = 5

# Video signaling: a WebSocket that pairs the robot's OpenBot app with the dashboard (see signaling.py)
SIGNALING_PATH = "/signaling"
# WebSockets can't send custom headers from the browser, so the key goes in the query string
SIGNALING_KEY_PARAM = "key"
DEFAULT_VIDEO_ROOM_ID = "OPTIMUS"
# Pings keep the socket open through NAT and drop phones that vanished without closing
SIGNALING_PING_INTERVAL_S = 25
ROBOT_ROLE = "robot"
BROWSER_ROLE = "browser"
# OpenBot's join message carries only these keys
JOIN_KEYS = {"roomId", "clientType"}
