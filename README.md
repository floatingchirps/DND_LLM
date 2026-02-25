# DND_LLM Flask Frontend

Simple Flask web UI for your D&D brainstorming LLM.

## What this adds

- One-page chat interface with:
  - Prompt input
  - **Send** button
  - Response history area
- Backend bridge that runs your existing `app.py` (or `RunDndBrain.bat`) and returns the output to the browser.
- Auto-scroll to newest message for a chat-like feel.

## Files

- `flask_web.py` - Flask server + subprocess bridge to your existing LLM launcher.
- `templates/index.html` - UI markup and minimal frontend JS.
- `static/styles.css` - Basic styling for readability.

## Requirements

- Python 3.9+
- Flask

Install dependency:

```bash
pip install flask
```

## Running locally

From the repository root:

```bash
python flask_web.py
```

Then open:

- <http://127.0.0.1:5000>

## How the backend command is chosen

When you submit a prompt, `flask_web.py` chooses the backend command in this order:

1. `DND_BACKEND_CMD` environment variable (if set)
2. `RunDndBrain.bat` (Windows only)
3. `app.py`

It passes the prompt both as a CLI argument and stdin for compatibility, captures stdout, and sends it back to the UI.

### Optional: explicit command override

If your launch command is custom, set:

```bash
# Linux/macOS example
export DND_BACKEND_CMD="python app.py"

# Windows PowerShell example
$env:DND_BACKEND_CMD="python app.py"
```

Then run `python flask_web.py` normally.
