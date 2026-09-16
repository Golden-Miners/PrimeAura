from datetime import datetime, timedelta
from ..data.models import OHLCVBar
from ..signals.models import Signal
from ..scanner.pipeline import generate_from_bars
from .metrics import calculate_metrics
from .models import BacktestMetrics, TradeResult
from .replay import resolve_signal_on_bars, run_replay
from .engine import ExecutionCosts

_TIMEFRAME_MINUTES={"M5":5,"M15":15,"H1":60}

def _closed_as_of(bars,decision_time,timeframe):
    duration=timedelta(minutes=_TIMEFRAME_MINUTES[timeframe])
    return [bar for bar in bars if bar.timestamp+duration<=decision_time]

def _future_after(bars,decision_time):
    return [bar for bar in bars if bar.timestamp>=decision_time]

def run_historical(instrument,bars_by_tf,warmup=250,max_signals=None):
    m5=sorted(bars_by_tf["M5"],key=lambda x:x.timestamp); h1=sorted(bars_by_tf["H1"],key=lambda x:x.timestamp); m15=sorted(bars_by_tf["M15"],key=lambda x:x.timestamp)
    paired=[]; last_exit_time=None; last_decision_time=None
    for i in range(warmup,len(m5)):
        decision_bar=m5[i]; decision_time=decision_bar.timestamp+timedelta(minutes=5)
        if last_decision_time is not None and decision_bar.timestamp<=last_decision_time: continue
        if last_exit_time is not None and decision_time<last_exit_time: continue
        history={"H1":_closed_as_of(h1,decision_time,"H1")[-500:],"M15":_closed_as_of(m15,decision_time,"M15")[-500:],"M5":m5[max(0,i-499):i]}
        if min(map(len,history.values()))<20: continue
        signals=generate_from_bars(instrument,history,decision_time=decision_time)
        if not signals: continue
        future=_future_after(m5,decision_time)
        for signal in signals:
            if signal.timestamp!=decision_time: continue
            result=resolve_signal_on_bars(signal,future)
            if result is not None:
                paired.append((signal,result)); last_exit_time=decision_time+timedelta(minutes=5*result.bars_held); last_decision_time=decision_time
                if max_signals is not None and len(paired)>=max_signals: return tuple(paired),calculate_metrics([x[1] for x in paired])
    return tuple(paired),calculate_metrics([x[1] for x in paired])

def split_train_test(start,end,train_ratio=0.7):
    if start.tzinfo is None or end.tzinfo is None or start>=end or not 0<train_ratio<1: raise ValueError("invalid train/test interval")
    split=start+(end-start)*train_ratio
    return (start,split),(split,end)

def split_trade_results_by_time(paired,split_time):
    train=[]; test=[]
    for signal,result in paired:
        if signal.timestamp is None: continue
        (train if signal.timestamp<split_time else test).append((signal,result))
    return tuple(train),tuple(test)

def build_walk_forward_windows(start,end,train_days,test_days):
    if start.tzinfo is None or end.tzinfo is None or start>=end or train_days<=0 or test_days<=0: raise ValueError("invalid walk-forward interval")
    train_delta=timedelta(days=train_days); test_delta=timedelta(days=test_days); cursor=start; windows=[]
    while cursor+train_delta+test_delta<=end:
        train_end=cursor+train_delta; test_end=train_end+test_delta; windows.append((cursor,train_end,train_end,test_end)); cursor=test_end
    return tuple(windows)

def evaluate_walk_forward_oos(bars_by_tf,windows,instrument,warmup=250):
    results=[]; all_oos=[]
    for _,_,test_start,test_end in windows:
        capped={tf:[bar for bar in sorted(bars,key=lambda x:x.timestamp) if bar.timestamp<=test_end] for tf,bars in bars_by_tf.items()}
        paired,_=run_historical(instrument,capped,warmup=warmup); window=[]
        for signal,trade in paired:
            if signal.timestamp is None: continue
            exit_time=signal.timestamp+timedelta(minutes=5*trade.bars_held)
            if test_start<=signal.timestamp<test_end and exit_time<=test_end: window.append((signal,trade)); all_oos.append((signal,trade))
        results.append(tuple(window))
    return windows,tuple(results),calculate_metrics([trade for _,trade in all_oos])

def summarize_walk_forward_oos(window_results):
    metrics=[calculate_metrics([trade for _,trade in trades]) for trades in window_results]; evaluated=[m for m in metrics if m.trade_count>0]; positive=sum(m.net_pnl>0 for m in evaluated)
    return {"windows_total":len(metrics),"windows_with_trades":len(evaluated),"windows_positive":positive,"windows_negative":len(evaluated)-positive,"all_evaluated_positive":bool(evaluated) and positive==len(evaluated)}

def cost_stress_results(signals,scenarios):
    return tuple((name,calculate_metrics(list(run_replay(signals,costs)))) for name,costs in scenarios)

def walk_forward_cost_stress(bars_by_tf,windows,instrument,scenarios,warmup=250):
    rows=[]
    for window_index,(_,_,test_start,test_end) in enumerate(windows,start=1):
        capped={tf:[bar for bar in sorted(bars,key=lambda x:x.timestamp) if bar.timestamp<=test_end] for tf,bars in bars_by_tf.items()}
        paired,_=run_historical(instrument,capped,warmup=warmup); oos=[]
        for signal,_ in paired:
            if signal.timestamp is None: continue
            exit_time=signal.timestamp+timedelta(minutes=5)
            if test_start<=signal.timestamp<test_end and exit_time<=test_end: oos.append((signal,[bar for bar in capped["M5"] if bar.timestamp>=signal.timestamp]))
        for name,costs in scenarios:
            m=calculate_metrics(list(run_replay(oos,costs))); rows.append({"window":window_index,"scenario":name,"trades":m.trade_count,"net_pnl":str(m.net_pnl),"win_rate":str(m.win_rate),"profit_factor":str(m.profit_factor),"max_drawdown":str(m.max_drawdown)})
    return tuple(rows)
