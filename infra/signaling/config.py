# Tunables for the video signaling relay. Secrets and table name come from env vars set by Terraform.

API_KEY_PARAM = "key"

# API Gateway closes WebSockets after 2 h; stale rows expire a bit later
CONNECTION_TTL_S = 3 * 3600

ROBOT_ROLE = "robot"
BROWSER_ROLE = "browser"

# OpenBot's join message carries only these keys
JOIN_KEYS = {"roomId", "clientType"}
