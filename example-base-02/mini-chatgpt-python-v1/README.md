# Mini ChatGPT UI – Python V1

A local, read-only Streamlit application for browsing a ChatGPT data export.

## Features
- Upload `conversations.json` or the ChatGPT export ZIP.
- Browse conversations from the sidebar.
- Search titles and message text.
- Filter by project metadata when present.
- Display the active conversation branch in chronological order.
- Render Markdown, tables, and fenced code blocks.

## Requirements
- Python 3.10+
- pip

## Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501), then upload your JSON or ZIP export.

## Privacy
The app does not call an AI API or send conversation content to a third-party service. Avoid deploying it publicly with private conversation data.

## Notes and limitations
- Project names are not consistently present in ChatGPT exports; missing projects appear as **Unassigned**.
- Images, audio, video, and file attachments are not rendered in V1.
- System, developer, and tool messages are omitted.
- Alternative/regenerated branches are not combined; the selected `current_node` branch is displayed.
- This is an archive viewer, not a live ChatGPT client.
