defmodule Sniper.WebhookTest do
  use ExUnit.Case, async: true
  import Plug.Test
  import Plug.Conn

  @opts Sniper.Webhook.init([])

  # Helper to compute valid signature for a body
  defp sign(body, secret) do
    :crypto.mac(:hmac, :sha256, secret, body)
    |> Base.encode16(case: :lower)
  end

  # Helper to create a webhook request with signature
  defp webhook_conn(body, secret) do
    signature = sign(body, secret)

    conn(:post, "/webhook", body)
    |> put_req_header("content-type", "application/json")
    |> put_req_header("x-hub-signature-256", "sha256=#{signature}")
  end

  describe "signature validation" do
    setup do
      # Set a test secret for these tests
      Application.put_env(:sniper, :github_webhook_secret, "test_secret")
      on_exit(fn -> Application.delete_env(:sniper, :github_webhook_secret) end)
      :ok
    end

    test "valid signature returns 200" do
      body = ~s({"action": "closed"})
      conn = webhook_conn(body, "test_secret")

      conn = Sniper.Webhook.call(conn, @opts)

      assert conn.status == 200
      assert conn.resp_body == "ok"
    end

    test "invalid signature returns 401" do
      body = ~s({"action": "opened"})

      conn =
        conn(:post, "/webhook", body)
        |> put_req_header("content-type", "application/json")
        |> put_req_header("x-hub-signature-256", "sha256=invalidsignature")

      conn = Sniper.Webhook.call(conn, @opts)

      assert conn.status == 401
      assert conn.resp_body == "invalid signature"
    end

    test "missing signature header returns 401" do
      body = ~s({"action": "opened"})

      conn =
        conn(:post, "/webhook", body)
        |> put_req_header("content-type", "application/json")

      conn = Sniper.Webhook.call(conn, @opts)

      assert conn.status == 401
      assert conn.resp_body == "invalid signature"
    end
  end

  describe "no secret configured" do
    setup do
      # Ensure no secret is set
      Application.delete_env(:sniper, :github_webhook_secret)
      :ok
    end

    test "skips validation when GITHUB_WEBHOOK_SECRET not set" do
      body = ~s({"action": "closed"})

      conn =
        conn(:post, "/webhook", body)
        |> put_req_header("content-type", "application/json")

      conn = Sniper.Webhook.call(conn, @opts)

      # Should pass without signature
      assert conn.status == 200
    end
  end

  describe "request handling" do
    setup do
      # Skip signature validation for these tests
      Application.delete_env(:sniper, :github_webhook_secret)
      :ok
    end

    test "invalid JSON returns 400" do
      conn =
        conn(:post, "/webhook", "not valid json")
        |> put_req_header("content-type", "application/json")

      conn = Sniper.Webhook.call(conn, @opts)

      assert conn.status == 400
      assert conn.resp_body == "invalid json"
    end

    test "valid JSON returns 200" do
      body = ~s({"action": "closed", "number": 1})

      conn =
        conn(:post, "/webhook", body)
        |> put_req_header("content-type", "application/json")

      conn = Sniper.Webhook.call(conn, @opts)

      assert conn.status == 200
      assert conn.resp_body == "ok"
    end

    test "unknown route returns 404" do
      conn = conn(:get, "/unknown")

      conn = Sniper.Webhook.call(conn, @opts)

      assert conn.status == 404
      assert conn.resp_body == "not found"
    end
  end
end
