# GitScribe 📜

> *Scribing knowledge from the Git universe*

GitScribe is a powerful Model Context Protocol (MCP) server that enables intelligent web scraping of Git-based documentation with Retrieval Augmented Generation (RAG) capabilities. This tool helps code assistants and developers efficiently extract, process, and retrieve information from documentation websites, GitHub repositories, and other Git-based resources to accelerate application development.

## ✨ Features

- **🌐 Universal Git Support**: Works with GitHub, GitLab, Bitbucket, and Azure DevOps
- **🧠 Intelligent RAG System**: ChromaDB + Sentence Transformers for semantic search
- **📄 Multi-Format Parsing**: Markdown, HTML, reStructuredText, and source code files
- **⚡ High Performance**: Async scraping with intelligent rate limiting
- **🔧 MCP Integration**: Full Model Context Protocol compliance for AI assistants
- **📊 Rich CLI**: Command-line interface for testing and management
- **🎯 Smart Filtering**: Automatic content filtering and relevance scoring

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install gitscribe-mcp

# Or install with uv (recommended for development)
uv sync

# Or install with pip for development
pip install -e .

# Or install dependencies manually
pip install -r requirements-gitscribe.txt
```

### Basic Usage

#### 1. Start the MCP Server
```bash
# Start the server for use with AI assistants
gitscribe server

# Or run directly with uv
uv run gitscribe server
```

#### 2. Scrape Documentation
```bash
# Scrape Python documentation
gitscribe scrape https://docs.python.org --depth 2 --output python_docs.json

# Scrape a GitHub repository
gitscribe scrape https://github.com/microsoft/vscode --formats md html rst
```

#### 3. Index Documents
```bash
# Index scraped documents into the RAG system
gitscribe index python_docs.json
```

#### 4. Search Documentation
```bash
# Search indexed documentation
gitscribe search "async await python examples"
gitscribe search "VSCode extension API" --limit 5
```

#### 5. Analyze Repositories
```bash
# Get repository information and structure
gitscribe repo-info https://github.com/microsoft/vscode
```

## 📋 MCP Tools

GitScribe provides the following MCP tools:

### `scrape_documentation`
Scrape and index documentation from a Git repository or website.

**Parameters:**
- `url` (string, required): Repository or documentation URL
- `depth` (integer, optional): Maximum crawling depth (default: 3)
- `formats` (array, optional): Supported document formats

### `search_documentation`
Search indexed documentation using semantic search.

**Parameters:**
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Maximum number of results (default: 10)
- `filter` (object, optional): Filter criteria (language, framework, etc.)

### `get_code_examples`
Extract code examples related to a specific topic.

**Parameters:**
- `topic` (string, required): Programming topic or concept
- `language` (string, optional): Programming language filter
- `framework` (string, optional): Framework or library filter

## 🛠️ Configuration

GitScribe can be configured through environment variables:

```bash
# Server settings
export GITSCRIBE_DEBUG=true
export GITSCRIBE_MAX_DEPTH=3
export GITSCRIBE_MAX_PAGES=100

# RAG system settings
export GITSCRIBE_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export GITSCRIBE_CHUNK_SIZE=1000
export GITSCRIBE_CHROMA_DIR="./chroma_db"

# Rate limiting
export GITSCRIBE_REQUEST_DELAY=1.0
export GITSCRIBE_CONCURRENT_REQUESTS=5

# Git platform authentication (optional)
export GITHUB_TOKEN="your_github_token"
export GITLAB_TOKEN="your_gitlab_token"
```

## 📖 Claude Desktop Integration

### Install

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

#### Development Configuration
```json
{
  "mcpServers": {
    "gitscribe": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/gitscribe",
        "run",
        "gitscribe",
        "server"
      ],
      "env": {
        "GITSCRIBE_DEBUG": "false"
      }
    }
  }
}
```

#### Published Server Configuration
```json
{
  "mcpServers": {
    "gitscribe": {
      "command": "uvx",
      "args": ["gitscribe", "server"]
    }
  }
}
```

## 🧪 Development

### Building and Publishing

1. Sync dependencies:
```bash
uv sync
```

2. Build package:
```bash
uv build
```

3. Publish to PyPI:
```bash
uv publish
```

### Debugging

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) for debugging:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/gitscribe run gitscribe server
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=gitscribe

# Run specific tests
uv run pytest tests/test_scraper.py
```

## 📚 Supported Formats

- **Documentation**: Markdown (`.md`), HTML (`.html`), reStructuredText (`.rst`)
- **Code Files**: Python (`.py`), JavaScript (`.js`), TypeScript (`.ts`), Java (`.java`), C++ (`.cpp`), Go (`.go`), Rust (`.rs`)
- **Configuration**: JSON, YAML, TOML
- **Web Content**: Dynamic HTML pages, static sites

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   MCP Server    │───▶│  Web Scraper    │
│ (Code Assistant)│    │   (GitScribe)   │    │ (Beautiful Soup)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   RAG System    │
                       │  - ChromaDB     │
                       │  - Embeddings   │
                       │  - Search       │
                       └─────────────────┘
```

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [ChromaDB](https://www.trychroma.com/) for vector database capabilities
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [Model Context Protocol](https://modelcontextprotocol.io/) for AI assistant integration

---

**GitScribe** - Making documentation accessible to AI assistants, one commit at a time! 🚀