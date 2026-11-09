import streamlit as st
from services.conversation_reader import load_conversations
from services.conversation_parser import parse_conversation, conversation_title, conversation_project
from utils.file_utils import format_timestamp

st.set_page_config(page_title="Mini ChatGPT UI", page_icon="💬", layout="wide")
st.title("💬 Mini ChatGPT UI")
st.caption("A local, read-only viewer for your ChatGPT data export.")

with st.sidebar:
    st.header("Conversation archive")
    uploaded = st.file_uploader("Upload ChatGPT export", type=["json", "zip"])
    if uploaded is None:
        st.info("Upload conversations.json or the ZIP downloaded from ChatGPT.")
        st.markdown("**Export steps:** ChatGPT Settings → Data Controls → Export Data.")
        st.stop()
    try:
        conversations = load_conversations(uploaded.name, uploaded.getvalue())
    except Exception as exc:
        st.error(f"Could not read this export: {exc}")
        st.stop()
    if not conversations:
        st.warning("No conversations found.")
        st.stop()
    st.success(f"Loaded {len(conversations):,} conversations")
    search = st.text_input("Search title or message")
    projects = sorted({conversation_project(c) for c in conversations})
    project = st.selectbox("Project", ["All projects"] + projects)
    filtered = []
    query = search.strip().casefold()
    for conv in conversations:
        if project != "All projects" and conversation_project(conv) != project:
            continue
        if query:
            title_match = query in conversation_title(conv).casefold()
            mapping = conv.get("mapping") or {}
            body = " ".join(str(((n.get("message") or {}).get("content") or {}).get("parts") or "")
                            for n in mapping.values() if isinstance(n, dict)).casefold()
            if not title_match and query not in body:
                continue
        filtered.append(conv)
    st.caption(f"{len(filtered):,} matching conversations")
    if not filtered:
        st.warning("No matching conversations.")
        st.stop()
    labels = [f"{conversation_title(c)} · {format_timestamp(c.get('create_time'))}" for c in filtered]
    selected_index = st.selectbox("Conversation", range(len(filtered)), format_func=lambda i: labels[i])
    selected = filtered[selected_index]

messages = parse_conversation(selected)
st.subheader(conversation_title(selected))
c1, c2, c3 = st.columns(3)
c1.metric("Messages", len(messages))
c2.metric("Project", conversation_project(selected))
c3.metric("Created", format_timestamp(selected.get("create_time")))
st.divider()
if not messages:
    st.info("No displayable messages in this conversation.")
else:
    for message in messages:
        with st.chat_message(message["role"]):
            st.caption("You" if message["role"] == "user" else "ChatGPT")
            st.markdown(message["content"])
            if message.get("timestamp"):
                st.caption(format_timestamp(message["timestamp"]))
st.divider()
st.caption("V1 · Read-only archive viewer · No AI API calls or external data transfer.")
