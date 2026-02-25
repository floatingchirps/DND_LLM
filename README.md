# DND_LLM Flask Frontend

Simple Flask web UI for your D&D brainstorming LLM.

## What this adds

- One-page chat interface with:
  - Prompt input
  - **Send** button
  - Response history area
- Backend bridge that runs your existing `app.py` (or `RunDndBrain.bat`) and returns the output to the browser.
- Auto-scroll to newest message for a chat-like feel.
- LLM warm-up on server start. The page keeps input disabled and shows **"LLM still booting up..."** until startup finishes.
- One-click Windows launcher (`LaunchDndWeb.bat`) that starts the server and opens the browser automatically.

## Files

- `flask_web.py` - Flask server + subprocess bridge to your existing LLM launcher.
- `templates/index.html` - UI markup and frontend JS.
- `static/styles.css` - Basic styling for readability.
- `LaunchDndWeb.bat` - Starts Flask server and opens browser (Windows).

## Requirements

- Python 3.9+
- Flask

Install dependency:

```bash
pip install flask
```

## Fast start (Windows)

Double-click:

- `LaunchDndWeb.bat`

This will:

1. start `python flask_web.py` in a Command Prompt window,
2. automatically open `http://127.0.0.1:5000/` in your browser.

## Manual start

From the repository root:

```bash
python flask_web.py
```

Then open:

- <http://127.0.0.1:5000>

## LLM startup behavior

When Flask starts, it runs a background warm-up call so the model can boot before user input is enabled.

- `/status` reports readiness.
- The frontend polls `/status` and disables chat input/button until ready.
- If startup fails, the page shows the startup error.

## How backend command is chosen

For each backend call, `flask_web.py` chooses this order:


1. `DND_BACKEND_CMD` environment variable (if set)
2. `RunDndBrain.bat` (Windows only)
3. `app.py`

It passes the prompt both as a CLI argument and stdin for compatibility, captures stdout, and sends it back to the UI.

### Optional overrides

Set a custom backend command:

```bash
# Linux/macOS example
export DND_BACKEND_CMD="python app.py"

# Windows PowerShell example
$env:DND_BACKEND_CMD="python app.py"
```

Set a custom warm-up prompt:

```bash
# Linux/macOS
export DND_BOOTSTRAP_PROMPT="What would you like to brainstorm about?"

# Windows PowerShell
$env:DND_BOOTSTRAP_PROMPT="What would you like to brainstorm about?"
```
