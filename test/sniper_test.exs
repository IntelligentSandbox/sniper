defmodule SniperTest do
  use ExUnit.Case
  doctest Sniper

  test "checks ok" do
    assert Sniper.hello() == :ok
  end
end
