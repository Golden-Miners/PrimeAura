from decimal import Decimal
from primeaura.signals.store import SignalStore
from primeaura.signals.report import SignalReport

def s(i): return SignalReport(i,"XAUUSD","BUY","smc","1",Decimal("100"),Decimal("98"),Decimal("104"),Decimal("3"),Decimal("80"),"t",("BOS",),(),str(i))
def test_recent_returns_newest_first(tmp_path):
 st=SignalStore(str(tmp_path/"s.jsonl")); st.append(s("1")); st.append(s("2"))
 assert [x["signal_id"] for x in st.recent()]==["2","1"]
