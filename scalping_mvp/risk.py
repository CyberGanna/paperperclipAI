from __future__ import annotations

import math

from .models import Direction, MarketSnapshot, RiskDecision, RiskLimits, TradeSignal


class RiskEngine:
    """Fail-closed, deterministic pre-trade risk gate."""

    def evaluate(
        self,
        signal: TradeSignal,
        market: MarketSnapshot,
        limits: RiskLimits,
        daily_pnl: float,
        open_notional: float = 0.0,
    ) -> RiskDecision:
        if signal.direction is Direction.FLAT:
            return RiskDecision(False, 0, "flat signal")
        if not 0 < signal.confidence <= 1:
            return RiskDecision(False, 0, "confidence must be between 0 and 1")
        if market.spread_bps > limits.max_spread_bps:
            return RiskDecision(False, 0, "spread limit exceeded")
        if daily_pnl <= -(limits.equity * limits.max_daily_loss):
            return RiskDecision(False, 0, "daily loss limit reached")

        if signal.direction is Direction.LONG:
            if not signal.stop_loss < signal.entry < signal.take_profit:
                return RiskDecision(False, 0, "invalid long levels")
        else:
            if not signal.take_profit < signal.entry < signal.stop_loss:
                return RiskDecision(False, 0, "invalid short levels")

        risk_per_unit = abs(signal.entry - signal.stop_loss)
        if risk_per_unit <= 0:
            return RiskDecision(False, 0, "stop distance must be positive")

        risk_budget = limits.equity * limits.max_risk_per_trade
        quantity_by_risk = math.floor(risk_budget / risk_per_unit)
        remaining_notional = limits.max_position_notional - open_notional
        quantity_by_notional = math.floor(max(0.0, remaining_notional) / signal.entry)
        quantity = min(quantity_by_risk, quantity_by_notional)
        if quantity < 1:
            return RiskDecision(False, 0, "position size below minimum")
        return RiskDecision(True, quantity, "risk checks passed")
