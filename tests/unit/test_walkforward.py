from datetime import datetime,timezone
from decimal import Decimal
from primeaura.data.models import OHLCVBar
from primeaura.research.walkforward import make_folds

def test_folds_are_forward_only():
    f=make_folds(100,60,20,20)
    assert f and all(x.train_end==x.test_start for x in f)
    assert all(a.test_end<=b.train_start for a,b in zip(f,f[1:]))
def test_insufficient_data_returns_no_folds():
    assert make_folds(10,8,4)==()
