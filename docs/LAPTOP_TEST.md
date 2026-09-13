# PrimeAura laptop test

## 1. Open the repository
Open a terminal in the PrimeAura checkout.

## 2. Create/activate the virtual environment
PowerShell:

    python -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1

If activation is blocked, use .\\.venv\\Scripts\\python.exe directly.

## 3. Install dependencies
Use the repository's dependency file if present:

    python -m pip install -r requirements.txt

Do not guess a dependency set if the file does not exist.

## 4. Run tests

    python -m pytest -q

Treat the first failure as the starting point for debugging.

## 5. MT5 connectivity
Install the MetaTrader 5 Python package in the same environment, open the desktop MT5 terminal, and ensure the broker's XAUUSD/XAGUSD symbols exist. A dedicated MT5 smoke-test command will be exposed later.

PrimeAura is read-only. Do not add order-placement code or credentials.

## Current status
The repository has data ingestion, validation, SMC analysis, MTF confluence, signal generation, scanner foundations, and research/backtesting components. The finished user-facing browser UI/CLI is not yet complete.