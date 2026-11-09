import json
from pathlib import Path
from services.conversation_parser import parse_conversation

sample = json.loads(Path("sample_conversations.json").read_text(encoding="utf-8"))
messages = parse_conversation(sample[0])
assert [m["role"] for m in messages] == ["user", "assistant"]
assert "variables" in messages[1]["content"]
print("Parser smoke test passed.")
