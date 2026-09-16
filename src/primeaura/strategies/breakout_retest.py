from decimal import Decimal
from .technical import atr, breakout_level

def breakout_retest(instrument,c):
    close,high,low=c["close"],c["high"],c["low"]; a=atr(high,low,close,14)
    if a is None or len(close)<22: return None
    upper=breakout_level(high,20); lower=min(low[-21:-1])
    if upper is not None and close[-2]>=upper and low[-1]<=upper and close[-1]>upper:
        sl=min(low[-1],upper)-a*Decimal("0.25"); e=close[-1]
        return {"instrument":instrument,"direction":"BUY","strategy_id":"breakout-retest","entry":e,"stop_loss":sl,"tp1":e+abs(e-sl)*Decimal("2"),"rr":Decimal("2"),"reasoning":["Confirmed upside breakout","Level retest","Bullish continuation"]}
    if close[-2]<=lower and high[-1]>=lower and close[-1]<lower:
        sl=max(high[-1],lower)+a*Decimal("0.25"); e=close[-1]
        return {"instrument":instrument,"direction":"SELL","strategy_id":"breakout-retest","entry":e,"stop_loss":sl,"tp1":e-abs(e-sl)*Decimal("2"),"rr":Decimal("2"),"reasoning":["Confirmed downside breakout","Level retest","Bearish continuation"]}
    return None
