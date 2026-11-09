import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, APIStatusError, RateLimitError

load_dotenv()

st.set_page_config(
    page_title="GenAI Chat Assistant | V4",
    page_icon="🤖",
    layout="centered",
)

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Give clear, accurate answers. Explain technical topics for beginners "
    "with practical examples and code when useful. Remember the conversation "
    "context when answering follow-up questions."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 GenAI Chat Assistant")
st.caption("V4 · Python + Streamlit + Groq · Conversation history")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Groq model ID", value=DEFAULT_MODEL)
    st.caption("Change this if the model is unavailable for your Groq account.")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Messages in this chat: {len(st.session_state.messages)}")
    st.caption("Conversation history is stored in this Streamlit session only.")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.warning("GROQ_API_KEY is missing. Add it to your .env file.")
    st.code("GROQ_API_KEY=your_actual_api_key")
    st.stop()

# Display existing conversation after every Streamlit rerun.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything about Python, Java, GenAI...")

if prompt:
    # Show and store the user's message.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Keep the complete session history as conversational context.
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    api_messages.extend(st.session_state.messages)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = Groq(
                    api_key=api_key,
                    timeout=45.0,
                    max_retries=2,
                )
                completion = client.chat.completions.create(
                    model=model.strip(),
                    messages=api_messages,
                    temperature=0.5,
                    max_tokens=1200,
                )
                answer = completion.choices[0].message.content or "I couldn't generate a response."
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except RateLimitError:
                error = (
                    "Groq rate limit reached. Please wait and try again. "
                    "Check your free-tier limits in the Groq Console."
                )
                st.error(error)
                # Remove the failed user message so it can be retried cleanly.
                st.session_state.messages.pop()

            except APIConnectionError:
                st.error("Could not connect to Groq. Check your internet connection.")
                st.session_state.messages.pop()

            except APIStatusError as exc:
                st.error(f"Groq API error ({exc.status_code}).")
                st.caption("Verify your API key and model ID in the Groq Console.")
                st.code(str(exc))
                st.session_state.messages.pop()

            except Exception as exc:
                st.error("An unexpected error occurred.")
                st.code(str(exc))
                st.session_state.messages.pop()
