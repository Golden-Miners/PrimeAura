from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from ..data.models import OHLCVBar

REQUIRED={"timestamp","open","high","low","close"}

def load_ohlcv_csv(path:str|Path,instrument:str,timeframe:str)->list[OHLCVBar]:
    import csv
    rows=[]
    with Path(path).open("r",encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)): raise ValueError(f"CSV must contain {sorted(REQUIRED)}")
        for row in reader:
            ts=row["timestamp"]
            dt=datetime.fromisoformat(ts.replace("Z","+00:00"))
            if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
            rows.append(OHLCVBar(instrument=instrument,timeframe=timeframe,timestamp=dt,open=Decimal(row["open"]),high=Decimal(row["high"]),low=Decimal(row["low"]),close=Decimal(row["close"]),volume=Decimal(row.get("volume","0"))))
    rows.sort(key=lambda x:x.timestamp)
    if any(a.timestamp==b.timestamp for a,b in zip(rows,rows[1:])): raise ValueError("Duplicate timestamps detected")
    return rows
