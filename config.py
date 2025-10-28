MONTHLY_BUDGET = 1000.0  # example

from config import MONTHLY_BUDGET

warning = None
if total > MONTHLY_BUDGET:
    warning = f"⚠️ Budget exceeded by ${total - MONTHLY_BUDGET:.2f}"

