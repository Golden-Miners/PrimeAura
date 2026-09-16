from decimal import Decimal

def sma(values:list[Decimal],period:int)->Decimal|None:
    if len(values)<period: return None
    return sum(values[-period:],Decimal("0"))/Decimal(period)

def ema(values:list[Decimal],period:int)->Decimal|None:
    if len(values)<period: return None
    k=Decimal("2")/Decimal(period+1)
    value=sum(values[:period],Decimal("0"))/Decimal(period)
    for price in values[period:]:
        value=(price-value)*k+value
    return value

def atr(high:list[Decimal],low:list[Decimal],close:list[Decimal],period:int=14)->Decimal|None:
    if len(close)<period+1: return None
    trs=[]
    for i in range(1,len(close)):
        trs.append(max(high[i]-low[i],abs(high[i]-close[i-1]),abs(low[i]-close[i-1])))
    return sum(trs[-period:],Decimal("0"))/Decimal(period)

def breakout_level(high:list[Decimal],lookback:int=20)->Decimal|None:
    if len(high)<=lookback: return None
    return max(high[-lookback-1:-1])

def momentum(close:list[Decimal],lookback:int=10)->Decimal|None:
    if len(close)<=lookback or close[-lookback]==0: return None
    return (close[-1]-close[-lookback])/close[-lookback]
