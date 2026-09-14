from datetime import datetime,timezone
from decimal import Decimal
from primeaura.data.mt5_history import MT5HistoryProvider,HistoryRequest
class MT5:
 TIMEFRAME_M15=15
 def symbol_info(self,s): return type("I",(),{"visible":True})()
 def copy_rates_from_pos(self,s,t,p,n): return [{"time":0,"open":1,"high":2,"low":0.5,"close":1.5,"tick_volume":7}]
class Resolver:
 def resolve(self,i): return i

def test_history_is_read_only():
 x=MT5HistoryProvider(MT5(),Resolver()).history(HistoryRequest("XAUUSD","M15",1))[0]
 assert x["instrument"]=="XAUUSD" and x["close"]==Decimal("1.5") and x["timestamp"]==datetime(1970,1,1,tzinfo=timezone.utc)
