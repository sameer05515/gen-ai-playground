import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(page_title="My First GenAI App", page_icon="🤖", layout="centered")
st.title("🤖 My First GenAI Text Assistant")
st.caption("A beginner-friendly GenAI project using Python, Streamlit and Google Gemini.")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY is missing. Add it to your .env file and restart the app.")
    st.code("GEMINI_API_KEY=your_api_key_here")
    st.stop()

client = genai.Client(api_key=api_key)

task = st.selectbox(
    "What would you like the AI to do?",
    ["Explain a concept", "Summarize text", "Improve my writing", "Generate ideas"]
)

user_text = st.text_area(
    "Enter your text or question",
    height=180,
    placeholder="Example: Explain Python functions with a simple example."
)

if st.button("Generate response", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("Please enter some text first.")
    else:
        prompts = {
            "Explain a concept": f"Explain this concept to a beginner. Use simple language and a small example:\n\n{user_text}",
            "Summarize text": f"Summarize the following text into clear bullet points:\n\n{user_text}",
            "Improve my writing": f"Improve the clarity and grammar of this text while preserving its meaning:\n\n{user_text}",
            "Generate ideas": f"Generate 5 practical ideas based on this request. Explain each briefly:\n\n{user_text}",
        }

        with st.spinner("The AI is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompts[task]
                )
                st.subheader("AI response")
                st.markdown(response.text or "The model returned an empty response.")
            except Exception as exc:
                st.error("Something went wrong while calling Gemini.")
                st.caption("Check your API key, internet connection and model availability.")
                st.code(str(exc))

st.divider()
st.caption("Learning tip: Try asking it to explain Java, Spring Boot, React or Python topics.")
