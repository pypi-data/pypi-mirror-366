from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider

def get_provider(name: str, **kwargs):
    if name == "openai":
        return OpenAIProvider(**kwargs)
    elif name == "anthropic":
        return AnthropicProvider(**kwargs)
    raise ValueError(f"Unknown provider: {name}")
