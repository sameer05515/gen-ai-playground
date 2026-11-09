import io
import json
import zipfile


def _extract_conversations(payload):
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("conversations", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        if "mapping" in payload:
            return [payload]
    raise ValueError("Unsupported JSON format; expected a ChatGPT conversations export.")


def load_conversations(filename: str, content: bytes):
    if filename.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            matches = [n for n in archive.namelist()
                       if n.lower().endswith("conversations.json") and not n.startswith("__MACOSX/")]
            if not matches:
                raise ValueError("ZIP does not contain conversations.json.")
            matches.sort(key=lambda n: ("/" in n.strip("/"), len(n)))
            raw = archive.read(matches[0])
    else:
        raw = content
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid JSON file: {exc}") from exc
    return _extract_conversations(payload)
