import boto3
from boto3.dynamodb.conditions import Key

ROOM_INDEX = "room"


class DynamoConnections:
    def __init__(self, table_name):
        self._table = boto3.resource("dynamodb").Table(table_name)

    def put(self, connection_id, room_id, role, expires):
        self._table.put_item(Item={"connectionId": connection_id, "roomId": room_id, "role": role, "expires": expires})

    def get(self, connection_id):
        return self._table.get_item(Key={"connectionId": connection_id}).get("Item")

    def delete(self, connection_id):
        self._table.delete_item(Key={"connectionId": connection_id})

    def in_room(self, room_id):
        return self._table.query(IndexName=ROOM_INDEX, KeyConditionExpression=Key("roomId").eq(room_id))["Items"]


class ApiGatewayNotifier:
    def __init__(self, request_context, gone_error):
        endpoint = f"https://{request_context['domainName']}/{request_context['stage']}"
        self._client = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)
        self._gone_error = gone_error

    def send(self, connection_id, data):
        try:
            self._client.post_to_connection(ConnectionId=connection_id, Data=data.encode())
        except self._client.exceptions.GoneException as error:
            raise self._gone_error(connection_id) from error
