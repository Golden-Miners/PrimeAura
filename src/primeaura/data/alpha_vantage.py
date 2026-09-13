from datetime import datetime, timezone
from decimal import Decimal
from ..data.models import OHLCVBar

class AlphaVantageMetalProvider:
    """Daily gold/silver historical provider. Intraday is intentionally unsupported here."""
    ENDPOINT="https://www.alphavantage.co/query"
    SYMBOLS={"XAUUSD":"XAU","XAGUSD":"XAG"}

    def __init__(self, api_key:str):
        if not api_key: raise ValueError("Alpha Vantage API key is required")
        self.api_key=api_key

    def history(self,instrument:str,start:datetime,end:datetime)->list[OHLCVBar]:
        if instrument not in self.SYMBOLS: raise ValueError(f"Unsupported metal: {instrument}")
        import requests
        params={"function":"GOLD_SILVER_HISTORY","symbol":self.SYMBOLS[instrument],"interval":"daily","apikey":self.api_key}
        response=requests.get(self.ENDPOINT,params=params,timeout=20); response.raise_for_status(); payload=response.json()
        rows=payload.get("data",payload.get("prices",[]))
        bars=[]
        for row in rows:
            dt=datetime.fromisoformat(row["date"]).replace(tzinfo=timezone.utc)
            if start<=dt<end:
                close=Decimal(str(row["value"]))
                bars.append(OHLCVBar(instrument=instrument,timeframe="1D",timestamp=dt,open=close,high=close,low=close,close=close,volume=Decimal("0")))
        return sorted(bars,key=lambda x:x.timestamp)
