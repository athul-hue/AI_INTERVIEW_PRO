import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

st.set_page_config(page_title="AI Interview Bot", page_icon="🤖", layout="centered")

def get_client():
    if not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)

def ask_llm(prompt):
    client = get_client()
    if client is None:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to .env and restart the app.")
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    return response.text.strip()

def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("The AI did not return valid JSON.")
    return json.loads(match.group(0))

def generate_question(role, difficulty, number, previous_questions):
    previous = "\n".join(f"- {q}" for q in previous_questions) if previous_questions else "None"
    prompt = f"""
You are an expert technical interviewer.

Job role: {role}
Difficulty: {difficulty}
Question number: {number}

Generate ONE interview question suitable for this role.
Do not repeat any previous question.

Previous questions:
{previous}

Return ONLY this JSON:
{{
  "question": "the interview question",
  "topic": "short topic name"
}}

The question should be practical and suitable for a student/fresher interview.
"""
    data = extract_json(ask_llm(prompt))
    return data["question"], data.get("topic", "General")

def evaluate_answer(role, question, answer):
    prompt = f"""
You are an expert technical interviewer evaluating a fresher.

Job role: {role}

Interview question:
{question}

Candidate answer:
{answer}

Evaluate correctness, relevance, clarity, and technical understanding.

Return ONLY this JSON:
{{
  "score": 0,
  "feedback": "2-4 sentences explaining what was good and what could improve.",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"]
}}

Score from 0 to 10.
"""
    return extract_json(ask_llm(prompt))

def final_report(role, evaluations):
    history = "\n".join(
        f"Question {i+1}: {x['score']}/10 - {x['feedback']}"
        for i, x in enumerate(evaluations)
    )
    prompt = f"""
You are an interview coach.

Job role: {role}
Interview evaluation history:
{history}

Return ONLY this JSON:
{{
  "overall_score": 0,
  "summary": "2-4 sentence overall assessment",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "areas_to_improve": ["area 1", "area 2", "area 3"],
  "recommendation": "one short recommendation"
}}

overall_score must be from 0 to 10.
"""
    return extract_json(ask_llm(prompt))

def reset():
    for key in ["started","finished","question","topic","question_number",
                "questions","evaluations","current_evaluation","final_report"]:
        st.session_state.pop(key, None)

defaults = {
    "started": False, "finished": False, "question": "", "topic": "",
    "question_number": 1, "questions": [], "evaluations": [],
    "current_evaluation": None, "final_report": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<style>
.main-title{text-align:center;font-size:42px;font-weight:700;margin-bottom:4px}
.subtitle{text-align:center;color:#777;margin-bottom:25px}
.score{font-size:32px;font-weight:700}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 AI Interview Bot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Practice technical interviews with a Gemini AI interviewer</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Interview Settings")
    role = st.selectbox("Select Job Role", [
        "AI/ML Engineer", "Data Scientist", "Python Developer",
        "Data Analyst", "Generative AI Engineer", "Software Developer"
    ])
    difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"], index=1)
    total_questions = st.slider("Number of Questions", 3, 10, 5)

    if st.button("🔄 Reset Interview", use_container_width=True):
        reset()
        st.rerun()

    st.divider()
    st.caption("Tech Stack")
    st.caption("Python • Streamlit • Gemini API • Google GenAI SDK • python-dotenv")

if not GEMINI_API_KEY:
    st.warning("Gemini API key not configured. Add GEMINI_API_KEY to your .env file.")

if not st.session_state.started and not st.session_state.finished:
    st.subheader("Start a Practice Interview")
    st.write(f"You will answer **{total_questions} questions** for the **{role}** role at **{difficulty}** difficulty.")
    st.info("Gemini will generate questions, evaluate answers, give scores and feedback, and generate the next question.")

    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        if not GEMINI_API_KEY:
            st.error("Please configure your Gemini API key first.")
        else:
            with st.spinner("Generating your first interview question..."):
                try:
                    q, topic = generate_question(role, difficulty, 1, [])
                    st.session_state.started = True
                    st.session_state.question = q
                    st.session_state.topic = topic
                    st.session_state.question_number = 1
                    st.session_state.questions = [q]
                    st.session_state.evaluations = []
                    st.session_state.current_evaluation = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not start the interview: {e}")

elif st.session_state.started and not st.session_state.finished:
    number = st.session_state.question_number
    st.progress((number - 1) / total_questions, text=f"Question {number} of {total_questions}")
    st.caption(f"Topic: {st.session_state.topic}")
    st.subheader(st.session_state.question)

    answer = st.text_area("Your Answer", height=180, placeholder="Type your interview answer here...", key=f"answer_{number}")

    if st.button("📤 Submit Answer", type="primary", use_container_width=True):
        if not answer.strip():
            st.error("Please write an answer before submitting.")
        else:
            with st.spinner("Gemini is evaluating your answer..."):
                try:
                    evaluation = evaluate_answer(role, st.session_state.question, answer)
                    st.session_state.current_evaluation = evaluation
                    st.session_state.evaluations.append(evaluation)
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not evaluate the answer: {e}")

    evaluation = st.session_state.current_evaluation
    if evaluation:
        st.divider()
        st.subheader("📊 AI Evaluation")
        score = float(evaluation.get("score", 0))
        st.markdown(f'<div class="score">Score: {score:.1f}/10</div>', unsafe_allow_html=True)
        st.write(evaluation.get("feedback", ""))

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Strengths**")
            for item in evaluation.get("strengths", []):
                st.write(f"• {item}")
        with c2:
            st.markdown("**Improve**")
            for item in evaluation.get("improvements", []):
                st.write(f"• {item}")

        if number < total_questions:
            if st.button("➡️ Next Question", type="primary", use_container_width=True):
                with st.spinner("Generating the next question..."):
                    try:
                        q, topic = generate_question(role, difficulty, number + 1, st.session_state.questions)
                        st.session_state.question_number += 1
                        st.session_state.question = q
                        st.session_state.topic = topic
                        st.session_state.questions.append(q)
                        st.session_state.current_evaluation = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not generate the next question: {e}")
        else:
            if st.button("🏁 Finish Interview", type="primary", use_container_width=True):
                with st.spinner("Preparing your final report..."):
                    try:
                        report = final_report(role, st.session_state.evaluations)
                        st.session_state.final_report = report
                        st.session_state.started = False
                        st.session_state.finished = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not generate the final report: {e}")

elif st.session_state.finished:
    st.balloons()
    st.subheader("🎉 Interview Completed")
    report = st.session_state.final_report or {}
    overall = float(report.get("overall_score", 0))
    st.markdown(f'<div class="score">Overall Score: {overall:.1f}/10</div>', unsafe_allow_html=True)
    st.write(report.get("summary", ""))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 💪 Strengths")
        for item in report.get("strengths", []):
            st.write(f"• {item}")
    with c2:
        st.markdown("### 📈 Areas to Improve")
        for item in report.get("areas_to_improve", []):
            st.write(f"• {item}")

    st.info(f"**Recommendation:** {report.get('recommendation', 'Keep practicing!')}")
    st.divider()
    st.markdown("### Question-by-Question Scores")
    for i, evaluation in enumerate(st.session_state.evaluations, 1):
        st.write(f"**Question {i}: {float(evaluation.get('score', 0)):.1f}/10** — {evaluation.get('feedback','')}")

    if st.button("🔁 Start New Interview", type="primary", use_container_width=True):
        reset()
        st.rerun()
