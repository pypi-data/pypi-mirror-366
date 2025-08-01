# JornadaRPA.AgentAI

Agent AI abstraction layer for RPA bots using providers like OpenAI, Anthropic.

## Installation

```bash
pip install JornadaRPA.AgentAI[all]
```

## Usage

```python
from JornadaRPA.AgentAI.providers import get_provider

provider = get_provider("openai", api_key="sk-...", model="gpt-4")
response = provider.run("Hello, world!")
print(response)
```
