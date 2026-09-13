import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="PrimeAura", page_icon="◆", layout="wide")
st.title("PrimeAura")
st.caption("Read-only trading signal intelligence — no order execution")

root = Path("data/signals/signal_history.jsonl")
diagnostic_root = Path("data/signals/scan_diagnostics.json")

def load_rows():
    if not root.exists():
        return []
    with root.open(encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()][::-1]

def load_diagnostics():
    if not diagnostic_root.exists():
        return {}
    return json.loads(diagnostic_root.read_text(encoding="utf-8"))

st.sidebar.header("Market Scanner")
instrument_text = st.sidebar.text_input("Symbols", "XAUUSD, XAGUSD")
requested_symbols = tuple(x.strip() for x in instrument_text.split(",") if x.strip())
scan_count = st.sidebar.number_input("Bars per timeframe", min_value=100, max_value=2000, value=500, step=100)

if st.sidebar.button("Scan MT5 now", type="primary"):
    try:
        from src.primeaura.scanner.live import LiveScanner
        if not requested_symbols:
            st.error("Enter at least one symbol.")
        else:
            scanner = LiveScanner()
            created = []
            for symbol in requested_symbols:
                created.extend(scanner.scan(symbol, int(scan_count)))
            st.success(f"Scan complete. {len(created)} new signal(s) recorded.")
            st.rerun()
    except Exception as exc:
        st.error(f"MT5 scan failed: {exc}")

rows = load_rows()
diagnostics = load_diagnostics()

st.sidebar.header("Filters")
instruments = sorted({r.get("instrument", "") for r in rows})
strategies = sorted({r.get("strategy_id", "") for r in rows})
instrument = st.sidebar.selectbox("Instrument", ["All", *instruments])
strategy = st.sidebar.selectbox("Strategy", ["All", *strategies])

filtered = [
    r for r in rows
    if (instrument == "All" or r.get("instrument") == instrument)
    and (strategy == "All" or r.get("strategy_id") == strategy)
]

c1, c2, c3 = st.columns(3)
c1.metric("Signals", len(filtered))
c2.metric("Active", sum(r.get("status") == "ACTIVE" for r in filtered))
c3.metric("Strategies", len({r.get("strategy_id") for r in filtered}))

st.subheader("Latest Signals")
if not filtered:
    st.info("No signals recorded yet. A zero-signal scan is valid when the confluence gate is not satisfied.")

st.subheader("Latest Scan Diagnostics")
shown_diagnostics = [s for s in requested_symbols if s in diagnostics]
if not shown_diagnostics:
    st.caption("Run an MT5 scan to populate diagnostics.")
else:
    for symbol in shown_diagnostics:
        with st.expander(f"{symbol} — Why no signal?", expanded=False):
            for d in diagnostics[symbol]:
                st.markdown(f"**{d['direction']}**")
                passed = d.get("passed", [])
                missing = d.get("missing", [])
                st.write("Passed: " + (", ".join(passed) if passed else "None"))
                st.write("Missing: " + (", ".join(missing) if missing else "None"))
                gate = d.get("final_gate", "Unknown")
                if gate.startswith("PASS:"):
                    st.success(gate)
                else:
                    st.warning(gate)
                if d.get("entry") is not None:
                    st.write(
                        f"Entry: {d['entry']} | SL: {d.get('stop_loss', '—')} | "
                        f"TP1: {d.get('tp1', '—')} | RR1: {d.get('rr_tp1', '—')} | "
                        f"TP2: {d.get('tp2', '—')} | RR2: {d.get('rr_tp2', '—')}"
                    )

if filtered:
    for r in filtered:
        with st.container(border=True):
            a, b, c, d = st.columns(4)
            a.metric("Instrument", r.get("instrument", "—"))
            b.metric("Direction", r.get("direction", "—"))
            c.metric("Entry", r.get("entry", "—"))
            d.metric("RR1", r.get("rr", "—"))
            st.write(
                f"**Strategy:** {r.get('strategy_id', '—')} v{r.get('strategy_version', '—')} "
                f"| **Confidence:** {r.get('confidence', '—')}"
            )
            st.write(
                f"**SL:** {r.get('stop_loss', '—')} | **TP1:** {r.get('take_profit', '—')} | "
                f"**TP2:** {r.get('take_profit_2', '—')} | **RR2:** {r.get('rr_2', '—')}"
            )
            st.write(f"**Thesis:** {r.get('thesis', '—')}")
            if r.get("confluences"):
                st.write("**Confluences:** " + ", ".join(r["confluences"]))
            if r.get("risk_factors"):
                st.write("**Risk factors:** " + ", ".join(r["risk_factors"]))
            st.caption(f"{r.get('timestamp', '')} • {r.get('status', '')}")


st.divider()
st.header("Historical Backtest")
st.caption("Read-only historical research using MT5 closed candles. No orders are placed.")

bt_symbol = st.selectbox("Backtest instrument", ["XAUUSD", "XAGUSD"], key="bt_symbol")
from datetime import date, timedelta
bt_default_end = date.today()
bt_default_start = bt_default_end - timedelta(days=30)
bt_start = st.date_input("Start date", value=bt_default_start, key="bt_start")
bt_end = st.date_input("End date", value=bt_default_end, key="bt_end")

if st.button("Run historical backtest", type="primary"):
    if bt_start >= bt_end:
        st.error("End date must be after start date.")
    else:
        try:
            from datetime import datetime, time, timezone
            from src.primeaura.backtest.runner import run_historical
            from src.primeaura.data.market_service import MarketDataService

            start = datetime.combine(bt_start, time.min, tzinfo=timezone.utc)
            end = datetime.combine(bt_end, time.max, tzinfo=timezone.utc)
            data_start = start - timedelta(days=7)

            service = MarketDataService()
            service.connect()
            try:
                with st.spinner("Loading historical MT5 data and replaying the strategy..."):
                    historical = service.fetch_multi_timeframe_range(bt_symbol, data_start, end)
                    trades, metrics = run_historical(bt_symbol, historical)
            finally:
                service.close()

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Trades", metrics.trade_count)
            m2.metric("Win rate", f"{metrics.win_rate:.2f}%")
            m3.metric("Net P&L", str(metrics.net_pnl))
            m4.metric("Profit factor", str(metrics.profit_factor))
            m5.metric("Max drawdown", str(metrics.max_drawdown))

            if not trades:
                st.warning("No completed signals occurred in this period.")
            else:
                st.subheader("Historical trades")
                table = []
                for signal, result in trades:
                    table.append({
                        "Time": signal.timestamp if hasattr(signal, "timestamp") else "—",
                        "Direction": signal.direction,
                        "Entry": str(result.entry),
                        "Exit": str(result.exit),
                        "R": str(result.r_multiple),
                        "Bars": result.bars_held,
                    })
                st.dataframe(table, use_container_width=True)
        except Exception as exc:
            st.error(f"Backtest failed: {exc}")
