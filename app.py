# app.py
from datetime import date
from flask import Flask, render_template, request, redirect, url_for

from config import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    INVESTMENT_CATEGORIES,
    DEFAULT_TYPES,
    default_date_range,
)
from utils.io_utils import load_all, append_transaction
from utils.filters import filter_by_date, filter_by_types, filter_by_categories, filter_by_query
from utils.stats import summary_totals, monthly_summary, expenses_by_category, cumulative_balance
from utils.plots import plot_monthly_summary, plot_expenses_by_category, plot_cumulative_balance


app = Flask(__name__)


@app.route("/")
def index():
    df = load_all()

    # Filters from query params
    start_default, end_default = default_date_range()
    start = request.args.get("from", start_default)
    end = request.args.get("to", end_default)

    # Types: getlist() because multiple checkboxes
    types = request.args.getlist("types")
    if not types:
        types = DEFAULT_TYPES[:]  # default: all three

    # Categories: getlist() because <select multiple>
    categories = request.args.getlist("category")

    q = request.args.get("q", "").strip()

    # Apply filters
    df_filtered = df.copy()
    df_filtered = filter_by_date(df_filtered, start, end)
    df_filtered = filter_by_types(df_filtered, types)
    df_filtered = filter_by_categories(df_filtered, categories)
    df_filtered = filter_by_query(df_filtered, q)

    # Prepare display-friendly columns
    if not df_filtered.empty:
        df_filtered = df_filtered.copy()
        df_filtered["date_str"] = df_filtered["date"].dt.strftime("%Y-%m-%d")
        df_filtered["amount_str"] = df_filtered["amount"].map(lambda x: f"{x:.2f}")
    else:
        df_filtered["date_str"] = []
        df_filtered["amount_str"] = []

    # Stats
    totals = summary_totals(df_filtered)
    df_month = monthly_summary(df_filtered, start=start, end=end)
    df_cat = expenses_by_category(df_filtered)
    df_cum = cumulative_balance(df_filtered)

    # Plots
    plot_monthly_summary(df_month)
    plot_expenses_by_category(df_cat)
    plot_cumulative_balance(df_cum)

    # All unique categories in filtered data (for dropdown)
    all_categories = sorted(df["category"].dropna().unique().tolist()) if not df.empty else []

    return render_template(
        "index.html",
        transactions=df_filtered.to_dict(orient="records"),
        totals=totals,
        start=start,
        end=end,
        active_types=types,
        all_types=DEFAULT_TYPES,
        categories_selected=categories,
        categories_all=all_categories,
        q=q,
    )


@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        ttype = request.form.get("type")
        date_str = request.form.get("date")
        category = request.form.get("category")
        sub_category = request.form.get("sub_category", "")
        amount_str = request.form.get("amount", "0").replace(",", ".")
        account = request.form.get("account", "")
        description = request.form.get("description", "")

        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0

        tx = {
            "type": ttype,
            "date": date_str,
            "category": category,
            "sub_category": sub_category,
            "amount": amount,
            "account": account,
            "description": description,
        }

        append_transaction(tx)

        return redirect(url_for("index"))

    # GET
    ttype = request.args.get("type", "expense")
    if ttype not in DEFAULT_TYPES:
        ttype = "expense"

    if ttype == "expense":
        categories = EXPENSE_CATEGORIES
    elif ttype == "income":
        categories = INCOME_CATEGORIES
    else:
        categories = INVESTMENT_CATEGORIES

    today = date.today().isoformat()

    return render_template(
        "add_transaction.html",
        ttype=ttype,
        categories=categories,
        today=today,
    )


if __name__ == "__main__":
    app.run(debug=True)
