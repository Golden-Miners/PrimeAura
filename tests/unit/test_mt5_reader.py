from datetime import datetime,timezone
from primeaura.data.mt5_reader import MT5ReadOnly

class Rates:
    dtype=type("D",(),{"names":("time","open","high","low","close","tick_volume")})()
    def __iter__(self):
        return iter([{"time":0,"open":100.0,"high":102.0,"low":99.0,"close":101.0,"tick_volume":12}])

class FakeMT5:
    TIMEFRAME_M15=15
    def initialize(self): return True
    def shutdown(self): pass
    def symbol_select(self,symbol,visible): return True
    def copy_rates_from_pos(self,*args): return Rates()
    def last_error(self): return "none"

def test_mt5_reader_is_read_only_and_parses_bars():
    c=MT5ReadOnly(FakeMT5()); c.initialize(); s=c.bars("XAUUSD","M15",1); c.shutdown()
    assert s.source=="MT5" and s.bars[0].close==101
