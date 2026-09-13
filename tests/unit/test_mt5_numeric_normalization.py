from decimal import Decimal
from primeaura.data.mt5 import _decimal

def test_mt5_numeric_values_become_decimal():
    assert _decimal(123.45) == Decimal("123.45")
    assert _decimal(3003) == Decimal("3003")
