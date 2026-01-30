defmodule Sniper.PythonBridgeTest do
  use ExUnit.Case

  # These are integration tests that require the Python bridge to be running.
  # The bridge is started by the application supervisor.

  describe "send_message/1" do
    test "returns response with matching _id" do
      result = Sniper.PythonBridge.send_message(%{type: "hello", count: 42})

      assert is_map(result)
      assert Map.has_key?(result, "_id")
      assert result["status"] == "ok"
    end

    test "handles multiple sequential messages" do
      result1 = Sniper.PythonBridge.send_message(%{type: "hello", count: 1})
      result2 = Sniper.PythonBridge.send_message(%{type: "hello", count: 2})

      # Each message should get a unique _id
      assert result1["_id"] != result2["_id"]
      assert result1["status"] == "ok"
      assert result2["status"] == "ok"
    end
  end
end
