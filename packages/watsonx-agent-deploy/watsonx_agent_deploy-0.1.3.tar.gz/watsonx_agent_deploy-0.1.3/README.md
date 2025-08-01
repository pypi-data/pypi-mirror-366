# Watsonx Agent Deploy

Simple CLI tool to deploy multiple AI agents to IBM watsonx.ai

## Installation

```bash
pip install watsonx-agent-deploy
```

## Quick Start

1. **Generate agent folders** using the IBM CLI template:

   ```bash
   watsonx‑ai template new "base/langgraph‑react‑agent" my-agent
   ```

2. **Create a `.env` file** with:

   ```text
   WATSONX_APIKEY=your_api_key_here
   WATSONX_URL=https://your-watsonx-url.com
   SPACE_ID=your_space_id
   ```

3. **Deploy agents** by running:

   ```bash
   watsonx-deploy
   ```

## Required File Structure

Your project directory (current or specified via `--config-dir`) should follow this layout:

```
your-project-root/
├── .env                          # contains WATSONX_APIKEY, WATSONX_URL, SPACE_ID
├── my-agent/
│   └── config.toml              # agent-specific configuration
├── another-agent/
│   └── config.toml
├── sample-agent/
│   └── config.toml
```

### Notes:

* **Agent folders** must end with `'agent'` (e.g. `my-agent`), else they will be ignored.
* Each agent folder **must contain** a valid `config.toml`.
* The `.env` file must reside in the **root of your deployment directory** (or be specified via `--env-file`).

## Usage Examples

```bash
# Deploy agents from current default directory
watsonx-deploy

# Use a custom .env file
watsonx-deploy --env-file path/to/.env

# Deploy engines from a specific directory
watsonx-deploy --config-dir path/to/agents

# Enable verbose logging for troubleshooting
watsonx-deploy --verbose
```

## Requirements

* Python 3.11+
* Proper `.env` with required credentials
* Agent folders must follow naming and structure rules above

---

## License
MIT
