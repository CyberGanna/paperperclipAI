from __future__ import annotations

from itertools import count

from .models import Direction, MarketSnapshot, PaperOrder, RiskDecision, TradeSignal


class PaperBroker:
    """Local paper broker. It never connects to an exchange or broker."""

    def __init__(self) -> None:
        self._ids = count(1)
        self.orders: list[PaperOrder] = []

    def submit(
        self,
        signal: TradeSignal,
        decision: RiskDecision,
        market: MarketSnapshot,
    ) -> PaperOrder:
        if not decision.approved:
            raise ValueError("cannot submit a rejected risk decision")
        order = PaperOrder(
            order_id=f"paper-{next(self._ids):06d}",
            symbol=signal.symbol,
            direction=signal.direction,
            quantity=decision.quantity,
            price=market.ask if signal.direction is Direction.LONG else market.bid,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            status="PAPER_FILLED",
        )
        self.orders.append(order)
        return order
