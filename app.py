# app.py
"""
Launcher for the money manager.

- On machines with full dependencies (pandas, numpy, etc.),
  it runs app_complete.app.

- On minimal environments (e.g. Termux on phone) where that fails,
  it falls back to app_backup.app (CSV-only, no pandas).
"""

from __future__ import annotations

import traceback

"""try:
    from app_complete import app as full_app  # your existing heavy app
    app = full_app
    print("[money-manager] Using FULL app (app_complete.py).")
except Exception as e:
    print("[money-manager] Failed to start full app, falling back to SIMPLE app.")
    print("Reason:", repr(e))
    traceback.print_exc()"""
from app_backup import app as simple_app
app = simple_app
print("[money-manager] SIMPLE app (app_backup.py) running.")

if __name__ == "__main__":
    # host=0.0.0.0 so you can open it from the phone browser too
    app.run(host="0.0.0.0", port=5000, debug=True)
