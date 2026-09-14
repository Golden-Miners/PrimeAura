import json
from pathlib import Path
from datetime import date, timedelta

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
                counts = d.get("evidence_counts")
                if counts:
                    st.caption(
                        "Evidence: "
                        + " | ".join(f"{name}={value}" for name, value in counts.items())
                    )
                latest = d.get("latest_bars")
                if latest:
                    st.caption(
                        "Latest closed bars (UTC): "
                        + " | ".join(f"{tf}={value}" for tf, value in latest.items())
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

bt_symbol = st.selectbox("Backtest instrument", ["XAUUSD", "XAGUSD", "BTCUSD"], key="bt_symbol")
bt_default_end = date.today()
bt_default_start = bt_default_end - timedelta(days=30)
bt_start = st.date_input("Start date", value=bt_default_start, key="bt_start")
bt_end = st.date_input("End date", value=bt_default_end, key="bt_end")
wf_train_days = st.number_input("Walk-forward context days", min_value=1, max_value=365, value=14, step=1, key="wf_train_days")
wf_test_days = st.number_input("Walk-forward OOS days", min_value=1, max_value=90, value=7, step=1, key="wf_test_days")

st.subheader("Execution-cost stress assumptions")
st.caption("Enter price-unit costs for one side of the trade. These are research assumptions, not broker quotes.")
base_spread = st.number_input("Base spread (price units)", min_value=0.0, value=0.0, step=0.1, format="%.4f", key="bt_spread")
base_slippage = st.number_input("Base slippage (price units)", min_value=0.0, value=0.0, step=0.1, format="%.4f", key="bt_slippage")
base_fee = st.number_input("Base fee per completed trade (price units)", min_value=0.0, value=0.0, step=0.1, format="%.4f", key="bt_fee")

if st.button("Run historical backtest", type="primary"):
    if bt_start >= bt_end:
        st.error("End date must be after start date.")
    else:
        try:
            from datetime import datetime, time, timezone
            from src.primeaura.backtest.engine import ExecutionCosts
            from src.primeaura.backtest.runner import build_walk_forward_windows, cost_stress_results, evaluate_walk_forward_oos, run_historical, summarize_walk_forward_oos, walk_forward_cost_stress
            from src.primeaura.data.market_service import MarketDataService

            start = datetime.combine(bt_start, time.min, tzinfo=timezone.utc)
            end = datetime.combine(bt_end, time.max, tzinfo=timezone.utc)
            data_start = start - timedelta(days=30)

            service = MarketDataService()
            service.connect()
            try:
                with st.spinner("Loading historical MT5 data and replaying the strategy..."):
                    historical = service.fetch_multi_timeframe_range(bt_symbol, data_start, end)
                    from src.primeaura.data.integrity import validate_multitimeframe
                    integrity = validate_multitimeframe(historical)
                    st.subheader("Historical data integrity")
                    if integrity["valid"]:
                        st.success("PASS — no integrity violations detected in the fetched MT5 dataset.")
                    else:
                        st.error("FAIL — backtest blocked because the fetched MT5 dataset has integrity violations.")
                        for tf, issues in integrity["issues"].items():
                            st.write(f"**{tf}:**")
                            for issue in issues[:20]:
                                st.write(f"- {issue}")
                        st.stop()
                    trades, metrics = run_historical(bt_symbol, historical)
            finally:
                service.close()

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Trades", metrics.trade_count)
            m2.metric("Win rate", f"{metrics.win_rate:.2f}%")
            m3.metric("Net P&L", str(metrics.net_pnl))
            m4.metric("Profit factor", str(metrics.profit_factor))
            m5.metric("Max drawdown", str(metrics.max_drawdown))

            from src.primeaura.backtest.report import build_report
            from src.primeaura.backtest.runner import split_train_test

            report = build_report([result for _, result in trades])
            (train_start, train_end), (test_start, test_end) = split_train_test(start, end)
            st.subheader("Validation split")
            st.write(
                f"In-sample: {train_start.date()} -> {train_end.date()} | "
                f"Out-of-sample: {test_start.date()} -> {test_end.date()}"
            )
            from src.primeaura.backtest.runner import split_trade_results_by_time
            from src.primeaura.backtest.metrics import calculate_metrics
            train_trades, test_trades = split_trade_results_by_time(trades, test_start)
            train_metrics = calculate_metrics([r for _, r in train_trades])
            test_metrics = calculate_metrics([r for _, r in test_trades])
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("IS Trades", train_metrics.trade_count)
            s2.metric("IS Win Rate", f"{train_metrics.win_rate:.2f}%")
            s3.metric("OOS Trades", test_metrics.trade_count)
            s4.metric("OOS Win Rate", f"{test_metrics.win_rate:.2f}%")
            o1, o2, o3, o4 = st.columns(4)
            o1.metric("IS Net P&L", str(train_metrics.net_pnl))
            o2.metric("IS Profit Factor", str(train_metrics.profit_factor))
            o3.metric("OOS Net P&L", str(test_metrics.net_pnl))
            o4.metric("OOS Profit Factor", str(test_metrics.profit_factor))

            from src.primeaura.backtest.report import build_report
            is_report = build_report([r for _, r in train_trades])
            oos_report = build_report([r for _, r in test_trades])
            st.subheader("Validation risk")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("IS Max Drawdown", str(train_metrics.max_drawdown))
            r2.metric("OOS Max Drawdown", str(test_metrics.max_drawdown))
            r3.metric("IS P&L / DD", str(is_report.metrics.net_pnl / train_metrics.max_drawdown if train_metrics.max_drawdown else "—"))
            r4.metric("OOS P&L / DD", str(oos_report.metrics.net_pnl / test_metrics.max_drawdown if test_metrics.max_drawdown else "—"))

            if oos_report.equity_curve:
                st.subheader("Out-of-Sample Equity Curve")
                st.line_chart({
                    "OOS Cumulative P&L": [
                        float(point.cumulative_pnl) for point in oos_report.equity_curve
                    ]
                })
                st.line_chart({
                    "OOS Drawdown": [
                        float(point.drawdown) for point in oos_report.equity_curve
                    ]
                })
            if report.equity_curve:
                st.subheader("Equity Curve")
                st.line_chart({
                    "Cumulative P&L": [float(point.cumulative_pnl) for point in report.equity_curve]
                })
                st.line_chart({
                    "Drawdown": [float(point.drawdown) for point in report.equity_curve]
                })

            wf_windows = build_walk_forward_windows(start, end, int(wf_train_days), int(wf_test_days))
            if wf_windows:
                _, wf_results, wf_metrics = evaluate_walk_forward_oos(historical, wf_windows, bt_symbol)
                st.subheader("Walk-forward OOS robustness")
                st.caption("Rules remain fixed. The context period is not optimized; only completed trades wholly inside each OOS window are counted.")
                w1, w2, w3, w4 = st.columns(4)
                w1.metric("OOS Windows", len(wf_windows))
                w2.metric("OOS Trades", wf_metrics.trade_count)
                w3.metric("OOS Win Rate", f"{wf_metrics.win_rate:.2f}%")
                w4.metric("OOS Net P&L", str(wf_metrics.net_pnl))
                wf_summary = summarize_walk_forward_oos(wf_results)
                c1, c2, c3 = st.columns(3)
                c1.metric("Windows With Trades", wf_summary["windows_with_trades"])
                c2.metric("Positive OOS Windows", wf_summary["windows_positive"])
                c3.metric("Negative OOS Windows", wf_summary["windows_negative"])
                rows = []
                for i, window in enumerate(wf_windows):
                    train_start, train_end, test_start, test_end = window
                    window_trades = wf_results[i]
                    window_metrics = calculate_metrics([r for _, r in window_trades])
                    rows.append({
                        "Window": i + 1,
                        "Context": f"{train_start.date()} -> {train_end.date()}",
                        "OOS": f"{test_start.date()} -> {test_end.date()}",
                        "Trades": window_metrics.trade_count,
                        "Net P&L": str(window_metrics.net_pnl),
                    })
                st.dataframe(rows, use_container_width=True)

                wf_cost_scenarios = tuple(
                    (f"{multiplier}x costs", ExecutionCosts(
                        spread=base_spread * multiplier,
                        slippage=base_slippage * multiplier,
                        fee=base_fee * multiplier,
                    ))
                    for multiplier in (0, 1, 2, 3)
                )
                wf_cost_rows = walk_forward_cost_stress(
                    historical, wf_windows, bt_symbol, wf_cost_scenarios
                )
                st.subheader("Walk-forward OOS cost resilience")
                st.caption("Each cost scenario is evaluated independently inside each unseen OOS window.")
                st.dataframe(wf_cost_rows, use_container_width=True)
            else:
                st.info("The selected date range is too short for the configured walk-forward windows.")

            st.subheader("Execution-cost stress test")
            stress_signals = [
                (signal, [bar for bar in historical.get("M5", []) if signal.timestamp is not None and bar.timestamp >= signal.timestamp])
                for signal, _ in trades
                if signal.timestamp is not None
            ]
            scenarios = tuple(
                (f"{multiplier}x costs", ExecutionCosts(
                    spread=base_spread * multiplier,
                    slippage=base_slippage * multiplier,
                    fee=base_fee * multiplier,
                ))
                for multiplier in (0, 1, 2, 3)
            )
            stress = cost_stress_results(stress_signals, scenarios)
            st.dataframe(
                [
                    {
                        "Scenario": name,
                        "Trades": metrics.trade_count,
                        "Win Rate": f"{metrics.win_rate:.2f}%",
                        "Net P&L": str(metrics.net_pnl),
                        "Max Drawdown": str(metrics.max_drawdown),
                        "Profit Factor": str(metrics.profit_factor),
                    }
                    for name, metrics in stress
                ],
                use_container_width=True,
            )

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
