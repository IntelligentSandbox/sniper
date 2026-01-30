defmodule Sniper.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      {Sniper.PythonBridge, []},
      {Plug.Cowboy, scheme: :http, plug: Sniper.Webhook, options: [port: 4000]}
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: Sniper.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
