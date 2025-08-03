from typing import List, Optional, Any

import torch
import torch.nn.functional as F
from langchain_core.embeddings import Embeddings
from torch import Tensor


class Qwen3Embeddings(Embeddings):
    """Qwen3 embedding model integration.

    Setup:
        Install ``langchain-qwen3``

        .. code-block:: bash

            pip install -U langchain-qwen3

    Key init args:
        model: str
            Name of Qwen3 model to use. Defaults to 'Qwen/Qwen3-Embedding-0.6B'.
        max_length: int
            Maximum sequence length for tokenization. Defaults to 8192.
        device: Optional[str]
            Device to run the model on ('cpu', 'cuda:0', etc.). 
            If None, automatically uses CUDA if available, otherwise CPU.
        model_kwargs: Optional[dict[str, Any]]
            Additional arguments to pass to the model and tokenizer.
        use_modelscope: bool
            Whether to use modelscope instead of transformers. Defaults to False.

    Instantiate:
        .. code-block:: python

            from langchain_qwen3 import Qwen3Embeddings

            embed = Qwen3Embeddings()

            # or
            embed = Qwen3Embeddings(
                model='Qwen/Qwen3-Embedding-0.6B',
                max_length=4096,
                device='cuda:0',
                use_modelscope=True
            )

    Embed single text:
        .. code-block:: python

            input_text = 'The meaning of life is 42'
            embeddings = embed.embed_query(input_text)
            print(f"Embedding dimension: {len(embeddings)}")
            # Output: Embedding dimension: 1024

    Embed multiple texts:
        .. code-block:: python

            input_texts = ["Document 1 content", "Document 2 content"]
            embeddings = embed.embed_documents(input_texts)
            print(f"Number of documents: {len(embeddings)}")
            print(f"Embedding dimension: {len(embeddings[0])}")
            # Output: 
            # Number of documents: 2
            # Embedding dimension: 1024

    Using with task instructions:
        .. code-block:: python

            task = 'Given a web search query, retrieve relevant passages that answer the query'
            query = embed.get_detailed_instruct(task, 'Explain gravity')
            embeddings = embed.embed_query(query)

    """

    def __init__(
        self,
        model: str = 'Qwen/Qwen3-Embedding-0.6B',
        max_length: int = 8192,
        device: Optional[str] = None,
        model_kwargs: Optional[dict[str, Any]] = None,
        use_modelscope: bool = False,
    ):
        self.max_length = max_length

        if use_modelscope:
            from modelscope import AutoTokenizer, AutoModel
        else:
            from transformers import AutoTokenizer, AutoModel

        model_kwargs = {} if model_kwargs is None else model_kwargs
        if not device:
            device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

        self.tokenizer = AutoTokenizer.from_pretrained(
            model, padding_side='left', **model_kwargs
        )
        self.model = AutoModel.from_pretrained(model, **model_kwargs).to(
            torch.device(device)
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        # Tokenize the input texts
        batch_dict = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt',
        )
        batch_dict.to(self.model.device)
        with torch.no_grad():
            outputs = self.model(**batch_dict)
            embeddings = self.last_token_pool(
                outputs.last_hidden_state, batch_dict['attention_mask']
            )

            # normalize embeddings
            embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]


    @staticmethod
    def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        left_padding = attention_mask[:, -1].sum() == attention_mask.shape[0]
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[
                torch.arange(batch_size, device=last_hidden_states.device),
                sequence_lengths,
            ]

    @staticmethod
    def get_detailed_instruct(task_description: str, query: str) -> str:
        return f'Instruct: {task_description}\nQuery:{query}'
