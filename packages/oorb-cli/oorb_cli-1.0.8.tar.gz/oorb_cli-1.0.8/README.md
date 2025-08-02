# OORB CLI – Robotics coding Assistant

**OORB** (Open Organic Robotics Benchmark) is an open-source initiative focused on advancing robotics through AI-powered tools and benchmarks. 

**OORB CLI** is a command-line assistant designed to answer questions and assist with tasks related to **ROS2** (Robot Operating System 2). Powered by modern language models and enhanced with vector search and retrieval-augmented generation, it serves as an intelligent tool for roboticists and developers working with ROS2.

---

## Features

* Focused exclusively on **ROS2**
* Interactive and one-shot Q&A modes
* Backend support for **OpenAI**, **Azure OpenAI**, and **Ollama**
* Local inference support with Ollama
* Retrieval-augmented answers with Milvus vector store
* Configurable model, temperature, and backend preferences
* **Tool calling capabilities** with access to:
  - `read_file` - Read and analyze files
  - `write_file` - Create and modify files
  - `search_in_files` - Search across file contents
  - `run_command` - Execute system commands
  - `list_directory` - Browse directory structures
  - `edit_file_lines` - Make precise file edits

### Note: 
You can find a quick demo of the CLI on the following link : [link](https://youtu.be/6o50YBeWZ04)


---


## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install oorb-cli
```

The CLI is available on [PyPI](https://pypi.org/project/oorb-cli/) and can be installed directly via pip.

### Option 2: Development Installation

#### 1. Clone the repository

```bash
git clone https://github.com/OORB-Open-Organic-Robotics/oorb-cli
cd oorb-cli
```

#### 2. Create virtual environment and install dependencies using `uv`

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

This installs the CLI in *editable mode*, allowing you to make changes to the source code without reinstalling.

> **Note:** `uv pip install -e .` is functionally equivalent to `pip install -e .`, but uses `uv` for faster dependency resolution and isolated builds.

---

## Configuration

Set the appropriate API key depending on the backend you intend to use.

### OpenAI

```bash
export OPENAI_API_KEY="your-key"
```

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="your-endpoint"
```

---

## Usage

Once installed, the CLI becomes available via the `oorb` command (or `python oorb_cli.py` if unlinked).

### Main Commands

#### `chat` - Interactive ROS2 Assistant

Start an interactive chat session or ask a single question with full customization options.

**Basic Usage:**
```bash
# Interactive mode
oorb chat

# Single question mode
oorb chat -p "How do I create a custom message type in ROS2?"
```

**Available Options:**
- `-b, --backend` - Choose LLM backend: `azure`, `openai`, or `ollama`
- `-m, --model` - Specify model name (e.g., `gpt-4o-mini`, `gpt-3.5-turbo`)
- `-t, --temperature` - Set response creativity (0.0-1.0, default: 0.3)
- `-p, --prompt` - Single prompt for non-interactive mode
- `--use-tools/--no-tools` - Enable/disable tool calling (default: auto-detect)

**Examples:**
```bash
# Use specific backend and model
oorb chat -b openai -m gpt-4o-mini -t 0.7

# Quick question with custom settings
oorb chat -b azure -m gpt-3.5-turbo -p "Create a ROS2 launch file for navigation"

# Disable tools for faster responses
oorb chat --no-tools -p "What is a ROS2 node?"
```

#### `list-models` - View Available Models

Display all available models for different backends.

**Basic Usage:**
```bash
oorb list-models
```

**Available Options:**
- `-b, --backend` - Filter by specific backend: `azure`, `openai`, or `ollama`

**Examples:**
```bash
# List all models
oorb list-models

# List only OpenAI models
oorb list-models -b openai

# List only local Ollama models
oorb list-models -b ollama
```

#### `status` - System Health Check

Check system configuration, API keys, and service availability.

**Basic Usage:**
```bash
oorb status
```

**What it shows:**
- API key configuration status
- Ollama service status and available models
- Retrieval API connectivity
- Available backends
- Configuration warnings and errors
- Quick setup recommendations

---

## Contributing

We welcome contributions to the OORB CLI project! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidelines on how to contribute to the project.

---

## License

This project is open-source and available under the appropriate license. Please check the LICENSE file for details.
