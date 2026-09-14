from datetime import datetime, timezone
from types import SimpleNamespace

from src.primeaura.data.mt5 import _server_offset


def test_infers_three_hour_broker_offset_when_latest_bar_is_three_hours_ahead():
    now = datetime.now(timezone.utc)
    latest = int((now.timestamp() + 3 * 3600).to_integral_value()) if hasattr(now.timestamp(), "to_integral_value") else int(now.timestamp() + 3 * 3600)
    rates = [SimpleNamespace()]
    rates[0] = {"time": latest}
    assert _server_offset(rates).total_seconds() == 3 * 3600


def test_keeps_utc_when_latest_bar_is_not_in_the_future():
    now = datetime.now(timezone.utc)
    latest = int(now.timestamp() - 5 * 60)
    rates = [{"time": latest}]
    assert _server_offset(rates).total_seconds() == 0
