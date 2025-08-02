# LitAI

AI-powered literature review assistant that helps researchers find papers, extract key insights, and synthesize findings with proper citations.

## Overview

LitAI is a command-line tool that streamlines academic literature review by:
- Finding relevant papers through natural language search
- Extracting key claims and evidence from PDFs
- Synthesizing multiple papers to answer research questions
- Managing citations in BibTeX format

## Features

### Paper Discovery
- Search academic papers using natural language queries
- Powered by Semantic Scholar API
- View abstracts and metadata before adding to library

### Paper Management
- Build a local library of research papers
- Automatic PDF download from ArXiv
- Duplicate detection and organized storage

### AI-Powered Extraction
- Extract key claims with supporting evidence
- Automatic section references and quotes
- Cached results for instant access

### Literature Synthesis
- Generate comprehensive literature reviews
- Answer specific research questions across multiple papers
- Proper inline citations (Author et al., Year)
- Export-ready markdown format

### Natural Language Interface
- Chat-based interaction for complex queries
- Context-aware conversations about your research
- Multi-paper analysis and comparison

## Installation

### Prerequisites
- Python 3.11 or higher
- API key for OpenAI or Anthropic

### Install with pip
```bash
pip install litai
```

### Install from source
```bash
git clone https://github.com/yourusername/litai.git
cd litai
uv sync  # or pip install -e .
```

## Configuration

Set your API key as an environment variable:

```bash
# For OpenAI
export OPENAI_API_KEY=sk-...

# For Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

Launch the interactive interface:
```bash
litai
```

### Basic Commands

```bash
# Search for papers
> /find attention mechanisms for computer vision

# Add papers to your library (by search result number)
> /add 1 3 5

# List papers in your library
> /list

# Read and extract key points from a paper
> /read 1

# Generate BibTeX citation
> /cite 1

# Synthesize multiple papers
> /synthesize Compare transformer and CNN architectures

# Natural language queries
> What are the main advantages of vision transformers over CNNs?

# Clear the screen
> /clear

# Remove papers from library
> /remove 2
```

### Advanced Usage

```bash
# Multi-paper synthesis with specific papers
> /synthesize --papers 1,3,5 How do different attention mechanisms impact performance?

# Extract key points from multiple papers at once
> /read 1 3 5

# Natural conversation mode
> Tell me about the evolution of attention mechanisms in deep learning
> Focus specifically on computer vision applications
> What papers should I read to understand this topic?
```

## Example Use Cases

### 1. Literature Review for Research Paper
*[To be added by maintainer]*

### 2. Quick Overview of a New Field
*[To be added by maintainer]*

### 3. Finding Contradictions in Literature
*[To be added by maintainer]*

### 4. Building a Reading List
*[To be added by maintainer]*

### 5. Understanding Paper Relationships
*[To be added by maintainer]*

## Data Storage

LitAI stores all data locally in `~/.litai/`:
- `litai.db` - SQLite database with paper metadata and extractions
- `pdfs/` - Downloaded PDF files
- `logs/` - Application logs for debugging

## Development

### Project Structure
```
litai/
├── src/litai/
│   ├── cli.py          # Command-line interface
│   ├── database.py     # Data persistence layer
│   ├── llm.py          # LLM client (OpenAI/Anthropic)
│   ├── papers.py       # Paper search and management
│   ├── pdf.py          # PDF processing
│   ├── synthesis.py    # Literature synthesis
│   └── tools.py        # Extraction tools
├── tests/              # Test suite
├── docs/               # Documentation
└── pyproject.toml      # Project configuration
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=litai

# Run specific test file
pytest tests/test_papers.py
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Update CHANGELOG.md
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Roadmap

- TBD

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Built with [Semantic Scholar API](https://www.semanticscholar.org/product/api)
- Powered by OpenAI/Anthropic language models
- Beautiful CLI with Rich and Click

## Support

- Report issues: [GitHub Issues](https://github.com/harmonbhasin/litai/issues)
- Documentation: [docs/](docs/)
- Logs for debugging: `~/.litai/logs/litai.log`

---

*LitAI - Making literature review as easy as having a conversation*
