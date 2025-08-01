import requests

class HuggingFaceProvider:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def run(self, messages, tools=None):
        prompt = messages[-1]["content"]
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.model}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"inputs": prompt}
        )
        return response.json()[0]["generated_text"]