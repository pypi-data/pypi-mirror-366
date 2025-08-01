import requests

class OllamaProvider:
    def __init__(self, api_key, model):
        self.model = model

    def run(self, messages, tools=None):
        prompt = messages[-1]["content"]
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": self.model,
            "prompt": prompt
        })
        return response.json()["response"]