# Claude OpenRouter Tool

[![CI](https://github.com/belyak/claude-open-router-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/belyak/claude-open-router-tool/actions/workflows/ci.yml)

Command-line utility for OpenRouter integration with Claude Code. Automates installation and configuration of `@musistudio/claude-code-router` npm package.

## Installation

```bash
pipx install claude-openrouter-tool
```

## Requirements

- Python 3.9+
- Node.js/npm
- OpenRouter API key

## Commands

### setup
```bash
claude-openrouter-tool setup
```
Interactive configuration wizard. Performs npm verification, package installation, API key input, model selection, and configuration file creation.

### check
```bash
claude-openrouter-tool check
```
Validates npm installation, router package status, configuration file structure, and API key functionality.

### update
```bash
claude-openrouter-tool update
```
Updates `@musistudio/claude-code-router` to latest version.

### config
```bash
claude-openrouter-tool config
```
Interactive configuration management. Supports viewing settings, editing API keys, managing models, and setting defaults.

## Supported Models

| Model | Parameters | Application |
|-------|------------|-------------|
| `deepseek/deepseek-r1:free` | 671B | Complex reasoning (default) |
| `deepseek/deepseek-v3-0324:free` | 685B MoE | General coding |
| `qwen/qwen-2.5-coder-32b-instruct:free` | 32B | Code generation |
| Llama/Mistral variants | Various | Lightweight operations |

## Configuration

File location: `~/.claude-code-router/config.json`

```json
{
  "Providers": [{
    "name": "openrouter",
    "api_base_url": "https://openrouter.ai/api/v1/chat/completions",
    "api_key": "sk-or-...",
    "models": ["deepseek/deepseek-r1:free"]
  }],
  "Router": {
    "default": "openrouter,deepseek/deepseek-r1:free"
  }
}
```

## Usage

1. Install: `pipx install claude-openrouter-tool`
2. Obtain API key: [OpenRouter.ai](https://openrouter.ai)
3. Configure: `claude-openrouter-tool setup`
4. Verify: `claude-openrouter-tool check`

## Model Management

Add additional models via configuration menu:
```bash
claude-openrouter-tool config
```

Supported model additions:
- `anthropic/claude-3-haiku:beta`
- `google/gemini-pro-1.5`
- `openai/gpt-4o-mini`

Change default model via "Set Default Model" menu option.

## Integration

Router package proxies API requests to OpenRouter. Configured models appear automatically in Claude Code interface.

## Troubleshooting

### Issues and Solutions

| Problem | Solution |
|---------|----------|
| npm not found | Install Node.js from nodejs.org, verify PATH |
| Permission denied | Use `sudo npm install -g @musistudio/claude-code-router` |
| Invalid API key | Verify `sk-or-...` format, check account credits |
| Configuration missing | Execute `claude-openrouter-tool setup` |
| Models not visible | Verify package status, restart Claude Code |

### Diagnostics

```bash
claude-openrouter-tool check
```

Reports npm status, package version, configuration validity, and API key functionality.

### References

- [OpenRouter documentation](https://openrouter.ai/docs)
- [Router repository](https://github.com/musistudio/claude-code-router)

## Alternative Commands

```bash
ortool-claude setup|check|config|update
```

## Development

### Technology Stack
- Python 3.9+, Click framework
- pytest with pexpect testing
- uv package management

### Environment Setup
```bash
git clone <repository-url>
cd claude-openrouter-tool
uv sync
uv run pre-commit install
```

### Testing
```bash
uv run pytest
```

### Architecture Components
- JSON configuration management
- Automated npm package handling
- Interactive CLI with inquirer prompts
- Comprehensive validation system
