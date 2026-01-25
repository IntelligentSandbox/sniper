defmodule Sniper do
  @moduledoc """
  Sniper - AI-powered code review tool.

  Main API for interacting with the Sniper system.
  """

  # TODO: Add HTTP endpoint (Phoenix/Plug) to receive GitHub webhook
  # TODO: Webhook handler calls send_message(%{type: "main", payload: payload})

  @doc """
  Send a message to the Python bridge for processing.

  ## Examples

      iex> Sniper.send_message(%{type: "hello", count: 1})
      %{"_id" => 1, "error" => nil, "response" => "hello from python 1", "status" => "ok"}

  """
  def send_message(message) do
    Sniper.PythonBridge.send_message(message)
  end

  @doc """
  Simple health check function.

  ## Examples

      iex> Sniper.health_check()
      :ok

  """
  def health_check do
    :ok
  end
end
