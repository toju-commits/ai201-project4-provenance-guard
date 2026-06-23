import json
import os
import re
from typing import Dict

from dotenv import load_dotenv
from groq import Groq

from labels import get_attribution, get_label
from stylometry import analyze_stylometry


load_dotenv()


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(value, max_value))


def extract_json(text: str) -> Dict:
    """
    Attempts to parse JSON from an LLM response.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"ai_score": 0.5, "reasoning": "Could not parse model output; defaulted to uncertain."}


def mock_llm_classifier(text: str) -> Dict:
    """
    Safe fallback for demos when GROQ_API_KEY is missing.
    Uses simple patterns to produce a rough score.
    """
    lowered = text.lower()

    ai_markers = [
        "in conclusion",
        "it is important to note",
        "as an ai",
        "delve",
        "tapestry",
        "moreover",
        "furthermore",
        "realm",
        "underscores"
    ]

    score = 0.35

    marker_hits = sum(1 for marker in ai_markers if marker in lowered)
    score += marker_hits * 0.08

    word_count = len(re.findall(r"\b\w+\b", text))
    if word_count > 120:
        score += 0.10

    if text.count(";") >= 2:
        score += 0.05

    score = clamp(score)

    return {
        "ai_score": round(score, 3),
        "reasoning": "Mock classifier used because GROQ_API_KEY was not available."
    }


def groq_llm_classifier(text: str) -> Dict:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return mock_llm_classifier(text)

    client = Groq(api_key=api_key)

    system_prompt = """
You are an AI text attribution classifier for a creative writing platform.

Your job:
Estimate how likely the submitted text is AI-generated.

Return ONLY valid JSON:
{
  "ai_score": number between 0 and 1,
  "reasoning": "brief explanation"
}

Important:
- Do not claim certainty.
- Be cautious about false positives.
- Human writers can be polished, formal, or repetitive.
- AI-generated text can be messy or stylized.
"""

    user_prompt = f"""
Analyze this creative text:

{text}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ],
            temperature=0.1,
            max_tokens=300
        )

        raw_output = completion.choices[0].message.content
        parsed = extract_json(raw_output)

        ai_score = clamp(float(parsed.get("ai_score", 0.5)))

        return {
            "ai_score": round(ai_score, 3),
            "reasoning": parsed.get("reasoning", "No reasoning provided.")
        }

    except Exception as error:
        fallback = mock_llm_classifier(text)
        fallback["reasoning"] += f" Groq error fallback: {str(error)}"
        return fallback


def detect_text_attribution(text: str) -> Dict:
    llm_result = groq_llm_classifier(text)
    stylometry_result = analyze_stylometry(text)

    llm_score = float(llm_result["ai_score"])
    stylometric_score = float(stylometry_result["score"])

    combined_score = (0.65 * llm_score) + (0.35 * stylometric_score)
    combined_score = round(clamp(combined_score), 3)

    attribution = get_attribution(combined_score)

    return {
        "attribution": attribution,
        "confidence": combined_score,
        "label": get_label(attribution),
        "signal_scores": {
            "llm_score": llm_score,
            "stylometric_score": stylometric_score
        },
        "signal_details": {
            "llm_reasoning": llm_result["reasoning"],
            "stylometry": stylometry_result
        }
    }