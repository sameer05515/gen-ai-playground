from datetime import datetime, timezone


def format_timestamp(value) -> str:
    if value is None:
        return "—"
    try:
        dt = datetime.fromtimestamp(float(value), tz=timezone.utc).astimezone()
        return dt.strftime("%d %b %Y, %I:%M %p")
    except (TypeError, ValueError, OverflowError, OSError):
        return "—"
