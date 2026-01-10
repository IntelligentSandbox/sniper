import sys
import json

# This receives all the messages from Elixir. 
# It's going to import all the other Python modules (LangChain, ChromaDB, etc)
# When we're going for scaling we are going to use elixir workers 
# All send request to the same bridge but the bridge.py routes the right function based on the type field. No multiple Python processes.

def handle_msg(msg):
    type = msg.get("type")

    if type == "hello":
        count = msg.get("count", 0)
        return {"response": f"hello from python {count}", "status": "ok"}

    else:
        return {"error": f"Unknown message type: {type}", "status": "error"}

for line in sys.stdin:
    msg = json.loads(line)
    response = handle_msg(msg)
    response["_id"] = msg.get("_id")
    print(json.dumps(response))
    sys.stdout.flush()
