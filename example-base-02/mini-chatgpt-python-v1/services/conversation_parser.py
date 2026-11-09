def conversation_title(conversation: dict) -> str:
    return str(conversation.get("title") or "Untitled conversation").strip()


def conversation_project(conversation: dict) -> str:
    value = conversation.get("project") or conversation.get("project_name")
    if isinstance(value, dict):
        value = value.get("name") or value.get("title")
    return str(value or "Unassigned").strip()


def _message_text(message: dict) -> str:
    content = message.get("content") or {}
    parts = content.get("parts") or []
    result = []
    for part in parts:
        if isinstance(part, str):
            result.append(part)
        elif isinstance(part, dict):
            text = part.get("text") or part.get("transcript")
            if text:
                result.append(str(text))
    if not result and content.get("text"):
        result.append(str(content["text"]))
    return "\n\n".join(result).strip()


def _ordered_nodes(mapping: dict, current_node):
    if current_node and current_node in mapping:
        chain, seen, node_id = [], set(), current_node
        while node_id and node_id in mapping and node_id not in seen:
            seen.add(node_id)
            node = mapping[node_id]
            chain.append((node_id, node))
            node_id = node.get("parent")
        chain.reverse()
        return chain

    def sort_key(pair):
        value = ((pair[1].get("message") or {}).get("create_time")) or 0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0
    return sorted([(k, v) for k, v in mapping.items() if isinstance(v, dict)], key=sort_key)


def parse_conversation(conversation: dict) -> list[dict]:
    mapping = conversation.get("mapping") or {}
    if not isinstance(mapping, dict):
        return []
    messages = []
    for _, node in _ordered_nodes(mapping, conversation.get("current_node")):
        message = node.get("message")
        if not isinstance(message, dict):
            continue
        role = (message.get("author") or {}).get("role") or "unknown"
        if role not in ("user", "assistant"):
            continue
        content = _message_text(message)
        if content:
            messages.append({"role": role, "content": content,
                             "timestamp": message.get("create_time"), "message_id": message.get("id")})
    return messages
