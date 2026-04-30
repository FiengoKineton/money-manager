from datetime import date
import csv, calendar
from pathlib import Path
from config import DATA_DIR
from utils.pending_utils import append_pending

RECURRING_CSV = DATA_DIR / "recurring.csv"


def get_valid_date(year, month, desired_day):
    last_day = calendar.monthrange(year, month)[1]
    return min(desired_day, last_day)

def load_recurring():
    if not RECURRING_CSV.exists():
        return []
    with RECURRING_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_recurring():
    today = date.today()
    rules = load_recurring()

    for r in rules:
        desired_day = int(r["day_of_month"])

        valid_day = get_valid_date(today.year, today.month, desired_day)

        if today.day == valid_day:
            append_pending({
                "type": r["type"],
                "amount": float(r["amount"]),
                "category": r["category"],
                "account": "auto",
                "description": r["name"],
            }, today)


def append_recurring(rule):
    path = RECURRING_CSV

    fieldnames = [
        "id", "name", "type", "amount", "category",
        "frequency", "day_of_month", "start_date", "last_generated"
    ]

    rows = load_recurring()
    new_id = max([int(r["id"]) for r in rows], default=0) + 1

    row = {
        "id": new_id,
        "name": rule["name"],
        "type": rule["type"],
        "category": rule["category"],
        "amount": str(rule["amount"]),
        "frequency": "monthly",
        "day_of_month": str(rule["day_of_month"]),
        "start_date": "",
        "last_generated": "",
    }

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if path.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(row)


def delete_recurring(rule_id):
    rows = load_recurring()
    rows = [r for r in rows if int(r["id"]) != rule_id]

    if rows:
        with RECURRING_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

