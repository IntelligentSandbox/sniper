# Sniper

Sniper is an AI-powered GitHub App tool/bot that automates code review and bug detection.

## Prerequisites

- Elixir 1.14+
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Installation

### 1. Install Elixir

**macOS (Homebrew):**
```bash
brew install elixir
```

**Ubuntu/Debian:**
```bash
sudo apt-get install elixir
```

**Other platforms:** See the [official Elixir installation guide](https://elixir-lang.org/install.html).

### 2. Install uv (Python package manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Homebrew:**
```bash
brew install uv
```

**Other platforms:** See the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 3. Install project dependencies

```bash
# Install Elixir dependencies
mix deps.get

# Install Python dependencies
cd python
uv sync
```

Or use the Makefile:
```bash
make install
```

### 4. Configure environment variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and set your `GROQ_API_KEY`.

## Usage

### Running the Elixir webhook server

```bash
# Keep the server running (recommended)
make run

# Or with an interactive Elixir shell (useful for development)
iex -S mix
```

The webhook server will be available at `http://localhost:4000`.

### Local Development with Webhooks

For local development, use [smee](https://smee.io/) to forward GitHub webhooks to your local server:

1. Create a channel at https://smee.io/
2. Set the Smee URL as your GitHub App's webhook URL
3. Run the smee client to forward requests:

```bash
smee -u https://smee.io/YOUR_CHANNEL_ID --path /webhook --port 4000
```

### Running the Python bridge (standalone)

```bash
make run-python
```
