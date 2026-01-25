defmodule Sniper.PythonBridge do
  @moduledoc """
  Python bridge for IPC communication.

  Handles communication between Elixir and Python processes
  using JSON messages over stdin/stdout.
  """

  use GenServer
  require Logger

  @doc """
  Starts the Python bridge GenServer.
  """
  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  @impl true
  def init(_) do
    project_root = File.cwd!()
    pythonbridge_dir = Path.join([project_root, "pythonbridge"])
    python_path = Path.join([pythonbridge_dir, "bridge.py"])

    case File.exists?(python_path) do
      true ->
        port =
          Port.open(
            {:spawn_executable, System.find_executable("sh")},
            [
              :binary,
              :exit_status,
              args: [
                "-c",
                "PYTHONPATH=#{project_root} uv run --directory #{pythonbridge_dir} python -m pythonbridge.bridge"
              ]
            ]
          )

        {:ok, %{port: port, callers: %{}, buffer: "", id_counter: 0}}

      false ->
        {:stop, "Python bridge file not found: #{python_path}"}
    end
  end

  @impl true
  def handle_call({:send, message}, from, state) do
    # Message IDs correlate async requests with responses
    message_id = state.id_counter + 1
    message_with_id = Map.put(message, "_id", message_id)
    json_message = Jason.encode!(message_with_id)
    Port.command(state.port, json_message <> "\n")

    {:noreply,
     %{state | callers: Map.put(state.callers, message_id, from), id_counter: message_id}}
  end

  @impl true
  def handle_info({_port, {:data, data}}, state) do
    # Buffer handles partial data chunks from Port
    new_buffer = state.buffer <> data

    case split_lines(new_buffer) do
      {lines, remaining} ->
        state = Enum.reduce(lines, state, &process_response/2)
        {:noreply, %{state | buffer: remaining}}

      :incomplete ->
        {:noreply, %{state | buffer: new_buffer}}
    end
  end

  @impl true
  def handle_info({_port, {:exit_status, _status}}, state) do
    {:stop, :normal, state}
  end

  @doc """
  Send a message to the Python bridge.

  ## Parameters
  - message: Map containing the message to send

  ## Returns
  - {:ok, response} on success
  - response on success (for backward compatibility)

  ## Examples
      Sniper.PythonBridge.send_message(%{type: "hello", count: 1})
  """
  def send_message(message) do
    try do
      GenServer.call(__MODULE__, {:send, message}, 5000)
    catch
      :exit, {:noproc, _} ->
        {:error, "Python bridge not running"}

      :exit, {:timeout, _} ->
        {:error, "Python bridge timeout"}
    end
  end

  defp split_lines(data) do
    case String.split(data, "\n") do
      lines when length(lines) == 1 -> :incomplete
      lines -> {Enum.filter(lines, &(&1 != "")), ""}
    end
  end

  defp process_response(line, state) when line == "", do: state

  defp process_response(line, state) do
    case Jason.decode(line) do
      {:ok, response} ->
        case Map.get(response, "_id") do
          nil ->
            # Log untagged responses for debugging
            Logger.debug("Received response without _id: #{inspect(response)}")
            state

          id ->
            case Map.get(state.callers, id) do
              nil ->
                Logger.warning("Received response for unknown request id: #{id}")
                state

              from ->
                callers = Map.delete(state.callers, id)
                GenServer.reply(from, response)
                %{state | callers: callers}
            end
        end

      {:error, reason} ->
        Logger.error("Failed to decode JSON response: #{reason}, line: #{line}")
        state
    end
  end
end
