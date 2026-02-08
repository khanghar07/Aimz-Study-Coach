import os
import json
import requests
from typing import Dict, Any, List


def _model_name():
    # Default to a Gemini 3 model to align with hackathon requirements.
    return os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")


def _extract_json(text: str):
    if not text:
        return None
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return None


def analyze_study_material(
    api_key: str,
    goal: str,
    level: str,
    time_budget: str,
    parts: List[Dict[str, Any]],
    stats: Dict[str, Any],
) -> Dict[str, Any]:
    model = _model_name()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    prompt = f"""
You are a multimodal study coach.

Student goal: {goal}
Student level: {level}
Time budget: {time_budget}
Input stats: {stats}

Tasks:
1) Extract key concepts and definitions.
2) Identify confusing or weak areas a student might have.
3) Create a focused study plan with timeboxed steps.
4) Generate 8 flashcards (Q/A).
5) Generate a 6-question quiz with answers and short explanations.
6) Weak-Spot Radar: 3 diagnostic questions + predicted weak topics.
7) Exam Day Simulator: a timed mock exam outline (sections + minutes).
8) Mistake Library: common pitfalls and misconceptions.
9) Socratic Mode: 5 guiding questions to lead the learner.
10) Rewrite Notes: clean bullet notes + short outline.
11) Memory Hooks: mnemonics or memory cues.
12) Code Debug Coach: if code is present, list likely bugs and fixes.
13) Spaced Review Pack: 7-day review schedule.

Return JSON ONLY with this schema:
{{
  "summary": "...",
  "key_concepts": ["..."],
  "confusion_points": ["..."],
  "study_plan": [
    {{"step": "...", "time": "10 min", "goal": "..."}}
  ],
  "flashcards": [
    {{"q": "...", "a": "..."}}
  ],
  "quiz": [
    {{"q": "...", "a": "...", "explanation": "..."}}
  ],
  "next_actions": ["..."],
  "weak_spot_radar": {{
    "questions": ["..."],
    "predicted_weak_topics": ["..."]
  }},
  "exam_simulator": {{
    "sections": [
      {{"name":"...", "minutes":10, "description":"..."}}
    ]
  }},
  "mistake_library": ["..."],
  "socratic_mode": ["..."],
  "rewritten_notes": {{
    "bullets": ["..."],
    "outline": ["..."]
  }},
  "memory_hooks": ["..."],
  "code_debug_coach": [
    {{"issue":"...", "why":"...", "fix":"..."}}
  ],
  "spaced_review_pack": [
    {{"day":"Day 1", "focus":"..."}}
  ]
}}
"""

    contents = [{"parts": [{"text": prompt}]}]
    contents[0]["parts"].extend(parts)

    payload = {"contents": contents}
    r = requests.post(url, json=payload, timeout=60)
    data = r.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = _extract_json(text)
        return parsed if parsed is not None else {"error": "Model response parse failed", "raw": data}
    except Exception:
        return {"error": "Model response parse failed", "raw": data}


def answer_question(
    api_key: str,
    question: str,
    analysis: Dict[str, Any],
) -> Dict[str, Any]:
    model = _model_name()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    prompt = f"""
You are Aimz, a study and code understanding assistant.

User question:
{question}

Context (previous analysis JSON):
{json.dumps(analysis)[:8000]}

Give a clear, step-by-step explanation. If the question is about code, explain the logic, highlight pitfalls, and suggest improvements.
Return JSON ONLY:
{{"answer":"...", "bullets":["...","..."], "next_steps":["..."]}}
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=payload, timeout=60)
    data = r.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = _extract_json(text)
        if parsed is not None:
            return parsed
        # Fallback: wrap plain text into structured response
        return {"answer": text.strip(), "bullets": [], "next_steps": []}
    except Exception:
        return {"error": "Model response parse failed", "raw": data}
