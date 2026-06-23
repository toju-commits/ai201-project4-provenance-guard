LABELS = {
    "likely_ai": "This piece is labeled as likely AI-generated based on multiple detection signals. Confidence is high, but creators may appeal this decision.",
    "uncertain": "This piece has an uncertain attribution result. Our system found mixed signals, so readers should interpret the label with caution.",
    "likely_human": "This piece is labeled as likely human-written. Automated systems can be imperfect, but current signals do not strongly indicate AI generation."
}


def get_attribution(score: float) -> str:
    """
    Convert combined AI-likelihood score into attribution category.
    Higher threshold for likely_ai reduces harmful false positives.
    """
    if score >= 0.75:
        return "likely_ai"
    if score >= 0.40:
        return "uncertain"
    return "likely_human"


def get_label(attribution: str) -> str:
    return LABELS.get(attribution, LABELS["uncertain"])