from contextlib import closing
from datetime import datetime, timedelta, timezone

from crate import client
from crate.client.exceptions import Error, ProgrammingError

from config import ENTITY_ID_PREFIX, HISTORY_TABLE, SENSOR_COLUMNS, VALUE_DECIMALS
from orion import BackendError
from readings import format_ts

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def build_sql(query):
    column = SENSOR_COLUMNS[query.sensor]
    sql = f"SELECT entity_id, time_index, {column} FROM {HISTORY_TABLE} WHERE {column} IS NOT NULL"
    args = []
    if query.start is not None:
        sql += " AND time_index >= ?"
        args.append(query.start)
    if query.end is not None:
        sql += " AND time_index <= ?"
        args.append(query.end)
    sql += " ORDER BY time_index DESC LIMIT ?"
    args.append(query.limit)
    return sql, args


def to_item(sensor, entity_id, time_index_ms, value):
    item = {"ts": format_ts(EPOCH + timedelta(milliseconds=time_index_ms)), "device": entity_id.removeprefix(ENTITY_ID_PREFIX)}
    if sensor == "gps":
        # QuantumLeap turns geo:point into a GeoJSON Point, which is [lon, lat]
        lon, lat = value["coordinates"]
        return {**item, "lat": lat, "lon": lon}
    return {**item, "value": round(value, VALUE_DECIMALS)}


class CrateHistory:
    """Reads the time series QuantumLeap writes into CrateDB, newest first."""

    def __init__(self, crate_url):
        self._url = crate_url

    def query(self, query):
        sql, args = build_sql(query)
        try:
            with closing(client.connect(self._url, username="crate", timeout=5)) as connection:
                cursor = connection.cursor()
                cursor.execute(sql, args)
                rows = cursor.fetchall()
        except ProgrammingError as error:
            # QuantumLeap creates the table with the first notification
            if "RelationUnknown" in str(error):
                return []
            raise BackendError(f"CrateDB: {error}") from error
        except Error as error:
            raise BackendError(f"CrateDB: {error}") from error
        return [to_item(query.sensor, *row) for row in rows]
