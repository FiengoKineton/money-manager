import csv
from datetime import date
from pathlib import Path
from config import DATA_DIR

PENDING_CSV = DATA_DIR / "pending.csv"


def _ensure_csv():
    if not PENDING_CSV.exists():
        with PENDING_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "type", "date_due", "amount",
                "category", "account", "description", "status"
            ])


def load_pending():
    _ensure_csv()
    with PENDING_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _next_id():
    rows = load_pending()
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1


def append_pending(tx, due_date):
    _ensure_csv()
    row = {
        "id": _next_id(),
        "type": tx["type"],
        "date_due": due_date.isoformat(),
        "amount": tx["amount"],
        "category": tx["category"],
        "account": tx["account"],
        "description": tx["description"],
        "status": "pending",
    }

    with PENDING_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)


def mark_executed(tx_id):
    rows = load_pending()
    for r in rows:
        if int(r["id"]) == tx_id:
            r["status"] = "executed"

    with PENDING_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)