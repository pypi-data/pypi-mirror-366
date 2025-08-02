import os
from typing import Optional

try:
    from litellm import embedding
except ImportError:
    raise ImportError("Please install litellm: pip install litellm")

from mem0.configs.embeddings.base import BaseEmbedderConfig
from mem0.embeddings.base import EmbeddingBase


class LiteLLMEmbedding(EmbeddingBase):
    def __init__(self, config: Optional[BaseEmbedderConfig] = None):
        super().__init__(config)

        self.config.model = self.config.model or "text-embedding-3-small"
        self.config.embedding_dims = self.config.embedding_dims

        # Get API key from config or environment
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        # Set up any additional environment variables for LiteLLM
        if hasattr(self.config, "base_url") and self.config.base_url:
            os.environ["OPENAI_API_BASE"] = self.config.base_url

    def embed(self, text: str):
        """
        Get the embedding for the given text using LiteLLM.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """
        try:
            response = embedding(model=self.config.model, input=[text])
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Error generating embedding with LiteLLM: {str(e)}")
