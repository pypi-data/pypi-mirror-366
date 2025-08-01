import json
import os

class Memory:
    def __init__(self, path="agent_memory.json"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f)
        self._load()

    def _load(self):
        with open(self.path, "r") as f:
            self.history = json.load(f)

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.history, f, indent=2)

    def add(self, role, content):
        self.history.append({"role": role, "content": content})
        self._save()

    def get_context(self, last_n=6):
        return self.history[-last_n:]

    def clear(self):
        self.history = []
        self._save()