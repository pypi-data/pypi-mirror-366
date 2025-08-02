# Universal LLM Safeguard Layer

## Project overview

Universal LLM Safeguard Layer is a modular middleware written in Python that enforces content safety for applications interacting with large language models (LLMs). It implements a canonical filter pipeline designed for the Trinity framework: every decision is explicit, logged and auditable, and there are no silent failure modes. The layer normalises inputs, checks for authorised override phrases, runs a configurable suite of filters, aggregates the results and writes a structured log entry on every invocation. This makes it suitable for AI systems that must meet strict safety and audit requirements while remaining easy to integrate into existing code bases.

### The high‑level pipeline is:

- **Pre‑processing** – sanitise and normalise the incoming text and attach any contextual metadata.
- **Override detection** – detect exactly one authorised phrase (e.g. from a parent or moderator) and, if present, strip it from the text and permit the message regardless of filter output. Ambiguous or missing overrides are rejected and logged.
- **Filtering** – run the configured filters on the cleaned text. The built‑in filters include:
  - **Keyword/regex filter** – checks for banned keywords and regular expressions.
  - **Classifier filter** – optionally uses a HuggingFace model to score toxicity/abuse categories and compares them against configurable warn/block thresholds.
  - **Perspective API filter** – optionally calls the Google Perspective API for additional scoring.

Each filter returns `(allowed, flags, reasons)` where:
- `allowed` is a boolean,
- `flags` is a list of machine‑readable identifiers,
- `reasons` is a list of human‑readable explanations.

- **Aggregation** – merge and deduplicate flags and reasons across all filters.
- **Logging** – write a JSON‑lines entry with the timestamp, status, flags, reasons, override metadata, user/session identifiers, anonymised text and any additional context.
- **Post‑processing** – allow downstream hooks to augment the result before returning a canonical dictionary.

### The return value from the pipeline always includes the keys:

- `status` – `"allowed"` or `"blocked"`
- `flags` – list of flag identifiers (e.g. `"keyword"`, `"classifier_toxic"`)
- `reasons` – corresponding human‑readable explanations
- `override` – `True` if an override phrase was used
- `role` – `"parent"`, `"moderator"` or `None`

This strict schema promotes type‑safety, cognitive alignment and ease of integration. Unexpected errors are never swallowed; instead they are logged with `status="error"` and the exception is re‑raised.

---

## Installation

The package is distributed on PyPI under the name `safeguard`. A minimal installation installs only the core filtering logic; optional extras install framework adapters.

```bash
pip install safeguard

# Framework extras (optional)
pip install "safeguard[flask]"    # Flask integration
pip install "safeguard[fastapi]"  # FastAPI integration
pip install "safeguard[django]"   # Django integration
```

To work from source:

```bash
git clone <repository_url>
cd safeguard
python3 -m venv .venv
source .venv/bin/activate    # Use .venv\Scripts\activate on Windows
pip install -U pip setuptools
pip install .
pip install ".[dev]"         # Installs test and lint dependencies
```

---

## Configuration

Configuration is provided via a JSON file or Python dictionary. The default file lives in `safeguarding/config/safeguard_config.json` and is merged onto sensible defaults by `load_config()`.

### Important configuration sections:

- `rules.banned_keywords` – list of lower‑cased substrings. If any appear, the message is blocked with the `"keyword"` flag.
- `rules.banned_regex` – list of regex patterns. Matches add a `"regex"` flag and block the message.
- `classifier.enabled` – enables HuggingFace classifier. Scores are compared to warn/block thresholds.
- `perspective_api.enabled` – enables Google Perspective API. Thresholds mirror classifier logic.
- `logging.log_path` – file path for audit logs.
- `logging.anonymize` – whether to redact text in logs (default: true).
- `override.parent_phrases`, `override.moderator_phrases` – lists of allowed override phrases.

### Example `safeguard_config.json`

```json
{
  "rules": {
    "banned_keywords": ["sex", "drugs", "violence", "suicide"],
    "banned_regex": [".*naked.*", ".*let's keep this secret.*"]
  },
  "classifier": {
    "enabled": false,
    "model": "unitary/toxic-bert",
    "thresholds": {
      "toxic": { "warn": 0.5, "block": 0.7 },
      "insult": { "warn": 0.5, "block": 0.7 }
    }
  },
  "perspective_api": {
    "enabled": false
  },
  "logging": {
    "log_path": "safeguard_flags.log",
    "anonymize": true
  },
  "override": {
    "parent_phrases": ["override123"],
    "moderator_phrases": ["modunlock!"]
  }
}
```

Load with:

```python
from safeguarding.utils.config_loader import load_config
config = load_config()
```

---

## Programmatic usage

The core entry point is `run_all_filters()` from `safeguarding.core.orchestrator`.

```python
from safeguarding.core.orchestrator import run_all_filters
from safeguarding.utils.config_loader import load_config

config = load_config()
config["classifier"]["enabled"] = False
config["perspective_api"]["enabled"] = False

result = run_all_filters(
    text="Let's talk about drugs override123",
    source="input",
    user_id="user42",
    session_id="sessionA",
    config=config
)

if result["status"] == "blocked":
    print("Content blocked:", result["reasons"])
else:
    print("Allowed:", result)
```

### Return schema:

| Key       | Type           | Description                                   |
|-----------|----------------|-----------------------------------------------|
| status    | str            | `"allowed"` or `"blocked"`                   |
| flags     | List[str\|dict] | Identifiers for filter hits (e.g. `"regex"`) |
| reasons   | List[str]      | Human-readable explanations                  |
| override  | bool           | True if override used                        |
| role      | str or None    | `"parent"`, `"moderator"`, or `None`         |

---

## Logging and override behaviour

Every run creates a JSON audit log containing:

- `timestamp`
- `source` – e.g. `"input"` or `"output"`
- `status` – `"allowed"`, `"blocked"`, `"override"` or `"error"`
- `flags`, `reasons`
- `override_used`, `override_role`
- `text` – `[REDACTED]` or full content
- `user_id`, `session_id`
- `action_type` – e.g. `"block"` or `"allow"`
- `context` – any additional metadata

Override phrases must match exactly. Zero or multiple matches = reject. All override attempts are logged.

---

## Framework integration

Adapters are provided for Flask and FastAPI.

### Flask

```python
from flask import Flask, request, jsonify
from safeguarding.middleware.flask_adapter import safeguard_filter, safeguard_endpoint
from safeguarding.utils.config_loader import load_config

app = Flask(__name__)
config = load_config()

@app.route("/filter", methods=["POST"])
def filter_text():
    data = request.get_json() or {}
    text = data.get("text", "")
    result = safeguard_filter(text, config=config)
    if result["status"] != "allowed":
        return jsonify(result), 403
    return jsonify(result)

@app.route("/chat", methods=["POST"])
@safeguard_endpoint(config)
def chat():
    return jsonify({"message": "Hello!"})
```

### FastAPI

```python
from fastapi import FastAPI
from safeguarding.middleware.fastapi_adapter import FastAPISafeguardMiddleware
from safeguarding.utils.config_loader import load_config

app = FastAPI()
config = load_config()

app.add_middleware(FastAPISafeguardMiddleware, config=config)

@app.post("/messages")
async def receive(data: dict):
    return {"echo": data.get("text")}
```

Both return `403` with flags/reasons on block. All overrides are logged.

---

## Version and licence

Current version: **0.1.0**  
Licence: **MIT**  
See `LICENSE` for terms.

---

## Contributing

Contributions welcome! Please open issues or PRs. Follow the design principles:

- No hidden behaviour  
- No silent failures  
- Full auditability  
- Include tests for new logic
