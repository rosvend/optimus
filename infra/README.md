# Optimus telemetry infra

A public HTTPS endpoint where the car uploads temperature, humidity and GPS readings, and where anyone with the API key can read them back.

```
car / script ──HTTPS + x-api-key──▶ Lambda Function URL ──▶ Lambda (Python) ──▶ DynamoDB (optimus-telemetry)
```

Everything is serverless, so there is nothing to start each AWS Academy session. The URL keeps answering between sessions.

## Using the API

Ask Roy for the **URL** and **API key**. Send the key in the `x-api-key` header on every request. Requests without it get `401`.

### Upload readings: `POST /`

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
| `device` | Optional, defaults to `optimus` |
| `readings` | 1 to 50 per request |
| `age_ms` | How many ms ago the reading was taken (default `0`). The server timestamps it as `now - age_ms`, so readings buffered while offline keep their real time without a clock on the board. |
| `temperature` | °C, -40 to 125. Optional. |
| `humidity` | %, 0 to 100. Optional. |
| `lat`, `lon` | Degrees. Send both or neither, for example leave them out while the GPS has no fix. |

Each reading needs at least one sensor value. Responses are `200 {"stored": n}` (one item per sensor value), `400` for invalid data, `401` for a bad key, and `413` for more than 50 readings.

```bash
curl -X POST "$URL" -H "x-api-key: $KEY" -H "content-type: application/json" \
  -d '{"readings":[{"temperature":22.5,"humidity":60,"lat":6.24,"lon":-75.58}]}'
```

From an ESP32 (Arduino):

```cpp
WiFiClientSecure client;
client.setInsecure();               // skips certificate validation; fine for a class project
HTTPClient http;
http.begin(client, INGEST_URL);
http.addHeader("content-type", "application/json");
http.addHeader("x-api-key", INGEST_API_KEY);
int status = http.POST("{\"readings\":[{\"age_ms\":0,\"temperature\":22.5,\"humidity\":60}]}");
http.end();                          // keep buffered readings until status == 200
```

Keep the URL and key in a gitignored config header, not in the code.

### Read readings: `GET /?sensor=...`

| Param | Rule |
|---|---|
| `sensor` | `temperature`, `humidity` or `gps` (required) |
| `from`, `to` | ISO-8601 times, for example `2026-10-14T10:00:00Z` (optional) |
| `limit` | Default 100, max 500 |

Results are newest first:

```bash
curl "$URL?sensor=gps&from=2026-10-14T00:00:00Z&limit=20" -H "x-api-key: $KEY"
# {"items": [{"ts": "2026-10-14T14:48:25.053Z", "lat": 6.24, "lon": -75.58, "device": "optimus"}]}
```

## Deploying (Roy)

You need Terraform ≥ 1.6, and the `academy` AWS profile with fresh credentials from the Learner Lab "AWS Details" panel.

```bash
cd infra/terraform
terraform init
terraform apply
terraform output -raw ingest_url
terraform output -raw api_key        # share privately with the team
```

- **Settings:** all tunables live in `terraform/terraform.tfvars` (Terraform) and `lambda/config.py` (API limits and ranges).
- **State:** the Terraform state is local and gitignored, so deploy from the same machine. Re-running `apply` keeps the same URL and key.
- **Teardown:** `terraform destroy` removes everything, including the data.

## Tests

```bash
pip install -r infra/lambda/requirements-dev.txt
python -m pytest infra/lambda
```
