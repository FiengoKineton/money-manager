from datetime import date
import csv
import calendar
from config import DATA_DIR
from utils.pending_utils import append_pending, load_pending

RECURRING_CSV = DATA_DIR / "recurring.csv"

RECURRING_FIELDS = [
    "id",
    "name",
    "type",
    "amount",
    "frequency",
    "day_of_month",
    "category",
    "start_date",
    "last_generated",
]


def _ensure_recurring_csv():
    """Create recurring.csv with the correct header if it does not exist."""
    if not RECURRING_CSV.exists():
        with RECURRING_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=RECURRING_FIELDS)
            writer.writeheader()


def _normalize_row(row):
    """
    Keep the recurring CSV schema stable even if older rows miss columns.
    This prevents DictWriter errors and makes old files easier to migrate.
    """
    normalized = {field: row.get(field, "") for field in RECURRING_FIELDS}

    if not normalized["frequency"]:
        normalized["frequency"] = "monthly"

    return normalized


def _write_recurring(rows):
    _ensure_recurring_csv()
    with RECURRING_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RECURRING_FIELDS)
        writer.writeheader()
        writer.writerows([_normalize_row(r) for r in rows])


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def get_valid_date(year, month, desired_day):
    """Return the real calendar day for this month, clamping 29/30/31 safely."""
    last_day = calendar.monthrange(year, month)[1]
    desired_day = max(1, min(int(desired_day), 31))
    return min(desired_day, last_day)


def load_recurring():
    _ensure_recurring_csv()
    with RECURRING_CSV.open(newline="", encoding="utf-8") as f:
        return [_normalize_row(row) for row in csv.DictReader(f)]


def _already_generated_this_month(row, today):
    """
    A monthly recurring rule can only generate once for each year/month.
    This is the key check that prevents duplicates when the page is refreshed.
    """
    last_generated = _parse_date(row.get("last_generated"))
    if not last_generated:
        return False

    return last_generated.year == today.year and last_generated.month == today.month


def _matching_pending_exists(row, due_date):
    """
    Safety net for rows created before last_generated existed/was updated.
    If a matching pending/executed item already exists for this same month,
    do not create another one.
    """
    due = due_date.isoformat()
    name = str(row.get("name", ""))
    r_type = str(row.get("type", ""))
    category = str(row.get("category", ""))

    try:
        amount = float(row.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0.0

    for tx in load_pending():
        if tx.get("date_due") != due:
            continue
        if tx.get("description") != name:
            continue
        if tx.get("type") != r_type:
            continue
        if tx.get("category") != category:
            continue

        try:
            tx_amount = float(tx.get("amount", 0))
        except (TypeError, ValueError):
            tx_amount = 0.0

        if abs(tx_amount - amount) < 0.01:
            return True

    return False


def generate_recurring(today=None):
    """
    Generate due monthly recurring payments exactly once per month.

    Important behavior:
    - Uses last_generated to remember the month that has already run.
    - Checks the actual due date, not only the day number.
    - Does not backfill the current month if the rule was created after this
      month's due date.
    - Returns the number of new pending rows created.
    """
    today = today or date.today()
    rows = load_recurring()

    changed = False
    created = 0

    for row in rows:
        if row.get("frequency", "monthly") != "monthly":
            continue

        try:
            desired_day = int(row.get("day_of_month", 1))
        except (TypeError, ValueError):
            desired_day = 1

        valid_day = get_valid_date(today.year, today.month, desired_day)
        due_date = date(today.year, today.month, valid_day)

        # Do not generate before the due date.
        if today < due_date:
            continue

        # Do not generate for a month that was already processed.
        if _already_generated_this_month(row, today):
            continue

        # If the rule was created after this month's due date, do not create
        # a retroactive payment. It will start from next month.
        start_date = _parse_date(row.get("start_date"))
        if start_date and due_date < start_date:
            continue

        # Extra protection for older data where last_generated may still be blank.
        if _matching_pending_exists(row, due_date):
            row["last_generated"] = due_date.isoformat()
            changed = True
            continue

        append_pending(
            {
                "type": row["type"],
                "amount": float(row["amount"]),
                "category": row["category"],
                "account": "auto",
                "description": row["name"],
            },
            due_date,
        )

        row["last_generated"] = due_date.isoformat()
        changed = True
        created += 1

    if changed:
        _write_recurring(rows)

    return created


def append_recurring(rule):
    rows = load_recurring()
    new_id = max([int(r["id"]) for r in rows if str(r.get("id", "")).isdigit()], default=0) + 1

    row = {
        "id": str(new_id),
        "name": rule["name"],
        "type": rule["type"],
        "amount": str(rule["amount"]),
        "frequency": "monthly",
        "day_of_month": str(rule["day_of_month"]),
        "category": rule["category"],
        "start_date": date.today().isoformat(),
        "last_generated": "",
    }

    rows.append(row)
    _write_recurring(rows)


def delete_recurring(rule_id):
    rows = load_recurring()
    rows = [r for r in rows if int(r["id"]) != rule_id]
    _write_recurring(rows)
