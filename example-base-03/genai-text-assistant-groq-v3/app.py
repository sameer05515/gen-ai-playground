import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from groq import APIConnectionError, APIStatusError, RateLimitError

load_dotenv()
st.set_page_config(page_title="GenAI Text Assistant | Groq", page_icon="🤖")
st.title("🤖 GenAI Text Assistant")
st.caption("Python + Streamlit + Groq | Free-tier friendly")

TASKS = {
    "Explain a concept": "Explain the following to a beginner, with a short example:",
    "Summarize text": "Summarize the following in concise bullet points:",
    "Improve writing": "Improve the clarity and grammar without changing the meaning:",
    "Generate ideas": "Generate five practical ideas based on the following:",
}

task = st.selectbox("Choose a task", list(TASKS))
user_text = st.text_area("Enter your text or question", height=180)
model = st.sidebar.text_input("Groq model ID", value=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"))
st.sidebar.caption("Free-tier availability and limits may change. Check your Groq console.")

if st.button("Generate", type="primary"):
    if not user_text.strip():
        st.warning("Please enter a question or some text.")
    elif not os.getenv("GROQ_API_KEY"):
        st.error("Missing GROQ_API_KEY. Copy .env.example to .env and add your key.")
    else:
        try:
            client = Groq(api_key=os.environ["GROQ_API_KEY"], timeout=30.0, max_retries=2)
            with st.spinner("Generating..."):
                response = client.chat.completions.create(
                    model=model.strip(),
                    messages=[
                        {"role": "system", "content": "You are a helpful, clear, beginner-friendly assistant."},
                        {"role": "user", "content": f"{TASKS[task]}\\n\\n{user_text}"},
                    ],
                    temperature=0.5,
                    max_tokens=700,
                )
            answer = response.choices[0].message.content
            st.subheader("Response")
            st.markdown(answer or "No text was returned.")
        except RateLimitError:
            st.error("Rate limit reached. Wait and retry, or check free-tier limits in Groq Console.")
        except APIConnectionError:
            st.error("Could not connect to Groq. Check your internet connection.")
        except APIStatusError as exc:
            st.error(f"Groq API error ({exc.status_code}). Verify your model ID and API access.")
            st.code(str(exc))
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
