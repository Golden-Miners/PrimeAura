from decimal import Decimal
from .technical import atr,breakout_level

def breakout_retest(instrument,c):
 close,high,low=c["close"],c["high"],c["low"]; a=atr(high,low,close,14); level=breakout_level(high,20)
 if a is None or level is None or len(close)<22: return None
 # A retest is accepted only when the prior candle touched/crossed the level and current candle closes back above it.
 if close[-2]>=level and low[-1]<=level and close[-1]>level:
  sl=min(low[-1],level)-a*Decimal("0.25"); tp=close[-1]+abs(close[-1]-sl)*Decimal("2")
  return {"instrument":instrument,"direction":"BUY","strategy_id":"breakout-retest","entry":close[-1],"stop_loss":sl,"tp1":tp,"rr":Decimal("2"),"reasoning":["Confirmed breakout","Level retest","Bullish continuation"]}
 return None
