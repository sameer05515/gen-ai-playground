# GenAI Text Assistant — Groq V3

Beginner Python + Streamlit app with four features: explanation, summarization, writing improvement, and idea generation.

## Setup (Windows / VS Code)

1. Get an API key from https://console.groq.com/keys
2. Open a terminal in this folder.
3. Run:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Edit `.env` and replace `replace_with_your_key` with your Groq key.
5. Start:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the URL shown by Streamlit (typically http://localhost:8501).

## Model and pricing

Default model ID: `openai/gpt-oss-20b`. You can change it in `.env` or the sidebar.
Groq free-tier quotas and model availability can change. Check the Groq Console before use. This project does not require a paid subscription, but does require an API key and internet access. Avoid enabling paid billing if you want to stay at zero cost.

## Troubleshooting

- **401:** API key is invalid or not configured.
- **404 / model error:** Check available model IDs at https://console.groq.com/docs/models and change the sidebar model.
- **429:** Free-tier rate limit reached; wait before retrying.
- **Connection error:** Check internet access.

Never commit or share your `.env` file.
