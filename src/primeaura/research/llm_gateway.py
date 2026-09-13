from typing import Protocol

class LocalLLM(Protocol):
    def generate(self,prompt:str)->str: ...

class LLMResearchGateway:
    """Provider-neutral boundary for Ollama/OpenClaw/Hermes/local models.

    The research layer receives text/proposals only. It cannot access MT5
    trading APIs or execute orders.
    """
    def __init__(self,llm:LocalLLM): self.llm=llm
    def research(self,prompt:str)->str: return self.llm.generate(prompt)
