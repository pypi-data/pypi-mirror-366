       # Commit-Gen - AI-Powered Git Commit Message Generator

[![PyPI version](https://badge.fury.io/py/commit-gen.svg)](https://badge.fury.io/py/commit-gen)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Generate intelligent commit messages using AI with support for multiple providers including OpenRouter, Ollama, Google Gemini, and Mistral AI.**

## 🚀 Quick Start

### Installation

```bash
pip install commit-gen
```

### First Time Setup

```bash
# Interactive setup wizard (recommended)
commit-gen --setup

# Or manual setup
commit-gen --set-provider openrouter
commit-gen --set-api-key YOUR_API_KEY
```

### Basic Usage

```bash
# Interactive file selection and commit
commit-gen

# Commit specific files
commit-gen --files src/main.py tests/test_main.py

# Commit all files
commit-gen --all

# Commit and push
commit-gen --push
```

## ✨ Key Features

- **🤖 AI-Powered**: Generate commit messages using advanced AI models
- **📁 Interactive File Selection**: Choose which files to commit with arrow key navigation
- **🔧 Multiple AI Providers**: Support for OpenRouter, Ollama, Google Gemini, Mistral AI
- **⚙️ Easy Configuration**: Interactive setup wizard and simple CLI commands
- **📝 Smart Review**: Edit and confirm commit messages before committing
- **🚀 Auto Push**: Optional automatic push to remote repository

## 🛠️ Supported AI Providers

| Provider | Type | Default Model | API Key Required |
|----------|------|---------------|------------------|
| **OpenRouter** | Cloud | moonshotai/kimi-k2:free | ✅ |
| **Ollama** | Local | qwen2.5-coder:7b | ❌ |
| **Google Gemini** | Cloud | gemini-2.5-flash | ✅ |
| **Mistral AI** | Cloud | mistral-large-2411 | ✅ |
| **Custom** | Any | Configurable | ✅ |

## 📖 Usage Examples

### Interactive File Selection

```bash
commit-gen
```

Shows an interactive interface where you can:
- Navigate files with ↑/↓ arrow keys
- Toggle selection with SPACE
- See file status (modified, added, untracked)
- View file sizes and categories

### Quick Commits

```bash
# Commit specific files
commit-gen --files src/main.py tests/test_main.py

# Commit all modified files
commit-gen --all

# Commit and push automatically
commit-gen --push
```

### Provider Configuration

```bash
# Set provider
commit-gen --set-provider gemini

# Set API key
commit-gen --set-api-key YOUR_API_KEY

# Set custom model
commit-gen --set-model gemini-2.5-pro

# View current config
commit-gen --config
```

## 🔧 Configuration

### Interactive Setup (Recommended)

```bash
commit-gen --setup
```

Guides you through:
- Provider selection
- API key configuration
- Model selection
- Connection testing

### Manual Configuration

```bash
# Show available providers
commit-gen --providers

# Configure OpenRouter
commit-gen --set-provider openrouter
commit-gen --set-api-key YOUR_OPENROUTER_KEY

# Configure Ollama (local)
commit-gen --set-provider ollama
# No API key needed for Ollama

# Configure Google Gemini
commit-gen --set-provider gemini
commit-gen --set-api-key YOUR_GEMINI_KEY

# Configure Mistral AI
commit-gen --set-provider mistral
commit-gen --set-api-key YOUR_MISTRAL_KEY
```

## 🎯 Advanced Features

### Custom Prompts

```bash
commit-gen --prompt "Generate a conventional commit message: {changes}"
```

### Changelog Generation

```bash
commit-gen --changelog
commit-gen --changelog --compare-branch develop
```

### Debug Mode

```bash
commit-gen --debug
```

### Troubleshooting

### Issue: Command not found after installation

If `commit-gen` command is not found after installation:

1. **Check if symlink exists:**
   ```bash
   ls -la /usr/local/bin/commit-gen
   ```

2. **If symlink is broken, recreate it:**
   ```bash
   sudo ln -s /path/to/your/project/commit-gen.py /usr/local/bin/commit-gen
   ```

3. **For pip installation, check PATH:**
   ```bash
   which commit-gen
   echo $PATH
   ```

### Issue: Configuration files not cleaned up

If configuration files remain after uninstallation:

```bash
rm -rf ~/.config/git-commit-ai/
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Git**: Working git repository
- **AI Provider**: At least one AI provider configured

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://gitlab.mobio.vn/mobio/tools/gen-commit-message) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://gitlab.mobio.vn/mobio/tools/gen-commit-message/-/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments
- Powered by various AI providers
- Inspired by the need for better commit messages
