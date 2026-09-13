from decimal import Decimal
from primeaura.research.evaluation import evaluate_r_multiples

def test_metrics_are_calculated_from_r_multiples():
    m=evaluate_r_multiples([Decimal("2"),Decimal("-1"),Decimal("3"),Decimal("-0.5")])
    assert m.trades==4 and m.wins==2 and m.losses==2 and m.net_r==Decimal("3.5") and m.profit_factor==Decimal("10")/Decimal("3")
def test_empty_results_are_safe():
    m=evaluate_r_multiples([]); assert m.trades==0 and m.win_rate==0 and m.profit_factor is None
