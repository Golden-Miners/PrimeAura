from decimal import Decimal
from .models import BacktestMetrics, TradeResult

def calculate_metrics(trades: list[TradeResult]) -> BacktestMetrics:
    if not trades: return BacktestMetrics(trade_count=0,wins=0,losses=0,win_rate=Decimal(0),net_pnl=Decimal(0),max_drawdown=Decimal(0),profit_factor=Decimal(0))
    wins=sum(t.pnl>0 for t in trades); losses=sum(t.pnl<0 for t in trades)
    gross_win=sum((t.pnl for t in trades if t.pnl>0),Decimal(0)); gross_loss=-sum((t.pnl for t in trades if t.pnl<0),Decimal(0))
    equity=peak=Decimal(0); dd=Decimal(0)
    for t in trades:
        equity+=t.pnl; peak=max(peak,equity); dd=max(dd,peak-equity)
    pf=gross_win/gross_loss if gross_loss else (Decimal("Infinity") if gross_win else Decimal(0))
    return BacktestMetrics(trade_count=len(trades),wins=wins,losses=losses,win_rate=Decimal(wins)*100/Decimal(len(trades)),net_pnl=sum((t.pnl for t in trades),Decimal(0)),max_drawdown=dd,profit_factor=pf)
