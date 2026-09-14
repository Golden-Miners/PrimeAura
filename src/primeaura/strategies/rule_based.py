from decimal import Decimal
from .technical import atr,breakout_level,momentum,sma

def _signal(instrument,direction,entry,sl,tp,reasoning,strategy_id):
    risk=abs(entry-sl); rr=abs(tp-entry)/risk if risk else Decimal("0")
    if rr<Decimal("2"): return None
    return {"instrument":instrument,"direction":direction,"strategy_id":strategy_id,"entry":entry,"stop_loss":sl,"tp1":tp,"rr":rr,"reasoning":reasoning}

def momentum_continuation(instrument,c):
    close,high,low=c["close"],c["high"],c["low"]
    a=atr(high,low,close,c.get("atr_period",14)); m=momentum(close,c.get("momentum_lookback",10))
    if a is None or m is None: return None
    if m>c.get("momentum_threshold",Decimal("0.003")) and close[-1]>sma(close,20):
        return _signal(instrument,"BUY",close[-1],close[-1]-a,close[-1]+a*Decimal("2"),["Positive momentum","Price above SMA20","ATR risk model"],"momentum")
    if m<-c.get("momentum_threshold",Decimal("0.003")) and close[-1]<sma(close,20):
        return _signal(instrument,"SELL",close[-1],close[-1]+a,close[-1]-a*Decimal("2"),["Negative momentum","Price below SMA20","ATR risk model"],"momentum")
    return None

def volatility_breakout(instrument,c):
    close,high,low=c["close"],c["high"],c["low"]
    level=breakout_level(high,c.get("lookback",20)); a=atr(high,low,close,14)
    if level is None or a is None: return None
    if close[-1]>level and (close[-1]-level)>=a*Decimal("0.1"):
        return _signal(instrument,"BUY",close[-1],close[-1]-a,close[-1]+a*Decimal("2"),["Prior-high breakout","Volatility expansion confirmation"],"volatility-breakout")
    return None
