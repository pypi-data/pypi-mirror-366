import re
def run_tool(input_text): return ", ".join(re.findall(r"\d+", input_text))