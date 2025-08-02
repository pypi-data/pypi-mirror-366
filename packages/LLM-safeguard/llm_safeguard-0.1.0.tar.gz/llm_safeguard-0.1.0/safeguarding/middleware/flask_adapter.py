from flask import Flask, request, jsonify
from safeguarding.core.orchestrator import run_all_filters
from safeguarding.utils.config_loader import load_config
from typing import Dict, Any


def safeguard_filter(text: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies the full safeguard pipeline to the input text.

    Args:
        text (str): The user- or AI-generated message.
        config (dict): Config dict to pass to filters. Must not be None.

    Returns:
        dict: A structured response with status, flags, and reasons.
    """
    config = config or load_config()

    log_path = config.get("logging", {}).get("log_path", "safeguard_flags.log")
    anonymize = config.get("logging", {}).get("anonymize", True)
    user_id = config.get("user_id", "anon")
    session_id = config.get("session_id", "anon_session")

    result = run_all_filters(
        text=text,
        context={},
        log_path=log_path,
        anonymize=anonymize,
        user_id=user_id,
        session_id=session_id,
        config=config
    )

    return {
        "status": result.get("status", "blocked"),
        "flags": result.get("flags", []),
        "reasons": result.get("reasons", [])
    }


# Optional drop-in example Flask app (for standalone testing)
def create_flask_app() -> Flask:
    app = Flask(__name__)
    config = load_config()

    @app.route("/filter", methods=["POST"])
    def filter_text():
        """
        Expects JSON: { "text": "..." }
        Returns: { "status": "allowed|blocked", "flags": [...], "reasons": [...] }
        """
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' in request"}), 400

        result = safeguard_filter(data["text"], config=config)

        if result["status"] == "blocked":
            return jsonify(result), 403
        return jsonify(result)

    return app


# Optional: add safeguard as a reusable Flask decorator (drop-in)
def safeguard_endpoint(config: Dict[str, Any]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = request.get_json()
            text = data.get("text", "")

            log_path = config.get("logging", {}).get("log_path", "safeguard_flags.log")
            anonymize = config.get("logging", {}).get("anonymize", True)
            user_id = config.get("user_id", "anon")
            session_id = config.get("session_id", "anon_session")

            result = run_all_filters(
                text=text,
                context={},
                log_path=log_path,
                anonymize=anonymize,
                user_id=user_id,
                session_id=session_id,
                config=config
            )

            if result.get("status", "") != "allowed":
                return jsonify({
                    "error": "Input blocked by safeguard filters",
                    "flags": result.get("flags", []),
                    "reasons": result.get("reasons", [])
                }), 403

            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
