# JornadaRPA.AgentAI

A simple and powerful local AI Agent framework with memory and tool support. Ideal for RPA and automation use cases.

## Installation

```bash
pip install JornadaRPA.AgentAI
```

## Usage

```python
from JornadaRPA.AgentAI.providers import get_provider
from JornadaRPA.AgentAI.agent import AgentAI

provider = get_provider("openai")(api_key="your-key", model="gpt-4")
agent = AgentAI(provider)

response = agent.plan_and_execute("Hello, AI!")
print(response)

agent.clear_memory()
```