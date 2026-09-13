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
scan_count = st.sidebar.number_input("Bars per timeframe", min_value=100, max_value=2000, value=500, step=100)

if st.sidebar.button("Scan MT5 now", type="primary"):
    try:
        from src.primeaura.scanner.live import LiveScanner
        symbols = tuple(x.strip() for x in instrument_text.split(",") if x.strip())
        if not symbols:
            st.error("Enter at least one symbol.")
        else:
            scanner = LiveScanner()
            created = []
            for symbol in symbols:
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

for symbol in sorted(diagnostics):
    if instrument != "All" and symbol != instrument:
        continue
    with st.expander(f"{symbol} — Why no signal?"):
        for d in diagnostics[symbol]:
            st.markdown(f"**{d['direction']}**")
            passed = d.get("passed", [])
            missing = d.get("missing", [])
            st.write("Passed: " + (", ".join(passed) if passed else "None"))
            st.write("Missing: " + (", ".join(missing) if missing else "None"))
            if not missing:
                st.success("All confluence requirements passed; signal-generation/RR gates decide the final result.")

if filtered:
    for r in filtered:
        with st.container(border=True):
            a, b, c, d = st.columns(4)
            a.metric("Instrument", r.get("instrument", "—"))
            b.metric("Direction", r.get("direction", "—"))
            c.metric("Entry", r.get("entry", "—"))
            d.metric("RR", r.get("rr", "—"))
            st.write(
                f"**Strategy:** {r.get('strategy_id', '—')} v{r.get('strategy_version', '—')} "
                f"| **Confidence:** {r.get('confidence', '—')}"
            )
            st.write(f"**SL:** {r.get('stop_loss', '—')} | **TP:** {r.get('take_profit', '—')}")
            st.write(f"**Thesis:** {r.get('thesis', '—')}")
            if r.get("confluences"):
                st.write("**Confluences:** " + ", ".join(r["confluences"]))
            if r.get("risk_factors"):
                st.write("**Risk factors:** " + ", ".join(r["risk_factors"]))
            st.caption(f"{r.get('timestamp', '')} • {r.get('status', '')}")
