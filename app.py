from uuid import uuid4

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from audit_log import add_log_entry, find_content, get_recent_entries
from detector import detect_text_attribution


app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Provenance Guard",
        "description": "Creative writing AI attribution API",
        "endpoints": {
            "submit": "POST /submit",
            "appeal": "POST /appeal",
            "log": "GET /log"
        }
    })


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit_content():
    data = request.get_json(silent=True) or {}

    text = data.get("text", "").strip()
    creator_id = data.get("creator_id", "").strip()

    if not text:
        return jsonify({
            "error": "Missing required field: text"
        }), 400

    if not creator_id:
        return jsonify({
            "error": "Missing required field: creator_id"
        }), 400

    content_id = str(uuid4())

    detection = detect_text_attribution(text)

    response = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": detection["attribution"],
        "confidence": detection["confidence"],
        "label": detection["label"],
        "signal_scores": detection["signal_scores"],
        "signal_details": detection["signal_details"],
        "status": "labeled"
    }

    add_log_entry({
        "event_type": "submission",
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": detection["attribution"],
        "confidence": detection["confidence"],
        "llm_score": detection["signal_scores"]["llm_score"],
        "stylometric_score": detection["signal_scores"]["stylometric_score"],
        "label": detection["label"],
        "status": "labeled"
    })

    return jsonify(response), 201


@app.route("/appeal", methods=["POST"])
def appeal_content():
    data = request.get_json(silent=True) or {}

    content_id = data.get("content_id", "").strip()
    creator_reasoning = data.get("creator_reasoning", "").strip()

    if not content_id:
        return jsonify({
            "error": "Missing required field: content_id"
        }), 400

    if not creator_reasoning:
        return jsonify({
            "error": "Missing required field: creator_reasoning"
        }), 400

    original_content = find_content(content_id)

    if not original_content:
        return jsonify({
            "error": "No submitted content found for that content_id"
        }), 404

    appeal_entry = add_log_entry({
        "event_type": "appeal",
        "content_id": content_id,
        "creator_id": original_content.get("creator_id"),
        "previous_attribution": original_content.get("attribution"),
        "previous_confidence": original_content.get("confidence"),
        "creator_reasoning": creator_reasoning,
        "status": "under_review"
    })

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Appeal received and logged for human review.",
        "appeal": appeal_entry
    }), 200


@app.route("/log", methods=["GET"])
def view_log():
    limit = request.args.get("limit", default=20, type=int)
    limit = max(1, min(limit, 100))

    return jsonify({
        "entries": get_recent_entries(limit)
    })


@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many submissions. Please wait before trying again."
    }), 429


if __name__ == "__main__":
    app.run(debug=True)