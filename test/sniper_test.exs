defmodule SniperTest do
  use ExUnit.Case
  doctest Sniper

  test "health check returns ok" do
    assert Sniper.health_check() == :ok
  end
end
