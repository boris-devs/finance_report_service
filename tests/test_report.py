import unittest
from datetime import date
from decimal import Decimal as D
from pathlib import Path

from finance_report.loading.csv_loader import load_dataset
from finance_report.reporting.allocation import allocate_pool
from finance_report.reporting.report import build_report
from finance_report.domain.models import Work, WorkStatus

DATA = Path(__file__).resolve().parent.parent / "data"
ON = date(2026, 11, 10)


class SampleDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report(load_dataset(DATA), ON)
        cls.works = {l.work_id: l for l in cls.report.lines}
        cls.contracts = {c.contract_id: c for c in cls.report.contracts}

    def test_d1_works(self):
        paid = {w: self.works[w].paid for w in ("W-11", "W-12", "W-13", "W-14", "W-15", "W-16")}
        self.assertEqual(paid, {"W-11": D(100000), "W-12": D(100000), "W-13": D(0),
                                "W-14": D(100000), "W-15": D(15000), "W-16": D(0)})

    def test_d1_totals(self):
        c = self.contracts["D-1"]
        self.assertEqual((c.paid_total, c.remaining, c.queued), (D(315000), D(185000), D(150000)))

    def test_refund_is_not_paid(self):  # P-2 возвращён 10.09
        self.assertEqual(self.contracts["D-1"].paid_total, D(315000))

    def test_payment_after_date_ignored(self):  # P-8 от 12.11
        self.assertEqual(self.contracts["D-2"].paid_total, D(75000))

    def test_work_completed_after_date_is_planned(self):  # W-23 принята 11.11
        self.assertEqual(self.works["W-23"].state, "planned")
        self.assertEqual(self.works["W-23"].remaining, D(15000))

    def test_refund_not_yet_happened(self):
        r = build_report(load_dataset(DATA), date(2026, 9, 5))
        self.assertEqual({c.contract_id: c.paid_total for c in r.contracts}["D-1"], D(350000))

    def test_cancelled_after_date_is_active(self):
        r = build_report(load_dataset(DATA), date(2026, 10, 1))
        self.assertEqual({l.work_id: l.state for l in r.lines}["W-13"], "planned")


class AllocationTest(unittest.TestCase):
    def _w(self, id, price):
        return Work(id, "D", id, D(price), WorkStatus.DONE, None, None)

    def test_fifo_and_leftover(self):
        a = allocate_pool([self._w("A", 100), self._w("B", 50)], {}, D(170))
        self.assertEqual(a.by_work, {"A": D(100), "B": D(50)})
        self.assertEqual(a.leftover, D(20))

    def test_direct_payment_reduces_room(self):
        a = allocate_pool([self._w("A", 100)], {"A": D(30)}, D(100))
        self.assertEqual((a.by_work["A"], a.leftover), (D(70), D(30)))


if __name__ == "__main__":
    unittest.main()
