import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

ROOT = Path(__file__).resolve().parent


def build_backend_command(prompt: str) -> list[str]:
    """Build the command that will execute the existing D&D LLM script."""
    custom_cmd = os.getenv("DND_BACKEND_CMD")
    if custom_cmd:
        return shlex.split(custom_cmd) + [prompt]

    bat_file = ROOT / "RunDndBrain.bat"
    py_file = ROOT / "app.py"

    if bat_file.exists():
        if platform.system().lower().startswith("win"):
            return ["cmd", "/c", str(bat_file), prompt]
        # On non-Windows machines, fall back to Python entrypoint when possible.
        if py_file.exists():
            return [sys.executable, str(py_file), prompt]
        raise RuntimeError("RunDndBrain.bat was found, but this host is not Windows and app.py was not found.")

    if py_file.exists():
        return [sys.executable, str(py_file), prompt]

    raise RuntimeError(
        "No backend runner found. Add app.py or RunDndBrain.bat, "
        "or set DND_BACKEND_CMD to your LLM launch command."
    )


def run_llm(prompt: str) -> str:
    command = build_backend_command(prompt)
    completed = subprocess.run(
        command,
        input=prompt,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=180,
    )

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Unknown backend error"
        raise RuntimeError(f"Backend command failed (exit {completed.returncode}): {stderr}")

    output = completed.stdout.strip()
    return output or "(No response text returned by backend command.)"


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/send")
def send_prompt():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    try:
        response = run_llm(prompt)
        return jsonify({"response": response})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "The LLM took too long to respond."}), 504
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True)
