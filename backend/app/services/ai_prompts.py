ANALYSIS_PROMPT_TEMPLATE = """You are an expert technical recruiter analyzing how well a candidate matches a job opening.

## Job Description
{job_description}

## Required Skills
{required_skills}

## Preferred Skills
{preferred_skills}

## Candidate Resume
{resume_text}

Respond with ONLY a valid JSON object in exactly this shape, with no other text before or after it:

{{
  "overall_match_score": <integer 0-100>,
  "technical_skills_score": <integer 0-100>,
  "experience_score": <integer 0-100>,
  "culture_score": <integer 0-100>,
  "strengths": ["<short strength 1>", "<short strength 2>"],
  "missing_skills": ["<missing skill 1>"],
  "suggested_questions": ["<interview question 1>", "<interview question 2>"]
}}

Provide 2-4 items for strengths, missing_skills, and suggested_questions. Base every score
and observation strictly on the text provided — do not invent experience or skills not
mentioned in the resume."""


def build_analysis_prompt(job_description, required_skills, preferred_skills, resume_text):
    return ANALYSIS_PROMPT_TEMPLATE.format(
        job_description=job_description or "Not provided.",
        required_skills=", ".join(required_skills) if required_skills else "Not specified.",
        preferred_skills=", ".join(preferred_skills) if preferred_skills else "Not specified.",
        resume_text=resume_text or "Not provided.",
    )