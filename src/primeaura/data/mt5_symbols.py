class MT5SymbolResolver:
    """Resolve configured logical symbols to broker-specific MT5 symbols."""
    def __init__(self,mt5,aliases=None): self.mt5=mt5; self.aliases=aliases or {}
    def resolve(self,instrument:str)->str:
        candidates=[]
        if instrument in self.aliases: candidates.append(self.aliases[instrument])
        candidates += [instrument, instrument.replace("USD", "USD."), instrument+"m", instrument+".m", instrument+".a"]
        for name in candidates:
            info=self.mt5.symbol_info(name)
            if info is not None:
                if not getattr(info,"visible",True): self.mt5.symbol_select(name,True)
                return name
        raise LookupError(f"MT5 symbol not found for {instrument}; configure an explicit alias")
