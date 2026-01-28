defmodule Sniper.Webhook do
  use Plug.Router
  require Logger

  plug(Plug.Logger)
  plug(:match)
  plug(:dispatch)

  post "/webhook" do
    {:ok, body, conn} = Plug.Conn.read_body(conn)

    case Jason.decode(body) do
      {:ok, payload} ->
        action = Map.get(payload, "action")
        Logger.info("Webhook received: action=#{action}")

        if action in ["opened", "synchronize", "reopened"] do
          Logger.info("Processing PR review...")

          Task.start(fn ->
            result = Sniper.send_message(%{type: "main", payload: payload})
            Logger.info("Review result: #{inspect(result)}")
          end)
        end

        send_resp(conn, 200, "ok")

      {:error, _} ->
        Logger.error("Invalid JSON in webhook body")
        send_resp(conn, 400, "invalid json")
    end
  end

  match _ do
    send_resp(conn, 404, "not found")
  end
end
