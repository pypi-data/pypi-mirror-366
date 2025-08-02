from typing import Optional, Literal
from litellm import embedding
from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.embeddings.base import EmbeddingBase


class LiteLLMEmbedding(EmbeddingBase):
    def __init__(self, config: Optional[BaseEmbedderConfig] = None):
        super().__init__(config)
        self.config.api_key = self.config.api_key
        self.config.model = self.config.model
        self.config.embedding_dims = self.config.embedding_dims or None

    def embed(
        self,
        text: str,
        memory_action: Optional[Literal["add", "search", "update"]] = None,
    ):
        """
        Get the embedding for the given text using LiteLLM.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """


        try:
            response = embedding(
                model=self.config.model,
                input=[text],
                dimensions=self.config.embedding_dims,
                api_key=self.config.api_key
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            print(self.config.api_key, flush=True)
            raise RuntimeError(f"Error generating embedding with LiteLLM: {str(e)}")

