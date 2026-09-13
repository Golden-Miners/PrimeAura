from decimal import Decimal
from primeaura.research.evaluation import EvaluationMetrics
from primeaura.research.validation import ValidationPolicy,validate

def m(trades=120,pf=Decimal("1.5"),net=Decimal("10"),dd=Decimal("8")):
 return EvaluationMetrics(trades,70,50,Decimal("58.3"),net,Decimal("0.08"),dd,pf)
def test_strong_result_is_accepted():
 d=validate(m(),3); assert d.accepted and d.status=="VALIDATED"
def test_weak_result_is_rejected():
 d=validate(m(trades=20,pf=Decimal("0.9"),net=Decimal("-2")),3); assert not d.accepted and d.status=="REJECTED" and d.reasons
