from decimal import Decimal

def trend_pullback(instrument:str, c:dict):
    """Conservative adapter: emits only when supplied context explicitly confirms trend/pullback."""
    if c.get("trend") in ("BULLISH","BEARISH") and c.get("pullback_confirmed") and c.get("rr",Decimal("0"))>=Decimal("2"):
        return {"instrument":instrument,"direction":"BUY" if c["trend"]=="BULLISH" else "SELL","strategy_id":"trend-pullback","entry":c["entry"],"stop_loss":c["stop_loss"],"tp1":c["tp1"],"reasoning":["Higher-timeframe trend confirmed","Pullback confirmed","RR gate passed"]}
    return None

def breakout_retest(instrument:str,c:dict):
    """Conservative adapter: requires explicit breakout, retest and continuation evidence."""
    if c.get("breakout_confirmed") and c.get("retest_confirmed") and c.get("continuation_confirmed") and c.get("rr",Decimal("0"))>=Decimal("2"):
        return {"instrument":instrument,"direction":c.get("direction"),"strategy_id":"breakout-retest","entry":c["entry"],"stop_loss":c["stop_loss"],"tp1":c["tp1"],"reasoning":["Breakout confirmed","Retest confirmed","Continuation confirmed","RR gate passed"]}
    return None
