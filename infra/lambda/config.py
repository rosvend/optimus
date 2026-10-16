# Tunables for the telemetry API. Secrets and table name come from env vars set by Terraform.

SENSORS = ("temperature", "humidity", "gps")

# Inclusive (min, max) accepted for each reading field
RANGES = {
    "temperature": (-40.0, 125.0),
    "humidity": (0.0, 100.0),
    "lat": (-90.0, 90.0),
    "lon": (-180.0, 180.0),
}

DEFAULT_DEVICE = "optimus"
MAX_READINGS_PER_BATCH = 50

DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 500
QUERY_MIN_TS = "0000-01-01T00:00:00.000Z"
QUERY_MAX_TS = "9999-12-31T23:59:59.999Z"

API_KEY_HEADER = "x-api-key"
