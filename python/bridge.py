import sys
import json

# Python bridge router for Sniper
# Routes messages from Elixir to appropriate Python modules

def handle_msg(msg):
    """
    Route messages based on type field.

    Required fields:
    - "type": Message type for routing
    - "_id": Request correlation ID (added automatically by Elixir)
    """
    type = msg.get("type")

    if type == "example":
        return {"status": "ok"}
    else:
        return {"error": f"Unknown message type: {type}", "status": "error"}

for line in sys.stdin:
    try:
        msg = json.loads(line)
        response = handle_msg(msg)
        response["_id"] = msg.get("_id")
        print(json.dumps(response))
        sys.stdout.flush()
    except json.JSONDecodeError as e:
        error_response = {"error": f"JSON decode error: {e}", "status": "error"}
        print(json.dumps(error_response))
        sys.stdout.flush()
