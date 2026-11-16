"""Распределение платежей без привязки к работе по работам договора."""
from dataclasses import dataclass
from decimal import Decimal

from finance_report.domain.models import Work


@dataclass(frozen=True)
class Allocation:
    by_work: dict[str, Decimal]  # work_id -> сколько отнесено из общего пула
    leftover: Decimal  # что не поместилось ни в одну работу


def allocate_pool(works_in_order: list[Work], direct: dict[str, Decimal], pool: Decimal) -> Allocation:
    """Раскладывает пул по работам в заданном порядке (FIFO).

    Каждая работа берёт не больше, чем ей не хватает до цены с учётом
    платежей, уже привязанных к ней напрямую.
    """
    by_work: dict[str, Decimal] = {}
    for work in works_in_order:
        room = max(work.price - direct.get(work.id, Decimal(0)), Decimal(0))
        take = min(room, pool)
        by_work[work.id] = take
        pool -= take
    return Allocation(by_work, pool)
