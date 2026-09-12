from enum import Enum


class SignalDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NO_SIGNAL = "NO_SIGNAL"


class SignalStatus(str, Enum):
    GENERATED = "GENERATED"
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    TP1_HIT = "TP1_HIT"
    TP2_HIT = "TP2_HIT"
    STOPPED = "STOPPED"
    EXPIRED = "EXPIRED"
    INVALIDATED = "INVALIDATED"
