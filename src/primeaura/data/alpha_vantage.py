from datetime import datetime

class AlphaVantageMetalProvider:
    """Reference adapter for Alpha Vantage metals data.

    The currently documented GOLD_SILVER_HISTORY endpoint provides a historical
    value series, not the full OHLC bars required by PrimeAura SMC analysis.
    Therefore this adapter deliberately refuses to convert close-only values
    into synthetic OHLC candles.
    """
    ENDPOINT="https://www.alphavantage.co/query"
    SYMBOLS={"XAUUSD":"XAU","XAGUSD":"XAG"}

    def __init__(self, api_key:str):
        if not api_key: raise ValueError("Alpha Vantage API key is required")
        self.api_key=api_key

    def history(self,instrument:str,start:datetime,end:datetime):
        raise NotImplementedError("Alpha Vantage metals history is close/value-only for this adapter; use an OHLC provider for PrimeAura signal research.")
