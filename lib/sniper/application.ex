defmodule Sniper.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Starts a worker by calling: Sniper.Worker.start_link(arg)
      # {Sniper.Worker, arg}
      {Sniper.PythonBridge, []}
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: Sniper.Supervisor]
    result = Supervisor.start_link(children, opts)

    if Mix.env() != :test do
      run_demo()
    end

    result
  end

  defp run_demo do
    Process.sleep(100)
    response1 = Sniper.PythonBridge.send_message(%{type: "hello", count: 1})
    IO.puts("Received: #{Jason.encode!(response1)}")

    response2 = Sniper.PythonBridge.send_message(%{type: "hello", count: 2})
    IO.puts("Received: #{Jason.encode!(response2)}")
  end
end
