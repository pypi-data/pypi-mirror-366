# langchain-qwen3

This package contains the LangChain integration with Qwen3

## Installation

```bash
pip install -U langchain-qwen3
```

## Embeddings

`Qwen3Embeddings` class exposes embeddings from Qwen3.

```python
from langchain_qwen3 import Qwen3Embeddings

embeddings = Qwen3Embeddings()

# Each query must come with a one-sentence instruction that describes the task
task = 'Given a web search query, retrieve relevant passages that answer the query'
query = embeddings.get_detailed_instruct(task, 'Explain gravity')

embeddings.embed_query(query)
```
