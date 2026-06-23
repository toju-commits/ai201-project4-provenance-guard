import re
import statistics
from typing import Dict, List


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r"[.!?]+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(value, max_value))


def analyze_stylometry(text: str) -> Dict:
    """
    Returns stylometric metrics plus an AI-likelihood heuristic score.

    This is intentionally simple and explainable:
    - Very low sentence length variance can suggest generated text.
    - Very low type-token ratio can suggest repetitive/generated text.
    - Very even/clean punctuation can suggest generated text.
    """
    sentences = split_sentences(text)
    words = tokenize(text)

    if not words:
        return {
            "score": 0.5,
            "average_sentence_length": 0,
            "sentence_length_variance": 0,
            "type_token_ratio": 0,
            "punctuation_density": 0,
            "notes": ["No usable words found; returning uncertain stylometric score."]
        }

    sentence_lengths = [len(tokenize(sentence)) for sentence in sentences] or [len(words)]
    average_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

    if len(sentence_lengths) > 1:
        sentence_length_variance = statistics.variance(sentence_lengths)
    else:
        sentence_length_variance = 0

    unique_words = set(words)
    type_token_ratio = len(unique_words) / len(words)

    punctuation_count = len(re.findall(r"[,.!?;:]", text))
    punctuation_density = punctuation_count / max(len(words), 1)

    notes = []

    # Heuristic scoring.
    score_parts = []

    # AI writing often has very even sentence lengths.
    if sentence_length_variance < 8:
        score_parts.append(0.75)
        notes.append("Low sentence length variance may indicate generated or highly uniform writing.")
    elif sentence_length_variance < 20:
        score_parts.append(0.55)
        notes.append("Moderate sentence length variance gives mixed signal.")
    else:
        score_parts.append(0.25)
        notes.append("High sentence length variance suggests more human-like variation.")

    # Lower lexical diversity can indicate formulaic text.
    if type_token_ratio < 0.45:
        score_parts.append(0.70)
        notes.append("Low type-token ratio suggests repetitive wording.")
    elif type_token_ratio < 0.65:
        score_parts.append(0.50)
        notes.append("Moderate type-token ratio gives mixed signal.")
    else:
        score_parts.append(0.25)
        notes.append("High type-token ratio suggests diverse wording.")

    # Very balanced punctuation density can sometimes indicate polished AI prose.
    if 0.08 <= punctuation_density <= 0.18:
        score_parts.append(0.60)
        notes.append("Punctuation density falls in a polished, regular range.")
    else:
        score_parts.append(0.40)
        notes.append("Punctuation density does not strongly suggest AI generation.")

    # Extremely polished average sentence lengths can lean AI, but weakly.
    if 14 <= average_sentence_length <= 24:
        score_parts.append(0.60)
        notes.append("Average sentence length falls in a common generated-prose range.")
    else:
        score_parts.append(0.40)
        notes.append("Average sentence length does not strongly suggest AI generation.")

    stylometric_score = sum(score_parts) / len(score_parts)

    return {
        "score": round(clamp(stylometric_score), 3),
        "average_sentence_length": round(average_sentence_length, 3),
        "sentence_length_variance": round(sentence_length_variance, 3),
        "type_token_ratio": round(type_token_ratio, 3),
        "punctuation_density": round(punctuation_density, 3),
        "notes": notes
    }