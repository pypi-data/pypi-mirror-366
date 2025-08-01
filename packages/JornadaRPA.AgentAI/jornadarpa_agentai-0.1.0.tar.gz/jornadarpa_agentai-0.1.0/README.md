\# JornadaRPA.AgentAI



A simple, modular and local AI Agent framework with memory and tool support. Ideal for RPA use cases.



\## Install



```bash

pip install JornadaRPA.AgentAI



BASIC SAMPLE


from JornadaRPA.AgentAI.providers import get\_provider

from JornadaRPA.AgentAI.agent import AgentAI



provider = get\_provider("openai")(api\_key="...", model="gpt-4")

agent = AgentAI(provider)



result = agent.plan\_and\_execute("Hello!")

print(result)



