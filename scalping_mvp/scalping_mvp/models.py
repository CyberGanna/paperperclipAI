from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    bid: float
    ask: float
    last: float
    vwap: float
    atr: float
    timestamp: datetime

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread_bps(self) -> float:
        return ((self.ask - self.bid) / self.mid) * 10_000


@dataclass(frozen=True)
class TradeSignal:
    symbol: str
    direction: Direction
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float
    reason: str


@dataclass(frozen=True)
class RiskLimits:
    equity: float
    max_risk_per_trade: float = 0.005
    max_daily_loss: float = 0.02
    max_position_notional: float = 10_000.0
    max_spread_bps: float = 15.0


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    quantity: int
    reason: str


@dataclass(frozen=True)
class PaperOrder:
    order_id: str
    symbol: str
    direction: Direction
    quantity: int
    price: float
    stop_loss: float
    take_profit: float
    status: str
