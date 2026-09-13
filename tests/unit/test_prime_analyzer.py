from datetime import datetime,timezone,timedelta
from decimal import Decimal
from primeaura.scanner.prime_analyzer import analyze_timeframes

def bars(n):
    return [{"timestamp":datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(hours=i),"open":Decimal("1"),"high":Decimal(str(2+i)), "low":Decimal("0"),"close":Decimal(str(2+i))} for i in range(n)]
def test_adapter_requires_all_timeframes():
    try: analyze_timeframes({"H1":[],"M15":[]})
    except KeyError as e: assert "M5" in str(e)
    else: raise AssertionError("M5 must be required")
