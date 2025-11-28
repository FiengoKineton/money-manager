# utils/stats.py
import pandas as pd


def summary_totals(df: pd.DataFrame) -> dict:
    """Return total income, expense, investment, net and savings rate."""
    income = df[df["type"] == "income"]["signed_amount"].sum()
    # signed_amount for expenses & investments is negative
    expenses = df[df["type"] == "expense"]["signed_amount"].sum()
    investments = df[df["type"] == "investment"]["signed_amount"].sum()
    net = df["signed_amount"].sum()

    # convert expenses/investments back to positive for reporting
    expenses_abs = -expenses
    investments_abs = -investments

    savings_rate = 0.0
    if income > 1e-9:
        savings_rate = max(net, 0.0) / income * 100.0

    return {
        "income": float(income),
        "expenses": float(expenses_abs),
        "investments": float(investments_abs),
        "net": float(net),
        "savings_rate": float(savings_rate),
    }



def monthly_summary(df: pd.DataFrame, start: str | None = None, end: str | None = None) -> pd.DataFrame:
    """Income, expenses, investments, net per month over [start, end], with all months included."""
    if df.empty:
        return pd.DataFrame(columns=["month", "income", "expenses", "investments", "net"])

    # Determine month range from selected dates
    if start:
        start_dt = pd.to_datetime(start, errors="coerce")
    else:
        start_dt = df["date"].min()

    if end:
        end_dt = pd.to_datetime(end, errors="coerce")
    else:
        end_dt = df["date"].max()

    if pd.isna(start_dt) or pd.isna(end_dt):
        return pd.DataFrame(columns=["month", "income", "expenses", "investments", "net"])

    # Month range from start month to end month
    month_range = pd.period_range(start=start_dt.to_period("M"),
                                  end=end_dt.to_period("M"),
                                  freq="M")
    month_index = month_range.astype(str)

    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")

    def agg_signed(sub):
        income = sub[sub["type"] == "income"]["signed_amount"].sum()
        expenses = sub[sub["type"] == "expense"]["signed_amount"].sum()
        investments = sub[sub["type"] == "investment"]["signed_amount"].sum()
        net = sub["signed_amount"].sum()
        # positive for reporting
        return pd.Series({
            "income": income,
            "expenses": -expenses,
            "investments": -investments,
            "net": net,
        })

    grouped = df.groupby("month").apply(agg_signed)
    grouped.index = grouped.index.astype(str)

    # Reindex over full month grid, fill missing with 0
    grouped = grouped.reindex(month_index, fill_value=0.0).reset_index()
    grouped = grouped.rename(columns={"index": "month"})
    return grouped



def expenses_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Total expenses per category."""
    ex = df[df["type"] == "expense"]
    if ex.empty:
        return pd.DataFrame(columns=["category", "total"])
    grouped = ex.groupby("category")["signed_amount"].sum().reset_index()
    grouped["total"] = -grouped["signed_amount"]
    grouped = grouped.drop(columns=["signed_amount"])
    return grouped.sort_values(by="total", ascending=False)


def cumulative_balance(df: pd.DataFrame) -> pd.DataFrame:
    """Cumulative sum of signed_amount ordered by date."""
    if df.empty:
        return pd.DataFrame(columns=["date", "balance"])
    df = df.sort_values(by="date")
    cum = df[["date", "signed_amount"]].copy()
    cum["balance"] = cum["signed_amount"].cumsum()
    return cum[["date", "balance"]]
