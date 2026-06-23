# Provenance Guard Planning

## Project Overview

Provenance Guard is a backend system for creative platforms that evaluates text-based creative work and estimates whether it is likely AI-generated, uncertain, or likely human-written. The goal is not to punish creators, but to provide transparent attribution labels while allowing creators to appeal decisions.

## Target Users

The primary users are:
- Creative platform moderators
- Writers submitting poems, stories, or blog posts
- Readers who want transparency about content origin
- Platform teams that need auditable AI attribution decisions

## Problem

Creative platforms face a difficult challenge: AI-generated text can be submitted as human work, but automated detectors are imperfect and can falsely accuse real writers. Provenance Guard addresses this by using multiple signals, confidence scoring, transparency labels, audit logging, rate limiting, and an appeal process.

## Core Requirements

The system will provide:
- POST /submit for content attribution checks
- POST /appeal for creator appeals
- GET /log for demo-friendly audit log inspection
- Two-signal detection:
  - Groq LLM classifier
  - Stylometric heuristics
- Confidence score from 0 to 1
- Attribution result:
  - likely_ai
  - uncertain
  - likely_human
- Plain-language transparency labels
- Structured audit logs
- Flask-Limiter rate limiting

## Detection Signals

### Signal 1: LLM Classifier

The LLM classifier will use Groq to estimate the likelihood that a submitted text was AI-generated. It should return a score between 0 and 1.

### Signal 2: Stylometric Heuristics

The stylometric signal will use simple text statistics:
- Average sentence length
- Sentence length variance
- Type-token ratio
- Punctuation density

These metrics are used as a second independent signal to avoid relying on only one model-based judgment.

## Confidence Scoring

The combined score will be calculated as:

combined_ai_score = 0.65 * llm_ai_score + 0.35 * stylometric_ai_score

Thresholds:
- score >= 0.75: likely_ai
- score >= 0.40 and score < 0.75: uncertain
- score < 0.40: likely_human

The threshold for likely_ai is intentionally high because false positives can harm human creators.

## Transparency Labels

### likely_ai

"This piece is labeled as likely AI-generated based on multiple detection signals. Confidence is high, but creators may appeal this decision."

### uncertain

"This piece has an uncertain attribution result. Our system found mixed signals, so readers should interpret the label with caution."

### likely_human

"This piece is labeled as likely human-written. Automated systems can be imperfect, but current signals do not strongly indicate AI generation."

## Appeal Process

Creators can appeal by submitting:
- content_id
- creator_reasoning

The system will update the content status to under_review and log the appeal. The project will not automatically reclassify appealed content.

## Rate Limiting

The /submit endpoint will be limited to:
- 10 requests per minute
- 100 requests per day

This protects the system from abuse, spam, and excessive API usage.

## Audit Logging

Each submission log entry will include:
- timestamp
- content_id
- creator_id
- attribution result
- confidence score
- LLM score
- stylometric score
- status

Each appeal log entry will include:
- timestamp
- content_id
- creator reasoning
- updated status

## Limitations

AI text detection is not perfectly reliable. The system should be treated as a transparency aid, not a final judgment. Human review remains important, especially for appeals and borderline cases.