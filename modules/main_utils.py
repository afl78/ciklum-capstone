import os
import sys
import json

class ConsoleLogger:
    """Duplicates stdout stream to both terminal console and a timestamped log file,
    automatically unescaping literal raw \\n sequences in all printed strings."""
    
    def __init__(self, log_filepath):
        self.terminal = sys.stdout
        self.log_file = open(log_filepath, "w", encoding="utf-8")

    def write(self, message):
        if isinstance(message, str) and "\\n" in message:
            message = message.replace("\\n", "\n")
            
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def isatty(self):
        """Delegates tty check to original stdout to fix HuggingFace log styling."""
        return getattr(self.terminal, "isatty", lambda: False)()

    def close(self):
        self.log_file.close()

def load_tasks(config_path="config/tasks.json"):
    """Loads externalized tasks from a JSON config file with fallback protection."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Tasks file not found at '{config_path}'")
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            raise ValueError(f"❌ '{config_path}' is empty. Populate it with valid JSON tasks.")
        return json.loads(content)

def log_agent_execution_stream(result):
    """Parses and formats LangGraph state messages to print tool calls in real time."""
    messages = result.get("messages", [])
    
    print("\n🛠️  [AGENT EXECUTION LOGS & TOOL CALLS]:")
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args")
                print(f"   ➔ ⚙️  [Tool Invoked]: {tool_name}")
                print(f"      📥 [Parameters]: {tool_args}")
        elif msg.type == "tool":
            raw_content = str(msg.content).replace("\\n", "\n")
            preview = raw_content[:120].replace('\n', ' ')
            print(f"   ➔ 🟢 [Tool Response ({msg.name})]: {preview}...")