defmodule Sniper.PythonBridge do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  @impl true
  def init(_) do
    python_path = Path.join([File.cwd!(), "python", "bridge.py"])
    port = Port.open({:spawn, "python3 #{python_path}"}, [:binary, :exit_status])
    # Port spawns external Python process for IPC
    {:ok, %{port: port, callers: %{}, buffer: "", id_counter: 0}}
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

  def send_message(message) do
    GenServer.call(__MODULE__, {:send, message}, 5000)
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
            state

          id ->
            case Map.get(state.callers, id) do
              nil ->
                state

              from ->
                callers = Map.delete(state.callers, id)
                GenServer.reply(from, response)
                %{state | callers: callers}
            end
        end

      {:error, _} ->
        state
    end
  end
end
