"""Построение отчёта по договорам и работам на дату."""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from finance_report.domain.models import Contract, Dataset, Payment, Work
from finance_report.reporting.allocation import allocate_pool
from finance_report.reporting.as_of import (
    contract_exists, payment_is_paid, payment_is_queued, work_is_active, work_is_done,
)

ZERO = Decimal("0.00")


@dataclass(frozen=True)
class WorkLine:
    work_id: str
    contract_id: str
    title: str
    state: str  # done / planned / cancelled - на дату отчёта
    price: Decimal
    paid_direct: Decimal  # платежи, привязанные к работе
    paid_allocated: Decimal  # доля платежей по договору, отнесённая к работе
    remaining: Decimal

    @property
    def paid(self) -> Decimal:
        return self.paid_direct + self.paid_allocated


@dataclass(frozen=True)
class ContractSummary:
    contract_id: str
    contractor: str
    contract_amount: Decimal
    works_total: Decimal  # сумма цен неотменённых работ
    paid_total: Decimal  # всего ушло подрядчику (за вычетом возвратов)
    paid_on_works: Decimal
    unallocated: Decimal  # заплачено сверх цен работ
    remaining: Decimal  # осталось оплатить по работам
    queued: Decimal  # в очереди на оплату (в «осталось» не вычитается)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Report:
    as_of: date
    lines: list[WorkLine]
    contracts: list[ContractSummary]


def _sum(values) -> Decimal:
    return sum(values, ZERO)


def _work_state(work: Work, on: date) -> str:
    if not work_is_active(work, on):
        return "cancelled"
    return "done" if work_is_done(work, on) else "planned"


def _allocation_order(works: list[Work], on: date) -> list[Work]:
    """Сначала принятые (по дате приёмки), затем остальные по номеру."""
    done = sorted((w for w in works if work_is_done(w, on)), key=lambda w: (w.completed_at, w.id))
    rest = sorted((w for w in works if not work_is_done(w, on)), key=lambda w: w.id)
    return done + rest


def _contract_report(
    contract: Contract, works: list[Work], payments: list[Payment], on: date
) -> tuple[list[WorkLine], ContractSummary]:
    active = [w for w in works if work_is_active(w, on)]
    active_ids = {w.id for w in active}
    paid = [p for p in payments if payment_is_paid(p, on)]
    warnings: list[str] = []

    direct: dict[str, Decimal] = {}
    pool = ZERO
    for p in paid:
        if p.work_id in active_ids:
            direct[p.work_id] = direct.get(p.work_id, ZERO) + p.amount
        else:
            pool += p.amount
            if p.work_id:
                warnings.append(
                    f"{p.id}: привязан к отменённой/неизвестной работе {p.work_id}, "
                    "учтён как платёж по договору"
                )

    alloc = allocate_pool(_allocation_order(active, on), direct, pool)

    lines = []
    for w in sorted(works, key=lambda w: w.id):
        state = _work_state(w, on)
        if state == "cancelled":
            lines.append(WorkLine(w.id, w.contract_id, w.title, state, w.price, ZERO, ZERO, ZERO))
            continue
        d = direct.get(w.id, ZERO)
        a = alloc.by_work[w.id]
        lines.append(WorkLine(w.id, w.contract_id, w.title, state, w.price, d, a, max(w.price - d - a, ZERO)))

    active_lines = [l for l in lines if l.state != "cancelled"]
    works_total = _sum(l.price for l in active_lines)
    if works_total != contract.amount:
        warnings.append(
            f"сумма договора {contract.amount} не равна сумме неотменённых работ {works_total} "
            f"(разница {contract.amount - works_total})"
        )
    if alloc.leftover:
        warnings.append(f"переплата сверх цен работ: {alloc.leftover}")

    summary = ContractSummary(
        contract_id=contract.id,
        contractor=contract.contractor,
        contract_amount=contract.amount,
        works_total=works_total,
        paid_total=_sum(p.amount for p in paid),
        paid_on_works=_sum(l.paid for l in active_lines),
        unallocated=alloc.leftover,
        remaining=_sum(l.remaining for l in active_lines),
        queued=_sum(p.amount for p in payments if payment_is_queued(p, on)),
        warnings=warnings,
    )
    return lines, summary


def build_report(data: Dataset, on: date) -> Report:
    lines: list[WorkLine] = []
    summaries: list[ContractSummary] = []
    for contract in sorted(data.contracts, key=lambda c: c.id):
        if not contract_exists(contract, on):
            continue
        works = [w for w in data.works if w.contract_id == contract.id]
        payments = [p for p in data.payments if p.contract_id == contract.id]
        c_lines, summary = _contract_report(contract, works, payments, on)
        lines += c_lines
        summaries.append(summary)
    return Report(on, lines, summaries)
