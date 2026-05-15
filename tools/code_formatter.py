import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def format_code(source: str, filepath: Optional[str] = None) -> str:
    """Format Python code using autopep8 or black."""
    try:
        return _format_with_autopep8(source)
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            return _format_with_black(source)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return source


def _format_with_autopep8(source: str) -> str:
    result = subprocess.run(
        ["autopep8", "--aggressive", "--aggressive", "--max-line-length", "88", "-"],
        input=source,
        capture_output=True,
        text=True,
        timeout=15,
    )
    result.check_returncode()
    return result.stdout


def _format_with_black(source: str) -> str:
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(source)
        tmp_path = f.name

    try:
        subprocess.run(
            ["black", "--quiet", "--line-length", "88", tmp_path],
            check=True,
            timeout=15,
        )
        return Path(tmp_path).read_text(encoding="utf-8")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def add_type_annotations(source: str) -> str:
    """Basic type annotation injection for known patterns."""
    lines = source.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^def \w+\(self", stripped) and ":rtype:" not in source:
            if line.rstrip().endswith(":"):
                line = line.rstrip() + " -> None:"
        result.append(line)

    return "\n".join(result)


import re
