# 📄 ATS Resume Checker

A Streamlit app that scores a resume for ATS (Applicant Tracking System) compatibility
and suggests concrete improvements, powered by Google's Gemini Flash model.

## Features
- Upload a resume as **PDF** or **DOCX**
- Optional job description for a targeted keyword match
- ATS score out of 100 plus a 6-category breakdown
- Strengths, missing keywords and prioritized improvements
- Download the report as JSON

## Run locally
1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Get a free API key from <https://aistudio.google.com/apikey>.
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Paste your API key in the sidebar (or see below to store it as a secret).

### Optional: store the key locally
Create `.streamlit/secrets.toml` (never commit this file):
```toml
GEMINI_API_KEY = "your-key-here"
```

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub.
2. Go to <https://share.streamlit.io>, sign in with GitHub, click **Create app**.
3. Select the repo, branch `main`, and main file `app.py`.
4. Open **Advanced settings → Secrets** and add: `GEMINI_API_KEY = "your-key-here"`
5. Click **Deploy**.

## Notes
- The default model is `gemini-2.5-flash`; you can change it in the sidebar if Google
  releases a newer Flash model.
- Scanned/image-only PDFs have no extractable text and cannot be scored.
- The score is an AI estimate, not the output of any specific commercial ATS.
- Your resume text is sent to the Gemini API. Don't upload documents you can't share.
