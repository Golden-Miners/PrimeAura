import sys
import types

from primeaura.data.mt5 import MT5DataSource


class _SymbolInfo:
    name = "XAUUSD"
    trade_mode = 0
    digits = 2
    point = 0.01


def test_session_info_degrades_when_mt5_session_api_is_unavailable(monkeypatch):
    fake_mt5 = types.SimpleNamespace(
        symbol_select=lambda instrument, enabled: True,
        symbol_info=lambda instrument: _SymbolInfo(),
        copy_rates_from_pos=lambda instrument, timeframe, start_pos, count: [
            {"time": 1_000_000_000}
        ],
        TIMEFRAME_M5="TIMEFRAME_M5",
    )
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)

    result = MT5DataSource().session_info("XAUUSD")

    assert result["name"] == "XAUUSD"
    assert result["sessions"] == {}
    assert result["session_metadata_available"] is False


def test_session_info_uses_mt5_session_api_when_available(monkeypatch):
    calls = []

    def symbol_info_session_trade(instrument, day, index):
        calls.append((instrument, day, index))
        if day == 0 and index == 0:
            return (3600, 7200)
        return None

    fake_mt5 = types.SimpleNamespace(
        symbol_select=lambda instrument, enabled: True,
        symbol_info=lambda instrument: _SymbolInfo(),
        copy_rates_from_pos=lambda instrument, timeframe, start_pos, count: [
            {"time": 1_000_000_000}
        ],
        TIMEFRAME_M5="TIMEFRAME_M5",
        symbol_info_session_trade=symbol_info_session_trade,
    )
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)

    result = MT5DataSource().session_info("XAUUSD")

    assert result["session_metadata_available"] is True
    assert result["sessions"][0]
    assert result["sessions"][0][0]["from"] == 3600
    assert result["sessions"][0][0]["to"] == 7200
    assert calls[0] == ("XAUUSD", 0, 0)
