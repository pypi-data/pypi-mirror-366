# Rust Crate Pipeline

A comprehensive system for gathering, enriching, and analyzing metadata for Rust crates using AI-powered insights, web scraping, and dependency analysis.

## Quickstart

```bash
pip install rust-crate-pipeline
python -m rust_crate_pipeline --config-file my_config.json
```

- Requires **Python 3.11+**
- For GPU/DeepSeek/llama-cpp-python, see the 'Advanced' section below

## Features

- Enhanced web scraping (Crawl4AI + Playwright)
- AI enrichment (local or Azure OpenAI, DeepSeek, Lambda.AI, etc.)
- Multi-provider LLM support (see Advanced)
- Cargo build/test/audit
- Batch processing, JSON output, Docker support

## Requirements

- **Python 3.11+**
- Git, Cargo, Playwright (auto-installed)

## Installation

```bash
pip install rust-crate-pipeline
# For dev: pip install -e .
# Install Playwright browsers (required for enhanced scraping)
playwright install
```

## Configuration

- All configuration is via a single JSON file, passed with `--config-file <path>`
- No config file is auto-loaded; you must specify the path

Example `my_config.json`:
```json
{
    "batch_size": 10,
    "n_workers": 4,
    "max_retries": 3,
    "checkpoint_interval": 10,
    "use_azure_openai": false,
    "enable_crawl4ai": true,
    "model_path": "/path/to/model.gguf"
}
```

Set required environment variables as needed (e.g., `GITHUB_TOKEN`, Azure/OpenAI keys, etc.)

## Usage

### Basic Usage

```bash
python -m rust_crate_pipeline --config-file my_config.json
```

### Custom Options (combine as needed)

```bash
python -m rust_crate_pipeline \
  --config-file my_config.json \
  --batch-size 20 \
  --n-workers 8 \
  --max-tokens 2048 \
  --checkpoint-interval 5 \
  --log-level DEBUG \
  --output-path ./results
```

### Advanced: Multi-Provider LLM & GPU

- For local DeepSeek, GPU, or custom LLMs, set `model_path` and `n_gpu_layers` in your config file.
- For Azure/OpenAI/Lambda.AI, set `use_azure_openai: true` and provide the required environment variables.
- For full LLM provider support, see [README_LLM_PROVIDERS.md](README_LLM_PROVIDERS.md)

## Development

- Build: `python -m build`
- Test: `pytest --cov=rust_crate_pipeline tests/`
- Lint: `pyright rust_crate_pipeline/`
- Format: `black rust_crate_pipeline/`
- Publish: `twine upload dist/*`

## Changelog

See `CHANGELOGS/CHANGELOG_v1.5.0.md` and previous changelogs for release history.
