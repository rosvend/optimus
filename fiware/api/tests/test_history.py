from history import build_sql, to_item
from readings import Query

# 2026-10-14T15:00:00.000Z
MS = 1791990000000


def test_sql_filters_the_sensor_column_and_time_range():
    sql, args = build_sql(Query("temperature", "2026-10-14T10:00:00.000Z", "2026-10-14T11:00:00.000Z", 20))

    assert "temperature IS NOT NULL" in sql
    assert "time_index >= ?" in sql and "time_index <= ?" in sql
    assert sql.endswith("ORDER BY time_index DESC LIMIT ?")
    assert args == ["2026-10-14T10:00:00.000Z", "2026-10-14T11:00:00.000Z", 20]


def test_sql_without_range_has_no_time_filter():
    sql, args = build_sql(Query("gps", None, None, 5))

    assert "location IS NOT NULL" in sql
    assert "time_index >=" not in sql
    assert args == [5]


def test_value_item_rounds_the_float32_noise():
    item = to_item("temperature", "urn:ngsi-ld:Robot:optimus", MS, 23.399999618530273)

    assert item == {"ts": "2026-10-14T15:00:00.000Z", "device": "optimus", "value": 23.4}


def test_gps_item_unpacks_geojson_lon_lat():
    item = to_item("gps", "urn:ngsi-ld:Robot:optimus", MS + 5, {"type": "Point", "coordinates": [-75.58, 6.24]})

    assert item == {"ts": "2026-10-14T15:00:00.005Z", "device": "optimus", "lat": 6.24, "lon": -75.58}
