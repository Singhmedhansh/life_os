import importlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from styles import apply_workspace_theme


DATA_DIR = Path("data")


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _scan_csv_for_keys(path: Path, keys: list[str]) -> float:
    try:
        df = pd.read_csv(path)
    except Exception:
        return 0.0

    total = 0.0
    lowered = {c.lower(): c for c in df.columns}
    for key in keys:
        for col_l, col in lowered.items():
            if key in col_l:
                total += pd.to_numeric(df[col], errors="coerce").fillna(0).sum()
    return _safe_number(total, 0.0)


def _scan_json_for_keys(path: Path, keys: list[str]) -> float:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0.0

    def walk(node: Any) -> float:
        subtotal = 0.0
        if isinstance(node, dict):
            for k, v in node.items():
                k_l = str(k).lower()
                if any(key in k_l for key in keys):
                    subtotal += _safe_number(v, 0.0)
                subtotal += walk(v)
        elif isinstance(node, list):
            for item in node:
                subtotal += walk(item)
        return subtotal

    return walk(payload)


def _compute_kpis() -> dict[str, str]:
    expenses = 0.0
    academic_progress = 0.0
    habit_streak = 0.0

    if DATA_DIR.exists():
        for file in DATA_DIR.glob("*"):
            suffix = file.suffix.lower()
            if suffix == ".csv":
                expenses += _scan_csv_for_keys(file, ["expense", "spent", "amount", "cost"])
                academic_progress += _scan_csv_for_keys(file, ["progress", "grade", "score", "completion"])
                habit_streak += _scan_csv_for_keys(file, ["streak", "habit", "days"])
            elif suffix == ".json":
                expenses += _scan_json_for_keys(file, ["expense", "spent", "amount", "cost"])
                academic_progress += _scan_json_for_keys(file, ["progress", "grade", "score", "completion"])
                habit_streak += _scan_json_for_keys(file, ["streak", "habit", "days"])

    academic_pct = min(100.0, max(0.0, academic_progress))
    return {
        "Total Expenses": f"${expenses:,.2f}",
        "Academic Progress": f"{academic_pct:.0f}%",
        "Habit Streaks": f"{habit_streak:.0f} days",
        "Data Sources": str(len(list(DATA_DIR.glob('*')))) if DATA_DIR.exists() else "0",
    }


def _render_dashboard() -> None:
    st.title("Dashboard")
    st.caption("Your productivity workspace at a glance")
    st.divider()

    kpis = _compute_kpis()
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Expenses", kpis["Total Expenses"])
    with c2:
        st.metric("Academic Progress", kpis["Academic Progress"])
    with c3:
        st.metric("Habit Streaks", kpis["Habit Streaks"])
    with c4:
        st.metric("Data Sources", kpis["Data Sources"])

    st.markdown('<p class="kpi-caption">Minimal summary view · no-scroll KPIs</p>', unsafe_allow_html=True)
    st.divider()


def _run_view(module_name: str) -> None:
    module = importlib.import_module(module_name)
    candidates = ("render", "show", "app", "main", "run", "page")
    for fn_name in candidates:
        fn = getattr(module, fn_name, None)
        if callable(fn):
            fn()
            return
    st.warning(f"No callable entrypoint found in `{module_name}`. Tried: {', '.join(candidates)}")


def main() -> None:
    st.set_page_config(page_title="Life OS", page_icon="🧩", layout="wide")
    apply_workspace_theme()

    st.sidebar.markdown("### Life OS")
    page = st.sidebar.radio(
        "Navigation",
        options=["🏠 Dashboard", "💰 Finance", "📚 Academics", "⚡ Health"],
        index=0,
        label_visibility="collapsed",
    )

    if page == "🏠 Dashboard":
        _render_dashboard()
    elif page == "💰 Finance":
        _run_view("views.finance")
    elif page == "📚 Academics":
        _run_view("views.academics")
    elif page == "⚡ Health":
        _run_view("views.health")


if __name__ == "__main__":
    main()