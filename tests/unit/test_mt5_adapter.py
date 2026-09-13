from datetime import datetime
from primeaura.data.mt5 import MT5DataSource

def test_timeframe_map_contains_required_timeframes():
    from primeaura.data.mt5 import TIMEFRAME_MAP
    assert set(TIMEFRAME_MAP)=={"M5","M15","H1"}

def test_terminal_path_prefers_environment(monkeypatch):
    monkeypatch.setenv("PRIMEAURA_MT5_PATH", r"C:\MT5\terminal64.exe")
    assert MT5DataSource().terminal_path == r"C:\MT5\terminal64.exe"
