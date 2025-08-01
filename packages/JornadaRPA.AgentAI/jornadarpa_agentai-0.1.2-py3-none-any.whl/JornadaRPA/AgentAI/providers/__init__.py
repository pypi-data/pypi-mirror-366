from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .mistral_provider import MistralProvider
from .huggingface_provider import HuggingFaceProvider
from .gemini_provider import GeminiProvider

def get_provider(name: str):
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "mistral": MistralProvider,
        "huggingface": HuggingFaceProvider,
        "gemini": GeminiProvider,
    }
    return providers.get(name.lower())