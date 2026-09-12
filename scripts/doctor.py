"""Lightweight PrimeAura environment diagnostics.

Run with: python scripts/doctor.py
This script intentionally uses only the Python standard library.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import sys


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "OK" if ok else "MISSING"
    suffix = f" — {detail}" if detail else ""
    print(f"[{mark}] {label}{suffix}")


def main() -> int:
    print("PrimeAura environment doctor")
    print("=" * 30)

    check("Python", sys.version_info >= (3, 11), platform.python_version())
    check("Git", shutil.which("git") is not None)
    check("Ollama", shutil.which("ollama") is not None)

    for package in ("numpy", "pandas", "pydantic", "yaml"):
        check(package, importlib.util.find_spec(package) is not None)

    check(
        "Cloud API configuration",
        any(
            os.getenv(name)
            for name in ("GROQ_API_KEY", "OPENROUTER_API_KEY", "GEMINI_API_KEY")
        ),
        "optional",
    )

    print("\nNo broker/trade-execution checks are performed: PrimeAura is signal-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
