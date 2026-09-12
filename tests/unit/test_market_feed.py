from pathlib import Path
from primeaura.data.market_feed import load_ohlcv_csv

def test_load_and_sort_csv(tmp_path:Path):
 p=tmp_path/"x.csv"; p.write_text("timestamp,open,high,low,close,volume\n2026-01-01T00:01:00+00:00,2,3,1,2.5,10\n2026-01-01T00:00:00+00:00,1,2,0.5,1.5,8\n",encoding="utf-8")
 b=load_ohlcv_csv(p,"XAUUSD","M1"); assert len(b)==2 and b[0].close==1.5
