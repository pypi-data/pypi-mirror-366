
import anthropic
from ..providers_base import ProviderBase

class AnthropicProvider(ProviderBase):
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def run(self, messages, tools=None):
        user_msg = [m["content"] for m in messages if m["role"] == "user"][-1]
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=1000
        )
        return response.content[0].text
