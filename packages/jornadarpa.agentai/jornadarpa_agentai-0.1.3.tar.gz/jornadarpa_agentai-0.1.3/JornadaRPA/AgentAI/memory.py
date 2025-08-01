
class Memory:
    def __init__(self):
        self.messages = []

    def append(self, role, content):
        self.messages.append({"role": role, "content": content})

    def clear(self):
        self.messages = []

    def build_messages(self, new_prompt):
        return self.messages + [{"role": "user", "content": new_prompt}]
