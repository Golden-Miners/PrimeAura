import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

def _json_safe(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value

class DiagnosticStore:
    def __init__(self, path: str = "data/signals/scan_diagnostics.json"):
        self.path = Path(path)

    def save(self, instrument: str, diagnostics) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = self.load()
        data[instrument] = [_json_safe(asdict(item)) for item in diagnostics]
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
