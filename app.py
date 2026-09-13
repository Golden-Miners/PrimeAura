import streamlit as st
from pathlib import Path
import json

st.set_page_config(page_title="PrimeAura", page_icon="◆", layout="wide")
st.title("PrimeAura")
st.caption("Read-only trading signal intelligence — no order execution")

root=Path("data/signals/signal_history.jsonl")
rows=[]
if root.exists():
    with root.open(encoding="utf-8") as f:
        rows=[json.loads(x) for x in f if x.strip()][::-1]

st.sidebar.header("Filters")
instruments=sorted({r.get("instrument","") for r in rows})
strategies=sorted({r.get("strategy_id","") for r in rows})
instrument=st.sidebar.selectbox("Instrument",["All",*instruments])
strategy=st.sidebar.selectbox("Strategy",["All",*strategies])

filtered=[r for r in rows if (instrument=="All" or r.get("instrument")==instrument) and (strategy=="All" or r.get("strategy_id")==strategy)]

c1,c2,c3=st.columns(3)
c1.metric("Signals",len(filtered))
c2.metric("Active",sum(r.get("status")=="ACTIVE" for r in filtered))
c3.metric("Strategies",len({r.get("strategy_id") for r in filtered}))

st.subheader("Latest Signals")
if not filtered:
    st.info("No signals recorded yet. Connect the MT5 scanner after the signal engine is validated.")
else:
    for r in filtered:
        with st.container(border=True):
            a,b,c,d=st.columns(4)
            a.metric("Instrument",r.get("instrument","—"))
            b.metric("Direction",r.get("direction","—"))
            c.metric("Entry",r.get("entry","—"))
            d.metric("RR",r.get("rr","—"))
            st.write(f"**Strategy:** {r.get('strategy_id','—')} v{r.get('strategy_version','—')}  |  **Confidence:** {r.get('confidence','—')}")
            st.write(f"**SL:** {r.get('stop_loss','—')}  |  **TP:** {r.get('take_profit','—')}")
            st.write(f"**Thesis:** {r.get('thesis','—')}")
            if r.get("confluences"): st.write("**Confluences:** " + ", ".join(r["confluences"]))
            if r.get("risk_factors"): st.write("**Risk factors:** " + ", ".join(r["risk_factors"]))
            st.caption(f"{r.get('timestamp','')} • {r.get('status','')}")
