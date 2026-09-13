from datetime import datetime,timezone
from decimal import Decimal
from primeaura.data.mt5_provider import MT5MarketDataProvider

def test_aliases_are_read_only():
 p=MT5MarketDataProvider({"XAUUSD":"GOLD","XAGUSD":"SILVER"}); assert p.symbol_aliases["XAUUSD"]=="GOLD"

def test_requires_connection():
 p=MT5MarketDataProvider()
 try: p.history("XAUUSD","M15",datetime.now(timezone.utc),datetime.now(timezone.utc))
 except RuntimeError as e: assert "connect" in str(e)
 else: raise AssertionError("history must require explicit MT5 connection")
