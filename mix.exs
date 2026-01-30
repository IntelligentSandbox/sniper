defmodule Sniper.MixProject do
  use Mix.Project

  def project do
    [
      app: :sniper,
      version: "0.1.0",
      elixir: "~> 1.18",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger],
      mod: {Sniper.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:jason, "~> 1.4"},
      {:plug_cowboy, "~> 2.7"},
      {:dotenvy, "~> 0.8"},
      {:credo, "~> 1.7", only: [:dev, :test], runtime: false}
    ]
  end
end
