from openai import OpenAI
from ..providers_base import ProviderBase

class OpenAIProvider(ProviderBase):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)  

    def run(self, messages, tools=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools or []
        )
        return response.choices[0].message.content
