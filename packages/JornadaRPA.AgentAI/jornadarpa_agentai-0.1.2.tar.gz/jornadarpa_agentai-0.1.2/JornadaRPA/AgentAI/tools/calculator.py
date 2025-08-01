def run_tool(input_text):
    try:
        return f"Result: {eval(input_text, {'__builtins__': {}})}"
    except:
        return "Invalid expression."