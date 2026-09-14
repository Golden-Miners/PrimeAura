from primeaura.research.mt5_runner import MT5ResearchRunner
class P:
 def history(self,request): return []
class R:
 def run(self,instrument,bars): return type('Report',(),{'runs':()})()
def test_mt5_runner_is_read_only_orchestration():
 r=MT5ResearchRunner(P(),R()).run('XAUUSD')
 assert r.instrument=='XAUUSD' and r.bars==0 and r.report.runs==()
