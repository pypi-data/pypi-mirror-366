from JornadaRPA.AgentAI.memory import Memory
from JornadaRPA.AgentAI.tools import TOOLS

class AgentAI:
    def __init__(self, provider):
        self.provider = provider
        self.memory = Memory()

    def plan_and_execute(self, prompt: str) -> str:
        if prompt.strip().lower() == "!reset":
            self.clear_memory()
            return "Memory cleared."

        self.memory.add("user", prompt)
        messages = self.memory.get_context() + [{
            "role": "system",
            "content": (
                "You are a smart assistant with access to tools: "
                + ", ".join(TOOLS.keys()) + ". "
                "Use format: tool:<tool_name>:<input> to request a tool."
            )
        }]

        output = self.provider.chat(messages)
        self.memory.add("assistant", output)

        if output.startswith("tool:"):
            try:
                _, tool_name, tool_input = output.split(":", 2)
                tool_func = TOOLS.get(tool_name.strip())
                if not tool_func:
                    return f"Unknown tool: {tool_name}"
                result = tool_func(tool_input.strip())
                self.memory.add("tool", result)
                return self.plan_and_execute(f"The result was: {result}")
            except Exception as e:
                return f"Tool execution failed: {str(e)}"

        return output

    def clear_memory(self):
        self.memory.clear()