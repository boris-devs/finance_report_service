"""Вывод отчёта в два CSV-файла (works_report.csv, contracts_report.csv)."""
import csv
from pathlib import Path

from finance_report.reporting.report import Report


def _write(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def write_csv(report: Report, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write(out_dir / "works_report.csv",
           ["contract_id", "work_id", "title", "state", "price", "paid", "remaining"],
           [[l.contract_id, l.work_id, l.title, l.state, l.price, l.paid, l.remaining] for l in report.lines])
    _write(out_dir / "contracts_report.csv",
           ["contract_id", "contractor", "contract_amount", "works_total", "paid_total",
            "paid_on_works", "remaining", "unallocated", "queued"],
           [[c.contract_id, c.contractor, c.contract_amount, c.works_total, c.paid_total,
             c.paid_on_works, c.remaining, c.unallocated, c.queued] for c in report.contracts])
