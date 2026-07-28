[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](README.pt-BR.md)

# Antropomorphic Writing

This tool adds a human touch to text. Drop something in and it translates and rewrites it over and over until it reads like a person wrote it.

The idea is simple. AI-generated text leaves traces. By moving between different languages, those machine-like patterns gradually fall apart.

## How it works

```
EN → Portuguese → Chinese → Japanese → Finnish → EN
```

| Step | Engine | Description |
|:----:|:-------|:------------|
| 0 | DeepSeek | Rewrites the original text in **Portuguese** with a natural tone |
| 1 | DeepSeek | Translates and rewrites Portuguese into **Chinese** |
| 2 | DeepSeek | Translates Chinese into **Japanese** using context from the previous step |
| 3 | Google Translate | Translates Japanese into **Finnish** |
| 4 | Niutrans / Google | Translates Finnish back into **English** |

Each pass removes more of the AI traces. By default the pipeline runs in **double pass** — the text goes through the entire chain twice before coming back to English. You can disable it with `double_pass=False` if you prefer a single pass.

## Requirements

- Python 3.10+
- A DeepSeek API key (any OpenAI-compatible provider works)

## Installation

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy the example file and add your API key:

```bash
cp config/config.example.toml config/config.toml
# Edit config/config.toml and set your deepseek_api_key
```

## Usage

```bash
# Through the script
./humanize.sh "Text to humanize"

# As a Python module
export LLM_API_KEY="sk-..."
python -m src.standard.pipeline --input "text to humanize" --verbose  # double pass é padrão

# Directly in Python
from standard.pipeline import run_standard_pipeline
import toml

config = toml.load("config/config.toml")
result = run_standard_pipeline("text to humanize", config, double_pass=True)
print(result["result"])
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | Your API key |
| `LLM_BASE_URL` | API base URL (optional) |
| `LLM_MODEL` | Model name (optional) |

## License

MIT — use it however you like.
