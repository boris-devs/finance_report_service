"""Состояние сущностей на заданную дату.

Выгрузка отражает «сейчас», а отчёт нужен «на дату», поэтому статус
восстанавливаем по датам событий, а не по полю status.
"""
from datetime import date

from finance_report.domain.models import Contract, Payment, Work, WorkStatus


def contract_exists(contract: Contract, on: date) -> bool:
    return contract.signed_at <= on


def work_is_active(work: Work, on: date) -> bool:
    """Работа не отменена на дату (отмена позже даты отчёта ещё не случилась)."""
    return not (work.status is WorkStatus.CANCELLED and (work.cancelled_at is None or work.cancelled_at <= on))


def work_is_done(work: Work, on: date) -> bool:
    return work.status is WorkStatus.DONE and work.completed_at is not None and work.completed_at <= on


def payment_is_paid(payment: Payment, on: date) -> bool:
    """Деньги ушли к дате и ещё не были возвращены."""
    if payment.paid_at is None or payment.paid_at > on:
        return False
    return payment.refunded_at is None or payment.refunded_at > on


def payment_is_queued(payment: Payment, on: date) -> bool:
    """Заведён в учёт, но деньги к дате ещё не ушли."""
    return payment.created_at <= on and (payment.paid_at is None or payment.paid_at > on)
