from primeaura.research.experiment_store import ExperimentEvidence,ExperimentStore

def test_evidence_is_persisted(tmp_path):
 s=ExperimentStore(str(tmp_path/"e.jsonl")); s.record(ExperimentEvidence("e1","gold","5","7","VALIDATED","ACCEPTED",("walk-forward",)))
 rows=s.all(); assert rows[0]["experiment_id"]=="e1" and rows[0]["challenger_net_r"]=="7"
