# langchain-qwen3

This package contains the LangChain integration with Qwen3

## Installation

```bash
pip install -U langchain-qwen3
```

And you should configure credentials by setting the following environment variables:

* TODO: fill this out

## Chat Models

`ChatQwen3` class exposes chat models from Qwen3.

```python
from langchain_qwen3 import ChatQwen3

llm = ChatQwen3()
llm.invoke("Sing a ballad of LangChain.")
```

## Embeddings

`Qwen3Embeddings` class exposes embeddings from Qwen3.

```python
from langchain_qwen3 import Qwen3Embeddings

embeddings = Qwen3Embeddings()
embeddings.embed_query("What is the meaning of life?")
```

## LLMs
`Qwen3LLM` class exposes LLMs from Qwen3.

```python
from langchain_qwen3 import Qwen3LLM

llm = Qwen3LLM()
llm.invoke("The meaning of life is")
```
