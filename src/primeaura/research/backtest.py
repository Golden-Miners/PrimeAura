from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class BacktestStats:
    trades:int
    wins:int
    losses:int
    net_r:Decimal
    win_rate:Decimal
    expectancy_r:Decimal

class SimpleSignalBacktester:
    """Deterministic event backtester. Uses only future bars after a signal; no look-ahead."""
    def run(self,bars,signals)->BacktestStats:
        wins=losses=0; net=Decimal("0")
        for sig in signals:
            future=[b for b in bars if b.timestamp>sig.detected_at]
            result=None
            for b in future:
                if sig.direction=="BUY":
                    if b.low<=sig.stop_loss: result=Decimal("-1"); break
                    if b.high>=sig.tp1: result=Decimal("1") ; break
                else:
                    if b.high>=sig.stop_loss: result=Decimal("-1"); break
                    if b.low<=sig.tp1: result=Decimal("1"); break
            if result is None: continue
            net+=result
            wins += result>0; losses += result<0
        trades=wins+losses
        wr=Decimal(wins)/Decimal(trades) if trades else Decimal("0")
        exp=net/Decimal(trades) if trades else Decimal("0")
        return BacktestStats(trades,wins,losses,net,wr,exp)
