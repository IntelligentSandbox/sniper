defmodule Sniper do
  @moduledoc """
  Sniper - AI-powered code review tool.

  Main API for interacting with the Sniper system.
  """

  @doc """
  Send a message to the Python bridge for processing.

  ## Examples

      iex> Sniper.send_message(%{type: "main", data: "test"})
      %{"_id" => 1, "status" => "ok"}

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
