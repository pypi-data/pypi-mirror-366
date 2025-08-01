import requests

class MistralProvider:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def run(self, messages, tools=None):
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": messages}
        )
        return response.json()["choices"][0]["message"]["content"]