from primeaura.strategies.strategy_runner import MultiStrategyEngine

def test_each_strategy_is_attributed_independently():
 e=MultiStrategyEngine({"trend-pullback":lambda i,c:{"strategy":"trend-pullback"}})
 results=e.evaluate("XAUUSD",{})
 assert any(x.strategy_id=="trend-pullback" and x.signal for x in results)
 assert any(x.strategy_id=="breakout-retest" and x.signal is None for x in results)

def test_strategy_failure_does_not_stop_other_strategies():
 def bad(i,c): raise RuntimeError("boom")
 e=MultiStrategyEngine({"trend-pullback":bad,"momentum":lambda i,c:"ok"})
 results=e.evaluate("XAUUSD",{})
 assert results[0].signal is None and "error" in results[0].reason
 assert any(x.strategy_id=="momentum" and x.signal=="ok" for x in results)
