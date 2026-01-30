defmodule Sniper.Webhook do
  use Plug.Router
  require Logger

  plug(Plug.Logger)
  plug(:match)
  plug(:dispatch)

  post "/webhook" do
    {:ok, body, conn} = Plug.Conn.read_body(conn)

    case validate_signature(conn, body) do
      :ok ->
        handle_webhook(conn, body)

      :error ->
        Logger.warning("Webhook signature validation failed")
        send_resp(conn, 401, "invalid signature")
    end
  end

  match _ do
    send_resp(conn, 404, "not found")
  end

  # Validates GitHub webhook signature using HMAC-SHA256
  defp validate_signature(conn, body) do
    secret = Application.get_env(:sniper, :github_webhook_secret)

    # Skip validation if no secret configured (development mode)
    if is_nil(secret) or secret == "" do
      Logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature validation")
      :ok
    else
      case Plug.Conn.get_req_header(conn, "x-hub-signature-256") do
        ["sha256=" <> signature] ->
          expected = compute_signature(body, secret)

          if Plug.Crypto.secure_compare(expected, signature) do
            :ok
          else
            :error
          end

        _ ->
          Logger.warning("Missing x-hub-signature-256 header")
          :error
      end
    end
  end

  # Compute HMAC-SHA256 and return as lowercase hex string
  defp compute_signature(body, secret) do
    :crypto.mac(:hmac, :sha256, secret, body)
    |> Base.encode16(case: :lower)
  end

  # Process validated webhook payload
  defp handle_webhook(conn, body) do
    case Jason.decode(body) do
      {:ok, payload} ->
        event = get_github_event(conn)
        action = Map.get(payload, "action")
        Logger.info("Webhook received: event=#{event} action=#{action}")

        if event == "issue_comment" do
          handle_issue_comment(payload, action)
        end

        send_resp(conn, 200, "ok")

      {:error, _} ->
        Logger.error("Invalid JSON in webhook body")
        send_resp(conn, 400, "invalid json")
    end
  end

  defp get_github_event(conn) do
    case Plug.Conn.get_req_header(conn, "x-github-event") do
      [event] -> event
      _ -> "unknown"
    end
  end

  # TODO: Ignoring everything else for now like deleted or edited
  defp handle_issue_comment(payload, "created") do
    body = get_in(payload, ["comment", "body"]) || ""
    is_pr = get_in(payload, ["issue", "pull_request"]) != nil
    if not is_pr, do: :ok, else: dispatch_command(body, payload)
  end

  defp handle_issue_comment(_payload, _action), do: :ok

  defp dispatch_command(body, payload) do
    pr = %{
      "number" => get_in(payload, ["issue", "number"]),
      "repository" => payload["repository"],
      "installation" => payload["installation"]
    }

    case parse_command(body) do
      "review" ->
        Task.start(fn -> Sniper.send_message(%{type: "main", payload: pr}) end)

      "ping" ->
        Task.start(fn -> Sniper.send_message(%{type: "comment", payload: pr, body: "pong"}) end)

      _ ->
        :ok
    end
  end

  defp parse_command(body) do
    body
    |> String.downcase()
    |> String.split()
    |> find_command()
  end

  defp find_command(["@snipercodeai", command | _]), do: command
  defp find_command([_ | rest]), do: find_command(rest)
  defp find_command([]), do: nil
end
