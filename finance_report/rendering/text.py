"""Вывод отчёта в виде текстовых таблиц."""
from decimal import Decimal

from finance_report.reporting.report import Report

STATE_RU = {"done": "принята", "planned": "в плане", "cancelled": "отменена"}

def money(value: Decimal) -> str:
    return f"{value:,.2f}".replace(",", " ")


def _table(headers: list[str], rows: list[list[str]], left: int) -> str:
    """Первые `left` колонок выравниваются влево, остальные (суммы) вправо."""
    widths = [max(len(cell) for cell in col) for col in zip(headers, *rows)]

    def fmt(row: list[str]) -> str:
        cells = [c.ljust(w) if i < left else c.rjust(w) for i, (c, w) in enumerate(zip(row, widths))]
        return "  ".join(cells)

    return "\n".join([fmt(headers), "  ".join("-" * w for w in widths), *map(fmt, rows)])


def render_text(report: Report) -> str:
    works = _table(
        ["Договор", "Работа", "Статус", "Цена", "Выплачено", "Осталось"],
        [[l.contract_id, f"{l.work_id} {l.title}", STATE_RU[l.state],
          money(l.price), money(l.paid), money(l.remaining)] for l in report.lines],
        left=3,
    )
    contracts = _table(
        ["Договор", "Подрядчик", "Сумма дог.", "Работы", "Выплачено", "Осталось", "Переплата", "В очереди"],
        [[c.contract_id, c.contractor, money(c.contract_amount), money(c.works_total),
          money(c.paid_total), money(c.remaining), money(c.unallocated), money(c.queued)]
         for c in report.contracts],
        left=2,
    )
    warnings = [f"[{c.contract_id}] {w}" for c in report.contracts for w in c.warnings]
    parts = [f"Отчёт на {report.as_of:%d.%m.%Y}", "", "По работам:", works, "", "По договорам:", contracts]
    if warnings:
        parts += ["", "Обратите внимание:", *warnings]
    return "\n".join(parts)
