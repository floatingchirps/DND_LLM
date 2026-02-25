import os
import platform
import shlex
import subprocess
import sys
import threading
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent

_llm_ready = False
_llm_boot_error = None
_llm_boot_lock = threading.Lock()


def build_backend_command(prompt: str) -> list[str]:
    """Build the command that will execute the existing D&D LLM script."""
    custom_cmd = os.getenv("DND_BACKEND_CMD")
    if custom_cmd:
        return shlex.split(custom_cmd) + [prompt]

    bat_file = ROOT / "RunDndBrain.bat"
    py_file = ROOT / "app.py"

    if bat_file.exists():
        if platform.system().lower().startswith("win"):
            # Many .bat files include `pause` prompts ("Press any key to continue...").
            # Pipe a newline so batch scripts do not block web requests waiting for keyboard input.
            bat_cmd = f'echo.|"{bat_file}"'
            return ["cmd", "/c", bat_cmd]
        if py_file.exists():
            return [sys.executable, str(py_file), prompt]
        raise RuntimeError("RunDndBrain.bat exists, but this host is not Windows and app.py was not found.")

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
        input=f"{prompt}\n",
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=300,
    )

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Unknown backend error"
        raise RuntimeError(f"Backend command failed (exit {completed.returncode}): {stderr}")

    output = completed.stdout.strip()
    return output or "(No response text returned by backend command.)"


def warm_up_llm() -> None:
    """
    Boot the LLM once in the background so first user prompt is not blocked by startup.
    """
    global _llm_ready, _llm_boot_error
    with _llm_boot_lock:
        if _llm_ready:
            return

        try:
            bootstrap_prompt = os.getenv("DND_BOOTSTRAP_PROMPT", "What would you like to brainstorm about?")
            run_llm(bootstrap_prompt)
            _llm_ready = True
            _llm_boot_error = None
        except Exception as exc:
            _llm_boot_error = str(exc)


def start_warmup_thread() -> None:
    thread = threading.Thread(target=warm_up_llm, daemon=True)
    thread.start()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/status")
def status():
    if _llm_ready:
        return jsonify({"ready": True})

    if _llm_boot_error:
        return jsonify({"ready": False, "error": _llm_boot_error}), 500

    return jsonify({"ready": False, "message": "LLM still booting up..."})


@app.post("/send")
def send_prompt():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    if not _llm_ready:
        if _llm_boot_error:
            return jsonify({"error": f"LLM failed to boot: {_llm_boot_error}"}), 500
        return jsonify({"error": "LLM still booting up..."}), 503

    try:
        response = run_llm(prompt)
        return jsonify({"response": response})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "The LLM took too long to respond."}), 504
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    start_warmup_thread()
    app.run(debug=True)
else:
    start_warmup_thread()
