# AI Interview Pro 🤖
AI-powered interview assistant built with Python, Streamlit, and Google Gemini API to explore LLM-powered interview preparation.

### 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- Google GenAI Python SDK (`google-genai`)
- python-dotenv

## ⚙️ Setup Instructions

### 1. Clone the repository

    git clone https://github.com/athul-hue/AI_INTERVIEW_PRO.git
    cd AI_INTERVIEW_PRO

### 2. Create a virtual environment

    python -m venv .venv

### 3. Activate the environment (Windows)

    .venv\Scripts\activate

### 4. Install dependencies

    pip install -r requirements.txt

### 5. Configure environment variables

Create a `.env` file in the project folder:

    GEMINI_API_KEY=your_actual_api_key
    GEMINI_MODEL=gemini-3.1-flash-lite

Replace `your_actual_api_key` with your own API key.
Never upload your real API key to GitHub.

### 6. Run the application

    streamlit run app.py

## 🔐 Security

- Keep API keys private.
- Add `.env` to `.gitignore`.
- Never commit passwords or private credentials.

## 👨‍💻 Developer

**Athul K Koshy**

- [GitHub](https://github.com/athul-hue)
- [LinkedIn](https://www.linkedin.com/in/athul-k-koshy-340bb8325/)
- [Portfolio](https://athulkoshy.netlify.app/)
