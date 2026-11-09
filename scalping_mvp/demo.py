from datetime import datetime, timezone
import json

from .models import MarketSnapshot, RiskLimits
from .orchestrator import SimulationOrchestrator


def main() -> None:
    market = MarketSnapshot(
        symbol="AAPL",
        bid=190.00,
        ask=190.02,
        last=190.01,
        vwap=189.80,
        atr=0.20,
        timestamp=datetime.now(timezone.utc),
    )
    limits = RiskLimits(equity=10_000.0, max_position_notional=5_000.0)
    result = SimulationOrchestrator().run_once(market, limits)
    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()
