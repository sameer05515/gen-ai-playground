# My First GenAI Text Assistant

A small beginner project that demonstrates how a Python application sends a prompt to a Generative AI model and displays the response.

## Features

- Explain a concept
- Summarize text
- Improve writing
- Generate ideas

## Tech stack

- Python
- Streamlit (web UI)
- Google GenAI Python SDK
- Gemini model (`gemini-3.8-flash`)

## 1. Requirements

- Python 3.10+
- Internet connection
- A Gemini API key

Create an API key in Google AI Studio: https://aistudio.google.com/app/apikey

## 2. Setup on Windows

Open PowerShell in this project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, run this command for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Configure the API key

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder:

```env
GEMINI_API_KEY=your_actual_api_key
```

Never commit or share your `.env` file.

## 4. Run

```powershell
streamlit run app.py
```

Streamlit will open the app in your browser (usually http://localhost:8501).

## 5. Try these prompts

- Explain Python lists with 3 examples.
- Explain the difference between Java HashMap and ConcurrentHashMap.
- Summarize this paragraph: [paste a paragraph].
- Generate 5 beginner Python project ideas.

## What you will learn

1. How a Python UI is built with Streamlit.
2. What an API key is and why it must be kept secret.
3. How a prompt is sent to a GenAI model.
4. How the model response is displayed in an application.
5. How to handle API errors.

## Basic flow

```text
User input
   |
   v
Streamlit app (app.py)
   |
   v
Prompt construction
   |
   v
Gemini API
   |
   v
Generated response
   |
   v
Display in browser
```

## Important

Model names and API availability can change. This project currently uses `gemini-3.8-flash`. If Google changes model availability for your API key, check the models enabled in Google AI Studio and update the `model` value in `app.py`.
