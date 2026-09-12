from .models import BacktestMetrics, ValidationResult

def validate_out_of_sample(metrics: BacktestMetrics, min_trades: int=100, min_profit_factor: float=1.0) -> ValidationResult:
    passed=metrics.trade_count>=min_trades and metrics.profit_factor>=min_profit_factor and metrics.net_pnl>0
    notes=[]
    if metrics.trade_count<min_trades: notes.append("Insufficient trade count")
    if metrics.profit_factor<min_profit_factor: notes.append("Profit factor below threshold")
    if metrics.net_pnl<=0: notes.append("Non-positive net PnL")
    return ValidationResult(stage="OUT_OF_SAMPLE",passed=passed,metrics=metrics,notes=tuple(notes))
