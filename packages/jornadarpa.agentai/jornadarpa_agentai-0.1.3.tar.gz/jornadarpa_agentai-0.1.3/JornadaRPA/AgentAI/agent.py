
from .providers import get_provider
from .memory import Memory

class AgentAI:
    def __init__(self, provider):
        self.provider = provider
        self.memory = Memory()

    def plan_and_execute(self, prompt, tools=None):
        messages = self.memory.build_messages(prompt)
        response = self.provider.run(messages, tools)
        self.memory.append("user", prompt)
        self.memory.append("assistant", response)
        return response

    def clear_memory(self):
        self.memory.clear()
