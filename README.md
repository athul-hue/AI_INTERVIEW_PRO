# AI Interview Bot — Gemini Version

A working LLM application for the LLM Application Challenge.

## Tech stack
- Python
- Streamlit
- Gemini API
- Google GenAI Python SDK (`google-genai`)
- python-dotenv

## Setup
```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create `.env`:
```text
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

Run:
```bash
.venv\Scripts\python.exe -m streamlit run app.py
```
