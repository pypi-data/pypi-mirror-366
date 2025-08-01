# LangChain Zunno Integration

A LangChain integration for Zunno LLM and Embeddings, providing easy-to-use wrappers for text generation and embeddings.

## Installation

```bash
pip install langchain-zunno
```

## Quick Start

### Text Generation (LLM)

```python
from langchain_zunno import ZunnoLLM

# Create an LLM instance
llm = ZunnoLLM(model_name="mistral:latest")

# Generate text
response = llm.invoke("Hello, how are you?")
print(response)
```

### Embeddings

```python
from langchain_zunno import ZunnoLLMEmbeddings

# Create an embeddings instance
embeddings = ZunnoLLMEmbeddings(model_name="mistral:latest")

# Get embeddings for a single text
embedding = embeddings.embed_query("Hello, how are you?")
print(f"Embedding dimension: {len(embedding)}")

# Get embeddings for multiple texts
texts = ["Hello world", "How are you?", "Good morning"]
embeddings_list = embeddings.embed_documents(texts)
print(f"Number of embeddings: {len(embeddings_list)}")
```

### Async Usage

```python
import asyncio
from langchain_zunno import ZunnoLLM, ZunnoLLMEmbeddings

async def main():
    # Async LLM
    llm = ZunnoLLM(model_name="mistral:latest")
    response = await llm.ainvoke("Hello, how are you?")
    print(response)
    
    # Async embeddings
    embeddings = ZunnoLLMEmbeddings(model_name="mistral:latest")
    embedding = await embeddings.aembed_query("Hello, how are you?")
    print(f"Embedding dimension: {len(embedding)}")

asyncio.run(main())
```

## Factory Functions

For convenience, you can use factory functions to create instances:

```python
from langchain_zunno import create_zunno_llm, create_zunno_embeddings

# Create LLM
llm = create_zunno_llm(
    model_name="mistral:latest",
    temperature=0.7,
    max_tokens=100
)

# Create embeddings
embeddings = create_zunno_embeddings(
    model_name="mistral:latest"
)
```

## Configuration

### LLM Configuration

- `model_name`: The name of the model to use
- `base_url`: API endpoint (default: "http://15.206.124.44/v1/prompt-response")
- `temperature`: Controls randomness in generation (default: 0.7)
- `max_tokens`: Maximum number of tokens to generate (optional)
- `timeout`: Request timeout in seconds (default: 300)

### Embeddings Configuration

- `model_name`: The name of the embedding model to use
- `base_url`: API endpoint (default: "http://15.206.124.44/v1/text-embeddings")
- `timeout`: Request timeout in seconds (default: 300)

## API Endpoints

The package connects to the following Zunno API endpoints:

- **Text Generation**: `http://15.206.124.44/v1/prompt-response`
- **Embeddings**: `http://15.206.124.44/v1/text-embeddings`

## Error Handling

The package includes comprehensive error handling:

```python
try:
    response = llm.invoke("Hello")
except Exception as e:
    print(f"Error: {e}")
```

## Development

### Installation for Development

```bash
git clone https://github.com/zunno/langchain-zunno.git
cd langchain-zunno
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support, please open an issue on GitHub or contact us at support@zunno.ai. 