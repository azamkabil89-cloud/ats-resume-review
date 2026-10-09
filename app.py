import io
import json
import os

import streamlit as st
from docx import Document
from google import genai
from google.genai import types
from pypdf import PdfReader

MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(page_title="ATS Resume Checker", page_icon="📄", layout="centered")


def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")


def extract_text(uploaded_file):
    data = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    return ""


def build_prompt(resume_text, job_description):
    jd = job_description.strip() or "No job description provided. Evaluate for general ATS readiness."
    return f"""You are an expert ATS (Applicant Tracking System) and senior recruiter.
Analyze the resume below and return ONLY valid JSON with this exact structure:
{{
  "ats_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "missing_keywords": ["..."],
  "improvements": ["<specific, actionable suggestion>"],
  "section_scores": {{
    "formatting": <0-100>,
    "keywords": <0-100>,
    "experience": <0-100>,
    "skills": <0-100>,
    "education": <0-100>
  }}
}}

JOB DESCRIPTION:
{jd}

RESUME:
{resume_text}
"""


def analyze_resume(api_key, resume_text, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=build_prompt(resume_text, job_description),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    text = (response.text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text)


def show_list(title, items):
    st.subheader(title)
    if not items:
        st.write("None")
    for item in items:
        st.markdown(f"- {item}")


# ---------------- UI ----------------
st.title("📄 ATS Resume Checker")
st.caption("Upload your resume to get an ATS score and improvement tips (powered by Gemini Flash).")

api_key = get_api_key()
if not api_key:
    api_key = st.text_input("Enter your Gemini API key", type="password")

uploaded = st.file_uploader("Upload resume (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"])
job_desc = st.text_area("Job description (optional, gives a more accurate score)", height=150)

if st.button("Analyze Resume", type="primary"):
    if not api_key:
        st.error("Please provide a Gemini API key.")
    elif uploaded is None:
        st.error("Please upload a resume first.")
    else:
        try:
            resume_text = extract_text(uploaded)
        except Exception as e:
            st.error(f"Could not read the file: {e}")
            st.stop()

        if len(resume_text.strip()) < 50:
            st.error("Could not extract enough text. If your PDF is a scanned image, upload a text-based PDF or DOCX.")
            st.stop()

        with st.spinner("Analyzing your resume..."):
            try:
                result = analyze_resume(api_key, resume_text, job_desc)
            except json.JSONDecodeError:
                st.error("The AI returned an unexpected response. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"Gemini API error: {e}")
                st.stop()

        score = max(0, min(100, int(result.get("ats_score", 0))))
        st.metric("ATS Score", f"{score} / 100")
        st.progress(score / 100)
        if score >= 80:
            st.success("Excellent! Your resume is highly ATS-friendly.")
        elif score >= 60:
            st.warning("Good, but there is room for improvement.")
        else:
            st.error("Needs significant improvement to pass ATS filters.")

        st.write(result.get("summary", ""))

        sections = result.get("section_scores", {})
        if sections:
            st.subheader("Section Scores")
            cols = st.columns(len(sections))
            for col, (name, val) in zip(cols, sections.items()):
                col.metric(name.capitalize(), val)

        show_list("✅ Strengths", result.get("strengths", []))
        show_list("⚠️ Weaknesses", result.get("weaknesses", []))
        show_list("🔑 Missing Keywords", result.get("missing_keywords", []))
        show_list("🛠️ Improvements", result.get("improvements", []))
