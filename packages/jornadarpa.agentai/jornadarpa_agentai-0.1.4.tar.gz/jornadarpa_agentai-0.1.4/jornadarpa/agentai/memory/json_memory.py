import json
import os

class JSONMemory:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            self.clear()

    def add_message(self, message):
        data = self.get_messages()
        data.append(message)
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_messages(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, 'r') as f:
            return json.load(f)

    def clear(self):
        with open(self.path, 'w') as f:
            json.dump([], f)