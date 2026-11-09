# GenAI Chat Assistant — V4

A beginner-friendly ChatGPT-style conversational app using Python, Streamlit and Groq.

## Features

- Chat-style interface
- Conversation history during the current Streamlit session
- Follow-up questions with previous messages as context
- Clear conversation button
- Configurable Groq model ID
- Basic handling for rate limits, connection failures and API errors

## Requirements

- Python 3.10+
- Internet connection
- Groq API key

Create an API key at https://console.groq.com/keys

## Setup on Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your key:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Run:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually http://localhost:8501.

## How conversation memory works

Streamlit reruns the script after each interaction. `st.session_state.messages` preserves the conversation for the current browser session. The app sends the system prompt and conversation messages to Groq for each new turn, allowing follow-up questions.

This is session memory, not permanent database storage. Refreshing/ending the session may clear it.

## Troubleshooting

- **401:** Check that `GROQ_API_KEY` is correct.
- **404 / model error:** Confirm the model ID is currently available to your account. You can edit it in the sidebar or `.env`.
- **429:** Wait and retry after the free-tier rate limit resets.
- **Connection error:** Check your internet connection.

Groq free-tier quotas and model availability can change. You do not need to enable paid billing to run the app within an available free tier. Never commit or share `.env`.
