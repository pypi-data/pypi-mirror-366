import google.generativeai as genai

class GeminiProvider:
    def __init__(self, api_key, model):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def run(self, messages, tools=None):
        chat = self.model.start_chat()
        for msg in messages:
            if msg["role"] == "user":
                response = chat.send_message(msg["content"])
        return response.text