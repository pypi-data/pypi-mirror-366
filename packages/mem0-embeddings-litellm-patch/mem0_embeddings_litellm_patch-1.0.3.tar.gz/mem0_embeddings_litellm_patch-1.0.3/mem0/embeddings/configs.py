from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class EmbedderConfig(BaseModel):
    provider: str = Field(
        description="Provider of the embedding model (e.g., 'ollama', 'openai')",
        default="openai",
    )
    config: Optional[dict] = Field(description="Configuration for the specific embedding model", default={})

    @field_validator("config")
    @classmethod
    def validate_config(cls, v, info: ValidationInfo):
        provider = info.data.get("provider")
        if provider in [
            "openai",
            "ollama",
            "huggingface",
            "azure_openai",
            "gemini",
            "vertexai",
            "together",
            "lmstudio",
            "langchain",
            "aws_bedrock",
            "voyageai",
            "litellm"  # Added litellm support
        ]:
            return v
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")


# Export for compatibility
__all__ = ['EmbedderConfig']
