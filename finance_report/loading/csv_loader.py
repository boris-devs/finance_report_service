"""Чтение CSV-выгрузки в доменные модели."""
import csv
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from pathlib import Path

from finance_report.domain.models import (
    Contract, Dataset, Payment, PaymentStatus, Work, WorkStatus,
)


def _date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def _money(value: str) -> Decimal:
    return Decimal(value)


def _read[T](path: Path, build: Callable[[dict[str, str]], T]) -> list[T]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [build(row) for row in csv.DictReader(f)]


def _contract(r: dict[str, str]) -> Contract:
    return Contract(r["contract_id"], r["contractor"], _money(r["amount"]), _date(r["signed_at"]))


def _work(r: dict[str, str]) -> Work:
    return Work(
        r["work_id"], r["contract_id"], r["title"], _money(r["price"]),
        WorkStatus(r["status"]), _date(r["completed_at"]), _date(r["cancelled_at"]),
    )


def _payment(r: dict[str, str]) -> Payment:
    return Payment(
        r["payment_id"], r["contract_id"], r["work_id"] or None, r["purpose"],
        _money(r["amount"]), PaymentStatus(r["status"]),
        _date(r["created_at"]), _date(r["paid_at"]), _date(r["refunded_at"]),
    )


def load_dataset(data_dir: Path) -> Dataset:
    return Dataset(
        contracts=_read(data_dir / "contracts.csv", _contract),
        works=_read(data_dir / "works.csv", _work),
        payments=_read(data_dir / "payments.csv", _payment),
    )
