# Optimus telemetry on FIWARE

The robot's temperature, humidity and GPS readings go through a FIWARE stack that runs with Docker Compose on any machine (a laptop or a cloud VM). The phone app uploads to a small microservice, Orion keeps each robot's current state, QuantumLeap turns every change into a time series in CrateDB, and the [dashboard](../dashboard/README.md) and Grafana read that history.

```
Android app ──POST + x-api-key──▶ api (Flask) ──NGSI v2──▶ Orion ──subscription──▶ QuantumLeap ──▶ CrateDB
                                    │                       │                                       │
browser ──▶ dashboard (served by api) ──GET + x-api-key──▶ api ◀──── SQL ─────────────────────────────┤
                                                                  MongoDB                    Grafana ◀┘
```

| Service | Image | Port | Role |
|---|---|---|---|
| `api` | built from [`api/`](api/) | `80` (public) | Telemetry API, video signaling and dashboard |
| `orion` | `fiware/orion:4.1.0` | `127.0.0.1:1026` | Context broker (NGSI v2), current state |
| `mongo-db` | `mongo:6.0` | internal | Orion's database |
| `quantumleap` | `orchestracities/quantumleap:1.0.0` | `127.0.0.1:8668` | Writes Orion notifications to CrateDB |
| `crate-db` | `crate:5.10` | `127.0.0.1:4200` | Time-series database (admin UI on 4200) |
| `grafana` | `grafana/grafana:11.6.0` | `3000` (public) | Ready-made "Optimus telemetry" dashboard |

Only `api` and Grafana are reachable from outside. Orion, QuantumLeap and CrateDB listen on localhost only, because they have no authentication. Reach them from your laptop with an SSH tunnel, for example `ssh -L 1026:localhost:1026 -L 4200:localhost:4200 user@vm`.

## Running it

You need Docker with Compose. On Linux hosts CrateDB also needs `sudo sysctl -w vm.max_map_count=262144`.

```bash
cd fiware
cp .env.example .env          # set API_KEY to a long random string
docker compose up -d --build
```

- **Dashboard:** `http://<host>/`. It asks for the API key once.
- **Grafana:** `http://<host>:3000` (user `admin`, password `GRAFANA_PASSWORD` or `admin`).
- **Android app:** set the "Cloud Telemetry" URL to `http://<host>/api/readings` and the key from `.env`. For the camera, see [Video streaming](#video-streaming).

After changing the dashboard or the API code, rebuild with `docker compose up -d --build api`. `docker compose down` stops everything and keeps the data; `docker compose down -v` deletes it too.

## Data model

Each device is one NGSI v2 entity, `urn:ngsi-ld:Robot:<device>` of type `Robot`:

| Attribute | Type | |
|---|---|---|
| `temperature` | `Number` | °C |
| `humidity` | `Number` | % |
| `location` | `geo:point` | `"lat, lon"` |
| `TimeInstant` | `DateTime` | Capture time; QuantumLeap uses it as the row time |

The api sends one update per reading, oldest first, with only the sensors that reading has. It creates the Orion → QuantumLeap subscription itself on the first upload, with `onlyChangedAttrs` so sensors a reading didn't carry are stored as `NULL` and don't repeat old values. QuantumLeap writes to the CrateDB table `doc.etrobot`.

Orion sends notifications one at a time (`-notificationMode threadpool:1000:1`). When they arrive in parallel, QuantumLeap races to create the table's columns and readings are lost.

Look at the raw data:

```bash
curl localhost:1026/v2/entities?options=keyValues                         # current state in Orion
curl localhost:1026/v2/subscriptions                                      # timesSent, lastSuccess
curl -X POST localhost:4200/_sql -d '{"stmt":"SELECT * FROM doc.etrobot ORDER BY time_index DESC LIMIT 10"}'
```

## API

Send the key in the `x-api-key` header on every request. Requests without it get `401`. If Orion or CrateDB are down the API answers `502`, and the app keeps the readings and retries.

### Upload readings: `POST /api/readings`

```json
{
  "device": "optimus",
  "readings": [
    {"age_ms": 1200, "temperature": 23.4, "humidity": 55.1, "lat": 6.2442, "lon": -75.5812}
  ]
}
```

| Field | Rule |
|---|---|
| `device` | Optional, defaults to `optimus`. 1-64 letters, digits, `_` or `-`. |
| `readings` | 1 to 50 per request |
| `age_ms` | How many ms ago the reading was taken (default `0`). The server timestamps it as `now - age_ms`, so readings buffered while offline keep their real time without a clock on the board. |
| `temperature` | °C, -40 to 125. Optional. |
| `humidity` | %, 0 to 100. Optional. |
| `lat`, `lon` | Degrees. Send both or neither, for example leave them out while the GPS has no fix. |

Each reading needs at least one sensor value. Responses are `200 {"stored": n}` (one per reading), `400` for invalid data, `401` for a bad key, and `413` for more than 50 readings.

```bash
curl -X POST "http://<host>/api/readings" -H "x-api-key: $KEY" -H "content-type: application/json" \
  -d '{"readings":[{"temperature":22.5,"humidity":60,"lat":6.24,"lon":-75.58}]}'
```

### Read readings: `GET /api/readings?sensor=...`

| Param | Rule |
|---|---|
| `sensor` | `temperature`, `humidity` or `gps` (required) |
| `from`, `to` | ISO-8601 times, for example `2026-10-14T10:00:00Z` (optional) |
| `limit` | Default 100, max 500 |

Results are newest first:

```bash
curl "http://<host>/api/readings?sensor=gps&from=2026-10-14T00:00:00Z&limit=20" -H "x-api-key: $KEY"
# {"items": [{"ts": "2026-10-14T14:48:25.053Z", "lat": 6.24, "lon": -75.58, "device": "optimus"}]}
```

## Video streaming

The OpenBot app already streams its camera over WebRTC; it just needs a signaling server to meet the browser. The api is that server: a WebSocket at `/signaling` that relays messages between the robot and the dashboard when both join the same room. The video itself flows directly between the phone and the browser.

On the phone, open **Settings > Web Controller** and set:

- **Room ID:** `VIDEO_ROOM_ID` from `.env` (default `OPTIMUS`).
- **Signaling server:** `ws://<host>/signaling?key=<API_KEY>`.

Then pick **Web** as the controller in the General panel. The dashboard's camera panel connects on its own and asks the robot to restart its stream, so the page can be opened before or after the robot.

A handshake without the right `key` gets `401`. Rooms live in the api's memory, so restarting it makes both sides reconnect (they retry on their own). The phone only uses a public STUN server: if the campus Wi-Fi or the mobile carrier blocks direct connections between the phone and the browser, the video won't connect and a TURN relay would be needed.

## Layout

```
fiware/
├── docker-compose.yml        # the whole stack
├── .env.example              # API key and ports (copy to .env, gitignored)
├── grafana/provisioning/     # CrateDB datasource and the Optimus dashboard
└── api/                      # microservice (Flask)
    ├── Dockerfile            # builds the dashboard, then the API image
    ├── app.py                # routes: /api/readings, /signaling, /config.json, the dashboard
    ├── readings.py           # validation of uploads and queries
    ├── orion.py              # NGSI v2 entity updates and the QuantumLeap subscription
    ├── history.py            # CrateDB queries
    ├── signaling.py          # WebRTC signaling relay between the robot and the dashboard
    ├── config.py             # tunables
    └── tests/
```

## Tests

```bash
pip install -r fiware/api/requirements-dev.txt
python -m pytest fiware/api
```
