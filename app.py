from datetime import datetime, timedelta, time, timezone
from pathlib import Path
import json
import streamlit as st

from src.primeaura.scanner.clock import local_now
from src.primeaura.scanner.live import LiveScanner
from src.primeaura.scanner.multi_strategy import STRATEGIES
from src.primeaura.scanner.strategy_diagnostic_store import StrategyDiagnosticStore

st.set_page_config(page_title="PrimeAura",page_icon="◆",layout="wide")
st.title("PrimeAura")
st.caption("Read-only trading signal intelligence • MT5 data • no broker connection • no order execution")

def load_signals():
    p=Path("data/signals/signal_history.jsonl")
    if not p.exists(): return []
    with p.open(encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()][::-1]

def load_strategy_diag():
    return StrategyDiagnosticStore().load()

def scan(symbols,strategies,bars):
    scanner=LiveScanner(); reports=[]; status={}
    for symbol in symbols:
        created,results=scanner.scan(symbol,bars,strategies)
        reports.extend(created)
        status[symbol]=[{"strategy_id":r.strategy_id,"status":r.status,"has_signal":r.signal is not None,"reason":r.reason} for r in results]
    return reports,status

st.sidebar.header("Scanner")
symbols=tuple(x.strip().upper() for x in st.sidebar.text_input("Instruments","XAUUSD, XAGUSD").split(",") if x.strip())
strategy_options=list(STRATEGIES)
strategies=tuple(st.sidebar.multiselect("Strategies",strategy_options,default=strategy_options))
bars=st.sidebar.number_input("Closed bars / timeframe",min_value=100,max_value=2000,value=500,step=100)
auto=st.sidebar.toggle("Auto scan",value=False)
interval=st.sidebar.selectbox("Auto-scan interval",["5 minutes","15 minutes","30 minutes"],index=0)
interval_seconds={"5 minutes":300,"15 minutes":900,"30 minutes":1800}[interval]

st.sidebar.caption(f"Machine local time: {local_now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
if st.sidebar.button("Scan MT5 now",type="primary"):
    if not symbols: st.error("Select at least one instrument.")
    elif not strategies: st.error("Select at least one strategy.")
    else:
        try:
            created,status=scan(symbols,strategies,int(bars))
            st.success(f"Scan completed at {local_now().strftime('%H:%M:%S %Z')}: {len(created)} new signal(s).")
            st.rerun()
        except Exception as exc:
            st.error(f"MT5 scan failed: {type(exc).__name__}: {exc}")

st.subheader("Live Scanner")

@st.fragment(run_every=interval_seconds if auto else None)
def live_scan_panel():
    if auto and symbols and strategies:
        try:
            created,status=scan(symbols,strategies,int(bars))
            if created:
                st.success(f"Automatic scan: {len(created)} signal(s) detected at {local_now().strftime('%H:%M:%S %Z')}.")
            else:
                st.info(f"Automatic scan completed at {local_now().strftime('%H:%M:%S %Z')}: no qualifying setup.")
        except Exception as exc:
            st.error(f"Automatic scan error: {type(exc).__name__}: {exc}")
    else:
        st.write("Auto scan is OFF. Use **Scan MT5 now** for an immediate scan.")

live_scan_panel()

rows=load_signals()
strategy_diag=load_strategy_diag()

c1,c2,c3,c4=st.columns(4)
c1.metric("Signals",len(rows))
c2.metric("Active",sum(r.get("status")=="ACTIVE" for r in rows))
c3.metric("Instruments",len({r.get("instrument") for r in rows}))
c4.metric("Strategies",len({r.get("strategy_id") for r in rows}))

st.subheader("Latest Signals")
if not rows:
    st.warning("No signal has been recorded yet. Run a scan. If none qualifies, the strategy-by-strategy diagnostics below will show exactly why.")
else:
    for r in rows[:30]:
        with st.container(border=True):
            a,b,c,d=st.columns(4)
            a.metric("Instrument",r.get("instrument","—"))
            b.metric("Direction",r.get("direction","—"))
            c.metric("Entry",r.get("entry","—"))
            d.metric("RR1",r.get("rr","—"))
            st.write(f"**Strategy:** {r.get('strategy_id','—')} v{r.get('strategy_version','—')} • **Confidence:** {r.get('confidence','—')}")
            st.write(f"**SL:** {r.get('stop_loss','—')} • **TP1:** {r.get('take_profit','—')} • **TP2:** {r.get('take_profit_2','—')} • **RR2:** {r.get('rr_2','—')}")
            st.write(f"**Reasoning:** {r.get('thesis','—')}")
            if r.get("risk_factors"): st.write("**Risk:** "+", ".join(r["risk_factors"]))
            st.caption(f"Detected: {r.get('timestamp','—')} • {r.get('status','')}")

st.subheader("Strategy Scanner Diagnostics")
st.caption("Every selected strategy is evaluated independently. 'No setup' is different from 'not implemented' or 'error'.")
for symbol in symbols:
    items=strategy_diag.get(symbol,[])
    if not items:
        continue
    with st.expander(symbol,expanded=True):
        for item in items:
            if item["has_signal"]:
                st.success(f"{item['strategy_id']} — SIGNAL • {item['status']}")
            elif item["status"]=="ERROR":
                st.error(f"{item['strategy_id']} — ERROR • {item['reason']}")
            else:
                st.info(f"{item['strategy_id']} — {item['status']} • {item['reason']}")

st.subheader("SMC Confluence Diagnostics")
diagnostic_path=Path("data/signals/scan_diagnostics.json")
if diagnostic_path.exists():
    diagnostics=json.loads(diagnostic_path.read_text(encoding="utf-8"))
    for symbol in symbols:
        for d in diagnostics.get(symbol,[]):
            with st.expander(f"{symbol} {d['direction']} — {d['final_gate']}"):
                st.write("Passed:",", ".join(d.get("passed",[])) or "None")
                st.write("Missing:",", ".join(d.get("missing",[])) or "None")
                st.write("Evidence:",d.get("evidence_counts",{}))
else:
    st.caption("Run a scan to populate SMC diagnostics.")

st.subheader("Research Strategy Catalog")
st.write("Current signal-capable research strategies:")
st.write(", ".join(strategy_options))
st.caption("A strategy is not labelled profitable merely because it generated a signal. Profitability requires out-of-sample and robustness validation.")

st.divider()
st.header("Historical SMC Backtest")
st.caption("The current backtest runner validates the locked SMC engine chronologically using closed MT5 candles. Other strategies are being scanned live independently and will receive dedicated backtest runners before promotion.")

bt_symbol=st.selectbox("Instrument",list(symbols) or ["XAUUSD"],key="bt_symbol")
bt_start=st.date_input("Start date",value=(local_now().date()-timedelta(days=60)),key="bt_start")
bt_end=st.date_input("End date",value=local_now().date(),key="bt_end")
if st.button("Run SMC historical backtest"):
    if bt_start>=bt_end:
        st.error("End date must be after start date.")
    else:
        try:
            from src.primeaura.data.market_service import MarketDataService
            from src.primeaura.backtest.runner import run_historical
            start=datetime.combine(bt_start,time.min,tzinfo=timezone.utc)
            end=datetime.combine(bt_end,time.max,tzinfo=timezone.utc)
            service=MarketDataService(); service.connect()
            try:
                historical=service.fetch_multi_timeframe_range(bt_symbol,start-timedelta(days=30),end)
            finally:
                service.close()
            trades,metrics=run_historical(bt_symbol,historical)
            a,b,c,d,e=st.columns(5)
            a.metric("Trades",metrics.trade_count); b.metric("Win rate",f"{metrics.win_rate:.2f}%"); c.metric("Net P&L",str(metrics.net_pnl)); d.metric("Profit factor",str(metrics.profit_factor)); e.metric("Max DD",str(metrics.max_drawdown))
        except Exception as exc:
            st.error(f"Backtest failed: {type(exc).__name__}: {exc}")
