"""Доменные модели. Все деньги - Decimal, все даты - date."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class WorkStatus(StrEnum):
    PLANNED = "planned"
    DONE = "done"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PAID = "paid"
    QUEUED = "queued"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class Contract:
    id: str
    contractor: str
    amount: Decimal
    signed_at: date


@dataclass(frozen=True)
class Work:
    id: str
    contract_id: str
    title: str
    price: Decimal
    status: WorkStatus
    completed_at: date | None
    cancelled_at: date | None


@dataclass(frozen=True)
class Payment:
    id: str
    contract_id: str
    work_id: str | None
    purpose: str
    amount: Decimal
    status: PaymentStatus
    created_at: date
    paid_at: date | None
    refunded_at: date | None


@dataclass(frozen=True)
class Dataset:
    contracts: list[Contract]
    works: list[Work]
    payments: list[Payment]
