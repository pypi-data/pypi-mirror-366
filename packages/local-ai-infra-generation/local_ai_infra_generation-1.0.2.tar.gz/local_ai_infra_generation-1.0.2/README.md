# local-AI-infra-generation

**local-AI-infra-generation** leverages local Large Language Models (LLMs) to analyze code repositories and automatically generate infrastructure files such as Dockerfiles and docker-compose.yml. All processing is performed locally, ensuring privacy and control over your codebase.

---

## Features

- **Codebase Embedding:** Index and embed your codebase for semantic search and retrieval.
- **Natural Language Q&A:** Ask questions about your codebase and receive context-aware answers.
- **Automated Infrastructure Generation:** Generate Dockerfiles and docker-compose.yml files tailored to your project.
- **Multi-language Support:** Works with Python, JavaScript, TypeScript, and Go projects.

---

## Getting Started

### 1. Prerequisites

- **Python 3.11+**  
  Ensure you have Python 3.11 or higher installed.  
  _Check with:_  
  ```sh
  python --version
  ```

- **[Ollama](https://ollama.com/download)**  
  Download and install Ollama for local LLM inference.

- **C/C++ Build Tools**  
  Required for building [tree-sitter-languages](https://pypi.org/project/tree-sitter-languages/).

- **Git** (optional, for cloning repositories)

### 2. Installation

#### a. Clone the Repository

```sh
git clone https://github.com/yourusername/local-AI-infra-generation.git
cd local-AI-infra-generation
```

#### b. Create a Virtual Environment

```sh
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### c. Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management, but you can use pip as well.

**With uv:**
```sh
uv pip install -r requirements.txt
uv pip install -e .
```

**Or with pip:**
```sh
pip install -r requirements.txt
pip install -e .
```

Alternatively, install via [pyproject.toml](pyproject.toml):

```sh
pip install .
```

---

## Usage

### 1. Start Ollama

Make sure the Ollama server is running:

```sh
ollama serve
```

### 2. Run the CLI

```sh
uv run python -m src.main --help  
```

#### Common Commands

- **Embed a Project:**
  ```sh
  uv run python -m src.main embed /path/to/your/project
  uv run python -m src.main embed ../PlotTwister
  ```

- **Ask a Question:**
  ```sh
  uv run python -m src.main ask "How does authentication work?" --project your_project_name
  uv run python -m src.main ask "what does the main.py do" --project "PlotTwister"
  ```

- **List Embedded Projects:**
  ```sh
  uv run python -m src.main list
  ```

- **Generate Dockerfile:**
  ```sh
  uv run python -m src.main generate-docker --project your_project_name
  ```
### generate full infra for a multi-service repo
  ```sh
  uv run python -m src.main generate-infra /path/to/repo --output infra
  ```
### generate just the Dockerfile for a single service folder
  ```sh
  uv run python -m src.main generate-docker /path/to/repo/service
  ```
- **Generate docker-compose.yml:**
  ```sh
  uv run python -m src.main generate-compose --project your_project_name
  ```

---

## Configuration

Edit [`src/config.yaml`](src/config.yaml) to customize:

- Model names and versions
- Supported languages and file extensions
- ChromaDB storage directory
- Ollama server URL

---

## Dependencies

Key packages (see [pyproject.toml](pyproject.toml) for full list):

- [chromadb](https://pypi.org/project/chromadb/)
- [langchain](https://pypi.org/project/langchain/)
- [langchain-community](https://pypi.org/project/langchain-community/)
- [pyyaml](https://pypi.org/project/pyyaml/)
- [requests](https://pypi.org/project/requests/)
- [tqdm](https://pypi.org/project/tqdm/)
- [tree-sitter-languages](https://pypi.org/project/tree-sitter-languages/)
- [typing-extensions](https://pypi.org/project/typing-extensions/)

---

## Development

- All source code is in [`src/`](src/).
- Prompt templates are in [`prompt/`](prompt/).
- Data and ChromaDB indexes are stored in [`data/`](data/).

### Running Tests

_TODO: Add unit tests and instructions for running them._

---

check db from chromadb: 

uv run python -m src.chroma_manager --db_dir data/chroma_index --list

uv run python -m src.chroma_manager --db_dir data/chroma_index --preview PlotTwister

## Troubleshooting

- **Ollama not found:**  
  Ensure Ollama is installed and available in your PATH.

- **tree-sitter language .so files missing:**  
  If you encounter errors about missing `.so` files, ensure [tree-sitter-languages](https://pypi.org/project/tree-sitter-languages/) is installed and built correctly.

- **Model download issues:**  
  The first run will download required models. Ensure you have a stable internet connection.

---

## TODO

- [ ] Add comprehensive unit and integration tests.
- [ ] Improve error handling and user feedback.
- [ ] Add support for more programming languages (e.g., Java, Rust).
- [ ] Enhance prompt templates for better infrastructure generation.
- [ ] Add web or GUI interface.
- [ ] Document API for programmatic usage.
- [ ] Support for private model registries and custom LLMs.
- [ ] Optimize embedding and retrieval for large codebases.
- [ ] Add CI/CD pipeline for automated testing and deployment.
- [ ] Generate terraforms artifacts.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

---

## Acknowledgements

- [Ollama](https://ollama.com/)
- [LangChain](https://www.langchain.com/)
- [ChromaDB](https://www.trychroma.com/)
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/)

---

## Contact

For questions or contributions, please open an issue or pull request on [GitHub](https://github.com/yourusername/local-AI-infra-generation).