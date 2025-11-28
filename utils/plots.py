# utils/plots.py
from pathlib import Path

import matplotlib
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
