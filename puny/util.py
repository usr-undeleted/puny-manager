import secrets
import shutil
import string
import subprocess
import sys

ALPHABET = string.ascii_letters + string.digits + string.punctuation


def generate_password(length: int) -> str:
    if length < 8:
        raise ValueError
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def check_master_password(password: str) -> tuple[str | None, str | None]:
    if len(password) < 4:
        return "master_password_too_short", None
    warnings = []
    if len(password) < 8:
        warnings.append("short")
    if not any(c in string.punctuation for c in password):
        warnings.append("no_symbol")
    if warnings:
        return None, "weak_master_password"
    return None, None


def schedule_clipboard_clear(timeout_s: int) -> None:
    if timeout_s <= 0:
        return
    if shutil.which("wl-copy"):
        clear_cmd = ["wl-copy", ""]
    elif shutil.which("xclip"):
        clear_cmd = ["xclip", "-selection", "clipboard"]
    else:
        return
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import time, subprocess;"
                f"time.sleep({timeout_s});"
                f"subprocess.run({clear_cmd!r}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)"
            ),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def smart_find(entries, query):
    exact = [e for e in entries if e.name == query]
    if exact:
        return exact[0]

    matches = [
        e
        for e in entries
        if query.lower()
        in (e.name + e.notes + e.username + e.url + " ".join(e.tags)).lower()
    ]
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    if shutil.which("fzf"):
        p = subprocess.run(
            ["fzf"],
            input="\n".join(e.name for e in matches),
            text=True,
            capture_output=True,
        )
        if p.returncode == 0:
            for e in matches:
                if e.name == p.stdout.strip():
                    return e

    return matches[0]
