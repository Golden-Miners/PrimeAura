from decimal import Decimal

from primeaura.scanner.diagnostic_store import DiagnosticStore
from primeaura.scanner.diagnostics import DirectionDiagnostic

def test_decimal_diagnostics_are_json_serializable(tmp_path):
    store = DiagnosticStore(str(tmp_path / "diagnostics.json"))
    item = DirectionDiagnostic(
        direction="SELL",
        passed=("H1 bias aligned",),
        missing=(),
        final_gate="BLOCKED: RR 1.25 < 2.0",
        entry=Decimal("3500.10"),
        stop_loss=Decimal("3510.10"),
        tp1=Decimal("3520.10"),
        rr_tp1=Decimal("1.25"),
    )
    store.save("XAUUSD", [item])
    data = store.load()
    assert data["XAUUSD"][0]["entry"] == "3500.10"
    assert data["XAUUSD"][0]["rr_tp1"] == "1.25"
