"""Точка входа: python -m finance_report --date 2026-11-10"""
import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from finance_report.loading.csv_loader import load_dataset
from finance_report.rendering.csv_files import write_csv
from finance_report.rendering.text import render_text
from finance_report.reporting.report import build_report

DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y")


def _parse_date(value: str) -> date:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"неверная дата: {value} (ГГГГ-ММ-ДД или ДД.ММ.ГГГГ)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Отчёт по оплате работ и договоров на дату")
    parser.add_argument("--date", type=_parse_date, required=True, help="дата отчёта")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="папка с CSV (по умолчанию data)")
    parser.add_argument("--csv-dir", type=Path, help="дополнительно сохранить CSV в эту папку")
    args = parser.parse_args(argv)

    sys.stdout.reconfigure(encoding="utf-8")
    report = build_report(load_dataset(args.data_dir), args.date)
    print(render_text(report))
    if args.csv_dir:
        write_csv(report, args.csv_dir)
    return 0
