# Provenance Guard

Provenance Guard is a Flask backend system for creative platforms that evaluates whether submitted text-based creative work is likely AI-generated, uncertain, or likely human-written.

The system is designed for poems, short story excerpts, blog posts, and other creative writing submissions. It provides a transparency label, confidence score, audit log, and creator appeal flow.

## Project Goal

Creative platforms need a way to provide transparency around AI-generated content without unfairly punishing human writers. Automated AI detectors are imperfect, so Provenance Guard uses multiple signals, cautious thresholds, explainable labels, and an appeal process.

## Features

* `POST /submit` endpoint for submitting creative text
* `POST /appeal` endpoint for creator appeals
* `GET /log` endpoint for viewing recent audit log entries
* Two-signal AI attribution detection
* Confidence score from 0 to 1
* Three attribution outcomes:

  * `likely_ai`
  * `uncertain`
  * `likely_human`
* Plain-language transparency labels
* Structured audit logging
* Rate limiting with Flask-Limiter
* Safe fallback mock classifier if no Groq API key is available

## Tech Stack

* Python
* Flask
* Flask-Limiter
* Groq API
* python-dotenv
* JSON audit logging

## Detection Approach

Provenance Guard uses two distinct detection signals.

### Signal 1: LLM Classifier

The first signal uses a Groq-powered LLM classifier to estimate the likelihood that a submitted text was AI-generated. The classifier returns an AI-likelihood score from 0 to 1.

If `GROQ_API_KEY` is not available, the app uses a safe mock classifier so the project can still run during demos.

### Signal 2: Stylometric Heuristics

The second signal uses simple Python-based stylometric analysis. It checks:

* Average sentence length
* Sentence length variance
* Type-token ratio
* Punctuation density

These metrics provide an explainable second signal so the system does not rely on a single model judgment.

## Confidence Scoring

The final AI-likelihood score is calculated as:

```txt
combined_ai_score = 0.65 * llm_ai_score + 0.35 * stylometric_ai_score
```

The LLM signal is weighted more heavily, but the stylometric signal still affects the final result.

## Attribution Thresholds

```txt
score >= 0.75       -> likely_ai
0.40 <= score < 0.75 -> uncertain
score < 0.40        -> likely_human
```

The threshold for `likely_ai` is intentionally high because false positives can harm human creators.

## Transparency Labels

### likely_ai

"This piece is labeled as likely AI-generated based on multiple detection signals. Confidence is high, but creators may appeal this decision."

### uncertain

"This piece has an uncertain attribution result. Our system found mixed signals, so readers should interpret the label with caution."

### likely_human

"This piece is labeled as likely human-written. Automated systems can be imperfect, but current signals do not strongly indicate AI generation."

## API Endpoints

## GET /

Returns service information and available endpoints.

Example response:

```json
{
  "service": "Provenance Guard",
  "description": "Creative writing AI attribution API",
  "endpoints": {
    "submit": "POST /submit",
    "appeal": "POST /appeal",
    "log": "GET /log"
  }
}
```

## POST /submit

Submits a piece of creative writing for attribution analysis.

Example request:

```json
{
  "text": "In conclusion, the modern world is a complex tapestry of innovation, creativity, and human ambition.",
  "creator_id": "creator_001"
}
```

Example response:

```json
{
  "content_id": "generated-uuid",
  "creator_id": "creator_001",
  "attribution": "uncertain",
  "confidence": 0.61,
  "label": "This piece has an uncertain attribution result. Our system found mixed signals, so readers should interpret the label with caution.",
  "signal_scores": {
    "llm_score": 0.59,
    "stylometric_score": 0.65
  },
  "status": "labeled"
}
```

## POST /appeal

Allows a creator to appeal a classification.

Example request:

```json
{
  "content_id": "generated-uuid",
  "creator_reasoning": "I wrote this myself and would like a human review."
}
```

Example response:

```json
{
  "content_id": "generated-uuid",
  "status": "under_review",
  "message": "Appeal received and logged for human review."
}
```

## GET /log

Returns recent structured audit log entries.

Example:

```txt
GET /log?limit=10
```

## Rate Limiting

The `/submit` endpoint is limited to:

```txt
10 requests per minute
100 requests per day
```

This protects the system from spam, abuse, and excessive API usage. It also helps prevent unnecessary cost if the Groq API is being used.

## Audit Logging

Every submission is logged with:

* Timestamp
* Content ID
* Creator ID
* Attribution result
* Confidence score
* LLM score
* Stylometric score
* Label
* Status

Every appeal is logged with:

* Timestamp
* Content ID
* Creator ID
* Previous attribution
* Previous confidence
* Creator reasoning
* Updated status

## Setup Instructions

Clone the repository:

```bash
git clone <repo-url>
cd ai201-project4-provenance-guard
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional: create a `.env` file with a Groq API key:

```txt
GROQ_API_KEY=your_key_here
```

Run the app:

```bash
python app.py
```

Open:

```txt
http://127.0.0.1:5000
```

## Example PowerShell Test

```powershell
$body = @{
  text = "In conclusion, the modern world is a complex tapestry of innovation, creativity, and human ambition. It is important to note that technology continues to reshape the way individuals communicate, create, and imagine the future."
  creator_id = "creator_001"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/submit" -Method POST -Body $body -ContentType "application/json"
```

## Limitations

AI text detection is not perfectly reliable. Provenance Guard should be treated as a transparency and moderation aid, not a final judgment. Human review is still important, especially for appeals and uncertain classifications.

## Future Improvements

* Store submissions and appeals in SQLite
* Add authentication for platform moderators
* Add a dashboard for reviewing appeals
* Add more robust stylometric features
* Add calibration using labeled human and AI writing samples
* Add creator history and platform-level moderation workflows

## Rubric Notes

## Signal Strengths and Weaknesses

Provenance Guard uses two detection signals.

### Signal 1: LLM Attribution Classifier

The LLM signal estimates whether the overall writing style resembles AI-generated text. It captures broad patterns such as overly generic phrasing, polished structure, repetitive transitions, and common generated-text wording.

What this signal can miss:

* A human writer who writes in a very polished or formal style may be scored as more AI-like.
* AI-generated text that is intentionally messy, emotional, or informal may be scored as more human-like.
* Short text samples may not provide enough evidence for a confident judgment.

### Signal 2: Stylometric Heuristics

The stylometric signal measures explainable text statistics:

* Average sentence length
* Sentence length variance
* Type-token ratio
* Punctuation density

This signal captures whether the writing has unusually even structure, repetitive vocabulary, or highly regular punctuation patterns.

What this signal can miss:

* Poems, lyrics, and experimental writing may naturally have unusual sentence structure.
* Short excerpts can produce unstable statistics.
* A careful human editor may produce text that looks highly regular.
* An AI system can generate varied sentence lengths if prompted to do so.

Because each signal can make different mistakes, the final result combines them instead of relying on one detector.

## Validation Approach

I tested the system with inputs designed to produce different confidence scores:

1. A polished, generic paragraph with phrases such as "In conclusion" and "It is important to note."
2. A rougher human-style creative excerpt with less regular structure.
3. A mixed sample with some polished structure but more personal or irregular wording.

The goal was to confirm that the system does not only return one label or one confidence range. The final confidence score changes based on both the LLM-style signal and the stylometric signal.

## Transparency Label Mockups

### High-confidence AI label

> This piece is labeled as likely AI-generated based on multiple detection signals. Confidence is high, but creators may appeal this decision.

### Uncertain label

> This piece has an uncertain attribution result. Our system found mixed signals, so readers should interpret the label with caution.

### High-confidence human label

> This piece is labeled as likely human-written. Automated systems can be imperfect, but current signals do not strongly indicate AI generation.

## Specific Known Limitations

Provenance Guard may misclassify poetry, lyrics, and experimental creative writing. These content types often use unusual punctuation, fragmented sentences, repetition, and irregular structure. Since the stylometric signal uses sentence length, punctuation density, and vocabulary diversity, a poem may look statistically unusual even when it is fully human-written.

The system may also struggle with very short submissions. A two-line excerpt does not provide enough text for stable sentence variance or type-token ratio measurements.

## Spec Reflection

The original plan treated the LLM classifier as the main detection signal and stylometry as a secondary support signal. During implementation, I added a mock classifier fallback when no Groq API key is available. This diverged from the ideal production plan, but it makes the demo reliable and allows the backend to run even without live API access.

I also added a `GET /log` endpoint even though the core requirements focused on submission and appeal endpoints. This was added to make the audit log easier to inspect during the demo and to clearly show structured submission and appeal entries.

## AI Usage

### AI Tool Use 1: Project Planning and Architecture

I used an AI assistant to help translate the project rubric into a concrete backend architecture. I directed the assistant to identify the required endpoints, detection pipeline, confidence scoring system, transparency labels, audit logging needs, and rate limiting requirements.

The output was a proposed file structure with `app.py`, `detector.py`, `stylometry.py`, `labels.py`, and `audit_log.py`.

I revised the plan by choosing cautious thresholds for the final attribution categories. In particular, I set the `likely_ai` threshold to 0.75 because a false accusation against a human writer is more harmful than allowing an uncertain case to remain uncertain.

### AI Tool Use 2: Code Generation and Refinement

I used an AI assistant to generate the first version of the Flask API and helper modules. I directed it to create a modular implementation with `/submit`, `/appeal`, `/log`, two detection signals, structured JSON responses, and JSON audit logging.

The output included the Flask routes, stylometric scoring function, label helper, detector pipeline, and audit log helper.

I revised the implementation by keeping the logic simple and demo-friendly. I also kept the Groq classifier behind an environment variable and added a mock fallback so the app could still run without exposing or requiring an API key during testing.
