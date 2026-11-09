from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import Direction, MarketSnapshot, RiskLimits, TradeSignal
from .paper import PaperBroker
from .risk import RiskEngine


class SimulationOrchestrator:
    """Coordinates deterministic agents for the phase-1 simulation."""

    def __init__(self) -> None:
        self.risk = RiskEngine()
        self.paper = PaperBroker()

    def technical_analysis(self, market: MarketSnapshot) -> TradeSignal:
        if market.last > market.vwap and market.atr > 0:
            return TradeSignal(
                symbol=market.symbol,
                direction=Direction.LONG,
                entry=market.ask,
                stop_loss=market.ask - market.atr,
                take_profit=market.ask + (market.atr * 1.5),
                confidence=0.65,
                reason="price above VWAP with positive ATR regime",
            )
        if market.last < market.vwap and market.atr > 0:
            return TradeSignal(
                symbol=market.symbol,
                direction=Direction.SHORT,
                entry=market.bid,
                stop_loss=market.bid + market.atr,
                take_profit=market.bid - (market.atr * 1.5),
                confidence=0.65,
                reason="price below VWAP with positive ATR regime",
            )
        return TradeSignal(market.symbol, Direction.FLAT, market.last, market.last, market.last, 0.0, "no setup")

    def run_once(
        self,
        market: MarketSnapshot,
        limits: RiskLimits,
        daily_pnl: float = 0.0,
        open_notional: float = 0.0,
    ) -> dict[str, Any]:
        signal = self.technical_analysis(market)
        decision = self.risk.evaluate(signal, market, limits, daily_pnl, open_notional)
        result: dict[str, Any] = {
            "market": asdict(market),
            "signal": asdict(signal),
            "risk": asdict(decision),
        }
        if decision.approved:
            result["order"] = asdict(self.paper.submit(signal, decision, market))
        return result
