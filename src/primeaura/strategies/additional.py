from decimal import Decimal
from .technical import atr, ema

def ema_crossover(instrument,c):
    close,high,low=c["close"],c["high"],c["low"]
    fast=ema(close,9); slow=ema(close,21); a=atr(high,low,close,14)
    if fast is None or slow is None or a is None or len(close)<22: return None
    prev_fast=ema(close[:-1],9); prev_slow=ema(close[:-1],21)
    if prev_fast is None or prev_slow is None: return None
    if prev_fast<=prev_slow and fast>slow:
        e=close[-1]; sl=e-a; return {"instrument":instrument,"direction":"BUY","strategy_id":"ema-crossover","entry":e,"stop_loss":sl,"tp1":e+2*a,"rr":Decimal("2"),"reasoning":["EMA9 crossed above EMA21","ATR stop model","2R target"]}
    if prev_fast>=prev_slow and fast<slow:
        e=close[-1]; sl=e+a; return {"instrument":instrument,"direction":"SELL","strategy_id":"ema-crossover","entry":e,"stop_loss":sl,"tp1":e-2*a,"rr":Decimal("2"),"reasoning":["EMA9 crossed below EMA21","ATR stop model","2R target"]}
    return None

def liquidity_sweep_ifvg(instrument,c):
    close,high,low=c["close"],c["high"],c["low"]
    a=atr(high,low,close,14)
    if a is None or len(close)<25: return None
    prior_high=max(high[-21:-1]); prior_low=min(low[-21:-1]); e=close[-1]
    # Current candle sweeps a recent liquidity extreme and closes back inside.
    if high[-1]>prior_high and e<prior_high and len(low)>=3 and low[-2]>high[-4]:
        sl=high[-1]+a*Decimal("0.1"); return {"instrument":instrument,"direction":"SELL","strategy_id":"liquidity-sweep-ifvg","entry":e,"stop_loss":sl,"tp1":e-a*Decimal("2"),"rr":Decimal("2"),"reasoning":["Buy-side liquidity swept","Bearish inverse FVG-style gap evidence","2R ATR target"]}
    if low[-1]<prior_low and e>prior_low and len(high)>=3 and high[-2]<low[-4]:
        sl=low[-1]-a*Decimal("0.1"); return {"instrument":instrument,"direction":"BUY","strategy_id":"liquidity-sweep-ifvg","entry":e,"stop_loss":sl,"tp1":e+a*Decimal("2"),"rr":Decimal("2"),"reasoning":["Sell-side liquidity swept","Bullish inverse FVG-style gap evidence","2R ATR target"]}
    return None
