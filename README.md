# Отчёт по оплате работ и договоров

Консольная программа на Python 3.12 (только стандартная библиотека). По CSV из `data/` и дате строит отчёт:
по каждой работе — цена, выплачено, осталось оплатить; по каждому договору — итоги.

## Запуск

```bash
python -m finance_report --date 10.11.2026
python -m finance_report --date 2026-11-10 --data-dir data --csv-dir out   # + сохранить CSV
```

Дата — `ДД.ММ.ГГГГ` или `ГГГГ-ММ-ДД`. Тесты: `python -m unittest discover -s tests -t .`

## Архитектура (модули)

| Модуль | Ответственность |
|---|---|
| `domain/models.py` | Неизменяемые модели (Decimal для денег) |
| `loading/csv_loader.py` | Чтение CSV → модели |
| `reporting/as_of.py` | Состояние работ/платежей на дату |
| `reporting/allocation.py` | Раскладка платежей без привязки по работам |
| `reporting/report.py` | Сборка отчёта |
| `rendering/` | Вывод: текст, CSV (расчёт от вывода не зависит) |
| `cli.py` | Аргументы командной строки |

Допущения и решения — в [DECISIONS.md](DECISIONS.md), записка бухгалтеру — в [NOTE_FOR_ACCOUNTANT.md](NOTE_FOR_ACCOUNTANT.md).
