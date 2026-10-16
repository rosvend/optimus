from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


class DynamoStore:
    def __init__(self, table_name):
        self._table = boto3.resource("dynamodb").Table(table_name)

    def put_many(self, items):
        with self._table.batch_writer(overwrite_by_pkeys=["sensor", "ts"]) as batch:
            for item in items:
                batch.put_item(Item={key: _to_dynamo(value) for key, value in item.items()})

    def query(self, query):
        response = self._table.query(
            KeyConditionExpression=Key("sensor").eq(query.sensor) & Key("ts").between(query.start, query.end),
            ScanIndexForward=False,
            Limit=query.limit,
        )
        return response["Items"]


def _to_dynamo(value):
    # DynamoDB rejects floats; str() keeps the value as sent instead of its binary expansion
    return Decimal(str(value)) if isinstance(value, float) else value
