# utils/plots.py
from pathlib import Path

import matplotlib, os
matplotlib.use("Agg")  # <--- ADD THIS: non-GUI backend

import matplotlib.pyplot as plt
import pandas as pd

from config import PLOTS_DIR


def plot_monthly_summary(df_monthly: pd.DataFrame, filename: str = "monthly_summary.png"):
    path = PLOTS_DIR / filename
    if df_monthly.empty:
        # create empty figure
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
        return

    fig, ax = plt.subplots(figsize=(7, 4))

    x = range(len(df_monthly))
    months = df_monthly["month"].tolist()

    ax.plot(x, df_monthly["income"], marker="o", label="Income")
    ax.plot(x, df_monthly["expenses"], marker="o", label="Expenses")
    ax.plot(x, df_monthly["investments"], marker="o", label="Investments")
    ax.plot(x, df_monthly["net"], marker="o", label="Net")

    ax.set_xticks(list(x))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_ylabel("Amount")
    ax.set_title("Monthly summary")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_expenses_by_category(df_cat: pd.DataFrame, filename: str = "expenses_by_category.png"):
    path = PLOTS_DIR / filename
    fig, ax = plt.subplots(figsize=(6, 4))

    if df_cat.empty:
        ax.text(0.5, 0.5, "No expenses", ha="center", va="center")
        ax.axis("off")
    else:
        cats = df_cat["category"].tolist()
        vals = df_cat["total"].tolist()
        ax.bar(cats, vals)
        ax.set_xticklabels(cats, rotation=45, ha="right")
        ax.set_ylabel("Total")
        ax.set_title("Expenses by category")
        ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_cumulative_balance(df_cum: pd.DataFrame, filename: str = "cumulative_balance.png"):
    path = PLOTS_DIR / filename
    fig, ax = plt.subplots(figsize=(7, 3))

    if df_cum.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        ax.axis("off")
    else:
        ax.plot(df_cum["date"], df_cum["balance"])
        ax.set_ylabel("Balance")
        ax.set_title("Cumulative balance")
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_weekday_spending(df_wd):
    """
    Bar chart: total expenses per weekday.
    """
    fig, ax = plt.subplots(figsize=(6, 3))

    if df_wd is not None and not df_wd.empty:
        ax.bar(df_wd["weekday"], df_wd["total"])
        ax.set_ylabel("Total expenses")
        ax.set_xlabel("Weekday")
    ax.set_title("Expenses by weekday")
    ax.grid(True, alpha=0.3)

    out = PLOTS_DIR / "weekday_spending.png"
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_rolling_net_flow(df_roll):
    """
    Line chart: daily net flow and 30-day rolling net.
    """
    fig, ax = plt.subplots(figsize=(7, 3))

    if df_roll is not None and not df_roll.empty:
        ax.plot(df_roll["date"], df_roll["daily_net"], label="Daily net")
        ax.plot(df_roll["date"], df_roll["rolling_net"], label="Rolling {}-day net".format(30))
        ax.legend()
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")

    ax.set_title("Net cash flow (daily & rolling)")
    ax.grid(True, alpha=0.3)

    out = PLOTS_DIR / "rolling_net_flow.png"
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_expenses_by_weekday(df_weekday,
                             out_path="static/plots/expenses_by_weekday.png"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))

    if df_weekday is None or df_weekday.empty:
        ax.text(0.5, 0.5, "No expense data",
                ha="center", va="center", fontsize=10)
        ax.axis("off")
    else:
        cats = df_weekday["weekday"].tolist()
        vals = df_weekday["total"].tolist()
        ax.bar(cats, vals)
        ax.set_ylabel("Total expenses")
        ax.set_xlabel("Weekday")
        ax.set_title("Expenses by weekday")
        ax.set_xticklabels(cats, rotation=45, ha="right")

    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

