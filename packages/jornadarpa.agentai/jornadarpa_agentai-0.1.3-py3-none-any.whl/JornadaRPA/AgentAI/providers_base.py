
class ProviderBase:
    def run(self, messages: list, tools=None) -> str:
        raise NotImplementedError("Provider must implement run() method.")
