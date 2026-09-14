from decimal import Decimal
from .technical import atr,sma

def _make(i,d,e,sl,tp,reason):
 r=abs(e-sl); rr=abs(tp-e)/r if r else Decimal("0")
 return None if rr<Decimal("2") else {"instrument":i,"direction":d,"strategy_id":reason[0],"entry":e,"stop_loss":sl,"tp1":tp,"rr":rr,"reasoning":reason[1:]}

def trend_pullback(instrument,c):
 close,high,low=c["close"],c["high"],c["low"]; a=atr(high,low,close,14); ma=sma(close,20)
 if a is None or ma is None or len(close)<21: return None
 if close[-2]>ma and close[-1]<=ma and close[-1]>close[-3]: return _make(instrument,"BUY",close[-1],close[-1]-a,close[-1]+a*Decimal("2"),["trend-pullback","Bullish trend filter","Pullback to SMA20","Continuation confirmation"])
 if close[-2]<ma and close[-1]>=ma and close[-1]<close[-3]: return _make(instrument,"SELL",close[-1],close[-1]+a,close[-1]-a*Decimal("2"),["trend-pullback","Bearish trend filter","Pullback to SMA20","Continuation confirmation"])
 return None

def mean_reversion(instrument,c):
 close,high,low=c["close"],c["high"],c["low"]; a=atr(high,low,close,14); ma=sma(close,20)
 if a is None or ma is None: return None
 deviation=close[-1]-ma
 if deviation<=-a*Decimal("2"): return _make(instrument,"BUY",close[-1],close[-1]-a,ma,["mean-reversion","Price >=2 ATR below SMA20","Target mean"])
 if deviation>=a*Decimal("2"): return _make(instrument,"SELL",close[-1],close[-1]+a,ma,["mean-reversion","Price >=2 ATR above SMA20","Target mean"])
 return None
