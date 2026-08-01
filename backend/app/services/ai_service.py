import os
import json
import anthropic
from app.services.ai_prompts import build_analysis_prompt

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL_NAME = "claude-sonnet-4-5"

def run_candidate_analysis(job_description, required_skills, preferred_skills, resume_text):
    prompt = build_analysis_prompt(job_description, required_skills, preferred_skills, resume_text)

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
    except anthropic.RateLimitError:
        raise RuntimeError("AI service is rate-limited right now.Please try again shortly.")
    except anthropic.APIConnectionError:
        raise RuntimeError("Could not reach the AI service. Check your connection and try again.")
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"AI service returned an error (status {e.status_code}).")

    raw_text = response.content[0].text
    return raw_text, MODEL_NAME

def parse_analysis_response(raw_text):
    """
    Attempts to extract and validate a structured analysis dict from the model's raw text.
    Raises ValueError with a clear message if parsing/validation fails.
    """
    cleaned = raw_text.strip()

    # Defensive step 1: strip markdown code fences if the model added them anyway
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[len("json"):].strip()

    # Defensive step 2: actually parse the JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}")

    # Defensive step 3: validate the shape — every key we expect is actually present
    required_keys = [
        "overall_match_score", "technical_skills_score", "experience_score",
        "culture_score", "strengths", "missing_skills", "suggested_questions",
    ]
    missing_keys = [k for k in required_keys if k not in data]
    if missing_keys:
        raise ValueError(f"Model response missing expected keys: {missing_keys}")

    # Defensive step 4: validate and clamp score ranges — never trust the model
    # to have actually respected "0-100" just because we asked
    score_keys = ["overall_match_score", "technical_skills_score", "experience_score", "culture_score"]
    for key in score_keys:
        value = data[key]
        if not isinstance(value, (int, float)):
            raise ValueError(f"'{key}' is not a number: {value}")
        data[key] = max(0, min(100, int(value)))  # clamp into valid range, just in case

    # Defensive step 5: ensure the list fields are actually lists of strings
    list_keys = ["strengths", "missing_skills", "suggested_questions"]
    for key in list_keys:
        if not isinstance(data[key], list):
            raise ValueError(f"'{key}' is not a list: {data[key]}")
        data[key] = [str(item) for item in data[key]]

    return data

def analyze_candidate(job_description, required_skills, preferred_skills, resume_text):
    raw_text, model_used = run_candidate_analysis(
        job_description, required_skills, preferred_skills, resume_text
    )
    parsed = parse_analysis_response(raw_text)
    parsed["model_used"] = model_used
    return parsed