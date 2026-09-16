from decimal import Decimal
from .technical import atr,breakout_level,momentum,sma

def _signal(instrument,direction,entry,sl,tp,reasoning,strategy_id):
    risk=abs(entry-sl); rr=abs(tp-entry)/risk if risk else Decimal("0")
    if rr<Decimal("2"): return None
    return {"instrument":instrument,"direction":direction,"strategy_id":strategy_id,"entry":entry,"stop_loss":sl,"tp1":tp,"rr":rr,"reasoning":reasoning}

def momentum_continuation(instrument,c):
    close,high,low=c["close"],c["high"],c["low"]; a=atr(high,low,close,c.get("atr_period",14)); m=momentum(close,c.get("momentum_lookback",10))
    if a is None or m is None: return None
    ma=sma(close,20)
    if ma is None: return None
    if m>c.get("momentum_threshold",Decimal("0.003")) and close[-1]>ma:
        return _signal(instrument,"BUY",close[-1],close[-1]-a,close[-1]+a*Decimal("2"),["Positive momentum","Price above SMA20","ATR risk model"],"momentum")
    if m<-c.get("momentum_threshold",Decimal("0.003")) and close[-1]<ma:
        return _signal(instrument,"SELL",close[-1],close[-1]+a,close[-1]-a*Decimal("2"),["Negative momentum","Price below SMA20","ATR risk model"],"momentum")
    return None

def volatility_breakout(instrument,c):
    close,high,low=c["close"],c["high"],c["low"]; a=atr(high,low,close,14)
    if a is None: return None
    upper=breakout_level(high,c.get("lookback",20)); lower=min(low[-21:-1]) if len(low)>20 else None
    if upper is not None and close[-1]>upper and close[-1]-upper>=a*Decimal("0.1"):
        return _signal(instrument,"BUY",close[-1],close[-1]-a,close[-1]+a*Decimal("2"),["Prior-high breakout","Volatility expansion confirmation"],"volatility-breakout")
    if lower is not None and close[-1]<lower and lower-close[-1]>=a*Decimal("0.1"):
        return _signal(instrument,"SELL",close[-1],close[-1]+a,close[-1]-a*Decimal("2"),["Prior-low breakdown","Volatility expansion confirmation"],"volatility-breakout")
    return None
