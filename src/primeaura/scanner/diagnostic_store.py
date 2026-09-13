import json
from pathlib import Path
from dataclasses import asdict

class DiagnosticStore:
    def __init__(self, path: str = "data/signals/scan_diagnostics.json"):
        self.path = Path(path)

    def save(self, instrument: str, diagnostics) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = self.load()
        data[instrument] = [asdict(item) for item in diagnostics]
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
